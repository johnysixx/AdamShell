"""A44 adversarial Cronenberg state checkpoint contract.

Five deliberately RED tests expose semantic consistency
checks not yet implemented in the checkpoint parser.

Other tests protect existing schema, digest, and live
verification behavior.

A locally recomputed SHA-256 is not authentication.
A parsed checkpoint grants no authority to restore
or republish any Universe entity.
"""

import hashlib
import io
import json
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_cronenberg_checkpoint import (
    CanonicalCronenbergStateCheckpoint,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergReconciler,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)

from universe.universe import Universe


WORLD = "a44_668_adversarial_checkpoint"
INCIDENT = "incident-adversarial-checkpoint"
OPERATION = "security_validation"


def rehash(payload):
    """Recalculate an untrusted local checksum."""

    body = {
        key: value
        for key, value in payload.items()
        if key != "checkpoint_sha256"
    }

    encoded = json.dumps(
        body,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    payload["checkpoint_sha256"] = (
        hashlib.sha256(encoded).hexdigest()
    )

    return payload


class A44CronenbergStateCheckpointAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_668_adversarial_"
        )

        self.addCleanup(
            directory.cleanup
        )

        root = Path(directory.name)

        outbox = LocalDurableSecurityIncidentOutbox.create(
            root / "incident.sqlite",
            max_pending=8,
            max_total=16,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id=WORLD
            )

            reconciler = SecurityIncidentCronenbergReconciler(
                universe=self.world,
                outbox=outbox,
            )

            with self.assertRaises(SecurityAttackDetected):
                reconciler.reject(
                    incident_id=INCIDENT,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "adversarial checkpoint diagnostic"
                    ),
                )

        self.Checkpoint = CanonicalCronenbergStateCheckpoint

        self.checkpoint = self.Checkpoint.capture(
            universe=self.world,
            incident_id=INCIDENT,
            source_operation=OPERATION,
        )

        self.entity = self.world.cronenbergs[0]

    def forged(self, mutate):
        payload = self.checkpoint.to_dict()

        mutate(
            payload["entity_state"]
        )

        return self.Checkpoint.parse_untrusted(
            rehash(payload)
        )

    # ------------------------------------------------
    # EXISTING PROTECTIONS: EXPECTED GREEN
    # ------------------------------------------------

    def test_valid_checkpoint_is_detached_and_non_authoritative(self):
        parsed = self.Checkpoint.parse_untrusted(
            self.checkpoint.to_dict()
        )

        self.assertEqual(
            parsed.to_dict(),
            self.checkpoint.to_dict(),
        )

        self.assertTrue(
            parsed.verify_live(self.world)
        )

        self.assertFalse(
            parsed.is_authoritative
        )

        self.assertFalse(
            parsed.is_restorable
        )

        self.assertFalse(
            parsed.can_republish
        )

    def test_rehashed_energy_forgery_is_not_live_truth(self):
        forged = self.forged(
            lambda state: state.__setitem__(
                "energy",
                state["energy"] + 10.0,
            )
        )

        # A structurally consistent local claim is not
        # automatically historical truth.
        self.assertFalse(
            forged.is_authoritative
        )

        with self.assertRaises(ValueError):
            forged.verify_live(
                self.world
            )

        self.assertTrue(
            self.checkpoint.verify_live(self.world)
        )

    def test_nonfinite_energy_rejected(self):
        payload = self.checkpoint.to_dict()

        payload["entity_state"]["energy"] = (
            float("nan")
        )

        with self.assertRaises(ValueError):
            self.Checkpoint.parse_untrusted(
                payload
            )

    def test_spatial_position_flag_mismatch_rejected(self):
        def mutate(state):
            state["spatial"]["position"] = None
            state["spatial"]["has_position"] = True

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )

    def test_hunger_derived_state_mismatch_rejected(self):
        def mutate(state):
            state["hunger"]["hungry_days"] = 0
            state["hunger"]["satiety_days_remaining"] = 0
            state["hunger"]["is_hungry"] = True

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )

    def test_quantum_link_count_mismatch_rejected(self):
        def mutate(state):
            state["quantum_link_system"]["links"] = []
            state["quantum_link_system"]["link_count"] = 3

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )

    def test_nested_aroma_schema_injection_rejected(self):
        def mutate(state):
            state["aroma"]["surface_residues"] = [{
                "source": "injected",
                "components": {},
                "intensity": 1.0,
                "decay_rate": 0.02,
                "age_ticks": 0,
                "unexpected": True,
            }]

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )

    # ------------------------------------------------
    # MISSING SEMANTIC INVARIANTS: EXPECTED RED
    # ------------------------------------------------

    def test_origin_source_component_must_match_traits(self):
        def mutate(state):
            state["origin"]["source_component"] = (
                "forged_checkpoint_component"
            )

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )

    def test_origin_error_type_must_match_traits(self):
        def mutate(state):
            original = state["origin"]["error_type"]

            state["origin"]["error_type"] = (
                "ValueError"
                if original != "ValueError"
                else "TypeError"
            )

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )

    def test_unknown_trait_influence_name_rejected(self):
        def mutate(state):
            state["traits"]["birth_influences"] = [{
                "trait": "not_a_cronenberg_trait",
                "amount": 0.25,
                "reason": "forged influence",
            }]

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )

    def test_duplicate_quantum_link_identity_rejected(self):
        def mutate(state):
            link = {
                "target_id": "cronenberg_other",
                "link_type": "echo",
                "strength": 0.75,
                "created_tick": 1,
                "metadata": {},
            }

            state["quantum_link_system"]["links"] = [
                dict(link),
                dict(link),
            ]

            # Count is deliberately consistent.
            # Duplicate (target_id, link_type) is not.
            state["quantum_link_system"]["link_count"] = 2

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )

    def test_quantum_counterpart_manifestation_without_pair_rejected(self):
        def mutate(state):
            quantum = state["quantum_state"]

            quantum["entangled"] = False
            quantum["pair_id"] = None
            quantum["counterpart_id"] = None
            quantum["counterpart_manifested"] = True

        with self.assertRaises(ValueError):
            self.forged(
                mutate
            )


if __name__ == "__main__":
    unittest.main()
