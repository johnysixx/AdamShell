"""A44 SQLite checkpoint revision-floor source.

A local, transactional checkpoint revision floor.

Public operations:

    bootstrap(...) -> create a new database exclusively
    open(...)      -> open and validate existing database
    hold()         -> hold a consistent revision snapshot
    advance_if_current(...) -> local SQLite transactional CAS

SECURITY BOUNDARY:

- Provides persistence across ordinary file reopen.
- SQLite transactions coordinate local concurrent readers
  and writers using the rollback-journal locking model.
- CAS is atomic within this single SQLite database.
- Caller-supplied root pins are NOT independently enrolled.
- Replacing the database with an older valid copy can
  roll back the stored revision.
- This is NOT a rollback-resistant external trust anchor.
- No genuine power-loss or hardware durability is proven.
- No atomicity with a separate signed backend is proven.
- No actual external backend CAS linearizability is proven.
- No checkpoint restore or republication is authorized.

Database files must be protected by the deployment
environment. Python objects are not a security boundary.

An error during publication can leave the outcome uncertain.
Inspect the database before considering a retry.
"""

import hmac
import os
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)


_MAX_SQLITE_INTEGER = (1 << 63) - 1
_LOCK_TIMEOUT_SECONDS = 0.15

_SCHEMA = """
CREATE TABLE checkpoint_revision_floor (
    singleton_id INTEGER PRIMARY KEY
        CHECK (singleton_id = 1),
    root_id TEXT NOT NULL,
    root_public_key BLOB NOT NULL,
    enrollment_epoch INTEGER NOT NULL
        CHECK (enrollment_epoch >= 0),
    minimum_revision INTEGER NOT NULL
        CHECK (minimum_revision >= 0)
)
"""


def _require_path(value):
    if type(value) is str:
        if not value:
            raise ValueError(
                "Invalid checkpoint floor database path."
            )

        value = Path(value)

    if not isinstance(value, Path):
        raise ValueError(
            "Invalid checkpoint floor database path."
        )

    if not str(value):
        raise ValueError(
            "Invalid checkpoint floor database path."
        )

    return value


def _require_public_key(value, name):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(
            f"Invalid {name}: expected 32 immutable bytes."
        )

    return bytes(value)


def _require_integer(value, name):
    if (
        type(value) is not int
        or value < 0
        or value > _MAX_SQLITE_INTEGER
    ):
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _require_root(root_id, root_public_key, epoch):
    root_id = _require_identity(
        root_id,
        "checkpoint floor root identity",
    )

    root_public_key = _require_public_key(
        root_public_key,
        "checkpoint floor root public key",
    )

    epoch = _require_integer(
        epoch,
        "checkpoint floor enrollment epoch",
    )

    return root_id, root_public_key, epoch


