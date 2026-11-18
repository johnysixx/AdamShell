"""A44 adversarial durable canonical archive tests.

EXPECTED RED:
An altered SQLite table with an additional unexpected
column must not pass archive.open(), even if its existing
rows and PRAGMA quick_check remain valid.

Other cases exercise malformed metadata, missing tables,
duplicate JSON keys, identity conflicts, history gaps,
tail truncation, invalid capacity and concurrent inserts.

These tests do not establish authenticated durability,
Universe reconstruction, malicious rollback resistance,
or cross-process exactly-once publication.
"""

import dataclasses
import io
import json
import sqlite3
import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, redirect_stdout
from pathlib import Path

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_canonical_archive import (
    LocalDurableCanonicalEvidenceArchive,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergReconciler,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)

from universe.universe import Universe


WORLD = "a44_666_adversarial_archive"
OPERATION = "security_validation"
INCIDENT = "incident-archive-adversarial"


class A44DurableCanonicalArchiveAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_666_archive_adversarial_"
        )

        self.addCleanup(directory.cleanup)

        self.root = Path(directory.name)
        self.path = self.root / "archive.sqlite"

        self.archive = LocalDurableCanonicalEvidenceArchive.create(
            self.path,
            universe_id=WORLD,
            max_entries=4,
        )

        self.outbox = LocalDurableSecurityIncidentOutbox.create(
            self.root / "outbox.sqlite",
            max_pending=8,
            max_total=16,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id=WORLD
            )

    def publish(self, incident_id=INCIDENT):
        coordinator = SecurityIncidentCronenbergReconciler(
            universe=self.world,
            outbox=self.outbox,
        )

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                coordinator.reject(
                    incident_id=incident_id,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "adversarial archive test"
                    ),
                )

    def capture(self, incident_id=INCIDENT):
        return self.archive.capture_live(
            universe=self.world,
            incident_id=incident_id,
            source_operation=OPERATION,
        )

    def reopen(self):
        return LocalDurableCanonicalEvidenceArchive.open(
            self.path,
            universe_id=WORLD,
        )

    def test_unexpected_record_column_rejected_on_open(self):
        """EXPECTED RED: extra SQLite schema column is ignored."""

        self.publish()
        self.assertTrue(self.capture())

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "ALTER TABLE canonical_evidence_records "
                "ADD COLUMN injected TEXT"
            )

            self.assertEqual(
                connection.execute(
                    "PRAGMA quick_check"
                ).fetchone(),
                ("ok",),
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_unsupported_sqlite_schema_version_rejected(self):
        self.publish()
        self.capture()

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "PRAGMA user_version=77"
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_foreign_metadata_universe_rejected(self):
        self.publish()
        self.capture()

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "UPDATE canonical_archive_metadata "
                "SET universe_id=?",
                ("foreign_archive",),
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_missing_archive_history_table_rejected(self):
        self.publish()
        self.capture()

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "DROP TABLE canonical_evidence_records"
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_malformed_stored_json_rejected(self):
        self.publish()
        self.capture()

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "UPDATE canonical_evidence_records "
                "SET payload_json=? "
                "WHERE incident_id=?",
                (
                    "{not-json",
                    INCIDENT,
                ),
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_duplicate_nested_json_key_rejected(self):
        self.publish()
        self.capture()

        original = self.archive.get_untrusted(
            INCIDENT
        ).to_dict()

        encoded = json.dumps(
            original,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
        )

        marker = '"schema_version":1'

        self.assertEqual(
            encoded.count(marker),
            1,
        )

        duplicate = encoded.replace(
            marker,
            '"schema_version":1,"schema_version":1',
            1,
        )

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "UPDATE canonical_evidence_records "
                "SET payload_json=? "
                "WHERE incident_id=?",
                (
                    duplicate,
                    INCIDENT,
                ),
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_row_and_payload_operation_conflict_rejected(self):
        self.publish()
        self.capture()

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "UPDATE canonical_evidence_records "
                "SET source_operation=? "
                "WHERE incident_id=?",
                (
                    "receipt_signature",
                    INCIDENT,
                ),
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_historical_sequence_gap_rejected(self):
        first = "incident-archive-gap-01"
        second = "incident-archive-gap-02"

        self.publish(first)
        self.publish(second)

        self.assertTrue(self.capture(first))
        self.assertTrue(self.capture(second))

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "DELETE FROM canonical_evidence_records "
                "WHERE incident_id=?",
                (first,),
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_historical_tail_truncation_rejected(self):
        first = "incident-archive-tail-01"
        second = "incident-archive-tail-02"

        self.publish(first)
        self.publish(second)

        self.assertTrue(self.capture(first))
        self.assertTrue(self.capture(second))

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "DELETE FROM canonical_evidence_records "
                "WHERE incident_id=?",
                (second,),
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_metadata_capacity_below_history_rejected(self):
        first = "incident-archive-cap-01"
        second = "incident-archive-cap-02"

        self.publish(first)
        self.publish(second)

        self.assertTrue(self.capture(first))
        self.assertTrue(self.capture(second))

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "UPDATE canonical_archive_metadata "
                "SET max_entries=1"
            )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_changed_live_manifestation_cannot_rewrite_archive(self):
        self.publish()
        self.assertTrue(self.capture())

        before = self.archive.get_untrusted(
            INCIDENT
        ).to_dict()

        manifestation = next(
            event
            for event in self.world.quantum_events
            if type(event) is CronenbergManifestedEvent
        )

        index = next(
            index
            for index, event in enumerate(
                self.world.quantum_events
            )
            if event is manifestation
        )

        self.world.quantum_events[index] = (
            dataclasses.replace(
                manifestation,
                quantum_tick=manifestation.quantum_tick + 1,
            )
        )

        with self.assertRaises(ValueError):
            self.capture()

        self.assertEqual(
            self.archive.get_untrusted(INCIDENT).to_dict(),
            before,
        )

        self.assertEqual(
            self.archive.incident_ids(),
            (INCIDENT,),
        )

    def test_concurrent_distinct_incident_captures_are_unique(self):
        """No concurrent Universe mutation occurs here."""

        first = "incident-parallel-archive-01"
        second = "incident-parallel-archive-02"

        self.publish(first)
        self.publish(second)

        requests = (
            first,
            second,
            first,
            second,
            first,
            second,
            first,
            second,
        )

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(
                pool.map(
                    self.capture,
                    requests,
                )
            )

        self.assertEqual(
            results.count(True),
            2,
        )

        self.assertEqual(
            results.count(False),
            6,
        )

        self.assertEqual(
            self.archive.incident_ids(),
            (first, second),
        )

        self.assertTrue(
            self.archive.get_untrusted(first).verify_live(
                self.world
            )
        )

        self.assertTrue(
            self.archive.get_untrusted(second).verify_live(
                self.world
            )
        )


if __name__ == "__main__":
    unittest.main()
