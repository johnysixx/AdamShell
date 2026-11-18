"""A44 incident-to-Cronenberg reconciliation contract.

Expected RED until the coordinator module exists.

The coordinator must:
- Persist a fresh recognized incident before publication.
- Bind incident ID to a canonical Universe manifestation.
- Avoid duplicate manifestation on replay.
- Reconcile a live Universe after lost SQLite ACK.
- Refuse an ambiguous pending incident without proof.
- Refuse forged local ACKs without matching Universe state.
- Keep publication and incident binding atomic.
- Fail closed on quotas, conflicts, and backend failures.

The existing attack boundary remains an experimental API.
This contract does not provide a production-wide detector.

The in-memory Universe is not automatically durable.
A newly constructed empty Universe cannot be treated as
proof that a pending incident has never been published.

Only temporary SQLite databases are used.
"""

import importlib
import io
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
    SecurityIncidentStatus,
)

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)

from universe.universe import Universe


MODULE = (
    "core.existence."
    "history_receipt_trust_incident_cronenberg_reconciliation"
)


def reconciler(universe, outbox):
    implementation = importlib.import_module(MODULE)

    return (
        implementation.SecurityIncidentCronenbergReconciler(
            universe=universe,
            outbox=outbox,
        )
    )


class FailOnceAppend(list):
    """Append first, then fail once to simulate partial write."""

    def __init__(self, values=()):
        super().__init__(values)
        self.armed = True

    def append(self, value):
        super().append(value)

        if self.armed:
            self.armed = False
            raise RuntimeError(
                "A44 injected manifestation append failure"
            )


class FailSecondAppend(list):
    """Fail on the second append in the same publication."""

    def __init__(self, values=()):
        super().__init__(values)
        self.calls = 0

    def append(self, value):
        super().append(value)
        self.calls += 1

        if self.calls == 2:
            raise RuntimeError(
                "A44 injected incident binding failure"
            )


class FailOnceAckProxy:
    """Forward SQLite operations but lose the first ACK."""

    def __init__(self, store):
        self.store = store
        self.fail = True

    def __getattr__(self, name):
        return getattr(self.store, name)

    def acknowledge(self, incident_id, cronenberg_id):
        if self.fail:
            self.fail = False
            raise OSError(
                "A44 injected acknowledgement outage"
            )

        return self.store.acknowledge(
            incident_id,
            cronenberg_id,
        )


