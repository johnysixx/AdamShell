"""A44 / 66.34D: fail-closed deployment-floor client adversarial tests.

The signed deployment source is a local simulated fixture, NOT an independently
secured monotonic authority. These tests do not prove cross-store atomicity,
secure key provisioning, or protection against correlated rollback.
"""

import sys
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_witness_deployment_floor_contract as deployment_contract


class A44WitnessDeploymentFloorAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.fixture = deployment_contract.A44WitnessDeploymentFloorContractTests(
            "test_01_matching_signed_floor_and_dual_read"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def gate(self, **changes):
        return self.fixture.gate(**changes)

    def test_01_wrong_trusted_floor_identity_rejected(self):
        gate = self.gate(expected_floor_id="different-deployment-floor")
        with self.assertRaises(ValueError):
            gate.read_generation()
        self.assertFalse(self.fixture.floor.active)

    def test_02_wrong_subject_pin_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            self.gate(expected_subject_id="different-subject")
        self.assertEqual(self.fixture.floor.holds, 0)

    def test_03_attacker_key_pin_rejected_at_read(self):
        attacker_key = deployment_contract.key_bytes(Ed25519PrivateKey.generate())
        gate = self.gate(expected_floor_public_key=attacker_key)
        with self.assertRaises(ValueError):
            gate.read_generation()
        self.assertFalse(self.fixture.floor.active)

    def test_04_malformed_signed_response_pairs_rejected(self):
        cases = (
            (),
            [],
            (b"only-one",),
            (b"one", b"two", b"three"),
            (None, None),
            (123, b"x" * 64),
            (b"x", b"y" * 63),
            (b"x" * 4097, b"y" * 64),
        )
        for case in cases:
            with self.subTest(case=str(type(case)), size=len(case)):
                self.fixture.floor.response = case
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
                self.assertFalse(self.fixture.floor.active)
        self.fixture.floor.response = None

    def test_05_validly_signed_domain_version_operation_substitution(self):
        for change in (
            {"domain": "AdamShell/A44/other/v1"},
            {"version": 2},
            {"version": True},
            {"operation": "cas"},
            {"operation": "lookup"},
        ):
            with self.subTest(change=change):
                self.fixture.floor.rewrite = (
                    lambda doc, change=change: {**doc, **change}
                )
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
        self.fixture.floor.rewrite = None

    def test_06_bad_authority_witness_and_challenge_hex(self):
        for field, value in (
            ("authority_public_key_hex", "A" * 64),
            ("authority_public_key_hex", "g" * 64),
            ("authority_public_key_hex", "0" * 63),
            ("authority_public_key_hex", None),
            ("witness_public_key_hex", "F" * 64),
            ("witness_public_key_hex", "0" * 65),
            ("challenge_hex", "0" * 64),
            ("challenge_hex", "x" * 64),
            ("challenge_hex", "a" * 63),
        ):
            with self.subTest(field=field, value=repr(value)[:16]):
                self.fixture.floor.rewrite = (
                    lambda doc, field=field, value=value: {**doc, field: value}
                )
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
        self.fixture.floor.rewrite = None

    def test_07_invalid_signed_epoch_types_and_bounds(self):
        for epoch in (True, False, -1, 1 << 100, 1.5, "1", None, 0):
            with self.subTest(epoch=epoch):
                self.fixture.floor.rewrite = (
                    lambda doc, epoch=epoch: {**doc, "epoch": epoch}
                )
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
        self.fixture.floor.rewrite = None

    def test_08_signed_epoch_behind_retained_minimum_rejected(self):
        gate = self.gate(minimum_epoch=3)
        self.fixture.floor.epoch = 2
        with self.assertRaises(ValueError):
            gate.read_generation()
        self.fixture.floor.epoch = 3
        self.assertEqual(gate.read_generation(), 1)

    def test_09_noncanonical_duplicate_extra_fields_rejected(self):
        for encoder in (
            lambda doc: deployment_contract.canonical(doc) + b" ",
            lambda doc: deployment_contract.canonical(doc).replace(
                b'"version":1', b'"version":1,"version":1'
            ),
        ):
            with self.subTest(encoder=repr(encoder)):
                self.fixture.floor.encoder = encoder
                with self.assertRaises(ValueError):
                    self.gate().read_generation()
        self.fixture.floor.encoder = deployment_contract.canonical
        self.fixture.floor.rewrite = lambda doc: {**doc, "unrecognized": 7}
        with self.assertRaises(ValueError):
            self.gate().read_generation()

    def test_10_invalid_floor_does_not_invoke_dual_read(self):
        self.fixture.floor.response_signer = Ed25519PrivateKey.generate()
        guard_type = type(self.fixture.guard)
        with patch.object(
            guard_type, "read_generation",
            side_effect=AssertionError("dual-read must not run"),
        ) as mocked:
            with self.assertRaises(ValueError):
                self.gate().read_generation()
            mocked.assert_not_called()
        self.assertFalse(self.fixture.floor.active)

    def test_11_invalid_floor_does_not_invoke_enrollment_binding(self):
        self.fixture.floor.fail = True
        guard_type = type(self.fixture.guard)
        with patch.object(
            guard_type, "bind_provisioning",
            side_effect=AssertionError("enrollment must not run"),
        ) as mocked:
            with self.assertRaises(ValueError):
                self.gate().bind_provisioning(
                    source=object(), manifest=b"invalid", signature=b"invalid"
                )
            mocked.assert_not_called()
        self.assertFalse(self.fixture.floor.active)

    def test_12_dual_read_failure_unwinds_floor_hold(self):
        guard_type = type(self.fixture.guard)
        with patch.object(
            guard_type, "read_generation",
            side_effect=TimeoutError("simulated inner authority failure"),
        ) as mocked:
            with self.assertRaises(ValueError):
                self.gate().read_generation()
            mocked.assert_called_once()
        self.assertEqual(self.fixture.floor.holds, 1)
        self.assertFalse(self.fixture.floor.active)

    def test_13_floor_hold_exit_failure_is_fail_closed(self):
        original = self.fixture.floor

        class FailOnExit:
            @contextmanager
            def hold(self, *, challenge):
                with original.hold(challenge=challenge) as response:
                    yield response
                raise RuntimeError("floor hold exit failed")

        with self.assertRaises(ValueError):
            self.gate(floor_source=FailOnExit()).read_generation()
        self.assertFalse(original.active)

    def test_14_missing_context_manager_fails_closed(self):
        class InvalidHold:
            def hold(self, *, challenge):
                return (b"payload", b"signature")

        guard_type = type(self.fixture.guard)
        with patch.object(guard_type, "read_generation") as mocked:
            with self.assertRaises(ValueError):
                self.gate(floor_source=InvalidHold()).read_generation()
            mocked.assert_not_called()

    def test_15_repeated_calls_use_distinct_32_byte_floor_challenges(self):
        original = self.fixture.floor

        class RecordingFloor:
            def __init__(self):
                self.challenges = []

            @contextmanager
            def hold(self, *, challenge):
                self.challenges.append(challenge)
                with original.hold(challenge=challenge) as response:
                    yield response

        provider = RecordingFloor()
        gate = self.gate(floor_source=provider)
        self.assertEqual(gate.read_generation(), 1)
        self.assertEqual(gate.read_generation(), 1)
        self.assertEqual(len(provider.challenges), 2)
        self.assertTrue(all(type(x) is bytes and len(x) == 32 for x in provider.challenges))
        self.assertNotEqual(provider.challenges[0], provider.challenges[1])

    def test_16_mutated_frozen_gate_revalidated_before_hold(self):
        for field, value in (
            ("minimum_epoch", -1),
            ("expected_floor_public_key", b"x" * 31),
            ("expected_floor_id", ""),
            ("expected_subject_id", "another-subject"),
        ):
            with self.subTest(field=field):
                gate = self.gate()
                object.__setattr__(gate, field, value)
                with self.assertRaises(ValueError):
                    gate.read_generation()
        self.assertEqual(self.fixture.floor.holds, 0)

    def test_17_enrollment_binding_occurs_inside_floor_hold(self):
        enrollment = self.fixture.fixture.provisioning()
        guard_type = type(self.fixture.guard)
        original = guard_type.bind_provisioning
        floor = self.fixture.floor

        def guarded_bind(instance, *, source, manifest, signature):
            if not floor.active:
                raise AssertionError("deployment floor hold not active")
            return original(instance, source=source, manifest=manifest, signature=signature)

        with patch.object(guard_type, "bind_provisioning", guarded_bind):
            binding = self.gate().bind_provisioning(
                source=enrollment.fixture.source,
                manifest=enrollment.fixture.manifest,
                signature=enrollment.fixture.signature,
            )
        self.assertEqual(binding.pins.provisioning_generation, 1)
        self.assertFalse(floor.active)

    def test_18_read_and_bind_are_nonmutating(self):
        before = self.fixture.fixture.fixture.operation_count()
        enrollment = self.fixture.fixture.provisioning()
        self.assertEqual(self.gate().read_generation(), 1)
        binding = self.gate().bind_provisioning(
            source=enrollment.fixture.source,
            manifest=enrollment.fixture.manifest,
            signature=enrollment.fixture.signature,
        )
        self.assertEqual(binding.pins.provisioning_generation, 1)
        self.assertEqual(self.fixture.fixture.fixture.operation_count(), before)


if __name__ == "__main__":
    unittest.main()
