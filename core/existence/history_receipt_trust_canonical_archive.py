"""A44 bounded local durable canonical evidence archive.

Capture requires a matching live canonical Universe
publication. The stored projection is detached and
structurally validated before every read/write.

The archive is NOT:
- an authenticated canonical checkpoint;
- a full Cronenberg object-state snapshot;
- a Universe reconstruction mechanism;
- an authorization or republication mechanism;
- malicious file rollback or tamper protection;
- an atomic transaction with the incident outbox;
- a cross-process exactly-once publication protocol.

An archived record is always non-authoritative.
"""

import json
import os
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)

from core.existence.history_receipt_trust_incident_outbox import (
    _require_batch_limit,
    _require_cronenberg_id,
    _require_incident_id,
    _require_operation,
)

from core.existence.history_receipt_trust_publication_witness import (
    _require_digest,
    _require_entries,
    _require_universe_id,
)


_SCHEMA_VERSION = 1


def _canonical_json(payload):
    """Exact local JSON encoding, not an authenticity proof."""

    try:
        return json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            "Canonical archive payload cannot be encoded."
        ) from exc


def _strict_object(pairs):
    """Reject duplicate JSON keys, including nested keys."""

    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                "Duplicate canonical archive JSON key."
            )

        result[key] = value

    return result


def _decode_record(row, *, universe_id):
    """Decode one row as untrusted detached evidence."""

    if (
        type(row) is not tuple
        or len(row) != 6
    ):
        raise ValueError(
            "Invalid canonical archive row."
        )

    (
        stored_universe,
        incident_id,
        source_operation,
        cronenberg_id,
        projection_sha256,
        payload_json,
    ) = row

    _require_universe_id(stored_universe)

    if stored_universe != universe_id:
        raise ValueError(
            "Canonical archive belongs to another Universe."
        )

    _require_incident_id(incident_id)
    _require_operation(source_operation)
    _require_cronenberg_id(cronenberg_id)
    _require_digest(projection_sha256)

    if (
        type(payload_json) is not str
        or not payload_json
    ):
        raise ValueError(
            "Invalid canonical archive JSON payload."
        )

    try:
        payload = json.loads(
            payload_json,
            object_pairs_hook=_strict_object,
        )

    except (ValueError, TypeError, RecursionError) as exc:
        raise ValueError(
            "Malformed canonical archive JSON payload."
        ) from exc

    evidence = (
        CanonicalSecurityPublicationEvidence
        .parse_untrusted(payload)
    )

    if (
        evidence.universe_id != stored_universe
        or evidence.incident_id != incident_id
        or evidence.source_operation != source_operation
        or evidence.cronenberg_id != cronenberg_id
        or evidence.projection_sha256
        != projection_sha256
    ):
        raise ValueError(
            "Canonical archive row/projection mismatch."
        )

    if payload_json != _canonical_json(evidence.to_dict()):
        raise ValueError(
            "Noncanonical archive serialization."
        )

    if (
        evidence.is_authoritative is not False
        or evidence.is_restorable is not False
    ):
        raise ValueError(
            "Unsafe canonical archive trust state."
        )

    return evidence


