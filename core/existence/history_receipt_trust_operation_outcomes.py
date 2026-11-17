"""Local durable operation outcomes for A44; NOT a trusted authority.

SQLite provides atomic local transactions and ordinary restart
persistence. A file rollback or replacement can rewrite both trust
and outcome history.

This class is deliberately NOT wired into production authorization.
"""

import hmac
import os
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import RLock

from core.existence.history_receipt_trust_publication_state import (
    _valid_snapshot,
)


_STATE_SCHEMA = """
CREATE TABLE authority_state (
    singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
    revision INTEGER NOT NULL CHECK(revision >= 1),
    source_ids_digest TEXT NOT NULL,
    catalog_digest TEXT NOT NULL
)
"""

_BOOTSTRAP_SCHEMA = """
CREATE TABLE bootstrap_state (
    singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
    revision INTEGER NOT NULL CHECK(revision >= 1),
    source_ids_digest TEXT NOT NULL,
    catalog_digest TEXT NOT NULL
)
"""

_OPERATION_SCHEMA = """
CREATE TABLE publication_operations (
    operation_id TEXT PRIMARY KEY,
    expected_revision INTEGER NOT NULL CHECK(expected_revision >= 1),
    expected_sources_digest TEXT NOT NULL,
    expected_catalog_digest TEXT NOT NULL,
    target_revision INTEGER NOT NULL CHECK(target_revision >= 1),
    target_sources_digest TEXT NOT NULL,
    target_catalog_digest TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('prepared', 'committed'))
)
"""

_PENDING_INDEX = """
CREATE UNIQUE INDEX one_pending_publication
ON publication_operations(status) WHERE status = 'prepared'
"""

_OPERATION_COLUMNS = (
    "operation_id, expected_revision, expected_sources_digest, "
    "expected_catalog_digest, target_revision, target_sources_digest, "
    "target_catalog_digest, status"
)


class PublicationOperationStatus(str, Enum):
    PREPARED = "prepared"
    COMMITTED = "committed"


@dataclass(frozen=True, slots=True)
class PublicationOperationOutcome:
    operation_id: str
    expected_committed: tuple
    target: tuple
    status: PublicationOperationStatus


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


def _snapshot(value):
    if not _valid_snapshot(value):
        raise ValueError(
            "Invalid publication catalog snapshot."
        )

    return value


def _require_target(predecessor, target):
    _snapshot(predecessor)
    _snapshot(target)

    if target[0] <= predecessor[0]:
        raise ValueError(
            "Target must increase committed revision."
        )

    if not hmac.compare_digest(
        predecessor[1],
        target[1],
    ):
        raise ValueError(
            "Pinned provider identities cannot change."
        )


def _decode_outcome(row):
    if row is None:
        return None

    if type(row) is not tuple or len(row) != 8:
        raise ValueError(
            "Malformed publication operation row."
        )

    operation_id, er, es, ec, tr, ts, tc, status = row

    _operation_id(operation_id)

    predecessor = _snapshot((er, es, ec))
    target = _snapshot((tr, ts, tc))

    _require_target(predecessor, target)

    try:
        state = PublicationOperationStatus(status)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            "Invalid publication outcome status."
        ) from exc

    return PublicationOperationOutcome(
        operation_id=operation_id,
        expected_committed=predecessor,
        target=target,
        status=state,
    )


def _get_outcome(connection, operation_id):
    row = connection.execute(
        f"SELECT {_OPERATION_COLUMNS} FROM publication_operations "
        "WHERE operation_id=?",
        (operation_id,),
    ).fetchone()

    return _decode_outcome(row)


def _read_bootstrap(connection):
    rows = connection.execute(
        "SELECT singleton_id, revision, "
        "source_ids_digest, catalog_digest "
        "FROM bootstrap_state"
    ).fetchall()

    if len(rows) != 1 or rows[0][0] != 1:
        raise ValueError(
            "Missing or ambiguous authority bootstrap."
        )

    return _snapshot(tuple(rows[0][1:]))


def _read_state(connection):
    rows = connection.execute(
        "SELECT singleton_id, revision, source_ids_digest, "
        "catalog_digest FROM authority_state"
    ).fetchall()

    if len(rows) != 1 or rows[0][0] != 1:
        raise ValueError(
            "Missing or ambiguous authority state."
        )

    committed = _snapshot(tuple(rows[0][1:]))

    # The genesis snapshot is recorded during bootstrap
    # in the same local SQLite database.
    #
    # It detects partial historical inconsistencies.
    # It does NOT prevent whole-file rollback or
    # coordinated rewriting of the entire database.
    predecessor = _read_bootstrap(connection)

    completed_rows = connection.execute(
        f"SELECT {_OPERATION_COLUMNS} "
        "FROM publication_operations "
        "WHERE status='committed' "
        "ORDER BY target_revision ASC, operation_id ASC"
    ).fetchall()

    for row in completed_rows:
        outcome = _decode_outcome(row)

        if (
            outcome.status
            is not PublicationOperationStatus.COMMITTED
        ):
            raise ValueError(
                "Unexpected historical operation status."
            )

        if outcome.expected_committed != predecessor:
            raise ValueError(
                "Broken committed publication history."
            )

        predecessor = outcome.target

    if predecessor != committed:
        raise ValueError(
            "Committed publication history does not "
            "match current authority state."
        )

    pending_rows = connection.execute(
        f"SELECT {_OPERATION_COLUMNS} "
        "FROM publication_operations "
        "WHERE status='prepared'"
    ).fetchall()

    if len(pending_rows) > 1:
        raise ValueError(
            "Conflicting pending authority operations."
        )

    if not pending_rows:
        return committed, None

    pending = _decode_outcome(pending_rows[0])

    if (
        pending.status
        is not PublicationOperationStatus.PREPARED
    ):
        raise ValueError(
            "Unexpected pending operation status."
        )

    if pending.expected_committed != committed:
        raise ValueError(
            "Prepared operation predecessor conflict."
        )

    return committed, (
        pending.operation_id,
        pending.target,
    )


