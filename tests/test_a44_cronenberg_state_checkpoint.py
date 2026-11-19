"""A44 canonical Cronenberg state checkpoint contract.

EXPECTED RED: the checkpoint module is not installed.

This contract concerns a supported canonical Cronenberg's
entity-state graph, not an entire Universe checkpoint.

Capture must include all supported runtime attributes
except the external Universe registry reference.

Unknown runtime fields, opaque ability objects, or
unsupported external policies must fail closed instead
of silently producing an incomplete checkpoint.

The snapshot is detached, versioned and hash-consistent.
Its SHA-256 is not an authentication mechanism.

Even a complete supported entity-state snapshot remains
non-authoritative and non-restorable at this stage.

No restoration, publication, or trusted-root enrollment.
"""

import dataclasses
import hashlib
import importlib
import io
import json
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path

from core.entity.cronenberg_system.consumption import (
    CronenbergConsumptionRecord,
)

from core.entity.components.spatial import (
    SpatialVector3,
)

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergReconciler,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)

from universe.universe import Universe


MODULE = (
    "core.existence."
    "history_receipt_trust_cronenberg_checkpoint"
)

WORLD = "a44_668_cronenberg_checkpoint"
INCIDENT = "incident-cronenberg-checkpoint"
OPERATION = "security_validation"

SCHEMA_VERSION = 1

PAYLOAD_KEYS = {
    "schema_version",
    "universe_id",
    "incident_id",
    "source_operation",
    "cronenberg_id",
    "projection_sha256",
    "entity_state",
    "checkpoint_sha256",
}

SCALAR_FIELDS = {
    "id",
    "name",
    "type",
    "age",
    "energy",
    "state",
    "active",
    "evolution_threshold",
    "evolved",
    "depth",
    "birth_allowed",
    "location",
    "size",
    "juice_value",
}

COMPONENT_FIELDS = {
    "abilities",
    "spatial",
    "aroma",
    "aroma_chemical_marker",
    "metabolism",
    "hunger",
    "travel",
    "growth",
    "consumed_cronenbergs",
    "traits",
    "quantum_link_system",
    "quantum_state",
    "origin",
    "profile",
    "bar_policy",
}


def canonical_bytes(payload):
    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def rehash(payload):
    body = {
        key: value
        for key, value in payload.items()
        if key != "checkpoint_sha256"
    }

    payload["checkpoint_sha256"] = (
        hashlib.sha256(
            canonical_bytes(body)
        ).hexdigest()
    )

    return payload