class A44IncidentCronenbergReconciliationTests(
    unittest.TestCase
):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_incident_reconciliation_"
        )

        self.addCleanup(directory.cleanup)

        self.path = (
            Path(directory.name) / "incidents.sqlite"
        )

        self.store = (
            LocalDurableSecurityIncidentOutbox.create(
                self.path,
                max_pending=3,
                max_total=8,
            )
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id="a44_reconciliation_world"
            )

    @staticmethod
    def attack():
        return SecurityAttackDetected(
            "ATTACKER_SECRET_UNTRUSTED_CONTENT"
        )

    def coordinator(self, *, universe=None, outbox=None):
        return reconciler(
            self.world if universe is None else universe,
            self.store if outbox is None else outbox,
        )

    def reject(
        self,
        coordinator,
        incident_id,
        operation="security_validation",
    ):
        with redirect_stdout(io.StringIO()):
            coordinator.reject(
                incident_id=incident_id,
                source_operation=operation,
                attack=self.attack(),
            )

    def manifestations(self):
        return tuple(
            event
            for event in self.world.quantum_events
            if isinstance(event, CronenbergManifestedEvent)
        )

    def assert_manifestation_bound(self, incident_id):
        record = self.store.get(incident_id)

        self.assertIs(
            record.status,
            SecurityIncidentStatus.DELIVERED,
        )

        self.assertEqual(len(self.world.cronenbergs), 1)
        self.assertEqual(len(self.world.entities), 1)
        self.assertEqual(len(self.manifestations()), 1)

        cronenberg = self.world.cronenbergs[0]

        self.assertIs(
            self.world.entities[0],
            cronenberg,
        )

        self.assertEqual(
            record.cronenberg_id,
            cronenberg.id,
        )

        self.assertEqual(
            self.manifestations()[0].cronenberg_id,
            cronenberg.id,
        )

        self.assertNotIn(
            "ATTACKER_SECRET_UNTRUSTED_CONTENT",
            self.manifestations()[0].error_message,
        )

        # Identity must be published in the Universe
        # as part of canonical publication, not only
        # kept in a transient coordinator instance.
        bound_events = [
            event
            for event in self.world.quantum_events
            if (
                getattr(event, "incident_id", None)
                == incident_id
                and getattr(event, "cronenberg_id", None)
                == cronenberg.id
                and getattr(event, "source_operation", None)
                == record.source_operation
            )
        ]

        self.assertEqual(
            len(bound_events),
            1,
            "Missing unique canonical incident binding.",
        )

    def test_fresh_rejection_records_manifests_and_acks(self):
        coordinator = self.coordinator()

        with self.assertRaises(SecurityAttackDetected):
            self.reject(
                coordinator,
                "incident-first-001",
            )

        self.assert_manifestation_bound(
            "incident-first-001"
        )

        reopened = LocalDurableSecurityIncidentOutbox.open(
            self.path
        )

        self.assertEqual(
            reopened.get("incident-first-001"),
            self.store.get("incident-first-001"),
        )

    def test_delivered_retry_does_not_duplicate(self):
        coordinator = self.coordinator()

        with self.assertRaises(SecurityAttackDetected):
            self.reject(
                coordinator,
                "incident-retry-001",
            )

        original = self.world.cronenbergs[0]

        # A new coordinator must not forget a published
        # incident in the same canonical Universe.
        second = self.coordinator()

        with self.assertRaises(SecurityAttackDetected):
            self.reject(
                second,
                "incident-retry-001",
            )

        self.assertEqual(
            self.world.cronenbergs,
            [original],
        )

        self.assert_manifestation_bound(
            "incident-retry-001"
        )

    def test_lost_ack_reconciles_without_second_manifestation(self):
        proxy = FailOnceAckProxy(self.store)
        first = self.coordinator(outbox=proxy)

        with self.assertRaises(ValueError):
            self.reject(
                first,
                "incident-lost-ack-001",
            )

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

        original = self.world.cronenbergs[0]

        self.assertIs(
            self.store.get("incident-lost-ack-001").status,
            SecurityIncidentStatus.PENDING,
        )

        # Reopen the outbox and create a new coordinator.
        # The same live Universe retains its binding.
        reopened = LocalDurableSecurityIncidentOutbox.open(
            self.path
        )

        second = self.coordinator(outbox=reopened)

        with self.assertRaises(SecurityAttackDetected):
            self.reject(
                second,
                "incident-lost-ack-001",
            )

        self.assertEqual(
            self.world.cronenbergs,
            [original],
        )

        self.assertEqual(
            self.store.get(
                "incident-lost-ack-001"
            ).cronenberg_id,
            original.id,
        )

        self.assert_manifestation_bound(
            "incident-lost-ack-001"
        )

    def test_ambiguous_pending_incident_fails_closed(self):
        self.store.record(
            "incident-ambiguous-001",
            "security_validation",
        )

        coordinator = self.coordinator()

        with self.assertRaises(ValueError):
            self.reject(
                coordinator,
                "incident-ambiguous-001",
            )

        self.assertEqual(len(self.world.cronenbergs), 0)
        self.assertEqual(len(self.world.quantum_events), 0)

        self.assertIs(
            self.store.get(
                "incident-ambiguous-001"
            ).status,
            SecurityIncidentStatus.PENDING,
        )

    def test_forged_delivered_row_never_grants_publication(self):
        incident_id = "incident-forged-delivered"

        self.store.record(
            incident_id,
            "security_validation",
        )

        self.store.acknowledge(
            incident_id,
            "cronenberg_deadbeef",
        )

        with self.assertRaises(ValueError):
            self.reject(
                self.coordinator(),
                incident_id,
            )

        self.assertEqual(len(self.world.cronenbergs), 0)

        self.assertEqual(
            self.store.get(incident_id).cronenberg_id,
            "cronenberg_deadbeef",
        )

    def test_partial_manifestation_rolls_back_and_keeps_pending(self):
        self.world.quantum_events = FailOnceAppend(
            self.world.quantum_events
        )

        with self.assertRaises(ValueError):
            self.reject(
                self.coordinator(),
                "incident-publish-failed",
            )

        self.assertEqual(len(self.world.cronenbergs), 0)
        self.assertEqual(len(self.world.entities), 0)
        self.assertEqual(len(self.world.quantum_events), 0)
        self.assertEqual(self.world.cronenberg_count, 0)

        self.assertIs(
            self.store.get(
                "incident-publish-failed"
            ).status,
            SecurityIncidentStatus.PENDING,
        )

    def test_incident_binding_failure_rolls_back_entire_publication(self):
        self.world.quantum_events = FailSecondAppend(
            self.world.quantum_events
        )

        with self.assertRaises(ValueError):
            self.reject(
                self.coordinator(),
                "incident-binding-failed",
            )

        self.assertEqual(len(self.world.cronenbergs), 0)
        self.assertEqual(len(self.world.entities), 0)
        self.assertEqual(len(self.world.quantum_events), 0)
        self.assertEqual(self.world.cronenberg_count, 0)

        self.assertIs(
            self.store.get(
                "incident-binding-failed"
            ).status,
            SecurityIncidentStatus.PENDING,
        )

    def test_conflicting_source_operation_fails_closed(self):
        self.store.record(
            "incident-conflict-001",
            "authority_reply",
        )

        with self.assertRaises(ValueError):
            self.reject(
                self.coordinator(),
                "incident-conflict-001",
                "receipt_signature",
            )

        self.assertEqual(len(self.world.cronenbergs), 0)
        self.assertEqual(
            self.store.get(
                "incident-conflict-001"
            ).source_operation,
            "authority_reply",
        )

    def test_full_outbox_denies_new_attack_publication(self):
        limited = (
            LocalDurableSecurityIncidentOutbox.create(
                self.path.parent / "limited.sqlite",
                max_pending=1,
                max_total=1,
            )
        )

        limited.record(
            "incident-capacity-existing",
            "security_validation",
        )

        with self.assertRaises(ValueError):
            self.reject(
                self.coordinator(outbox=limited),
                "incident-capacity-new",
            )

        self.assertEqual(len(self.world.cronenbergs), 0)

        self.assertIsNone(
            limited.get("incident-capacity-new")
        )

    def test_invalid_attack_marker_cannot_create_incident(self):
        coordinator = self.coordinator()

        with self.assertRaises(ValueError):
            with redirect_stdout(io.StringIO()):
                coordinator.reject(
                    incident_id="incident-invalid-marker",
                    source_operation="security_validation",
                    attack=ValueError("ordinary application error"),
                )

        self.assertIsNone(
            self.store.get("incident-invalid-marker")
        )

        self.assertEqual(len(self.world.cronenbergs), 0)

    def test_invalid_incident_id_fails_before_recording(self):
        coordinator = self.coordinator()

        for incident_id in (
            None,
            "",
            "../invalid",
            "invalid/id",
            "x" * 129,
        ):
            with self.subTest(incident_id=incident_id):
                with self.assertRaises(ValueError):
                    with redirect_stdout(io.StringIO()):
                        coordinator.reject(
                            incident_id=incident_id,
                            source_operation="security_validation",
                            attack=self.attack(),
                        )

        self.assertEqual(self.store.pending(), ())
        self.assertEqual(len(self.world.cronenbergs), 0)

    def test_distinct_incidents_create_distinct_cronenbergs(self):
        coordinator = self.coordinator()

        for incident_id in (
            "incident-distinct-001",
            "incident-distinct-002",
        ):
            with self.assertRaises(SecurityAttackDetected):
                self.reject(
                    coordinator,
                    incident_id,
                )

        self.assertEqual(len(self.world.cronenbergs), 2)
        self.assertEqual(len(self.manifestations()), 2)

        ids = {
            entity.id
            for entity in self.world.cronenbergs
        }

        self.assertEqual(len(ids), 2)

        for incident_id in (
            "incident-distinct-001",
            "incident-distinct-002",
        ):
            record = self.store.get(incident_id)

            self.assertIs(
                record.status,
                SecurityIncidentStatus.DELIVERED,
            )

            self.assertIn(
                record.cronenberg_id,
                ids,
            )


if __name__ == "__main__":
    unittest.main()
