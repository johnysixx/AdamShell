"""A44 experimental local durable publication witness journal.

PREPARED records local intent; OBSERVED records a local
assertion that some process saw a manifestation.

Neither state is an authenticated publication proof,
Universe reconstruction, authorization grant, or protection
against malicious file substitution, deletion, or rollback.
"""

import os
import re
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import RLock

from core.existence.history_receipt_trust_incident_outbox import (
    _require_cronenberg_id,
    _require_incident_id,
    _require_operation,
    _require_batch_limit,
)


_SCHEMA_VERSION = 1
_MAX_ENTRIES = 4096

_UNIVERSE_ID = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z"
)

_DIGEST = re.compile(
    r"[0-9a-f]{64}\Z"
)


class PublicationWitnessPhase(str, Enum):
    PREPARED = "prepared"
    OBSERVED = "observed"


@dataclass(frozen=True, slots=True)
class PublicationWitnessRecord:
    universe_id: str
    incident_id: str
    source_operation: str
    phase: PublicationWitnessPhase
    cronenberg_id: str | None
    manifestation_digest: str | None

    # Local observations are never authority evidence.
    is_authoritative: bool = field(
        default=False,
        init=False,
    )


def _require_universe_id(value):
    if (
        type(value) is not str
        or _UNIVERSE_ID.fullmatch(value) is None
    ):
        raise ValueError(
            "Invalid witness Universe identifier."
        )

    return value


def _require_digest(value):
    if (
        type(value) is not str
        or _DIGEST.fullmatch(value) is None
    ):
        raise ValueError(
            "Invalid manifestation digest."
        )

    return value


def _require_entries(value):
    if (
        type(value) is not int
        or not 1 <= value <= _MAX_ENTRIES
    ):
        raise ValueError(
            "Invalid witness journal capacity."
        )

    return value


def _decode_record(row, *, universe_id):
    if (
        type(row) is not tuple
        or len(row) != 6
    ):
        raise ValueError(
            "Invalid publication witness row."
        )

    (
        stored_universe,
        incident_id,
        operation,
        phase,
        cronenberg_id,
        digest,
    ) = row

    _require_universe_id(stored_universe)

    if stored_universe != universe_id:
        raise ValueError(
            "Publication witness belongs to another Universe."
        )

    _require_incident_id(incident_id)
    _require_operation(operation)

    if type(phase) is not str:
        raise ValueError(
            "Invalid witness phase."
        )

    try:
        state = PublicationWitnessPhase(phase)

    except ValueError as exc:
        raise ValueError(
            "Invalid witness phase."
        ) from exc

    if state is PublicationWitnessPhase.PREPARED:
        if (
            cronenberg_id is not None
            or digest is not None
        ):
            raise ValueError(
                "Prepared witness has an observation."
            )

    else:
        _require_cronenberg_id(cronenberg_id)
        _require_digest(digest)

    return PublicationWitnessRecord(
        universe_id=stored_universe,
        incident_id=incident_id,
        source_operation=operation,
        phase=state,
        cronenberg_id=cronenberg_id,
        manifestation_digest=digest,
    )


