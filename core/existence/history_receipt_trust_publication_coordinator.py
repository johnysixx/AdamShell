"""Experimental A44 trust publication coordinator.

Coordinates PREPARE, APPLY and FINALIZE against an injected
publication authority.

This is NOT a production security boundary. The injected
authority must independently guarantee authenticated identity,
durable atomic compare-and-swap, monotonic committed state,
and cross-process exclusion.

The current test authority is volatile. Existing uncoordinated
SQLite publication and legacy verification APIs remain callable.

No automatic crash recovery is implemented.
"""

import hmac
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass

from core.existence.history_receipt_trust_floor import (
    DurableProviderReceiptTrustFloor,
    _catalog_fingerprints,
    _read_floor,
)
from core.existence.history_receipt_trust_publication_state import (
    _valid_snapshot,
)


def _target_snapshot(lifecycle):
    sources, catalog = _catalog_fingerprints(lifecycle)

    snapshot = (
        lifecycle.revision,
        sources,
        catalog,
    )

    if not _valid_snapshot(snapshot):
        raise ValueError(
            "Invalid target trust catalog snapshot."
        )

    return snapshot


def _operation_id(value):
    if (
        type(value) is not str
        or not value
        or value != value.strip()
    ):
        raise ValueError(
            "Invalid publication operation identity."
        )

    return value


def _validate_state(state):
    if type(state) is not tuple or len(state) != 2:
        raise ValueError(
            "Malformed publication authority state."
        )

    committed, pending = state

    if not _valid_snapshot(committed):
        raise ValueError(
            "Invalid committed authority snapshot."
        )

    if pending is not None:
        if (
            type(pending) is not tuple
            or len(pending) != 2
        ):
            raise ValueError(
                "Malformed pending publication."
            )

        pending_id, pending_target = pending

        _operation_id(pending_id)

        if not _valid_snapshot(pending_target):
            raise ValueError(
                "Invalid pending publication target."
            )

        _require_newer_target(
            committed,
            pending_target,
        )

    return committed, pending


def _require_newer_target(committed, target):
    if not _valid_snapshot(target):
        raise ValueError(
            "Invalid target publication snapshot."
        )

    if target[0] <= committed[0]:
        raise ValueError(
            "Target revision must exceed committed revision."
        )

    if not hmac.compare_digest(
        committed[1],
        target[1],
    ):
        raise ValueError(
            "Pinned provider identities cannot change."
        )


@dataclass(frozen=True, slots=True)
class TrustPublicationCoordinator:
    """Coordinate publication under an injected authority lease.

    Every operation acquires the authority lease before taking
    the SQLite write transaction. The authority implementation
    must enforce that same serialization for verification.

    This coordinator does not authenticate the authority or
    make volatile state durable.
    """

    store: DurableProviderReceiptTrustFloor
    authority: object

    @contextmanager
    def _hold_authority(self):
        if type(self.store) is not DurableProviderReceiptTrustFloor:
            raise ValueError(
                "Invalid durable trust floor."
            )

        hold = getattr(
            self.authority,
            "hold_write",
            None,
        )

        read = getattr(
            self.authority,
            "read_state",
            None,
        )

        if not callable(hold) or not callable(read):
            raise ValueError(
                "Publication authority is unavailable."
            )

        try:
            with hold():
                committed, pending = _validate_state(
                    read()
                )

                yield committed, pending

        except OSError as exc:
            raise ValueError(
                "Publication authority is unavailable."
            ) from exc

    @contextmanager
    def _sqlite_transaction(self):
        try:
            with closing(
                self.store._connect(readonly=False)
            ) as connection:

                connection.execute("BEGIN IMMEDIATE")

                try:
                    yield connection
                    connection.commit()

                except BaseException:
                    connection.rollback()
                    raise

        except (OSError, sqlite3.Error) as exc:
            raise ValueError(
                "Trust publication SQLite transaction failed."
            ) from exc

    def prepare(self, lifecycle, *, operation_id):
        """Record a pending revision before any SQLite change."""

        operation_id = _operation_id(operation_id)
        target = _target_snapshot(lifecycle)

        with self._hold_authority() as (
            committed,
            pending,
        ):
            _require_newer_target(committed, target)

            if pending is not None:
                if pending != (operation_id, target):
                    raise ValueError(
                        "Conflicting pending publication."
                    )

            prepare = getattr(
                self.authority,
                "prepare",
                None,
            )

            if not callable(prepare):
                raise ValueError(
                    "Authority cannot prepare publication."
                )

            with self._sqlite_transaction() as connection:
                stored = _read_floor(connection)

                if pending is None:
                    if stored != committed:
                        raise ValueError(
                            "SQLite and committed authority "
                            "do not agree before PREPARE."
                        )

                elif stored not in (committed, target):
                    raise ValueError(
                        "Cannot retry PREPARE against "
                        "conflicting SQLite state."
                    )

                return prepare(
                    expected_committed=committed,
                    operation_id=operation_id,
                    target=target,
                )

    def apply(self, lifecycle, *, operation_id):
        """Apply the exact pending target to SQLite.

        A repeated APPLY for the same target is permitted.
        Pending authority state is never cleared here.
        """

        operation_id = _operation_id(operation_id)
        target = _target_snapshot(lifecycle)

        with self._hold_authority() as (
            committed,
            pending,
        ):
            _require_newer_target(committed, target)

            if pending != (operation_id, target):
                raise ValueError(
                    "No matching prepared publication."
                )

            with self._sqlite_transaction() as connection:
                stored = _read_floor(connection)

                if stored == target:
                    # Idempotent retry after the first APPLY.
                    return False

                if stored != committed:
                    raise ValueError(
                        "Conflicting SQLite publication state."
                    )

                cursor = connection.execute(
                    "UPDATE trust_floor "
                    "SET revision=?, catalog_digest=? "
                    "WHERE singleton_id=1 "
                    "AND revision=? "
                    "AND source_ids_digest=? "
                    "AND catalog_digest=?",
                    (
                        target[0],
                        target[2],
                        committed[0],
                        committed[1],
                        committed[2],
                    ),
                )

                if cursor.rowcount != 1:
                    raise ValueError(
                        "SQLite publication CAS failed."
                    )

                return True

    def finalize(self, lifecycle, *, operation_id):
        """Finalize only after SQLite contains the target.

        A durable authority must atomically replace committed
        trust and remove pending state using authenticated CAS.
        The test authority does not provide durability.
        """

        operation_id = _operation_id(operation_id)
        target = _target_snapshot(lifecycle)

        with self._hold_authority() as (
            committed,
            pending,
        ):
            _require_newer_target(committed, target)

            if pending != (operation_id, target):
                raise ValueError(
                    "No matching prepared publication."
                )

            finalize = getattr(
                self.authority,
                "finalize",
                None,
            )

            if not callable(finalize):
                raise ValueError(
                    "Authority cannot finalize publication."
                )

            with self._sqlite_transaction() as connection:
                if _read_floor(connection) != target:
                    raise ValueError(
                        "Cannot finalize before the exact "
                        "SQLite target is applied."
                    )

                # The SQLite lock remains held until the
                # authority finalization call completes.
                finalize(
                    expected_committed=committed,
                    operation_id=operation_id,
                    target=target,
                )

                return True
