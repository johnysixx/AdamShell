"""A44 / 66.34B RED contract: independently pinned deployment-generation floor.

Target module:
core.existence.history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor
Target class: PinnedSignedWitnessDeploymentFloor

from_sources(*, guard, floor_source, expected_floor_id,
             expected_floor_public_key, expected_subject_id, minimum_epoch)
read_generation() -> int
bind_provisioning(*, source, manifest, signature) -> PinnedHighWaterProvisioning

The floor source supplies a fresh, canonical, Ed25519-signed READ reply:
domain, version, operation, floor_id, subject_id,
authority_id, authority_public_key_hex, witness_id,
witness_public_key_hex, minimum_generation, epoch, challenge_hex.
It is held while verifying the dual-signed authority/witness read or binding.

This is an IN-MEMORY TEST DOUBLE. Neither different public keys nor an
injected provider prove a protected monotonic root, independently stored keys,
secure installation/rotation of pins, remote linearizability, or cross-store
atomicity. If all three states and caller minima roll back, this gate cannot
recognize it. No CAS or autonomous reconciliation is allowed at this layer.
"""

import importlib
import json
import shutil
import sys
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_checkpoint_protected_provisioning_floor_witness_contract as witness_contract

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor"
)
CLASS = "PinnedSignedWitnessDeploymentFloor"
DOMAIN = "AdamShell/A44/witness-deployment-floor/v1"
FLOOR_ID = "a44-external-deployment-floor"
SUBJECT_ID = witness_contract.SUBJECT_ID


