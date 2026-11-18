"""A44 local durable security incident outbox contract.

Expected RED until the incident outbox module exists.

This local SQLite outbox is NOT a trust authority.
It cannot resist arbitrary database replacement,
whole-file rollback or compromised application code.

Acknowledgement is only a local delivery claim.
It is NOT independent cryptographic evidence that a
Cronenberg was created in the intended Universe.

A later integration contract must establish a stable
incident-to-Cronenberg binding and reconcile crashes
between Universe publication and outbox acknowledgement.

Tests use temporary directories only.
"""

import ast
import dataclasses
import importlib
import sqlite3
import tempfile
import unittest

from pathlib import Path


MODULE = (
    "core.existence."
    "history_receipt_trust_incident_outbox"
)

VALID_OPERATIONS = (
    "signed_manifest_bootstrap",
    "authority_reply",
    "publication_fence",
    "receipt_signature",
    "security_validation",
)


def api():
    return importlib.import_module(MODULE)


class A44DurableSecurityIncidentOutboxTests(
    unittest.TestCase
):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(
            prefix="a44_incident_outbox_"
        )

        self.addCleanup(self.directory.cleanup)

        self.path = (
            Path(self.directory.name)
            / "security_incidents.sqlite"
        )

    def create(self, *, max_pending=8):
        return (
            api()
            .LocalDurableSecurityIncidentOutbox
            .create(
                self.path,
                max_pending=max_pending,
            )
        )

    def reopen(self):
        return (
            api()
            .LocalDurableSecurityIncidentOutbox
            .open(self.path)
        )

    @staticmethod
    def record(
        store,
        incident_id="incident-a44-0001",
        source_operation="receipt_signature",
    ):
        return store.record(
            incident_id,
            source_operation,
        )

    def test_create_empty_and_reopen(self):
        store = self.create()

        self.assertTrue(self.path.is_file())

        self.assertIs(
            type(store.pending()),
            tuple,
        )

        self.assertEqual(
            store.pending(),
            (),
        )

        self.assertIsNone(
            store.get("incident-a44-0001")
        )

        reopened = self.reopen()

        self.assertEqual(
            reopened.pending(),
            (),
        )

    def test_create_exclusive_and_missing_open_rejected(self):
        with self.assertRaises(ValueError):
            self.reopen()

        self.path.write_bytes(
            b"existing-file-must-not-be-overwritten"
        )

        before = self.path.read_bytes()

        with self.assertRaises(ValueError):
            self.create()

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.path.unlink()

        self.create()

        with self.assertRaises(ValueError):
            self.create()

    def test_record_persists_immutable_pending_state(self):
        store = self.create()

        self.assertIs(
            self.record(store),
            True,
        )

        incident = store.get(
            "incident-a44-0001"
        )

        self.assertIs(
            type(incident),
            api().SecurityIncidentRecord,
        )

        self.assertEqual(
            incident.incident_id,
            "incident-a44-0001",
        )

        self.assertEqual(
            incident.source_operation,
            "receipt_signature",
        )

        self.assertIs(
            incident.status,
            api().SecurityIncidentStatus.PENDING,
        )

        self.assertIsNone(
            incident.cronenberg_id,
        )

        self.assertTrue(
            dataclasses.is_dataclass(incident)
        )

        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(incident)
            ),
            (
                "incident_id",
                "source_operation",
                "status",
                "cronenberg_id",
            ),
        )

        with self.assertRaises(
            dataclasses.FrozenInstanceError
        ):
            incident.status = "delivered"

        reopened = self.reopen()

        self.assertEqual(
            reopened.get("incident-a44-0001"),
            incident,
        )

    def test_duplicate_record_idempotent_and_conflict(self):
        store = self.create()

        self.assertIs(
            self.record(store),
            True,
        )

        self.assertIs(
            self.record(store),
            False,
        )

        self.assertEqual(
            len(store.pending()),
            1,
        )

        with self.assertRaises(ValueError):
            self.record(
                store,
                source_operation="authority_reply",
            )

        self.assertEqual(
            len(self.reopen().pending()),
            1,
        )

    def test_pending_fifo_order_and_bounded_batch(self):
        store = self.create()

        incidents = (
            ("incident-003", "receipt_signature"),
            ("incident-001", "authority_reply"),
            ("incident-002", "publication_fence"),
        )

        for incident_id, operation in incidents:
            self.assertIs(
                self.record(
                    store,
                    incident_id,
                    operation,
                ),
                True,
            )

        self.assertEqual(
            tuple(
                item.incident_id
                for item in store.pending()
            ),
            (
                "incident-003",
                "incident-001",
                "incident-002",
            ),
        )

        self.assertEqual(
            tuple(
                item.incident_id
                for item in self.reopen().pending(limit=2)
            ),
            (
                "incident-003",
                "incident-001",
            ),
        )

        self.assertIs(
            type(store.pending(limit=1)),
            tuple,
        )

        self.assertEqual(
            len(store.pending(limit=1)),
            1,
        )

    def test_pending_quota_and_recovery_after_ack(self):
        store = self.create(max_pending=2)

        self.assertTrue(
            self.record(
                store,
                "incident-001",
            )
        )

        self.assertTrue(
            self.record(
                store,
                "incident-002",
            )
        )

        with self.assertRaises(ValueError):
            self.record(
                store,
                "incident-003",
            )

        self.assertEqual(
            len(self.reopen().pending()),
            2,
        )

        self.assertIs(
            store.acknowledge(
                "incident-001",
                "cronenberg_00000001",
            ),
            True,
        )

        self.assertIs(
            self.record(
                store,
                "incident-003",
            ),
            True,
        )

        self.assertEqual(
            tuple(
                item.incident_id
                for item in store.pending()
            ),
            (
                "incident-002",
                "incident-003",
            ),
        )

        # Quota exhaustion must fail closed.
        # It must never authorize a blocked operation.

    def test_acknowledge_once_and_persist(self):
        store = self.create()

        self.record(store)

        self.assertIs(
            store.acknowledge(
                "incident-a44-0001",
                "cronenberg_1234abcd",
            ),
            True,
        )

        incident = self.reopen().get(
            "incident-a44-0001"
        )

        self.assertIs(
            incident.status,
            api().SecurityIncidentStatus.DELIVERED,
        )

        self.assertEqual(
            incident.cronenberg_id,
            "cronenberg_1234abcd",
        )

        self.assertEqual(
            self.reopen().pending(),
            (),
        )

        # Local acknowledgement alone does not prove
        # real publication in the Universe.

    def test_acknowledge_idempotent_and_conflicts_rejected(self):
        store = self.create()

        self.record(store)

        with self.assertRaises(ValueError):
            store.acknowledge(
                "unknown-incident",
                "cronenberg_11111111",
            )

        self.assertIs(
            store.acknowledge(
                "incident-a44-0001",
                "cronenberg_11111111",
            ),
            True,
        )

        self.assertIs(
            store.acknowledge(
                "incident-a44-0001",
                "cronenberg_11111111",
            ),
            False,
        )

        with self.assertRaises(ValueError):
            store.acknowledge(
                "incident-a44-0001",
                "cronenberg_22222222",
            )

        self.assertIs(
            self.record(store),
            False,
        )

        self.assertEqual(
            store.get(
                "incident-a44-0001"
            ).cronenberg_id,
            "cronenberg_11111111",
        )

    def test_invalid_incident_identifiers_rejected(self):
        store = self.create()

        invalid = (
            None,
            True,
            12,
            b"incident-id",
            "",
            " ",
            " leading",
            "trailing ",
            "bad" + chr(10) + "id",
            "bad" + chr(0) + "id",
            "../outside",
            "x" * 129,
        )

        for value in invalid:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    store.record(
                        value,
                        "receipt_signature",
                    )

                with self.assertRaises(ValueError):
                    store.get(value)

        self.assertEqual(
            store.pending(),
            (),
        )

    def test_invalid_operations_and_limits_rejected(self):
        store = self.create()

        for operation in (
            None,
            123,
            True,
            "",
            "invalid_operation",
            " receipt_signature",
            "receipt_signature ",
        ):
            with self.subTest(operation=repr(operation)):
                with self.assertRaises(ValueError):
                    store.record(
                        "incident-a44-0001",
                        operation,
                    )

        for limit in (
            None,
            0,
            -1,
            True,
            1.5,
            "1",
            257,
        ):
            with self.subTest(limit=repr(limit)):
                with self.assertRaises(ValueError):
                    store.pending(limit=limit)

        for capacity in (
            None,
            0,
            -1,
            True,
            "2",
            4097,
        ):
            with self.subTest(capacity=repr(capacity)):
                alternate = (
                    Path(self.directory.name)
                    / f"invalid_{repr(capacity)}.sqlite"
                )

                with self.assertRaises(ValueError):
                    api().LocalDurableSecurityIncidentOutbox.create(
                        alternate,
                        max_pending=capacity,
                    )

                self.assertFalse(
                    alternate.exists()
                )

        self.assertEqual(
            store.pending(),
            (),
        )

    def test_independent_handles_share_idempotency(self):
        first = self.create(max_pending=2)
        second = self.reopen()

        self.assertTrue(
            self.record(
                first,
                "incident-shared-001",
            )
        )

        self.assertFalse(
            self.record(
                second,
                "incident-shared-001",
            )
        )

        self.assertTrue(
            self.record(
                second,
                "incident-shared-002",
            )
        )

        with self.assertRaises(ValueError):
            self.record(
                first,
                "incident-shared-003",
            )

        self.assertEqual(
            tuple(
                item.incident_id
                for item in first.pending()
            ),
            (
                "incident-shared-001",
                "incident-shared-002",
            ),
        )

        # This checks independent sequential handles.
        # True parallel races require further tests.

    def test_corrupted_database_fails_closed(self):
        store = self.create()

        self.record(store)

        self.path.write_bytes(
            b"not-a-valid-sqlite-database"
        )

        with self.assertRaises(ValueError):
            self.reopen()

        self.assertEqual(
            self.path.read_bytes(),
            b"not-a-valid-sqlite-database",
        )

        # Do not silently recreate missing history.

    def test_crash_before_ack_leaves_incident_pending(self):
        store = self.create()

        self.assertTrue(
            self.record(
                store,
                "incident-crash-001",
                "security_validation",
            )
        )

        # Model a process interruption after recording,
        # but before the Universe publication is
        # acknowledged. Nothing is marked delivered.

        reopened = self.reopen()

        pending = reopened.pending()

        self.assertEqual(
            len(pending),
            1,
        )

        self.assertEqual(
            pending[0].incident_id,
            "incident-crash-001",
        )

        self.assertIs(
            pending[0].status,
            api().SecurityIncidentStatus.PENDING,
        )

        self.assertIsNone(
            pending[0].cronenberg_id,
        )


if __name__ == "__main__":
    unittest.main()
