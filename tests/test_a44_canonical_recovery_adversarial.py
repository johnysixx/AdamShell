"""A44 adversarial canonical publication evidence tests.

EXPECTED RED: a subclass of CronenbergManifestedEvent
claiming an already manifested Cronenberg is ignored by
the current exact-type manifestation selection.

Other tests verify fail-closed handling of lookalike
bindings, duplicate entity identity, malformed provenance,
rehashed untrusted content, and detached evidence.

Concurrent capture tests cover read-only calls on an
unchanged Universe only. No mutation concurrency,
cross-process exactly-once, trusted persistence, or
entity restoration is established here.
"""

import dataclasses
import hashlib
import io
import json
import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergBoundEvent,
    SecurityIncidentCronenbergReconciler,
)

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)

from universe.universe import Universe


WORLD = "a44_665_adversarial_projection"
INCIDENT = "incident-adversarial-projection"
OPERATION = "security_validation"


class ShadowManifestation(CronenbergManifestedEvent):
    """A different runtime type claiming the same event."""


class ShadowBinding(SecurityIncidentCronenbergBoundEvent):
    """A different runtime type claiming the same incident."""


def canonical_digest(body):
    encoded = json.dumps(
        body,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


class A44CanonicalEvidenceAdversarialTests(unittest.TestCase):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_665_adversarial_"
        )

        self.addCleanup(directory.cleanup)

        self.outbox = LocalDurableSecurityIncidentOutbox.create(
            Path(directory.name) / "outbox.sqlite",
            max_pending=8,
            max_total=16,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id=WORLD
            )

            coordinator = SecurityIncidentCronenbergReconciler(
                universe=self.world,
                outbox=self.outbox,
            )

            with self.assertRaises(SecurityAttackDetected):
                coordinator.reject(
                    incident_id=INCIDENT,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "adversarial test incident"
                    ),
                )

        self.Evidence = CanonicalSecurityPublicationEvidence

        self.original = self.capture()

    def capture(self):
        return self.Evidence.capture(
            universe=self.world,
            incident_id=INCIDENT,
            source_operation=OPERATION,
        )

    def event(self, expected_type):
        matches = [
            event
            for event in self.world.quantum_events
            if type(event) is expected_type
        ]

        self.assertEqual(len(matches), 1)

        return matches[0]

    def shadow_manifestation(self, original):
        return ShadowManifestation(
            cronenberg_id=original.cronenberg_id,
            source_component=original.source_component,
            source_operation=original.source_operation,
            error_type=original.error_type,
            error_message=original.error_message,
            quantum_tick=original.quantum_tick,
        )

    def shadow_binding(self, original):
        return ShadowBinding(
            incident_id=original.incident_id,
            cronenberg_id=original.cronenberg_id,
            source_operation=original.source_operation,
        )

    def replace_event(self, old, new):
        index = next(
            index
            for index, event in enumerate(
                self.world.quantum_events
            )
            if event is old
        )

        self.world.quantum_events[index] = new

    def test_duplicate_manifestation_subclass_is_rejected(self):
        """EXPECTED RED: subclass duplicate must be ambiguous."""

        original = self.event(
            CronenbergManifestedEvent
        )

        shadow = self.shadow_manifestation(original)

        self.assertIsInstance(
            shadow,
            CronenbergManifestedEvent,
        )

        self.assertIsNot(
            type(shadow),
            CronenbergManifestedEvent,
        )

        self.world.quantum_events.append(shadow)

        self.assertEqual(
            sum(
                isinstance(event, CronenbergManifestedEvent)
                and event.cronenberg_id == original.cronenberg_id
                for event in self.world.quantum_events
            ),
            2,
        )

        with self.assertRaises(ValueError):
            self.capture()

    def test_only_manifestation_subclass_rejected(self):
        original = self.event(
            CronenbergManifestedEvent
        )

        self.replace_event(
            original,
            self.shadow_manifestation(original),
        )

        with self.assertRaises(ValueError):
            self.capture()

    def test_duplicate_incident_binding_subclass_rejected(self):
        original = self.event(
            SecurityIncidentCronenbergBoundEvent
        )

        self.world.quantum_events.append(
            self.shadow_binding(original)
        )

        with self.assertRaises(ValueError):
            self.capture()

    def test_only_incident_binding_subclass_rejected(self):
        original = self.event(
            SecurityIncidentCronenbergBoundEvent
        )

        self.replace_event(
            original,
            self.shadow_binding(original),
        )

        with self.assertRaises(ValueError):
            self.capture()

    def test_duplicate_cronenberg_registry_identity_rejected(self):
        original = self.world.cronenbergs[0]

        lookalike = SimpleNamespace(
            id=original.id,
            type="cronenberg",
        )

        self.world.cronenbergs.append(lookalike)

        with self.assertRaises(ValueError):
            self.capture()

    def test_duplicate_entity_registry_identity_rejected(self):
        original = self.world.cronenbergs[0]

        lookalike = SimpleNamespace(
            id=original.id,
            type="cronenberg",
        )

        self.world.entities.append(lookalike)

        with self.assertRaises(ValueError):
            self.capture()

    def test_modified_canonical_entity_type_rejected(self):
        original = self.world.cronenbergs[0]

        original.type = "not_cronenberg"

        with self.assertRaises(ValueError):
            self.capture()

    def test_modified_incident_binding_operation_rejected(self):
        original = self.event(
            SecurityIncidentCronenbergBoundEvent
        )

        self.replace_event(
            original,
            dataclasses.replace(
                original,
                source_operation="receipt_signature",
            ),
        )

        with self.assertRaises(ValueError):
            self.capture()

    def test_negative_manifestation_tick_rejected(self):
        original = self.event(
            CronenbergManifestedEvent
        )

        self.replace_event(
            original,
            dataclasses.replace(
                original,
                quantum_tick=-1,
            ),
        )

        with self.assertRaises(ValueError):
            self.capture()

    def test_rehashed_forged_binding_still_rejected(self):
        payload = self.original.to_dict()

        payload["binding"]["source_component"] = (
            "forged_authority"
        )

        payload["projection_sha256"] = canonical_digest({
            key: value
            for key, value in payload.items()
            if key != "projection_sha256"
        })

        with self.assertRaises(ValueError):
            self.Evidence.parse_untrusted(
                payload
            )

        self.assertTrue(
            self.original.verify_live(self.world)
        )

    def test_mutation_after_capture_invalidates_live_verification(self):
        before = self.original.to_dict()

        original = self.event(
            CronenbergManifestedEvent
        )

        self.replace_event(
            original,
            dataclasses.replace(
                original,
                quantum_tick=original.quantum_tick + 1,
            ),
        )

        self.assertEqual(
            self.original.to_dict(),
            before,
        )

        with self.assertRaises(ValueError):
            self.original.verify_live(self.world)

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

    def test_concurrent_read_only_capture_is_deterministic(self):
        """Read-only test; no concurrent Universe mutations."""

        expected = self.original.to_dict()

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(
                pool.map(
                    lambda _: self.capture().to_dict(),
                    range(12),
                )
            )

        self.assertEqual(
            results,
            [expected] * 12,
        )

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

        self.assertEqual(
            len(self.world.quantum_events),
            2,
        )


if __name__ == "__main__":
    unittest.main()