@dataclass(frozen=True, slots=True)
class LocalDurablePublicationAuthority:
    """Local SQLite outcome store, not an authenticated trust root."""

    _path: Path
    _lock: object = field(
        default_factory=RLock,
        repr=False,
        compare=False,
    )

    def _connect(self, *, readonly):
        try:
            uri = self._path.resolve(strict=True).as_uri()
            mode = "ro" if readonly else "rw"

            return sqlite3.connect(
                f"{uri}?mode={mode}",
                uri=True,
                isolation_level=None,
                timeout=10.0,
            )

        except (OSError, sqlite3.Error) as exc:
            raise ValueError(
                "Local authority database unavailable."
            ) from exc

    @contextmanager
    def _transaction(self, *, readonly):
        with self._lock:
            try:
                with closing(
                    self._connect(readonly=readonly)
                ) as connection:

                    connection.execute(
                        "BEGIN" if readonly else "BEGIN IMMEDIATE"
                    )

                    try:
                        yield connection

                        if readonly:
                            connection.rollback()
                        else:
                            connection.commit()

                    except BaseException:
                        connection.rollback()
                        raise

            except (OSError, sqlite3.Error) as exc:
                raise ValueError(
                    "Local publication authority "
                    "transaction failed."
                ) from exc

    @classmethod
    def bootstrap(cls, path, committed):
        committed = _snapshot(committed)
        target = Path(path)

        try:
            fd = os.open(
                target,
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
            )

        except OSError as exc:
            raise ValueError(
                "Authority already exists or "
                "cannot be initialized."
            ) from exc

        else:
            os.close(fd)

        authority = cls(target)

        with authority._transaction(
            readonly=False
        ) as connection:

            connection.execute(_STATE_SCHEMA)
            connection.execute(_BOOTSTRAP_SCHEMA)
            connection.execute(_OPERATION_SCHEMA)
            connection.execute(_PENDING_INDEX)

            connection.execute(
                "INSERT INTO authority_state "
                "(singleton_id, revision, "
                "source_ids_digest, catalog_digest) "
                "VALUES (1, ?, ?, ?)",
                committed,
            )

            connection.execute(
                "INSERT INTO bootstrap_state "
                "(singleton_id, revision, "
                "source_ids_digest, catalog_digest) "
                "VALUES (1, ?, ?, ?)",
                committed,
            )

        return authority

    @classmethod
    def open(cls, path):
        authority = cls(Path(path))
        authority.read_state()
        return authority

    def read_state(self):
        with self._transaction(
            readonly=True
        ) as connection:
            return _read_state(connection)

    def query_operation(self, operation_id):
        operation_id = _operation_id(operation_id)

        with self._transaction(
            readonly=True
        ) as connection:
            _read_state(connection)

            return _get_outcome(
                connection,
                operation_id,
            )

    def prepare(
        self,
        *,
        expected_committed,
        operation_id,
        target,
    ):
        operation_id = _operation_id(operation_id)
        _require_target(expected_committed, target)

        with self._transaction(
            readonly=False
        ) as connection:

            committed, pending = _read_state(connection)

            previous = _get_outcome(
                connection,
                operation_id,
            )

            if previous is not None:
                if (
                    previous.expected_committed == expected_committed
                    and previous.target == target
                    and previous.status
                    is PublicationOperationStatus.PREPARED
                    and pending == (operation_id, target)
                ):
                    return False

                raise ValueError(
                    "Operation identity is already assigned."
                )

            if committed != expected_committed:
                raise ValueError(
                    "Committed authority CAS conflict."
                )

            if pending is not None:
                raise ValueError(
                    "Another publication is pending."
                )

            connection.execute(
                "INSERT INTO publication_operations "
                f"({_OPERATION_COLUMNS}) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    operation_id,
                    *expected_committed,
                    *target,
                    PublicationOperationStatus.PREPARED.value,
                ),
            )

            return True

    def finalize(
        self,
        *,
        expected_committed,
        operation_id,
        target,
    ):
        operation_id = _operation_id(operation_id)
        _require_target(expected_committed, target)

        with self._transaction(
            readonly=False
        ) as connection:

            committed, pending = _read_state(connection)

            previous = _get_outcome(
                connection,
                operation_id,
            )

            if (
                previous is None
                or previous.expected_committed != expected_committed
                or previous.target != target
            ):
                raise ValueError(
                    "No matching publication operation."
                )

            if (
                previous.status
                is PublicationOperationStatus.COMMITTED
            ):
                if committed == target and pending is None:
                    return False

                raise ValueError(
                    "Committed operation history conflicts."
                )

            if committed != expected_committed:
                raise ValueError(
                    "Committed authority CAS conflict."
                )

            if pending != (operation_id, target):
                raise ValueError(
                    "No matching pending publication."
                )

            cursor = connection.execute(
                "UPDATE authority_state "
                "SET revision=?, "
                "source_ids_digest=?, catalog_digest=? "
                "WHERE singleton_id=1 AND revision=? "
                "AND source_ids_digest=? AND catalog_digest=?",
                (*target, *expected_committed),
            )

            if cursor.rowcount != 1:
                raise ValueError(
                    "Committed authority update conflict."
                )

            cursor = connection.execute(
                "UPDATE publication_operations "
                "SET status='committed' "
                "WHERE operation_id=? AND status='prepared'",
                (operation_id,),
            )

            if cursor.rowcount != 1:
                raise ValueError(
                    "Outcome commit conflict."
                )

            return True
