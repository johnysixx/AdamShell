"""A44 canonical security publication evidence contract.

EXPECTED RED until canonical recovery evidence is implemented.

Capture requires a real live canonical triad:
- one Cronenberg registered in both Universe registries;
- one matching CronenbergManifestedEvent;
- one SecurityIncidentCronenbergBoundEvent.

The detached projection must have deterministic canonical JSON
serialization and SHA-256 content binding.

A correct SHA-256 checksum is NOT an authenticity guarantee.
Untrusted parsed evidence is never a trusted checkpoint.
The projection is not a complete entity savegame.
It cannot authorize entity reconstruction or republication.

All test databases are temporary.
"""

import dataclasses
import hashlib
import importlib
import json
import tempfile
import unittest

from pathlib import Path

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergBoundEvent,
    SecurityIncidentCronenbergReconciler,
)

from core.existence.history_receipt_trust_publication_witness import (
    LocalDurablePublicationWitnessJournal,
)

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)

from universe.universe import Universe


MODULE = (
    "core.existence."
    "history_receipt_trust_canonical_recovery"
)

WORLD_ID = "a44_665_canonical_projection"
INCIDENT = "incident-canonical-projection"
OPERATION = "security_validation"


def canonical_digest(body):
    """Diagnostic canonical JSON digest; not a signature."""

    encoded = json.dumps(
        body,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


class A44CanonicalRecoveryContractTests(unittest.TestCase):

    def setUp(self):
        implementation = importlib.import_module(MODULE)

        self.Evidence = (
            implementation.CanonicalSecurityPublicationEvidence
        )

        directory = tempfile.TemporaryDirectory(
            prefix="a44_665_contract_"
        )

        self.addCleanup(directory.cleanup)

        self.directory = Path(directory.name)

        self.outbox = LocalDurableSecurityIncidentOutbox.create(
            self.directory / "outbox.sqlite",
            max_pending=8,
            max_total=16,
        )

        self.world = Universe(
            universe_id=WORLD_ID
        )

    def publish(
        self,
        incident_id=INCIDENT,
        source_operation=OPERATION,
    ):
        coordinator = SecurityIncidentCronenbergReconciler(
            universe=self.world,
            outbox=self.outbox,
        )

        with self.assertRaises(SecurityAttackDetected):
            coordinator.reject(
                incident_id=incident_id,
                source_operation=source_operation,
                attack=SecurityAttackDetected(
                    "canonical recovery test incident"
                ),
            )

    def capture(
        self,
        incident_id=INCIDENT,
        source_operation=OPERATION,
        universe=None,
    ):
        return self.Evidence.capture(
            universe=(
                self.world
                if universe is None
                else universe
            ),
            incident_id=incident_id,
            source_operation=source_operation,
        )

    def find_event(self, event_type):
        return next(
            event
            for event in self.world.quantum_events
            if type(event) is event_type
        )

    def test_capture_requires_live_canonical_triad(self):
        self.publish()

        record = self.capture()

        self.assertTrue(
            dataclasses.is_dataclass(record)
        )

        self.assertTrue(
            record.__dataclass_params__.frozen
        )

        self.assertEqual(record.universe_id, WORLD_ID)
        self.assertEqual(record.incident_id, INCIDENT)

        self.assertEqual(
            record.source_operation,
            OPERATION,
        )

        self.assertEqual(
            record.cronenberg_id,
            self.world.cronenbergs[0].id,
        )

        self.assertIs(record.is_authoritative, False)
        self.assertIs(record.is_restorable, False)

        payload = record.to_dict()

        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "universe_id",
                "incident_id",
                "source_operation",
                "cronenberg_id",
                "entity",
                "manifestation",
                "binding",
                "projection_sha256",
            },
        )

        self.assertEqual(
            payload["schema_version"],
            1,
        )

        self.assertEqual(
            payload["entity"],
            {
                "id": record.cronenberg_id,
                "type": "cronenberg",
            },
        )

        self.assertEqual(
            payload["manifestation"]["cronenberg_id"],
            record.cronenberg_id,
        )

        self.assertEqual(
            payload["binding"]["incident_id"],
            INCIDENT,
        )

        self.assertEqual(
            payload["projection_sha256"],
            canonical_digest({
                key: value
                for key, value in payload.items()
                if key != "projection_sha256"
            }),
        )

    def test_capture_deterministic_without_publication_side_effects(self):
        self.publish()

        before = (
            tuple(self.world.cronenbergs),
            tuple(self.world.entities),
            tuple(self.world.quantum_events),
            self.world.cronenberg_count,
        )

        first = self.capture()
        second = self.capture()

        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )

        after = (
            tuple(self.world.cronenbergs),
            tuple(self.world.entities),
            tuple(self.world.quantum_events),
            self.world.cronenberg_count,
        )

        self.assertEqual(before, after)

    def test_capture_result_immutable_and_serialization_detached(self):
        self.publish()

        record = self.capture()

        with self.assertRaises(
            dataclasses.FrozenInstanceError
        ):
            record.incident_id = "changed"

        payload = record.to_dict()

        payload["binding"]["incident_id"] = "forged"
        payload["manifestation"]["error_message"] = "forged"
        payload["entity"]["id"] = "cronenberg_deadbeef"

        self.assertEqual(
            record.to_dict()["binding"]["incident_id"],
            INCIDENT,
        )

        self.assertEqual(
            record.to_dict()["manifestation"]["error_message"],
            "A44 blocked security attack.",
        )

        self.assertEqual(
            record.to_dict()["entity"]["id"],
            record.cronenberg_id,
        )

    def test_missing_and_duplicate_binding_fail_closed(self):
        self.publish()

        binding = self.find_event(
            SecurityIncidentCronenbergBoundEvent
        )

        self.world.quantum_events.remove(binding)

        with self.assertRaises(ValueError):
            self.capture()

        self.world.quantum_events.append(binding)
        self.world.quantum_events.append(binding)

        with self.assertRaises(ValueError):
            self.capture()

    def test_missing_and_duplicate_manifestation_fail_closed(self):
        self.publish()

        manifestation = self.find_event(
            CronenbergManifestedEvent
        )

        self.world.quantum_events.remove(manifestation)

        with self.assertRaises(ValueError):
            self.capture()

        self.world.quantum_events.append(manifestation)
        self.world.quantum_events.append(manifestation)

        with self.assertRaises(ValueError):
            self.capture()

    def test_missing_and_duplicate_canonical_entity_fail_closed(self):
        self.publish()

        entity = self.world.cronenbergs.pop()

        with self.assertRaises(ValueError):
            self.capture()

        self.world.cronenbergs.append(entity)
        self.world.entities.append(entity)

        with self.assertRaises(ValueError):
            self.capture()

    def test_foreign_incident_operation_and_universe_fail_closed(self):
        self.publish()

        with self.assertRaises(ValueError):
            self.capture(
                incident_id="incident-other"
            )

        with self.assertRaises(ValueError):
            self.capture(
                source_operation="receipt_signature"
            )

        foreign = Universe(
            universe_id="a44_foreign_projection"
        )

        with self.assertRaises(ValueError):
            self.capture(universe=foreign)

    def test_manifestation_provenance_tamper_fails_closed(self):
        self.publish()

        manifestation = self.find_event(
            CronenbergManifestedEvent
        )

        index = self.world.quantum_events.index(
            manifestation
        )

        self.world.quantum_events[index] = (
            CronenbergManifestedEvent(
                cronenberg_id=manifestation.cronenberg_id,
                source_component=manifestation.source_component,
                source_operation=manifestation.source_operation,
                error_type="RuntimeError",
                error_message="changed attacker-provided data",
                quantum_tick=manifestation.quantum_tick,
            )
        )

        with self.assertRaises(ValueError):
            self.capture()

    def test_parse_untrusted_validates_shape_and_projection_digest(self):
        self.publish()

        payload = self.capture().to_dict()

        parsed = self.Evidence.parse_untrusted(
            payload
        )

        self.assertIsInstance(
            parsed,
            self.Evidence,
        )

        self.assertEqual(
            parsed.to_dict(),
            payload,
        )

        self.assertFalse(parsed.is_authoritative)
        self.assertFalse(parsed.is_restorable)

        variants = []

        changed = dict(payload)
        changed["projection_sha256"] = "a" * 64
        variants.append(changed)

        changed = dict(payload)
        changed["schema_version"] = True
        variants.append(changed)

        changed = dict(payload)
        changed["unexpected_key"] = "unsafe"
        variants.append(changed)

        changed = dict(payload)
        del changed["binding"]
        variants.append(changed)

        changed = dict(payload)
        changed["manifestation"] = "not-an-event"
        variants.append(changed)

        for variant in variants:
            with self.subTest(
                variant=tuple(variant.keys())
            ):
                with self.assertRaises(ValueError):
                    self.Evidence.parse_untrusted(
                        variant
                    )

    def test_verify_live_requires_original_canonical_evidence(self):
        self.publish()

        checkpoint = self.capture()

        self.assertIs(
            checkpoint.verify_live(self.world),
            True,
        )

        manifestation = self.find_event(
            CronenbergManifestedEvent
        )

        index = self.world.quantum_events.index(
            manifestation
        )

        self.world.quantum_events[index] = (
            CronenbergManifestedEvent(
                cronenberg_id=manifestation.cronenberg_id,
                source_component=manifestation.source_component,
                source_operation=manifestation.source_operation,
                error_type=manifestation.error_type,
                error_message=manifestation.error_message,
                quantum_tick=manifestation.quantum_tick + 1,
            )
        )

        with self.assertRaises(ValueError):
            checkpoint.verify_live(self.world)

    def test_valid_looking_rehashed_evidence_has_no_restore_authority(self):
        self.publish()

        payload = self.capture().to_dict()

        payload["manifestation"]["quantum_tick"] += 7

        payload["projection_sha256"] = (
            canonical_digest({
                key: value
                for key, value in payload.items()
                if key != "projection_sha256"
            })
        )

        untrusted = self.Evidence.parse_untrusted(
            payload
        )

        self.assertIs(
            untrusted.is_authoritative,
            False,
        )

        self.assertIs(
            untrusted.is_restorable,
            False,
        )

        with self.assertRaises(ValueError):
            untrusted.verify_live(self.world)

        fresh = Universe(
            universe_id=WORLD_ID
        )

        with self.assertRaises(ValueError):
            untrusted.verify_live(fresh)

        self.assertEqual(
            len(fresh.cronenbergs),
            0,
        )

        self.assertEqual(
            len(fresh.quantum_events),
            0,
        )

    def test_local_observed_journal_cannot_substitute_for_universe_evidence(self):
        journal = LocalDurablePublicationWitnessJournal.create(
            self.directory / "witness.sqlite",
            universe_id=WORLD_ID,
            max_entries=4,
        )

        self.assertTrue(
            journal.prepare(
                INCIDENT,
                OPERATION,
            )
        )

        self.assertTrue(
            journal.observe(
                INCIDENT,
                "cronenberg_deadbeef",
                "a" * 64,
            )
        )

        self.assertFalse(
            journal.get(INCIDENT).is_authoritative
        )

        with self.assertRaises(ValueError):
            self.capture()

        self.assertEqual(
            len(self.world.cronenbergs),
            0,
        )

        self.assertEqual(
            len(self.world.quantum_events),
            0,
        )


if __name__ == "__main__":
    unittest.main()
