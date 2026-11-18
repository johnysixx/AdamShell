"""Experimental local durable incident outbox for AdamShell A44.

SQLite provides ordinary restart durability and serialized local
writes, not an authenticated trust root, tamper resistance, or
rollback protection.

Acknowledgement is a local assertion, not independent proof that
the intended Universe contains the referenced Cronenberg.

This module does not authorize security-sensitive operations,
create Cronenbergs, or hold signing keys.
"""

import os
import re
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import RLock


_SCHEMA_VERSION = 2
_MAX_CAPACITY = 4096
_MAX_BATCH = 256

_ID = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z"
)

_CRONENBERG = re.compile(
    r"cronenberg_[0-9a-f]{8}\Z"
)

_OPERATIONS = frozenset({
    "signed_manifest_bootstrap",
    "authority_reply",
    "publication_fence",
    "receipt_signature",
    "security_validation",
})


class SecurityIncidentStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"


@dataclass(frozen=True, slots=True)
class SecurityIncidentRecord:
    incident_id: str
    source_operation: str
    status: SecurityIncidentStatus
    cronenberg_id: str | None


def _require_incident_id(value):
    if (
        type(value) is not str
        or _ID.fullmatch(value) is None
    ):
        raise ValueError(
            "Invalid security incident identifier."
        )

    return value


def _require_operation(value):
    if (
        type(value) is not str
        or value not in _OPERATIONS
    ):
        raise ValueError(
            "Invalid security incident operation."
        )

    return value


def _require_cronenberg_id(value):
    if (
        type(value) is not str
        or _CRONENBERG.fullmatch(value) is None
    ):
        raise ValueError(
            "Invalid Cronenberg identifier."
        )

    return value


def _require_capacity(value):
    if (
        type(value) is not int
        or not 1 <= value <= _MAX_CAPACITY
    ):
        raise ValueError(
            "Invalid pending incident capacity."
        )

    return value


def _require_batch_limit(value):
    if (
        type(value) is not int
        or not 1 <= value <= _MAX_BATCH
    ):
        raise ValueError(
            "Invalid pending incident batch limit."
        )

    return value


def _decode_record(row):
    if (
        type(row) is not tuple
        or len(row) != 4
    ):
        raise ValueError(
            "Invalid security incident record."
        )

    (
        incident_id,
        source_operation,
        status,
        cronenberg_id,
    ) = row

    _require_incident_id(incident_id)
    _require_operation(source_operation)

    if type(status) is not str:
        raise ValueError(
            "Invalid incident status."
        )

    try:
        state = SecurityIncidentStatus(status)

    except ValueError as exc:
        raise ValueError(
            "Invalid incident status."
        ) from exc

    if state is SecurityIncidentStatus.PENDING:
        if cronenberg_id is not None:
            raise ValueError(
                "Pending incident has a delivery binding."
            )

    else:
        _require_cronenberg_id(cronenberg_id)

    return SecurityIncidentRecord(
        incident_id=incident_id,
        source_operation=source_operation,
        status=state,
        cronenberg_id=cronenberg_id,
    )


