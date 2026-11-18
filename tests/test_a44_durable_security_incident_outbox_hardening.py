"""A44 local outbox hardening regression contracts.

These tests are initially RED against the existing
SQLite incident outbox implementation.

Requirements:
- Opening storage must validate every historical row.
- Every persisted incident identifier must be valid.
- Every persisted source operation must be allowed.
- Sequence numbers must be positive and canonical.
- Total retained history must have a fixed quota.

Tests operate only on temporary SQLite databases.

These controls do NOT authenticate local storage,
prevent whole-file rollback, or independently prove
Cronenberg manifestation.
"""

import sqlite3
import tempfile
import unittest

from contextlib import closing
from pathlib import Path

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)


class A44IncidentOutboxHardeningTests(unittest.TestCase):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_outbox_hardening_"
        )
        self.addCleanup(directory.cleanup)

        self.path = (
            Path(directory.name)
            / "incident_hardening.sqlite"
        )

    def create(self):
        return LocalDurableSecurityIncidentOutbox.create(
            self.path,
            max_pending=2,
        )

    def sql(self, statement, parameters=()):
        with closing(
            sqlite3.connect(self.path)
        ) as connection:
            with connection:
                connection.execute(
                    statement,
                    parameters,
                )

    def test_open_rejects_invalid_delivered_cronenberg_id(self):
        store = self.create()

        store.record(
            "incident-invalid-cronenberg",
            "receipt_signature",
        )

        self.sql(
            "UPDATE security_incidents "
            "SET status='delivered', "
            "cronenberg_id='invalid-reference' "
            "WHERE incident_id=?",
            ("incident-invalid-cronenberg",),
        )

        # Historical delivered rows must be inspected.
        # Pending-only scans miss this invalid binding.

        with self.assertRaises(ValueError):
            LocalDurableSecurityIncidentOutbox.open(
                self.path
            )

    def test_open_rejects_invalid_historical_operation(self):
        store = self.create()

        store.record(
            "incident-invalid-operation",
            "authority_reply",
        )

        self.sql(
            "UPDATE security_incidents "
            "SET source_operation=? "
            "WHERE incident_id=?",
            (
                "unknown_security_operation",
                "incident-invalid-operation",
            ),
        )

        with self.assertRaises(ValueError):
            LocalDurableSecurityIncidentOutbox.open(
                self.path
            )

    def test_open_rejects_invalid_historical_incident_id(self):
        store = self.create()

        store.record(
            "incident-valid-original",
            "security_validation",
        )

        self.sql(
            "UPDATE security_incidents "
            "SET incident_id=? "
            "WHERE incident_id=?",
            (
                "../invalid-incident",
                "incident-valid-original",
            ),
        )

        with self.assertRaises(ValueError):
            LocalDurableSecurityIncidentOutbox.open(
                self.path
            )

    def test_open_rejects_invalid_historical_sequence(self):
        store = self.create()

        store.record(
            "incident-sequence-zero",
            "publication_fence",
        )

        # SQLite accepts explicit sequence=0 for an
        # INTEGER PRIMARY KEY unless the application
        # independently validates this condition.

        self.sql(
            "UPDATE security_incidents "
            "SET sequence=0 "
            "WHERE incident_id=?",
            ("incident-sequence-zero",),
        )

        with self.assertRaises(ValueError):
            LocalDurableSecurityIncidentOutbox.open(
                self.path
            )

    def test_total_history_capacity_survives_acknowledgements(self):
        # A separate total capacity must prevent the
        # delivered history from growing indefinitely.
        #
        # New API contract:
        # create(path, max_pending=2, max_total=3)

        store = LocalDurableSecurityIncidentOutbox.create(
            self.path,
            max_pending=2,
            max_total=3,
        )

        for number in range(3):
            incident_id = f"incident-total-{number:03}"
            cronenberg_id = f"cronenberg_{number + 1:08x}"

            self.assertTrue(
                store.record(
                    incident_id,
                    "receipt_signature",
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

        # All records have been delivered, but the
        # total retention quota must still apply.

        with self.assertRaises(ValueError):
            store.record(
                "incident-total-003",
                "receipt_signature",
            )

        self.assertIsNone(
            LocalDurableSecurityIncidentOutbox.open(
                self.path
            ).get("incident-total-003")
        )


if __name__ == "__main__":
    unittest.main()
