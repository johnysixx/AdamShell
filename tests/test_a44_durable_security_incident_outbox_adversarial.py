"""A44 adversarial local incident-outbox diagnostics.

Tests cover concurrency, transactional failure and corruption.

Some tests intentionally demonstrate known vulnerabilities:
whole-file rollback, unauthenticated acknowledgements,
mutable local quota configuration, unbounded delivered
history and incomplete historical validation at open().

A passing diagnostic documenting a GAP does NOT mean that
the security weakness has been corrected.

Every SQLite database in this module is temporary.
"""

import shutil
import sqlite3
import tempfile
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
    SecurityIncidentStatus,
)


class A44DurableIncidentOutboxAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_outbox_adversarial_"
        )

        self.addCleanup(directory.cleanup)

        self.path = (
            Path(directory.name)
            / "incident_outbox.sqlite"
        )

        self.backup_path = (
            Path(directory.name)
            / "incident_backup.sqlite"
        )

    def create(self, capacity=8):
        return LocalDurableSecurityIncidentOutbox.create(
            self.path,
            max_pending=capacity,
        )

    def reopen(self):
        return LocalDurableSecurityIncidentOutbox.open(
            self.path
        )

    def sql(self, statement, parameters=()):
        with closing(
            sqlite3.connect(self.path)
        ) as connection:
            with connection:
                return connection.execute(
                    statement,
                    parameters,
                ).fetchall()

    def concurrent(self, count, action):
        gate = threading.Barrier(count)

        def worker(index):
            # Every worker owns a separate database handle.
            store = self.reopen()

            gate.wait(timeout=15)

            return action(store, index)

        with ThreadPoolExecutor(
            max_workers=count
        ) as executor:

            return list(
                executor.map(
                    worker,
                    range(count),
                )
            )

    def test_concurrent_duplicate_record_is_idempotent(self):
        self.create(capacity=2)

        results = self.concurrent(
            6,
            lambda store, index: store.record(
                "incident-shared-001",
                "receipt_signature",
            ),
        )

        self.assertEqual(
            results.count(True),
            1,
        )

        self.assertEqual(
            results.count(False),
            5,
        )

        pending = self.reopen().pending()

        self.assertEqual(len(pending), 1)

        self.assertEqual(
            pending[0].incident_id,
            "incident-shared-001",
        )

    def test_concurrent_capacity_cannot_be_exceeded(self):
        self.create(capacity=2)

        def record(store, index):
            try:
                return store.record(
                    f"incident-race-{index:03}",
                    "security_validation",
                )

            except ValueError:
                return "capacity-rejected"

        results = self.concurrent(
            4,
            record,
        )

        self.assertEqual(
            results.count(True),
            2,
        )

        self.assertEqual(
            results.count("capacity-rejected"),
            2,
        )

        self.assertEqual(
            len(self.reopen().pending()),
            2,
        )

    def test_concurrent_same_ack_is_idempotent(self):
        store = self.create()

        store.record(
            "incident-ack-same",
            "authority_reply",
        )

        results = self.concurrent(
            4,
            lambda handle, index: handle.acknowledge(
                "incident-ack-same",
                "cronenberg_00000001",
            ),
        )

        self.assertEqual(
            results.count(True),
            1,
        )

        self.assertEqual(
            results.count(False),
            3,
        )

        record = self.reopen().get(
            "incident-ack-same"
        )

        self.assertIs(
            record.status,
            SecurityIncidentStatus.DELIVERED,
        )

        self.assertEqual(
            record.cronenberg_id,
            "cronenberg_00000001",
        )

    def test_concurrent_conflicting_ack_fails_closed(self):
        store = self.create()

        store.record(
            "incident-ack-conflict",
            "publication_fence",
        )

        def acknowledge(handle, index):
            candidate = f"cronenberg_{index + 1:08x}"

            try:
                return (
                    candidate,
                    handle.acknowledge(
                        "incident-ack-conflict",
                        candidate,
                    ),
                )

            except ValueError:
                return (candidate, "rejected")

        results = self.concurrent(
            2,
            acknowledge,
        )

        successes = [
            candidate
            for candidate, result in results
            if result is True
        ]

        rejected = [
            candidate
            for candidate, result in results
            if result == "rejected"
        ]

        self.assertEqual(len(successes), 1)
        self.assertEqual(len(rejected), 1)

        persisted = self.reopen().get(
            "incident-ack-conflict"
        )

        self.assertEqual(
            persisted.cronenberg_id,
            successes[0],
        )

    def test_one_cronenberg_cannot_bind_two_incidents(self):
        store = self.create()

        store.record(
            "incident-first",
            "receipt_signature",
        )

        store.record(
            "incident-second",
            "receipt_signature",
        )

        self.assertTrue(
            store.acknowledge(
                "incident-first",
                "cronenberg_aabbccdd",
            )
        )

        with self.assertRaises(ValueError):
            store.acknowledge(
                "incident-second",
                "cronenberg_aabbccdd",
            )

        second = self.reopen().get(
            "incident-second"
        )

        self.assertIs(
            second.status,
            SecurityIncidentStatus.PENDING,
        )

        self.assertIsNone(
            second.cronenberg_id,
        )

    def test_failed_insert_rolls_back_without_leak(self):
        store = self.create(capacity=1)

        self.sql(
            "CREATE TRIGGER reject_incident_insert "
            "BEFORE INSERT ON security_incidents "
            "BEGIN "
            "SELECT RAISE(ABORT, 'injected write failure'); "
            "END"
        )

        with self.assertRaises(ValueError):
            store.record(
                "incident-write-failed",
                "security_validation",
            )

        self.assertEqual(
            self.reopen().pending(),
            (),
        )

        self.sql(
            "DROP TRIGGER reject_incident_insert"
        )

        self.assertTrue(
            store.record(
                "incident-write-failed",
                "security_validation",
            )
        )

        self.assertEqual(
            len(self.reopen().pending()),
            1,
        )

    def test_destroyed_incident_schema_fails_closed(self):
        store = self.create()

        store.record(
            "incident-schema-001",
            "authority_reply",
        )

        self.sql(
            "DROP TABLE security_incidents"
        )

        with self.assertRaises(ValueError):
            self.reopen()

        with self.assertRaises(ValueError):
            store.pending()

        # A missing table must not be silently recreated.

    def test_whole_file_rollback_remains_undetectable(self):
        store = self.create()

        store.record(
            "incident-before-backup",
            "security_validation",
        )

        shutil.copyfile(
            self.path,
            self.backup_path,
        )

        store.record(
            "incident-after-backup",
            "security_validation",
        )

        self.assertIsNotNone(
            store.get("incident-after-backup")
        )

        # Restore an older valid SQLite file.
        # No live transaction is open at this point.
        shutil.copyfile(
            self.backup_path,
            self.path,
        )

        reopened = self.reopen()

        self.assertIsNotNone(
            reopened.get("incident-before-backup")
        )

        self.assertIsNone(
            reopened.get("incident-after-backup")
        )

        # GAP: A valid older database is accepted.
        # SQLite integrity checks cannot establish
        # authenticated monotonic historical state.

    def test_unverified_acknowledgement_is_accepted(self):
        store = self.create()

        store.record(
            "incident-no-real-cronenberg",
            "security_validation",
        )

        self.assertTrue(
            store.acknowledge(
                "incident-no-real-cronenberg",
                "cronenberg_deadbeef",
            )
        )

        record = self.reopen().get(
            "incident-no-real-cronenberg"
        )

        self.assertIs(
            record.status,
            SecurityIncidentStatus.DELIVERED,
        )

        self.assertEqual(
            record.cronenberg_id,
            "cronenberg_deadbeef",
        )

        # GAP: The outbox did not consult a Universe.
        # This is not evidence of real manifestation.

    def test_delivered_history_has_total_quota(self):
        store = LocalDurableSecurityIncidentOutbox.create(
            self.path,
            max_pending=1,
            max_total=3,
        )

        for number in range(1, 4):
            incident_id = (
                f"incident-delivered-{number:03}"
            )

            cronenberg_id = (
                f"cronenberg_{number:08x}"
            )

            self.assertTrue(
                store.record(
                    incident_id,
                    "security_validation",
                )
            )

            self.assertTrue(
                store.acknowledge(
                    incident_id,
                    cronenberg_id,
                )
            )

        self.assertEqual(
            store.pending(),
            (),
        )

        with self.assertRaises(ValueError):
            store.record(
                "incident-delivered-004",
                "security_validation",
            )

        self.assertEqual(
            self.sql(
                "SELECT COUNT(*) FROM security_incidents"
            )[0][0],
            3,
        )

        # No automatic deletion of delivered history.

        # GAP: max_pending=1 did not bound the total
        # lifetime number of stored records.

    def test_local_metadata_tampering_changes_quota(self):
        store = self.create(capacity=1)

        store.record(
            "incident-quota-001",
            "receipt_signature",
        )

        with self.assertRaises(ValueError):
            store.record(
                "incident-quota-002",
                "receipt_signature",
            )

        self.sql(
            "UPDATE incident_outbox_metadata "
            "SET max_pending=2 "
            "WHERE singleton_id=1"
        )

        self.assertTrue(
            store.record(
                "incident-quota-002",
                "receipt_signature",
            )
        )

        self.assertEqual(
            len(self.reopen().pending()),
            2,
        )

        # GAP: A writable local database can change
        # its own pending capacity configuration.

    def test_invalid_delivered_row_rejected_on_open(self):
        store = self.create()

        store.record(
            "incident-invalid-history",
            "authority_reply",
        )

        self.sql(
            "UPDATE security_incidents "
            "SET status='delivered', "
            "cronenberg_id='invalid-reference' "
            "WHERE incident_id=?",
            ("incident-invalid-history",),
        )

        with self.assertRaises(ValueError):
            self.reopen()

        with self.assertRaises(ValueError):
            store.pending()

        # Invalid historical rows are no longer hidden
        # from ordinary pending-only operations.

        # GAP: A malformed delivered row can remain
        # hidden from ordinary pending-only scans.


if __name__ == "__main__":
    unittest.main()