class A44CronenbergStateCheckpointContractTests(
    unittest.TestCase
):

    def setUp(self):
        implementation = importlib.import_module(
            MODULE
        )

        self.Checkpoint = (
            implementation.CanonicalCronenbergStateCheckpoint
        )

        directory = tempfile.TemporaryDirectory(
            prefix="a44_668_checkpoint_contract_"
        )

        self.addCleanup(directory.cleanup)

        self.root = Path(directory.name)

        outbox = LocalDurableSecurityIncidentOutbox.create(
            self.root / "incident.sqlite",
            max_pending=8,
            max_total=16,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id=WORLD
            )

            coordinator = SecurityIncidentCronenbergReconciler(
                universe=self.world,
                outbox=outbox,
            )

            with self.assertRaises(SecurityAttackDetected):
                coordinator.reject(
                    incident_id=INCIDENT,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "checkpoint contract test"
                    ),
                )

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

        self.entity = self.world.cronenbergs[0]

        self.evidence = (
            CanonicalSecurityPublicationEvidence.capture(
                universe=self.world,
                incident_id=INCIDENT,
                source_operation=OPERATION,
            )
        )

    def capture(self):
        return self.Checkpoint.capture(
            universe=self.world,
            incident_id=INCIDENT,
            source_operation=OPERATION,
        )

    def test_supported_state_inventory_and_typed_components(self):
        checkpoint = self.capture()
        payload = checkpoint.to_dict()

        self.assertEqual(
            set(payload),
            PAYLOAD_KEYS,
        )

        self.assertEqual(
            payload["schema_version"],
            SCHEMA_VERSION,
        )

        self.assertEqual(
            payload["universe_id"],
            WORLD,
        )

        self.assertEqual(
            payload["incident_id"],
            INCIDENT,
        )

        self.assertEqual(
            payload["source_operation"],
            OPERATION,
        )

        self.assertEqual(
            payload["cronenberg_id"],
            self.entity.id,
        )

        self.assertEqual(
            payload["projection_sha256"],
            self.evidence.projection_sha256,
        )

        state = payload["entity_state"]

        # External Universe references belong to the
        # registration boundary, never the entity snapshot.
        runtime_fields = (
            set(vars(self.entity)) - {"universe"}
        )

        self.assertEqual(
            set(state),
            runtime_fields,
        )

        self.assertEqual(
            set(state),
            SCALAR_FIELDS | COMPONENT_FIELDS,
        )

        for name in SCALAR_FIELDS:
            with self.subTest(field=name):
                self.assertEqual(
                    state[name],
                    getattr(self.entity, name),
                )

        for name in (
            "metabolism",
            "hunger",
            "travel",
            "growth",
            "traits",
            "quantum_link_system",
            "abilities",
            "spatial",
        ):
            with self.subTest(component=name):
                self.assertEqual(
                    state[name],
                    getattr(
                        self.entity,
                        name,
                    ).public_state,
                )

        self.assertEqual(
            state["quantum_state"],
            self.entity.quantum_state.to_dict(),
        )

        self.assertEqual(
            state["origin"],
            self.entity.origin.to_dict(),
        )

        self.assertEqual(
            state["aroma"],
            self.entity.aroma.to_dict(),
        )

        self.assertEqual(
            state["aroma_chemical_marker"],
            {
                "molecule": (
                    self.entity.aroma_chemical_marker.molecule
                ),
                "formula": (
                    self.entity.aroma_chemical_marker.formula
                ),
            },
        )

        self.assertEqual(
            state["consumed_cronenbergs"],
            [],
        )

        self.assertIsNone(
            state["profile"]
        )

        self.assertIsNone(
            state["bar_policy"]
        )

    def test_detached_serialization_does_not_mutate_checkpoint(self):
        checkpoint = self.capture()

        original = checkpoint.to_dict()
        changed = checkpoint.to_dict()

        changed["entity_state"]["metabolism"][
            "pending_dark_energy"
        ] = 999.0

        changed["entity_state"]["aroma"][
            "base_intensity"
        ] = 999.0

        changed["entity_state"]["energy"] = -100.0

        self.assertEqual(
            checkpoint.to_dict(),
            original,
        )

        self.assertNotEqual(
            changed,
            original,
        )

        self.assertTrue(
            checkpoint.verify_live(
                self.world
            )
        )

    def test_runtime_mutation_requires_new_checkpoint(self):
        before = self.capture()

        self.entity.energy += 4.0

        self.entity.metabolism.pending_dark_energy += 2.0

        self.entity.hunger.hungry_days = 2

        self.entity.spatial.set_velocity(
            SpatialVector3(
                x=1.0,
                y=2.0,
                z=3.0,
            )
        )

        self.entity.quantum_link_system.add_link(
            target_id="cronenberg_other",
            link_type="echo",
            strength=0.75,
            created_tick=3,
            metadata={
                "source": "checkpoint_contract",
            },
        )

        self.entity.consumed_cronenbergs.append(
            CronenbergConsumptionRecord(
                name="previous_prey",
                mass=1.5,
                energy=2.5,
                digestion_days=3,
            )
        )

        with self.assertRaises(ValueError):
            before.verify_live(
                self.world
            )

        after = self.capture()

        self.assertNotEqual(
            before.checkpoint_sha256,
            after.checkpoint_sha256,
        )

        state = after.to_dict()["entity_state"]

        self.assertEqual(
            state["energy"],
            self.entity.energy,
        )

        self.assertEqual(
            state["metabolism"],
            self.entity.metabolism.public_state,
        )

        self.assertEqual(
            state["hunger"],
            self.entity.hunger.public_state,
        )

        self.assertEqual(
            state["spatial"],
            self.entity.spatial.public_state,
        )

        self.assertEqual(
            state["quantum_link_system"],
            self.entity.quantum_link_system.public_state,
        )

        self.assertEqual(
            state["consumed_cronenbergs"],
            [
                entry.to_dict()
                for entry in self.entity.consumed_cronenbergs
            ],
        )

        self.assertTrue(
            after.verify_live(self.world)
        )

    def test_checkpoint_digest_is_deterministic(self):
        first = self.capture()
        second = self.capture()

        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )

        payload = first.to_dict()
        expected = rehash(
            payload
        )

        self.assertEqual(
            first.checkpoint_sha256,
            expected["checkpoint_sha256"],
        )

        self.assertEqual(
            len(first.checkpoint_sha256),
            64,
        )

    def test_roundtrip_untrusted_remains_non_authoritative(self):
        checkpoint = self.capture()

        parsed = self.Checkpoint.parse_untrusted(
            checkpoint.to_dict()
        )

        self.assertIs(
            type(parsed),
            self.Checkpoint,
        )

        self.assertEqual(
            parsed.to_dict(),
            checkpoint.to_dict(),
        )

        self.assertTrue(
            parsed.verify_live(
                self.world
            )
        )

        self.assertTrue(
            dataclasses.is_dataclass(parsed)
        )

        self.assertIs(
            parsed.is_authoritative,
            False,
        )

        self.assertIs(
            parsed.is_restorable,
            False,
        )

        self.assertIs(
            parsed.can_republish,
            False,
        )

        with self.assertRaises(
            dataclasses.FrozenInstanceError
        ):
            parsed.checkpoint_sha256 = "a" * 64

    def test_wrong_digest_and_missing_required_fields_rejected(self):
        checkpoint = self.capture()

        invalid_digest = checkpoint.to_dict()
        invalid_digest["checkpoint_sha256"] = "f" * 64

        if (
            invalid_digest["checkpoint_sha256"]
            == checkpoint.checkpoint_sha256
        ):
            invalid_digest["checkpoint_sha256"] = "e" * 64

        with self.assertRaises(ValueError):
            self.Checkpoint.parse_untrusted(
                invalid_digest
            )

        missing = checkpoint.to_dict()
        del missing["projection_sha256"]

        with self.assertRaises(ValueError):
            self.Checkpoint.parse_untrusted(
                missing
            )

    def test_rehashed_modified_state_is_not_live_truth(self):
        checkpoint = self.capture()

        forged = checkpoint.to_dict()

        forged["entity_state"]["energy"] += 10.0

        rehash(
            forged
        )

        parsed = self.Checkpoint.parse_untrusted(
            forged
        )

        self.assertEqual(
            parsed.to_dict(),
            forged,
        )

        self.assertFalse(
            parsed.is_authoritative
        )

        self.assertFalse(
            parsed.is_restorable
        )

        with self.assertRaises(ValueError):
            parsed.verify_live(
                self.world
            )

        self.assertTrue(
            checkpoint.verify_live(
                self.world
            )
        )

    def test_unknown_and_missing_nested_fields_rejected(self):
        checkpoint = self.capture()

        extra_top = checkpoint.to_dict()
        extra_top["unexpected"] = True

        extra_nested = checkpoint.to_dict()
        extra_nested["entity_state"]["metabolism"][
            "unexpected"
        ] = 123

        missing_nested = checkpoint.to_dict()
        del missing_nested["entity_state"]["spatial"]

        for invalid in (
            extra_top,
            extra_nested,
            missing_nested,
        ):
            with self.subTest(
                keys=tuple(sorted(invalid))
            ):
                rehash(
                    invalid
                )

                with self.assertRaises(ValueError):
                    self.Checkpoint.parse_untrusted(
                        invalid
                    )

    def test_unknown_runtime_fields_and_opaque_abilities_fail_closed(self):
        self.entity.unexpected_runtime = object()

        try:
            with self.assertRaises(ValueError):
                self.capture()

        finally:
            del self.entity.unexpected_runtime

        self.entity.abilities.grant(
            "unsupported_opaque_ability",
            object(),
        )

        try:
            with self.assertRaises(ValueError):
                self.capture()

        finally:
            self.entity.abilities.revoke(
                "unsupported_opaque_ability"
            )

        self.entity.profile = object()

        try:
            with self.assertRaises(ValueError):
                self.capture()

        finally:
            self.entity.profile = None

        self.assertTrue(
            self.capture().verify_live(
                self.world
            )
        )

    def test_nonfinite_and_type_confusion_rejected(self):
        samples = (
            (self.entity, "energy", float("nan")),
            (
                self.entity.metabolism,
                "pending_dark_energy",
                float("inf"),
            ),
            (self.entity, "age", True),
            (
                self.entity.hunger,
                "hungry_days",
                True,
            ),
        )

        for target, field, invalid in samples:
            with self.subTest(field=field):
                original = getattr(
                    target,
                    field,
                )

                setattr(
                    target,
                    field,
                    invalid,
                )

                try:
                    with self.assertRaises(ValueError):
                        self.capture()

                finally:
                    setattr(
                        target,
                        field,
                        original,
                    )

    def test_foreign_universe_incident_or_operation_rejected(self):
        with redirect_stdout(io.StringIO()):
            foreign = Universe(
                universe_id="a44_foreign_checkpoint"
            )

        with self.assertRaises(ValueError):
            self.Checkpoint.capture(
                universe=foreign,
                incident_id=INCIDENT,
                source_operation=OPERATION,
            )

        with self.assertRaises(ValueError):
            self.Checkpoint.capture(
                universe=self.world,
                incident_id="incident-foreign-checkpoint",
                source_operation=OPERATION,
            )

        with self.assertRaises(ValueError):
            self.Checkpoint.capture(
                universe=self.world,
                incident_id=INCIDENT,
                source_operation="receipt_signature",
            )

    def test_empty_universe_never_restored_or_republished(self):
        checkpoint = self.capture()

        with redirect_stdout(io.StringIO()):
            empty = Universe(
                universe_id=WORLD
            )

        self.assertEqual(
            len(empty.entities),
            0,
        )

        self.assertEqual(
            len(empty.cronenbergs),
            0,
        )

        self.assertEqual(
            len(empty.quantum_events),
            0,
        )

        with self.assertRaises(ValueError):
            checkpoint.verify_live(
                empty
            )

        self.assertFalse(
            checkpoint.is_authoritative
        )

        self.assertFalse(
            checkpoint.is_restorable
        )

        self.assertFalse(
            checkpoint.can_republish
        )

        for method in (
            "restore",
            "republish",
            "authorize",
        ):
            self.assertFalse(
                hasattr(checkpoint, method)
            )

        self.assertEqual(
            len(empty.entities),
            0,
        )

        self.assertEqual(
            len(empty.cronenbergs),
            0,
        )

        self.assertEqual(
            len(empty.quantum_events),
            0,
        )


if __name__ == "__main__":
    unittest.main()