@dataclass(frozen=True, slots=True)
class LocalDurableCanonicalEvidenceArchive:
    """A bounded Universe-scoped SQLite evidence archive."""

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
                "Canonical archive database unavailable."
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

            except (sqlite3.Error, OSError) as exc:
                raise ValueError(
                    "Canonical archive transaction failed."
                ) from exc

    def _metadata(self, connection):
        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()

        if version != (_SCHEMA_VERSION,):
            raise ValueError(
                "Unsupported canonical archive schema."
            )

        rows = connection.execute(
            "SELECT singleton_id, schema_version, "
            "universe_id, max_entries "
            "FROM canonical_archive_metadata"
        ).fetchall()

        if (
            len(rows) != 1
            or rows[0][0] != 1
            or rows[0][1] != _SCHEMA_VERSION
        ):
            raise ValueError(
                "Missing or invalid archive metadata."
            )

        stored_universe = _require_universe_id(
            rows[0][2]
        )

        if stored_universe != self._universe_id:
            raise ValueError(
                "Canonical archive Universe identity mismatch."
            )

        return _require_entries(
            rows[0][3]
        )

    def _validate_schema(self, connection):
        """Require the exact v1 SQLite column layouts.

        PRAGMA table_xinfo includes hidden/generated
        columns, unlike table_info.

        This is structural validation, not authentication.
        It does not attest indexes, triggers, database
        provenance or malicious rollback resistance.
        """

        expected_layouts = {
            "canonical_archive_metadata": (
                (0, "singleton_id", "INTEGER", 0, None, 1, 0),
                (1, "schema_version", "INTEGER", 1, None, 0, 0),
                (2, "universe_id", "TEXT", 1, None, 0, 0),
                (3, "max_entries", "INTEGER", 1, None, 0, 0),
            ),
            "canonical_evidence_records": (
                (0, "sequence", "INTEGER", 0, None, 1, 0),
                (1, "universe_id", "TEXT", 1, None, 0, 0),
                (2, "incident_id", "TEXT", 1, None, 0, 0),
                (3, "source_operation", "TEXT", 1, None, 0, 0),
                (4, "cronenberg_id", "TEXT", 1, None, 0, 0),
                (5, "projection_sha256", "TEXT", 1, None, 0, 0),
                (6, "payload_json", "TEXT", 1, None, 0, 0),
            ),
        }

        for table, expected in expected_layouts.items():
            rows = connection.execute(
                f"PRAGMA table_xinfo({table})"
            ).fetchall()

            actual = tuple(
                tuple(row)
                for row in rows
            )

            if actual != expected:
                raise ValueError(
                    "Invalid canonical archive SQLite "
                    f"column layout: {table}."
                )

    def _validate_history(self, connection):
        """Validate all retained history, not just active rows."""

        self._validate_schema(connection)

        capacity = self._metadata(connection)

        previous_sequence = 0
        total = 0

        seen_incidents = set()
        seen_cronenbergs = set()

        rows = connection.execute(
            "SELECT sequence, universe_id, incident_id, "
            "source_operation, cronenberg_id, "
            "projection_sha256, payload_json "
            "FROM canonical_evidence_records "
            "ORDER BY sequence ASC"
        )

        for row in rows:
            sequence = row[0]

            if (
                type(sequence) is not int
                or sequence != previous_sequence + 1
            ):
                raise ValueError(
                    "Invalid canonical archive history sequence."
                )

            previous_sequence = sequence

            evidence = _decode_record(
                tuple(row[1:]),
                universe_id=self._universe_id,
            )

            if evidence.incident_id in seen_incidents:
                raise ValueError(
                    "Duplicate historical archive incident."
                )

            if evidence.cronenberg_id in seen_cronenbergs:
                raise ValueError(
                    "Duplicate historical archive Cronenberg."
                )

            seen_incidents.add(
                evidence.incident_id
            )

            seen_cronenbergs.add(
                evidence.cronenberg_id
            )

            total += 1

            if total > capacity:
                raise ValueError(
                    "Canonical archive capacity exceeded."
                )

        sequence_row = connection.execute(
            "SELECT seq FROM sqlite_sequence "
            "WHERE name='canonical_evidence_records'"
        ).fetchone()

        if (
            (total == 0 and sequence_row is not None)
            or (
                total != 0
                and (
                    sequence_row is None
                    or type(sequence_row[0]) is not int
                    or sequence_row[0] != previous_sequence
                )
            )
        ):
            raise ValueError(
                "Canonical archive append history mismatch."
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
        """Exclusively create one local Universe-scoped archive."""

        _require_universe_id(
            universe_id
        )

        _require_entries(
            max_entries
        )

        target = Path(path)

        try:
            descriptor = os.open(
                target,
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
            )

        except OSError as exc:
            raise ValueError(
                "Archive already exists or cannot be created."
            ) from exc

        else:
            os.close(descriptor)

        archive = cls(
            target,
            universe_id,
        )

        with archive._transaction(
            readonly=False
        ) as connection:

            connection.execute(
                "CREATE TABLE canonical_archive_metadata ("
                "singleton_id INTEGER PRIMARY KEY "
                "CHECK(singleton_id=1), "
                "schema_version INTEGER NOT NULL "
                "CHECK(schema_version=1), "
                "universe_id TEXT NOT NULL, "
                "max_entries INTEGER NOT NULL "
                "CHECK(max_entries BETWEEN 1 AND 4096))"
            )

            connection.execute(
                "CREATE TABLE canonical_evidence_records ("
                "sequence INTEGER PRIMARY KEY AUTOINCREMENT, "
                "universe_id TEXT NOT NULL, "
                "incident_id TEXT NOT NULL UNIQUE, "
                "source_operation TEXT NOT NULL, "
                "cronenberg_id TEXT NOT NULL UNIQUE, "
                "projection_sha256 TEXT NOT NULL, "
                "payload_json TEXT NOT NULL)"
            )

            connection.execute(
                "INSERT INTO canonical_archive_metadata "
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

        return archive

    @classmethod
    def open(
        cls,
        path,
        *,
        universe_id,
    ):
        """Reject malformed, missing and foreign archives."""

        _require_universe_id(
            universe_id
        )

        archive = cls(
            Path(path),
            universe_id,
        )

        with archive._transaction(
            readonly=True
        ) as connection:

            integrity = connection.execute(
                "PRAGMA quick_check"
            ).fetchone()

            if integrity != ("ok",):
                raise ValueError(
                    "Canonical archive database integrity failed."
                )

            archive._validate_history(
                connection
            )

        return archive

    def incident_ids(self, *, limit=256):
        """List a bounded FIFO of archived incident IDs."""

        _require_batch_limit(
            limit
        )

        with self._transaction(
            readonly=True
        ) as connection:

            self._validate_history(
                connection
            )

            rows = connection.execute(
                "SELECT incident_id "
                "FROM canonical_evidence_records "
                "ORDER BY sequence ASC LIMIT ?",
                (limit,),
            ).fetchall()

            return tuple(
                row[0]
                for row in rows
            )

    def get_untrusted(self, incident_id):
        """Read a detached claim without authority."""

        _require_incident_id(
            incident_id
        )

        with self._transaction(
            readonly=True
        ) as connection:

            self._validate_history(
                connection
            )

            row = connection.execute(
                "SELECT universe_id, incident_id, "
                "source_operation, cronenberg_id, "
                "projection_sha256, payload_json "
                "FROM canonical_evidence_records "
                "WHERE incident_id=?",
                (incident_id,),
            ).fetchone()

            if row is None:
                return None

            return _decode_record(
                tuple(row),
                universe_id=self._universe_id,
            )

    def capture_live(
        self,
        *,
        universe,
        incident_id,
        source_operation,
    ):
        """Capture only existing canonical live evidence.

        No local witness, caller-provided projection or
        archived payload can substitute for live capture.

        Capture does not mutate any Universe registry,
        create entities, acknowledge incidents or authorize
        publication.
        """

        _require_incident_id(
            incident_id
        )

        _require_operation(
            source_operation
        )

        if (
            getattr(universe, "id", None)
            != self._universe_id
        ):
            raise ValueError(
                "Canonical archive Universe identity mismatch."
            )

        evidence = (
            CanonicalSecurityPublicationEvidence.capture(
                universe=universe,
                incident_id=incident_id,
                source_operation=source_operation,
            )
        )

        if evidence.verify_live(universe) is not True:
            raise ValueError(
                "Canonical publication verification failed."
            )

        payload_json = _canonical_json(
            evidence.to_dict()
        )

        with self._transaction(
            readonly=False
        ) as connection:

            capacity, total = self._validate_history(
                connection
            )

            row = connection.execute(
                "SELECT universe_id, incident_id, "
                "source_operation, cronenberg_id, "
                "projection_sha256, payload_json "
                "FROM canonical_evidence_records "
                "WHERE incident_id=?",
                (incident_id,),
            ).fetchone()

            if row is not None:
                existing = _decode_record(
                    tuple(row),
                    universe_id=self._universe_id,
                )

                if existing.to_dict() != evidence.to_dict():
                    raise ValueError(
                        "Conflicting archived publication identity."
                    )

                return False

            if total >= capacity:
                raise ValueError(
                    "Canonical archive history capacity exhausted."
                )

            # A second incident cannot claim the same
            # Cronenberg identity even if local SQLite
            # uniqueness constraints were removed.
            collision = connection.execute(
                "SELECT incident_id "
                "FROM canonical_evidence_records "
                "WHERE cronenberg_id=?",
                (evidence.cronenberg_id,),
            ).fetchone()

            if collision is not None:
                raise ValueError(
                    "Cronenberg already archived for another incident."
                )

            connection.execute(
                "INSERT INTO canonical_evidence_records "
                "(universe_id, incident_id, "
                "source_operation, cronenberg_id, "
                "projection_sha256, payload_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    evidence.universe_id,
                    evidence.incident_id,
                    evidence.source_operation,
                    evidence.cronenberg_id,
                    evidence.projection_sha256,
                    payload_json,
                ),
            )

            return True