@dataclass(frozen=True, slots=True)
class LocalDurableSecurityIncidentOutbox:
    """Local transactional incident record, not a trust authority."""

    _path: Path

    _lock: object = field(
        default_factory=RLock,
        repr=False,
        compare=False,
    )

    def _connect(self, *, readonly):
        try:
            uri = self._path.resolve(
                strict=True
            ).as_uri()

            mode = (
                "ro"
                if readonly
                else "rw"
            )

            return sqlite3.connect(
                f"{uri}?mode={mode}",
                uri=True,
                isolation_level=None,
                timeout=10.0,
            )

        except (OSError, sqlite3.Error) as exc:
            raise ValueError(
                "Security incident database unavailable."
            ) from exc

    @contextmanager
    def _transaction(self, *, readonly):
        with self._lock:
            try:
                with closing(
                    self._connect(readonly=readonly)
                ) as connection:

                    connection.execute(
                        "BEGIN"
                        if readonly
                        else "BEGIN IMMEDIATE"
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
                    "Security incident transaction failed."
                ) from exc

    @staticmethod
    def _metadata(connection):
        rows = connection.execute(
            "SELECT singleton_id, schema_version, "
            "max_pending, max_total "
            "FROM incident_outbox_metadata"
        ).fetchall()

        if (
            len(rows) != 1
            or rows[0][0] != 1
            or rows[0][1] != _SCHEMA_VERSION
        ):
            raise ValueError(
                "Missing or invalid incident metadata."
            )

        max_pending = _require_capacity(rows[0][2])
        max_total = _require_capacity(rows[0][3])

        if max_total < max_pending:
            raise ValueError(
                "Total capacity below pending capacity."
            )

        return max_pending, max_total

    @classmethod
    def _validate_history(cls, connection):
        """Validate all retained incidents, including delivered."""

        max_pending, max_total = cls._metadata(connection)

        total = 0
        pending = 0
        previous_sequence = 0

        rows = connection.execute(
            "SELECT sequence, incident_id, "
            "source_operation, status, cronenberg_id "
            "FROM security_incidents "
            "ORDER BY sequence ASC"
        )

        for row in rows:
            sequence = row[0]

            if (
                type(sequence) is not int
                or sequence <= previous_sequence
                or sequence < 1
            ):
                raise ValueError(
                    "Invalid historical incident sequence."
                )

            previous_sequence = sequence

            incident = _decode_record(tuple(row[1:]))

            total += 1

            if total > max_total:
                raise ValueError(
                    "Total incident history capacity exceeded."
                )

            if (
                incident.status
                is SecurityIncidentStatus.PENDING
            ):
                pending += 1

                if pending > max_pending:
                    raise ValueError(
                        "Pending incident capacity exceeded."
                    )

        return max_pending, max_total, total, pending

    @classmethod
    def create(
        cls,
        path,
        *,
        max_pending=256,
        max_total=4096,
    ):
        """Exclusively initialize bounded local SQLite storage."""

        _require_capacity(max_pending)
        _require_capacity(max_total)

        if max_total < max_pending:
            raise ValueError(
                "Total capacity below pending capacity."
            )

        target = Path(path)

        try:
            fd = os.open(
                target,
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
            )

        except OSError as exc:
            raise ValueError(
                "Incident outbox exists or cannot be created."
            ) from exc

        else:
            os.close(fd)

        store = cls(target)

        with store._transaction(
            readonly=False
        ) as connection:

            connection.execute(
                "CREATE TABLE incident_outbox_metadata ("
                "singleton_id INTEGER PRIMARY KEY "
                "CHECK(singleton_id=1), "
                "schema_version INTEGER NOT NULL "
                "CHECK(schema_version=2), "
                "max_pending INTEGER NOT NULL "
                "CHECK(max_pending BETWEEN 1 AND 4096), "
                "max_total INTEGER NOT NULL "
                "CHECK(max_total BETWEEN 1 AND 4096 "
                "AND max_total >= max_pending))"
            )

            connection.execute(
                "CREATE TABLE security_incidents ("
                "sequence INTEGER PRIMARY KEY AUTOINCREMENT, "
                "incident_id TEXT NOT NULL UNIQUE, "
                "source_operation TEXT NOT NULL, "
                "status TEXT NOT NULL "
                "CHECK(status IN ('pending','delivered')), "
                "cronenberg_id TEXT UNIQUE, "
                "CHECK ((status='pending' "
                "AND cronenberg_id IS NULL) "
                "OR (status='delivered' "
                "AND cronenberg_id IS NOT NULL)))"
            )

            connection.execute(
                "INSERT INTO incident_outbox_metadata "
                "(singleton_id, schema_version, "
                "max_pending, max_total) "
                "VALUES (1, 2, ?, ?)",
                (max_pending, max_total),
            )

            connection.execute(
                "PRAGMA user_version=2"
            )

        return store

    @classmethod
    def open(cls, path):
        """Fail closed on malformed or unsupported incident history."""

        store = cls(Path(path))

        with store._transaction(
            readonly=True
        ) as connection:

            integrity = connection.execute(
                "PRAGMA quick_check"
            ).fetchone()

            if integrity != ("ok",):
                raise ValueError(
                    "Incident database integrity check failed."
                )

            version = connection.execute(
                "PRAGMA user_version"
            ).fetchone()

            if version != (_SCHEMA_VERSION,):
                raise ValueError(
                    "Unsupported incident schema version."
                )

            store._validate_history(connection)

        return store

    def get(self, incident_id):
        _require_incident_id(incident_id)

        with self._transaction(
            readonly=True
        ) as connection:

            self._validate_history(connection)

            row = connection.execute(
                "SELECT incident_id, source_operation, "
                "status, cronenberg_id "
                "FROM security_incidents "
                "WHERE incident_id=?",
                (incident_id,),
            ).fetchone()

            return (
                None
                if row is None
                else _decode_record(row)
            )

    def pending(self, *, limit=256):
        """Return a bounded FIFO batch of pending incidents."""

        _require_batch_limit(limit)

        with self._transaction(
            readonly=True
        ) as connection:

            self._validate_history(connection)

            rows = connection.execute(
                "SELECT incident_id, source_operation, "
                "status, cronenberg_id "
                "FROM security_incidents "
                "WHERE status='pending' "
                "ORDER BY sequence ASC LIMIT ?",
                (limit,),
            ).fetchall()

            return tuple(
                _decode_record(row)
                for row in rows
            )

    def record(self, incident_id, source_operation):
        """Record once, enforcing pending and total capacities."""

        _require_incident_id(incident_id)
        _require_operation(source_operation)

        with self._transaction(
            readonly=False
        ) as connection:

            (
                max_pending,
                max_total,
                current_total,
                current_pending,
            ) = self._validate_history(connection)

            row = connection.execute(
                "SELECT incident_id, source_operation, "
                "status, cronenberg_id "
                "FROM security_incidents "
                "WHERE incident_id=?",
                (incident_id,),
            ).fetchone()

            if row is not None:
                existing = _decode_record(row)

                if (
                    existing.source_operation
                    != source_operation
                ):
                    raise ValueError(
                        "Incident identity already assigned."
                    )

                return False

            if current_total >= max_total:
                raise ValueError(
                    "Total incident history capacity exhausted."
                )

            if current_pending >= max_pending:
                raise ValueError(
                    "Pending incident capacity exhausted."
                )

            connection.execute(
                "INSERT INTO security_incidents "
                "(incident_id, source_operation, "
                "status, cronenberg_id) "
                "VALUES (?, ?, 'pending', NULL)",
                (
                    incident_id,
                    source_operation,
                ),
            )

            return True

    def acknowledge(self, incident_id, cronenberg_id):
        """Store a local delivery claim, never authorization proof."""

        _require_incident_id(incident_id)
        _require_cronenberg_id(cronenberg_id)

        with self._transaction(
            readonly=False
        ) as connection:

            self._validate_history(connection)

            row = connection.execute(
                "SELECT incident_id, source_operation, "
                "status, cronenberg_id "
                "FROM security_incidents "
                "WHERE incident_id=?",
                (incident_id,),
            ).fetchone()

            if row is None:
                raise ValueError(
                    "Cannot acknowledge an unknown incident."
                )

            existing = _decode_record(row)

            if (
                existing.status
                is SecurityIncidentStatus.DELIVERED
            ):
                if existing.cronenberg_id == cronenberg_id:
                    return False

                raise ValueError(
                    "Conflicting Cronenberg acknowledgement."
                )

            changed = connection.execute(
                "UPDATE security_incidents "
                "SET status='delivered', cronenberg_id=? "
                "WHERE incident_id=? AND status='pending' "
                "AND cronenberg_id IS NULL",
                (
                    cronenberg_id,
                    incident_id,
                ),
            )

            if changed.rowcount != 1:
                raise ValueError(
                    "Incident acknowledgement conflict."
                )

            return True