def canonical(doc):
    return json.dumps(
        doc, sort_keys=True, ensure_ascii=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("ascii")


def key_bytes(signer):
    return signer.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class SimulatedSignedDeploymentFloor:
    """Local mock only; NOT a rollback-proof or external authority."""

    def __init__(self, signer, guard):
        self.signer = signer
        self.response_signer = signer
        self.guard = guard
        self.minimum_generation = 1
        self.epoch = 1
        self.lock = threading.RLock()
        self.active = False
        self.holds = 0
        self.fail = False
        self.replay = None
        self.response = None
        self.rewrite = None
        self.encoder = canonical

    def signed(self, challenge):
        doc = dict(
            domain=DOMAIN, version=1, operation="read",
            floor_id=FLOOR_ID, subject_id=SUBJECT_ID,
            authority_id=self.guard.client.expected_authority_id,
            authority_public_key_hex=(
                self.guard.client.expected_authority_public_key.hex()
            ),
            witness_id=self.guard.expected_witness_id,
            witness_public_key_hex=self.guard.expected_witness_public_key.hex(),
            minimum_generation=self.minimum_generation,
            epoch=self.epoch,
            challenge_hex=challenge.hex(),
        )
        if self.rewrite is not None:
            doc = self.rewrite(doc)
        message = self.encoder(doc)
        return message, self.response_signer.sign(message)

    @contextmanager
    def hold(self, *, challenge):
        with self.lock:
            self.holds += 1
            self.active = True
            try:
                if self.fail:
                    raise TimeoutError("External floor unavailable")
                yield (
                    self.response if self.response is not None
                    else self.replay if self.replay is not None
                    else self.signed(challenge)
                )
            finally:
                self.active = False


class A44WitnessDeploymentFloorContractTests(unittest.TestCase):
    def setUp(self):
        module = importlib.import_module(MODULE)
        self.target_type = getattr(module, CLASS)
        self.fixture = witness_contract.A44ProvisioningGenerationWitnessContractTests(
            "test_01_matching_signed_read"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.guard = self.fixture.guard()
        self.signer = Ed25519PrivateKey.generate()
        self.floor = SimulatedSignedDeploymentFloor(self.signer, self.guard)

    def gate(self, **changes):
        args = dict(
            guard=self.guard,
            floor_source=self.floor,
            expected_floor_id=FLOOR_ID,
            expected_floor_public_key=key_bytes(self.signer),
            expected_subject_id=SUBJECT_ID,
            minimum_epoch=1,
        )
        args.update(changes)
        return self.target_type.from_sources(**args)

    def advance_both(self):
        self.fixture.advance_both()

    def test_01_matching_signed_floor_and_dual_read(self):
        self.assertEqual(self.gate().read_generation(), 1)
        self.assertEqual(self.floor.holds, 1)

    def test_02_matching_signed_floor_and_enrollment(self):
        source = self.fixture.provisioning()
        bound = self.gate().bind_provisioning(
            source=source.fixture.source,
            manifest=source.fixture.manifest,
            signature=source.fixture.signature,
        )
        self.assertEqual(bound.pins.provisioning_generation, 1)
        self.assertFalse(self.floor.active)

    def test_03_correlated_two_store_rollback_detected_by_retained_external_floor(self):
        saved = Path(self.fixture.fixture.temp.name) / "old-before-two-store-rollback.sqlite3"
        shutil.copy2(self.fixture.fixture.path, saved)
        self.advance_both()
        self.floor.minimum_generation = 2
        self.assertEqual(self.gate().read_generation(), 2)
        shutil.copy2(saved, self.fixture.fixture.path)
        self.fixture.witness.generation = 1
        with self.assertRaises(ValueError):
            self.gate().read_generation()

    def test_04_floor_behind_dual_generation_is_allowed(self):
        self.advance_both()
        self.assertEqual(self.floor.minimum_generation, 1)
        self.assertEqual(self.gate().read_generation(), 2)

    def test_05_floor_ahead_of_dual_generation_is_rejected(self):
        self.floor.minimum_generation = 2
        with self.assertRaises(ValueError):
            self.gate().read_generation()

    def test_06_wrong_signed_floor_signer_rejected(self):
        self.floor.response_signer = Ed25519PrivateKey.generate()
        with self.assertRaises(ValueError):
            self.gate().read_generation()

    def test_07_signed_floor_identity_and_subject_substitution_rejected(self):
        for change in ({"floor_id": "impostor"}, {"subject_id": "other"}):
            with self.subTest(change=change):
                self.floor.rewrite = lambda doc, change=change: {**doc, **change}
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
        self.floor.rewrite = None

    def test_08_signed_floor_authority_and_witness_pin_substitution_rejected(self):
        changes = (
            {"authority_id": "other"},
            {"authority_public_key_hex": "0" * 64},
            {"witness_id": "other"},
            {"witness_public_key_hex": "0" * 64},
        )
        for change in changes:
            with self.subTest(change=change):
                self.floor.rewrite = lambda doc, change=change: {**doc, **change}
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
        self.floor.rewrite = None

    def test_09_replayed_signed_floor_challenge_rejected(self):
        self.floor.replay = self.floor.signed(b"x" * 32)
        with self.assertRaises(ValueError):
            self.gate().read_generation()

    def test_10_noncanonical_extra_or_duplicate_floor_fields_rejected(self):
        encoders = (
            lambda doc: canonical(doc) + b" ",
            lambda doc: canonical(doc).replace(
                b'"version":1', b'"version":1,"version":1'
            ),
        )
        for encoder in encoders:
            with self.subTest(encoder=repr(encoder)):
                self.floor.encoder = encoder
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
        self.floor.encoder = canonical
        self.floor.rewrite = lambda doc: {**doc, "unknown_field": "x"}
        with self.assertRaises(ValueError):
            self.gate().read_generation()

    def test_11_invalid_counters_rejected(self):
        for value in (True, False, -1, 1 << 100, "2", None):
            with self.subTest(value=value):
                self.floor.rewrite = lambda doc, value=value: {
                    **doc, "minimum_generation": value,
                }
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
        self.floor.rewrite = None
        self.floor.epoch = 0
        with self.assertRaises(ValueError):
            self.gate().read_generation()
        for value in (True, -1, 1 << 100, "1"):
            with self.subTest(epoch=value):
                with self.assertRaises(ValueError):
                    self.gate(minimum_epoch=value)

    def test_12_invalid_source_public_key_and_missing_guard_rejected(self):
        for key in (None, b"x" * 31, b"x" * 33, bytearray(b"x" * 32)):
            with self.subTest(key=repr(key)):
                with self.assertRaises(ValueError):
                    self.gate(expected_floor_public_key=key)
        with self.assertRaises(ValueError):
            self.gate(floor_source=object())
        with self.assertRaises(ValueError):
            self.gate(guard=object())

    def test_13_signed_floor_outage_fails_before_dual_read(self):
        self.floor.fail = True
        guard_type = type(self.guard)
        with patch.object(guard_type, "read_generation", side_effect=AssertionError("dual-read invoked")) as read:
            with self.assertRaises(ValueError):
                self.gate().read_generation()
            read.assert_not_called()
        self.assertFalse(self.floor.active)

    def test_14_floor_hold_surrounds_dual_read(self):
        guard_type = type(self.guard)
        original = guard_type.read_generation
        floor = self.floor

        def guarded_read(instance):
            if not floor.active:
                raise AssertionError("Deployment floor hold not active")
            return original(instance)

        with patch.object(guard_type, "read_generation", guarded_read):
            self.assertEqual(self.gate().read_generation(), 1)
        self.assertFalse(self.floor.active)

    def test_15_external_floor_signature_key_must_be_distinct(self):
        for signer in (self.fixture.fixture.signer, self.fixture.signer):
            with self.subTest(signer=repr(signer)):
                with self.assertRaises(ValueError):
                    self.gate(expected_floor_public_key=key_bytes(signer))

    def test_16_all_three_rollbacks_are_known_limit(self):
        saved = Path(self.fixture.fixture.temp.name) / "old-three-store-image.sqlite3"
        shutil.copy2(self.fixture.fixture.path, saved)
        self.advance_both()
        self.floor.minimum_generation = 2
        self.assertEqual(self.gate().read_generation(), 2)
        shutil.copy2(saved, self.fixture.fixture.path)
        self.fixture.witness.generation = 1
        self.floor.minimum_generation = 1
        self.assertEqual(self.gate().read_generation(), 1)
        # Deliberate known limit, not protection against physical rollback.

    def test_17_mutated_gate_minimum_epoch_must_fail_closed(self):
        gate = self.gate()
        object.__setattr__(gate, "minimum_epoch", -1)
        with self.assertRaises(ValueError):
            gate.read_generation()

    def test_18_read_only_does_not_publish_local_cas(self):
        before = self.fixture.fixture.operation_count()
        self.assertEqual(self.gate().read_generation(), 1)
        self.assertEqual(self.gate().read_generation(), 1)
        self.assertEqual(self.fixture.fixture.operation_count(), before)
        self.assertEqual(self.floor.holds, 2)


if __name__ == "__main__":
    unittest.main()
