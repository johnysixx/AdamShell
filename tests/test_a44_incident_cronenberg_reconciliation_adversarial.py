"""A44 adversarial incident-to-Cronenberg reconciliation.

One test is intentionally RED:
concurrent rollback must preserve an independently
committed manifestation for another incident.

Other tests check existing fail-closed recovery paths.

This is a local in-memory Universe diagnostic only.
It does not establish durable cross-process exactly-once
semantics or protection against a compromised host.

All SQLite databases are temporary.
"""

import io
import tempfile
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
    SecurityIncidentStatus,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergBoundEvent,
    SecurityIncidentCronenbergReconciler,
)

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)

from universe.universe import Universe


class PauseThenFailManifestAppend(list):
    """Pause A; let B commit; then fail A's publication."""

    def __init__(self, values, paused, release):
        super().__init__(values)
        self.paused = paused
        self.release = release
        self.armed = True

    def append(self, value):
        super().append(value)

        if (
            self.armed
            and isinstance(
                value,
                CronenbergManifestedEvent,
            )
            and value.source_operation
            == "security_validation"
        ):
            self.armed = False
            self.paused.set()

            if not self.release.wait(timeout=20):
                raise RuntimeError(
                    "Injected concurrency synchronization timeout."
                )

            raise RuntimeError(
                "Injected A publication failure "
                "after B committed."
            )


class FailOnceManifestAppend(list):
    def __init__(self, values):
        super().__init__(values)
        self.armed = True

    def append(self, value):
        super().append(value)

        if (
            self.armed
            and isinstance(
                value,
                CronenbergManifestedEvent,
            )
        ):
            self.armed = False
            raise RuntimeError(
                "Injected manifestation failure."
            )


class AckCommitThenFail:
    """Commit ACK in SQLite, then simulate lost response."""

    def __init__(self, store):
        self.store = store

    def __getattr__(self, name):
        return getattr(self.store, name)

    def acknowledge(self, incident_id, cronenberg_id):
        self.store.acknowledge(
            incident_id,
            cronenberg_id,
        )

        raise OSError(
            "Injected lost acknowledgement response."
        )