@dataclass(frozen=True, slots=True)
class LocalDurablePublicationWitnessJournal:
    """Bounded local SQLite claims, not a trust authority."""

    _path: Path
    _universe_id: str

    _lock: object = field(
        default_factory=RLock,
        compare=False,
        repr=False,
    )

    def _connect(self, *, readonly):
        try:
            uri = self._path.resolve(
                strict=True
            ).as_uri()

            mode = "ro" if readonly else "rw"

            return sqlite3.connect(
                f"{uri}?mode={mode}",
                uri=True,
                isolation_level=None,
                timeout=10.0,
            )

        except (sqlite3.Error, OSError) as exc:
            raise ValueError(
                "Publication witness database unavailable."
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
                    "Publication witness transaction failed."
                ) from exc

    def _metadata(self, connection):
        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()

        if version != (_SCHEMA_VERSION,):
            raise ValueError(
                "Unsupported publication witness schema version."
            )

        rows = connection.execute(
            "SELECT singleton_id, schema_version, "
            "universe_id, max_entries "
            "FROM publication_witness_metadata"
        ).fetchall()

        if (
            len(rows) != 1
            or rows[0][0] != 1
            or rows[0][1] != _SCHEMA_VERSION
        ):
            raise ValueError(
                "Missing or invalid publication witness metadata."
            )

        bound_id = _require_universe_id(
            rows[0][2]
        )

        if bound_id != self._universe_id:
            raise ValueError(
                "Publication witness Universe identity mismatch."
            )

        return _require_entries(rows[0][3])

    def _validate_history(self, connection):
        """Validate all prepared AND observed history."""

        capacity = self._metadata(connection)

        previous = 0
        total = 0

        seen_incidents = set()
        seen_cronenbergs = set()

        rows = connection.execute(
            "SELECT sequence, universe_id, incident_id, "
            "source_operation, phase, cronenberg_id, "
            "manifestation_digest "
            "FROM publication_witnesses "
            "ORDER BY sequence ASC"
        )

        for row in rows:
            sequence = row[0]

            if (
                type(sequence) is not int
                or sequence != previous + 1
            ):
                raise ValueError(
                    "Invalid witness history sequence."
                )

            previous = sequence

            entry = _decode_record(
                tuple(row[1:]),
                universe_id=self._universe_id,
            )

            if entry.incident_id in seen_incidents:
                raise ValueError(
                    "Duplicate historical witness incident identity."
                )

            seen_incidents.add(entry.incident_id)

            if entry.cronenberg_id is not None:
                if entry.cronenberg_id in seen_cronenbergs:
                    raise ValueError(
                        "Duplicate historical witness Cronenberg identity."
                    )

                seen_cronenbergs.add(entry.cronenberg_id)

            total += 1

            if total > capacity:
                raise ValueError(
                    "Publication witness capacity exceeded."
                )

        # Detect ordinary history truncation or sequence
        # gaps. A malicious writer who rewrites both the
        # journal and metadata remains outside this model.
        sequence_row = connection.execute(
            "SELECT seq FROM sqlite_sequence "
            "WHERE name='publication_witnesses'"
        ).fetchone()

        if (
            (total == 0 and sequence_row is not None)
            or (
                total != 0
                and (
                    sequence_row is None
                    or type(sequence_row[0]) is not int
                    or sequence_row[0] != previous
                )
            )
        ):
            raise ValueError(
                "Publication witness append history mismatch."
            )

        return capacity, total

    @classmethod
    def create(
        cls,
        path,
        *,
        universe_id,
        max_entries=4096,
    ):
        """Exclusively create a Universe-scoped journal."""

        _require_universe_id(universe_id)
        _require_entries(max_entries)

        target = Path(path)

        try:
            fd = os.open(
                target,
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
            )

        except OSError as exc:
            raise ValueError(
                "Witness journal exists or cannot be created."
            ) from exc

        else:
            os.close(fd)

        store = cls(
            target,
            universe_id,
        )

        with store._transaction(
            readonly=False
        ) as connection:

            connection.execute(
                "CREATE TABLE publication_witness_metadata ("
                "singleton_id INTEGER PRIMARY KEY "
                "CHECK(singleton_id=1), "
                "schema_version INTEGER NOT NULL "
                "CHECK(schema_version=1), "
                "universe_id TEXT NOT NULL, "
                "max_entries INTEGER NOT NULL "
                "CHECK(max_entries BETWEEN 1 AND 4096))"
            )

            connection.execute(
                "CREATE TABLE publication_witnesses ("
                "sequence INTEGER PRIMARY KEY AUTOINCREMENT, "
                "universe_id TEXT NOT NULL, "
                "incident_id TEXT NOT NULL UNIQUE, "
                "source_operation TEXT NOT NULL, "
                "phase TEXT NOT NULL "
                "CHECK(phase IN ('prepared', 'observed')), "
                "cronenberg_id TEXT UNIQUE, "
                "manifestation_digest TEXT, "
                "CHECK ((phase='prepared' "
                "AND cronenberg_id IS NULL "
                "AND manifestation_digest IS NULL) "
                "OR (phase='observed' "
                "AND cronenberg_id IS NOT NULL "
                "AND manifestation_digest IS NOT NULL)))"
            )

            connection.execute(
                "INSERT INTO publication_witness_metadata "
                "(singleton_id, schema_version, "
                "universe_id, max_entries) "
                "VALUES (1, 1, ?, ?)",
                (
                    universe_id,
                    max_entries,
                ),
            )

            connection.execute(
                "PRAGMA user_version=1"
            )

        return store

    @classmethod
    def open(
        cls,
        path,
        *,
        universe_id,
    ):
        """Reject missing, malformed or foreign journals."""

        _require_universe_id(universe_id)

        store = cls(
            Path(path),
            universe_id,
        )

        with store._transaction(
            readonly=True
        ) as connection:

            integrity = connection.execute(
                "PRAGMA quick_check"
            ).fetchone()

            if integrity != ("ok",):
                raise ValueError(
                    "Publication witness database integrity failed."
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
                "SELECT universe_id, incident_id, "
                "source_operation, phase, cronenberg_id, "
                "manifestation_digest "
                "FROM publication_witnesses "
                "WHERE incident_id=?",
                (incident_id,),
            ).fetchone()

            return (
                None
                if row is None
                else _decode_record(
                    row,
                    universe_id=self._universe_id,
                )
            )

    def pending(self, *, limit=256):
        """Return a bounded FIFO of PREPARED entries."""

        _require_batch_limit(limit)

        with self._transaction(
            readonly=True
        ) as connection:

            self._validate_history(connection)

            rows = connection.execute(
                "SELECT universe_id, incident_id, "
                "source_operation, phase, cronenberg_id, "
                "manifestation_digest "
                "FROM publication_witnesses "
                "WHERE phase='prepared' "
                "ORDER BY sequence ASC LIMIT ?",
                (limit,),
            ).fetchall()

            return tuple(
                _decode_record(
                    row,
                    universe_id=self._universe_id,
                )
                for row in rows
            )

    def prepare(
        self,
        incident_id,
        source_operation,
    ):
        """Append a unique PREPARED entry within quota."""

        _require_incident_id(incident_id)
        _require_operation(source_operation)

        with self._transaction(
            readonly=False
        ) as connection:

            (
                capacity,
                total,
            ) = self._validate_history(connection)

            row = connection.execute(
                "SELECT universe_id, incident_id, "
                "source_operation, phase, cronenberg_id, "
                "manifestation_digest "
                "FROM publication_witnesses "
                "WHERE incident_id=?",
                (incident_id,),
            ).fetchone()

            if row is not None:
                current = _decode_record(
                    row,
                    universe_id=self._universe_id,
                )

                if (
                    current.source_operation
                    != source_operation
                ):
                    raise ValueError(
                        "Publication witness identity conflict."
                    )

                return False

            if total >= capacity:
                raise ValueError(
                    "Publication witness history capacity exhausted."
                )

            connection.execute(
                "INSERT INTO publication_witnesses "
                "(universe_id, incident_id, "
                "source_operation, phase, cronenberg_id, "
                "manifestation_digest) "
                "VALUES (?, ?, ?, 'prepared', NULL, NULL)",
                (
                    self._universe_id,
                    incident_id,
                    source_operation,
                ),
            )

            return True

    def observe(
        self,
        incident_id,
        cronenberg_id,
        manifestation_digest,
    ):
        """Store a local claim, never a trusted proof."""

        _require_incident_id(incident_id)
        _require_cronenberg_id(cronenberg_id)
        _require_digest(manifestation_digest)

        with self._transaction(
            readonly=False
        ) as connection:

            self._validate_history(connection)

            row = connection.execute(
                "SELECT universe_id, incident_id, "
                "source_operation, phase, cronenberg_id, "
                "manifestation_digest "
                "FROM publication_witnesses "
                "WHERE incident_id=?",
                (incident_id,),
            ).fetchone()

            if row is None:
                raise ValueError(
                    "Cannot observe an unprepared incident."
                )

            existing = _decode_record(
                row,
                universe_id=self._universe_id,
            )

            if (
                existing.phase
                is PublicationWitnessPhase.OBSERVED
            ):
                if (
                    existing.cronenberg_id == cronenberg_id
                    and existing.manifestation_digest
                    == manifestation_digest
                ):
                    return False

                raise ValueError(
                    "Conflicting publication observation."
                )

            changed = connection.execute(
                "UPDATE publication_witnesses "
                "SET phase='observed', "
                "cronenberg_id=?, manifestation_digest=? "
                "WHERE incident_id=? AND phase='prepared' "
                "AND cronenberg_id IS NULL "
                "AND manifestation_digest IS NULL",
                (
                    cronenberg_id,
                    manifestation_digest,
                    incident_id,
                ),
            )

            if changed.rowcount != 1:
                raise ValueError(
                    "Publication observation conflict."
                )

            return True