@dataclass(frozen=True, slots=True)
class SQLiteCheckpointRevisionFloorSource:
    """SQLite-backed held checkpoint revision floor.

    The stored high-water mark only protects against
    ordinary local restarts and concurrent publication.

    It does not survive an attacker replacing the file
    with an older valid database.
    """

    _path: Path
    expected_root_id: str
    expected_root_public_key: bytes
    expected_epoch: int

    def __post_init__(self):
        _require_path(self._path)

        _require_root(
            self.expected_root_id,
            self.expected_root_public_key,
            self.expected_epoch,
        )

    def _connect(self, *, readonly):
        """Open an EXISTING database, never implicitly create one."""

        connection = None

        try:
            path_uri = self._path.resolve(
                strict=True
            ).as_uri()

            mode = "ro" if readonly else "rw"

            connection = sqlite3.connect(
                f"{path_uri}?mode={mode}",
                uri=True,
                isolation_level=None,
                timeout=_LOCK_TIMEOUT_SECONDS,
            )

            connection.execute(
                "PRAGMA busy_timeout=150"
            )

            if not readonly:
                connection.execute(
                    "PRAGMA synchronous=FULL"
                )

            return connection

        except (
            OSError,
            sqlite3.Error,
            ValueError,
        ) as exc:
            if connection is not None:
                connection.close()

            raise ValueError(
                "Checkpoint SQLite floor database unavailable."
            ) from exc

    def _validated_snapshot(self, connection):
        """Read exactly one row and enforce the pinned identity."""

        rows = connection.execute(
            "SELECT singleton_id, root_id, root_public_key, "
            "enrollment_epoch, minimum_revision "
            "FROM checkpoint_revision_floor"
        ).fetchall()

        # The SELECT establishes the SQLite read snapshot.
        # Verify the journal mode INSIDE that transaction.
        #
        # In WAL mode a writer may commit while this read
        # transaction remains active, breaking the held
        # publication-exclusion contract.
        #
        # Reject rather than silently switching modes.
        # Changing journal mode belongs to provisioning.
        journal_mode = connection.execute(
            "PRAGMA journal_mode"
        ).fetchone()

        if (
            type(journal_mode) is not tuple
            or len(journal_mode) != 1
            or type(journal_mode[0]) is not str
            or journal_mode[0].lower() != "delete"
        ):
            raise ValueError(
                "Unsupported checkpoint SQLite journal mode."
            )

        if len(rows) != 1:
            raise ValueError(
                "Missing or ambiguous checkpoint floor row."
            )

        (
            singleton_id,
            root_id,
            public_key,
            epoch,
            revision,
        ) = rows[0]

        if (
            type(singleton_id) is not int
            or singleton_id != 1
        ):
            raise ValueError(
                "Invalid checkpoint floor singleton."
            )

        root_id, public_key, epoch = _require_root(
            root_id,
            public_key,
            epoch,
        )

        revision = _require_integer(
            revision,
            "stored checkpoint floor revision",
        )

        if root_id != self.expected_root_id:
            raise ValueError(
                "Checkpoint floor root identity mismatch."
            )

        if not hmac.compare_digest(
            public_key,
            self.expected_root_public_key,
        ):
            raise ValueError(
                "Checkpoint floor root public key mismatch."
            )

        if epoch != self.expected_epoch:
            raise ValueError(
                "Checkpoint floor enrollment epoch mismatch."
            )

        return (
            root_id,
            bytes(public_key),
            epoch,
            revision,
        )

    @classmethod
    def bootstrap(
        cls,
        *,
        path,
        root_id,
        root_public_key,
        enrollment_epoch,
        minimum_revision,
    ):
        """Create a new floor without overwriting an old one.

        Validation occurs BEFORE creating the database file.
        Exclusive creation prevents ordinary rebootstrap.

        This operation does not independently enroll keys.
        """

        target = _require_path(path)

        root_id, root_public_key, epoch = (
            _require_root(
                root_id,
                root_public_key,
                enrollment_epoch,
            )
        )

        revision = _require_integer(
            minimum_revision,
            "initial checkpoint floor revision",
        )

        try:
            fd = os.open(
                target,
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
            )

            os.close(fd)

        except OSError as exc:
            raise ValueError(
                "Checkpoint floor already exists "
                "or cannot be created."
            ) from exc

        store = cls(
            _path=target,
            expected_root_id=root_id,
            expected_root_public_key=root_public_key,
            expected_epoch=epoch,
        )

        try:
            with closing(
                store._connect(readonly=False)
            ) as connection:

                try:
                    journal = connection.execute(
                        "PRAGMA journal_mode=DELETE"
                    ).fetchone()

                    if (
                        type(journal) is not tuple
                        or len(journal) != 1
                        or str(journal[0]).lower() != "delete"
                    ):
                        raise ValueError(
                            "Checkpoint SQLite rollback journal "
                            "mode unavailable."
                        )

                    connection.execute(
                        "BEGIN IMMEDIATE"
                    )

                    connection.execute(
                        _SCHEMA
                    )

                    connection.execute(
                        "INSERT INTO checkpoint_revision_floor "
                        "(singleton_id, root_id, root_public_key, "
                        "enrollment_epoch, minimum_revision) "
                        "VALUES (1, ?, ?, ?, ?)",
                        (
                            root_id,
                            root_public_key,
                            epoch,
                            revision,
                        ),
                    )

                    connection.commit()

                except BaseException:
                    if connection.in_transaction:
                        connection.rollback()

                    raise

            # Reopen and verify the actual stored row.
            with store.hold() as snapshot:
                if snapshot[3] != revision:
                    raise ValueError(
                        "Initial checkpoint floor mismatch."
                    )

            return store

        except Exception as exc:
            # Do not silently remove a file that might
            # already contain a partially committed state.
            # Manual inspection is safer than blind retry.
            raise ValueError(
                "Checkpoint floor initialization failed; "
                "inspect database before retry."
            ) from exc

    @classmethod
    def open(
        cls,
        *,
        path,
        expected_root_id,
        expected_root_public_key,
        expected_epoch,
    ):
        """Open an existing database and validate its held row."""

        try:
            target = _require_path(path)

            root_id, root_public_key, epoch = (
                _require_root(
                    expected_root_id,
                    expected_root_public_key,
                    expected_epoch,
                )
            )

            store = cls(
                _path=target,
                expected_root_id=root_id,
                expected_root_public_key=root_public_key,
                expected_epoch=epoch,
            )

            with store.hold():
                pass

            return store

        except Exception as exc:
            raise ValueError(
                "Checkpoint SQLite floor open failed."
            ) from exc

    @contextmanager
    def hold(self):
        """Hold a read transaction through caller verification.

        In SQLite rollback-journal mode, this read transaction
        prevents a conflicting writer from committing while
        the held snapshot is in use.

        All paths close the connection and release the lock.
        """

        try:
            self.__post_init__()

            with closing(
                self._connect(readonly=True)
            ) as connection:

                try:
                    connection.execute(
                        "BEGIN"
                    )

                    snapshot = self._validated_snapshot(
                        connection
                    )

                    yield snapshot

                finally:
                    if connection.in_transaction:
                        connection.rollback()

        except Exception as exc:
            raise ValueError(
                "Checkpoint SQLite held floor read failed."
            ) from exc

    def advance_if_current(
        self,
        *,
        expected_revision,
        next_revision,
    ):
        """Atomically advance the local SQLite revision floor.

        The transaction serializes local writers.

        Failed stale CAS operations never publish the target.
        A commit-related error may have an uncertain outcome:
        this method does not automatically retry or roll back
        a previously committed publication.
        """

        try:
            self.__post_init__()

            predecessor = _require_integer(
                expected_revision,
                "expected checkpoint floor predecessor",
            )

            target = _require_integer(
                next_revision,
                "next checkpoint floor revision",
            )

            if target <= predecessor:
                raise ValueError(
                    "Checkpoint floor target must increase."
                )

            with closing(
                self._connect(readonly=False)
            ) as connection:

                try:
                    connection.execute(
                        "BEGIN IMMEDIATE"
                    )

                    current = self._validated_snapshot(
                        connection
                    )

                    if current[3] != predecessor:
                        raise ValueError(
                            "Stale checkpoint floor CAS predecessor."
                        )

                    updated = connection.execute(
                        "UPDATE checkpoint_revision_floor "
                        "SET minimum_revision = ? "
                        "WHERE singleton_id = 1 "
                        "AND minimum_revision = ?",
                        (
                            target,
                            predecessor,
                        ),
                    )

                    if updated.rowcount != 1:
                        raise ValueError(
                            "Checkpoint floor CAS changed no row."
                        )

                    connection.commit()

                    return (
                        current[0],
                        current[1],
                        current[2],
                        target,
                    )

                except BaseException:
                    if connection.in_transaction:
                        connection.rollback()

                    raise

        except Exception as exc:
            raise ValueError(
                "Checkpoint SQLite floor CAS failed; "
                "inspect state before retry."
            ) from exc