class A44IncidentReconciliationAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_reconciliation_adversarial_"
        )

        self.addCleanup(directory.cleanup)

        self.path = (
            Path(directory.name)
            / "incidents.sqlite"
        )

        self.store = (
            LocalDurableSecurityIncidentOutbox.create(
                self.path,
                max_pending=8,
                max_total=16,
            )
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id="a44_adversarial_reconciliation"
            )

    @staticmethod
    def attack():
        return SecurityAttackDetected(
            "SECRET_ATTACK_INPUT_NOT_FOR_EVENTS"
        )

    def coordinator(self, world=None, store=None):
        return SecurityIncidentCronenbergReconciler(
            universe=self.world if world is None else world,
            outbox=self.store if store is None else store,
        )

    def attempt(self, incident_id, source_operation):
        coordinator = self.coordinator()

        try:
            coordinator.reject(
                incident_id=incident_id,
                source_operation=source_operation,
                attack=self.attack(),
            )

        except Exception as exc:
            return exc

        return None

    def successful(self, incident_id, operation="security_validation"):
        with redirect_stdout(io.StringIO()):
            result = self.attempt(
                incident_id,
                operation,
            )

        self.assertIsInstance(
            result,
            SecurityAttackDetected,
        )

        return result

    def bound(self, incident_id):
        return tuple(
            event
            for event in self.world.quantum_events
            if (
                isinstance(
                    event,
                    SecurityIncidentCronenbergBoundEvent,
                )
                and event.incident_id == incident_id
            )
        )

    def test_concurrent_rollback_preserves_other_committed_incident(self):
        """A rollback must finish before B publishes."""

        paused = threading.Event()
        release = threading.Event()
        second_started = threading.Event()
        second_finished = threading.Event()

        self.world.quantum_events = PauseThenFailManifestAppend(
            self.world.quantum_events,
            paused,
            release,
        )

        def publish_second():
            second_started.set()

            try:
                return self.attempt(
                    "incident-concurrent-b",
                    "receipt_signature",
                )

            finally:
                second_finished.set()

        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(
                self.attempt,
                "incident-concurrent-a",
                "security_validation",
            )

            second = None
            completed_during_a = None

            try:
                self.assertTrue(
                    paused.wait(timeout=10),
                    "A publication never reached the pause.",
                )

                second = pool.submit(publish_second)

                self.assertTrue(
                    second_started.wait(timeout=10),
                    "B worker never started.",
                )

                # Correct synchronization prevents B from
                # completing while A's publication is open.
                completed_during_a = second_finished.wait(
                    timeout=1.5
                )

            finally:
                # Never leave the first worker suspended.
                release.set()

            first_result = first.result(timeout=20)

            self.assertIsNotNone(
                second,
                "B publication was not submitted.",
            )

            second_result = second.result(timeout=20)

        self.assertIs(
            type(first_result),
            ValueError,
        )

        self.assertIsInstance(
            second_result,
            SecurityAttackDetected,
        )

        first_record = self.store.get(
            "incident-concurrent-a"
        )

        second_record = self.store.get(
            "incident-concurrent-b"
        )

        self.assertIs(
            first_record.status,
            SecurityIncidentStatus.PENDING,
        )

        self.assertIs(
            second_record.status,
            SecurityIncidentStatus.DELIVERED,
        )

        committed_id = second_record.cronenberg_id

        self.assertTrue(
            any(
                entity.id == committed_id
                for entity in self.world.cronenbergs
            ),
            "A44 CROSS-INCIDENT LOST PUBLICATION: "
            "A rollback erased B's committed Cronenberg.",
        )

        self.assertEqual(
            len(self.bound("incident-concurrent-b")),
            1,
            "A rollback erased B's canonical binding.",
        )

        self.assertEqual(
            len(self.bound("incident-concurrent-a")),
            0,
            "Failed A retained an incident binding.",
        )

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
            "Only B's Cronenberg may remain.",
        )

        self.assertFalse(
            completed_during_a,
            "A44 CROSS-INCIDENT OVERLAP: "
            "B completed before A's transaction ended.",
        )

    def test_ack_committed_then_response_lost_reconciles(self):
        proxy = AckCommitThenFail(self.store)

        coordinator = self.coordinator(store=proxy)

        with self.assertRaises(ValueError):
            with redirect_stdout(io.StringIO()):
                coordinator.reject(
                    incident_id="incident-ack-response-lost",
                    source_operation="security_validation",
                    attack=self.attack(),
                )

        record = self.store.get(
            "incident-ack-response-lost"
        )

        self.assertIs(
            record.status,
            SecurityIncidentStatus.DELIVERED,
        )

        original_id = record.cronenberg_id

        self.successful(
            "incident-ack-response-lost"
        )

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

        self.assertEqual(
            self.world.cronenbergs[0].id,
            original_id,
        )

    def test_delivered_replay_cannot_duplicate(self):
        self.successful(
            "incident-delivered-replay"
        )

        original = self.world.cronenbergs[0]

        self.successful(
            "incident-delivered-replay"
        )

        self.assertEqual(
            self.world.cronenbergs,
            [original],
        )

        self.assertEqual(
            len(self.bound("incident-delivered-replay")),
            1,
        )

    def test_pending_without_binding_is_held(self):
        self.store.record(
            "incident-ambiguous-pending",
            "security_validation",
        )

        with self.assertRaises(ValueError):
            with redirect_stdout(io.StringIO()):
                self.coordinator().reject(
                    incident_id="incident-ambiguous-pending",
                    source_operation="security_validation",
                    attack=self.attack(),
                )

        self.assertEqual(
            len(self.world.cronenbergs),
            0,
        )

    def test_duplicate_universe_bindings_are_rejected(self):
        self.successful(
            "incident-duplicate-binding"
        )

        original = self.bound(
            "incident-duplicate-binding"
        )[0]

        self.world.quantum_events.append(original)

        # attempt() returns the caught exception.
        result = self.attempt(
            "incident-duplicate-binding",
            "security_validation",
        )

        self.assertIs(
            type(result),
            ValueError,
        )

        self.assertIn(
            "Ambiguous or invalid Universe incident binding.",
            str(result),
        )

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

    def test_missing_manifestation_event_is_rejected(self):
        self.successful(
            "incident-missing-manifest"
        )

        self.world.quantum_events[:] = [
            event
            for event in self.world.quantum_events
            if not isinstance(
                event,
                CronenbergManifestedEvent,
            )
        ]

        result = self.attempt(
            "incident-missing-manifest",
            "security_validation",
        )

        self.assertIsInstance(result, ValueError)

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

    def test_missing_canonical_entity_is_rejected(self):
        self.successful(
            "incident-missing-entity"
        )

        self.world.cronenbergs.clear()

        result = self.attempt(
            "incident-missing-entity",
            "security_validation",
        )

        self.assertIsInstance(result, ValueError)

        self.assertEqual(
            self.world.cronenbergs,
            [],
        )

    def test_forged_ack_does_not_satisfy_reconciliation(self):
        incident_id = "incident-forged-ack"

        self.store.record(
            incident_id,
            "security_validation",
        )

        self.store.acknowledge(
            incident_id,
            "cronenberg_deadbeef",
        )

        result = self.attempt(
            incident_id,
            "security_validation",
        )

        self.assertIsInstance(result, ValueError)

        self.assertEqual(
            len(self.world.cronenbergs),
            0,
        )

    def test_delivered_incident_in_foreign_universe_is_denied(self):
        self.successful(
            "incident-foreign-universe"
        )

        with redirect_stdout(io.StringIO()):
            foreign_world = Universe(
                universe_id="a44_other_universe"
            )

        foreign = self.coordinator(
            world=foreign_world
        )

        with self.assertRaises(ValueError):
            foreign.reject(
                incident_id="incident-foreign-universe",
                source_operation="security_validation",
                attack=self.attack(),
            )

        self.assertEqual(
            len(foreign_world.cronenbergs),
            0,
        )

    def test_one_cronenberg_cannot_bind_two_incidents(self):
        self.successful(
            "incident-binding-first"
        )

        original_id = self.world.cronenbergs[0].id

        self.store.record(
            "incident-binding-second",
            "security_validation",
        )

        self.world.quantum_events.append(
            SecurityIncidentCronenbergBoundEvent(
                incident_id="incident-binding-second",
                cronenberg_id=original_id,
                source_operation="security_validation",
            )
        )

        result = self.attempt(
            "incident-binding-second",
            "security_validation",
        )

        self.assertIsInstance(result, ValueError)

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

    def test_failed_manifestation_retry_stays_pending(self):
        self.world.quantum_events = FailOnceManifestAppend(
            self.world.quantum_events
        )

        first = self.attempt(
            "incident-failed-retry",
            "security_validation",
        )

        self.assertIsInstance(first, ValueError)

        self.assertEqual(
            len(self.world.cronenbergs),
            0,
        )

        self.assertIs(
            self.store.get(
                "incident-failed-retry"
            ).status,
            SecurityIncidentStatus.PENDING,
        )

        second = self.attempt(
            "incident-failed-retry",
            "security_validation",
        )

        self.assertIsInstance(second, ValueError)

        self.assertEqual(
            len(self.world.cronenbergs),
            0,
        )

        # A previous failed publication is not proof
        # that blind republication is now safe.

    def test_source_operation_collision_is_denied(self):
        self.successful(
            "incident-operation-collision",
            "security_validation",
        )

        result = self.attempt(
            "incident-operation-collision",
            "authority_reply",
        )

        self.assertIsInstance(result, ValueError)

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

        self.assertEqual(
            self.store.get(
                "incident-operation-collision"
            ).source_operation,
            "security_validation",
        )


if __name__ == "__main__":
    unittest.main()
