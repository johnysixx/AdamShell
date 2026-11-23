"""A44 / 66.33D: fail-closed, read-only witness boundary regressions.

The witness is an IN-MEMORY test double, not an independent trust root.
These tests do not prove durable monotonic storage or cross-store atomicity.
"""

import sys
import unittest

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_checkpoint_protected_provisioning_floor_witness_contract as witness_contract


class A44ProvisioningGenerationWitnessAdversarialTests(unittest.TestCase):

    def setUp(self):
        self.fixture = (
            witness_contract
            .A44ProvisioningGenerationWitnessContractTests(
                "test_01_matching_signed_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def guard(self, **overrides):
        return self.fixture.guard(**overrides)

    def test_01_distinct_signers_different_subject_pin_rejected(self):
        wrong_client = self.fixture.fixture.client(
            expected_subject_id="other-subject"
        )

        with self.assertRaises(ValueError):
            self.guard(client=wrong_client)

        self.assertEqual(self.fixture.witness.holds, 0)

    def test_02_wrong_trusted_witness_identity_rejected_at_read(self):
        guard = self.guard(
            expected_witness_id="unrelated-witness"
        )

        with self.assertRaises(ValueError):
            guard.read_generation()

        self.assertFalse(self.fixture.witness.active)

    def test_03_wrong_32_byte_witness_key_rejected_at_read(self):
        other_key = witness_contract.public_key(
            Ed25519PrivateKey.generate()
        )

        guard = self.guard(
            expected_witness_public_key=other_key
        )

        with self.assertRaises(ValueError):
            guard.read_generation()

        self.assertFalse(self.fixture.witness.active)

    def test_04_malformed_response_containers_fail_closed(self):
        for response in (
            [],
            [b"payload", b"signature"],
            (b"x",),
            (b"x", b"y", b"z"),
            (None, None),
            (123, b"x" * 64),
            (b"x" * 4097, b"y" * 64),
        ):
            with self.subTest(
                type=type(response).__name__,
                size=repr(response)[:45],
            ):
                self.fixture.witness.response = response

                with self.assertRaises(ValueError):
                    self.guard().read_generation()

                self.assertFalse(self.fixture.witness.active)

        self.fixture.witness.response = None

    def test_05_validly_signed_wrong_domain_operation_version_rejected(self):
        changes = (
            {"domain": "AdamShell/A44/other/v1"},
            {"version": 2},
            {"version": True},
            {"operation": "cas"},
            {"operation": "lookup"},
        )

        for change in changes:
            with self.subTest(change=change):
                self.fixture.witness.rewrite = (
                    lambda document, change=change: {
                        **document,
                        **change,
                    }
                )

                with self.assertRaises(ValueError):
                    self.guard().read_generation()

        self.fixture.witness.rewrite = None

    def test_06_validly_signed_invalid_generation_types_rejected(self):
        for value in (
            True,
            False,
            -1,
            1 << 100,
            1.0,
            "1",
            None,
        ):
            with self.subTest(value=value):
                self.fixture.witness.rewrite = (
                    lambda document, generation=value: {
                        **document,
                        "generation": generation,
                    }
                )

                with self.assertRaises(ValueError):
                    self.guard().read_generation()

        self.fixture.witness.rewrite = None

    def test_07_correctly_signed_bad_challenge_encoding_rejected(self):
        self.fixture.witness.rewrite = (
            lambda document: {
                **document,
                "challenge_hex": "f" * 64,
            }
        )

        with self.assertRaises(ValueError):
            self.guard().read_generation()

        self.fixture.witness.rewrite = None

    def test_08_witness_failure_does_not_call_local_read(self):
        self.fixture.witness.fail = True

        client_type = type(self.fixture.fixture.client())

        with patch.object(
            client_type,
            "read_generation",
            side_effect=AssertionError(
                "Local read must not execute after witness failure"
            ),
        ) as local_read:

            with self.assertRaises(ValueError):
                self.guard().read_generation()

            local_read.assert_not_called()

        self.assertFalse(self.fixture.witness.active)

    def test_09_witness_failure_does_not_bind_provisioning(self):
        self.fixture.witness.fail = True

        client_type = type(self.fixture.fixture.client())

        with patch.object(
            client_type,
            "bind_provisioning",
            side_effect=AssertionError(
                "No enrollment binding after witness failure"
            ),
        ) as bind:

            with self.assertRaises(ValueError):
                self.guard().bind_provisioning(
                    source=object(),
                    manifest=b"invalid",
                    signature=b"invalid",
                )

            bind.assert_not_called()

        self.assertFalse(self.fixture.witness.active)

    def test_10_local_read_failure_does_not_escape_witness_hold(self):
        backend = self.fixture.fixture.reopened()

        class BrokenRead:

            @contextmanager
            def hold(self, *, challenge):
                raise TimeoutError("Local authority down")
                yield None

            advance_if_current = backend.advance_if_current
            lookup_operation = backend.lookup_operation

        client = self.fixture.fixture.client(
            backend=BrokenRead()
        )

        with self.assertRaises(ValueError):
            self.guard(client=client).read_generation()

        self.assertFalse(self.fixture.witness.active)
        self.assertEqual(self.fixture.witness.holds, 1)

    def test_11_witness_hold_exit_failure_fails_closed(self):
        original = self.fixture.witness

        class BadExit:

            @contextmanager
            def hold(self, *, challenge):
                with original.hold(
                    challenge=challenge
                ) as response:
                    yield response

                raise RuntimeError("Witness exit failed")

        with self.assertRaises(ValueError):
            self.guard(
                witness=BadExit()
            ).read_generation()

        self.assertFalse(original.active)

    def test_12_successful_signed_reads_never_publish_operations(self):
        backend_fixture = self.fixture.fixture

        before = backend_fixture.operation_count()

        self.assertEqual(before, 0)

        for _ in range(3):
            self.assertEqual(
                self.guard().read_generation(),
                1,
            )

        self.assertEqual(
            backend_fixture.operation_count(),
            before,
        )

        self.assertEqual(
            self.fixture.witness.holds,
            3,
        )

    def test_13_repeated_reads_use_distinct_witness_challenges(self):
        original = self.fixture.witness

        class RecordingWitness:

            def __init__(self):
                self.challenges = []

            @contextmanager
            def hold(self, *, challenge):
                self.challenges.append(challenge)

                with original.hold(
                    challenge=challenge
                ) as response:
                    yield response

        recorded = RecordingWitness()

        guard = self.guard(
            witness=recorded
        )

        self.assertEqual(guard.read_generation(), 1)
        self.assertEqual(guard.read_generation(), 1)

        self.assertEqual(len(recorded.challenges), 2)

        self.assertEqual(
            {len(c) for c in recorded.challenges},
            {32},
        )

        self.assertNotEqual(*recorded.challenges)

    def test_14_mutated_frozen_minimum_fails_runtime_revalidation(self):
        guard = self.guard()

        object.__setattr__(
            guard,
            "minimum_generation",
            -1,
        )

        with self.assertRaises(ValueError):
            guard.read_generation()

        self.assertEqual(self.fixture.witness.holds, 0)

    def test_15_mutated_frozen_signer_pin_fails_runtime_revalidation(self):
        guard = self.guard()

        object.__setattr__(
            guard,
            "expected_witness_public_key",
            b"x" * 31,
        )

        with self.assertRaises(ValueError):
            guard.read_generation()

        self.assertEqual(self.fixture.witness.holds, 0)

    def test_16_independent_witness_higher_minimum_cannot_be_downgraded(self):
        self.fixture.advance_both()

        guard = self.guard(
            minimum_generation=2
        )

        self.assertEqual(
            guard.read_generation(),
            2,
        )

        self.fixture.witness.generation = 1

        with self.assertRaises(ValueError):
            guard.read_generation()

        self.assertFalse(self.fixture.witness.active)


if __name__ == "__main__":
    unittest.main()
