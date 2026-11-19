"""A44 adversarial single signed-witness held binding tests.

Tests snapshot validation, nested lease teardown, signed
data integrity and checkpoint verification fault handling.

Deliberate security limitations:
- Caller-controlled root keys do not establish provenance.
- Reusing the same challenge remains possible.
- Revision rollback remains possible in volatile sources.
- In-process malicious monkeypatching is not isolated.
- No Universe restoration or republication is authorized.
"""

import sys
import unittest

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_signed_binding as contract
import test_a44_checkpoint_source_binding as source_contract
import test_a44_checkpoint_signed_witness as witness_contract

from core.existence.history_receipt_trust_checkpoint_attestation import (
    PinnedCronenbergCheckpointAttestationVerifier,
)

from core.existence.history_receipt_trust_checkpoint_signed_witness import (
    VerifiedCheckpointTrustWitness,
)


ROOT = contract.ROOT
AUTHORITY = contract.AUTHORITY
WORLD = contract.WORLD
GENERATION = contract.GENERATION
REVISION = contract.REVISION


class A44CheckpointSignedBindingAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointSignedBindingContractTests(
                "test_valid_single_signed_witness_checkpoint_verification"
            )
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def make_source(self, *, root=None, witness=None):
        return self.fixture.make_source(
            root_source=root,
            signed_witness_source=witness,
        )

    def verify(self, *, root=None, witness=None, **changes):
        return self.fixture.verify(
            self.make_source(
                root=root,
                witness=witness,
            ),
            **changes,
        )

    def assert_released(self, root=None, witness=None):
        root = self.fixture.root_source if root is None else root
        witness = (
            self.fixture.witness_source
            if witness is None
            else witness
        )

        self.assertFalse(root.active)
        self.assertFalse(witness.active)

    def test_factory_requires_held_sources(self):
        for invalid in (
            None,
            object(),
            [],
            {},
        ):
            with self.subTest(provider=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    self.fixture.binding_type.from_sources(
                        root_source=invalid,
                        signed_witness_source=(
                            self.fixture.witness_source
                        ),
                        expected_root_id=ROOT,
                        expected_authority_id=AUTHORITY,
                        expected_universe_id=WORLD,
                        expected_challenge=(
                            self.fixture.witness.challenge
                        ),
                    )

                with self.assertRaises(ValueError):
                    self.fixture.binding_type.from_sources(
                        root_source=self.fixture.root_source,
                        signed_witness_source=invalid,
                        expected_root_id=ROOT,
                        expected_authority_id=AUTHORITY,
                        expected_universe_id=WORLD,
                        expected_challenge=(
                            self.fixture.witness.challenge
                        ),
                    )

    def test_root_snapshot_strict_type_and_identity(self):
        original = self.fixture.root_source.snapshot

        class TupleChild(tuple):
            pass

        invalid = (
            None,
            (),
            [],
            TupleChild(original),
            (ROOT,),
            (*original, "extra"),
            ("foreign_root", original[1], original[2]),
            (ROOT, bytearray(original[1]), original[2]),
            (ROOT, original[1][:-1], original[2]),
            (ROOT, original[1], True),
            (ROOT, original[1], -1),
            (ROOT, original[1], "12"),
        )

        for snapshot in invalid:
            with self.subTest(snapshot=repr(snapshot)[:70]):
                root = source_contract.HeldSource(snapshot)

                with self.assertRaises(ValueError):
                    self.verify(root=root)

                self.assert_released(root=root)

    def test_signed_snapshot_strict_types(self):
        message, signature = (
            self.fixture.witness_source.snapshot
        )

        class TupleChild(tuple):
            pass

        class BytesChild(bytes):
            pass

        invalid = (
            None,
            (),
            [],
            TupleChild((message, signature)),
            (message,),
            (message, signature, "extra"),
            (bytearray(message), signature),
            (BytesChild(message), signature),
            (message, bytearray(signature)),
            (message, BytesChild(signature)),
            (b"", signature),
            (message, b""),
            (message, signature[:-1]),
            (message + b"x" * 4096, signature),
        )

        for snapshot in invalid:
            with self.subTest(snapshot=repr(snapshot)[:55]):
                witness = source_contract.HeldSource(snapshot)

                with self.assertRaises(ValueError):
                    self.verify(witness=witness)

                self.assert_released(witness=witness)

    def test_provider_entry_failures_release_leases(self):
        root_snapshot = self.fixture.root_source.snapshot
        witness_snapshot = self.fixture.witness_source.snapshot

        failures = (
            (
                source_contract.HeldSource(
                    root_snapshot,
                    fail_enter=ValueError("root entry fault"),
                ),
                source_contract.HeldSource(witness_snapshot),
            ),
            (
                source_contract.HeldSource(root_snapshot),
                source_contract.HeldSource(
                    witness_snapshot,
                    fail_enter=OSError("witness entry fault"),
                ),
            ),
        )

        for root, witness in failures:
            with self.subTest(
                root_fault=repr(root.fail_enter),
                witness_fault=repr(witness.fail_enter),
            ):
                with self.assertRaises(ValueError):
                    self.verify(root=root, witness=witness)

                self.assert_released(root, witness)

    def test_provider_exit_failures_release_leases(self):
        root_snapshot = self.fixture.root_source.snapshot
        witness_snapshot = self.fixture.witness_source.snapshot

        failures = (
            (
                source_contract.HeldSource(
                    root_snapshot,
                    fail_exit=ValueError("root exit fault"),
                ),
                source_contract.HeldSource(witness_snapshot),
            ),
            (
                source_contract.HeldSource(root_snapshot),
                source_contract.HeldSource(
                    witness_snapshot,
                    fail_exit=OSError("witness exit fault"),
                ),
            ),
        )

        for root, witness in failures:
            with self.subTest(
                root_fault=repr(root.fail_exit),
                witness_fault=repr(witness.fail_exit),
            ):
                with self.assertRaises(ValueError):
                    self.verify(root=root, witness=witness)

                self.assert_released(root, witness)

    def test_masked_nested_exit_failure_is_not_success(self):
        root = source_contract.SuppressingSource(
            self.fixture.root_source.snapshot
        )

        witness = source_contract.HeldSource(
            self.fixture.witness_source.snapshot,
            fail_exit=ValueError(
                "Injected nested signed-witness teardown fault"
            ),
        )

        with self.assertRaises(ValueError):
            self.verify(root=root, witness=witness)

        self.assert_released(root, witness)

        self.assertIn("suppressed", root.events)
        self.assertIn("exit", witness.events)

    def test_suppressed_snapshot_errors_fail_closed(self):
        root = source_contract.SuppressingSource(
            (ROOT, b"invalid", REVISION - 1)
        )

        witness = source_contract.HeldSource(
            self.fixture.witness_source.snapshot
        )

        with self.assertRaises(ValueError):
            self.verify(root=root, witness=witness)

        self.assert_released(root, witness)
        self.assertIn("suppressed", root.events)

        root = source_contract.HeldSource(
            self.fixture.root_source.snapshot
        )

        witness = source_contract.SuppressingSource(
            (b"", b"invalid")
        )

        with self.assertRaises(ValueError):
            self.verify(root=root, witness=witness)

        self.assert_released(root, witness)
        self.assertIn("suppressed", witness.events)

    def test_tampered_signed_witness_and_mixed_pair_rejected(self):
        original_message, original_signature = (
            self.fixture.witness_source.snapshot
        )

        alternate_message, alternate_signature = (
            self.fixture.witness.signed(
                self.fixture.document(
                    minimum_generation=0
                )
            )
        )

        self.assertNotEqual(
            original_message,
            alternate_message,
        )

        corrupted_signature = bytearray(original_signature)
        corrupted_signature[0] ^= 1

        attacker = Ed25519PrivateKey.generate()

        foreign_message, foreign_signature = (
            self.fixture.witness.signed(
                self.fixture.document(),
                signer=attacker,
            )
        )

        stale_message, stale_signature = (
            self.fixture.witness.signed(
                self.fixture.document(
                    minimum_generation=GENERATION
                )
            )
        )

        invalid_pairs = (
            (alternate_message, original_signature),
            (original_message, alternate_signature),
            (original_message, bytes(corrupted_signature)),
            (foreign_message, foreign_signature),
            (stale_message, stale_signature),
        )

        for message, signature in invalid_pairs:
            with self.subTest(
                message_size=len(message),
                signature_prefix=signature[:4].hex(),
            ):
                witness = source_contract.HeldSource(
                    (message, signature)
                )

                with self.assertRaises(ValueError):
                    self.verify(witness=witness)

                self.assert_released(witness=witness)

    def test_checkpoint_signer_substitution_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        message, signature = (
            self.fixture.checkpoint.signed(
                key=attacker
            )
        )

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

        self.assert_released()

    def test_downstream_checkpoint_failure_releases_both(self):
        observations = []

        def injected_failure(verifier, **kwargs):
            observations.append((
                self.fixture.root_source.active,
                self.fixture.witness_source.active,
            ))

            raise RuntimeError(
                "Injected checkpoint signature verification fault"
            )

        with patch.object(
            PinnedCronenbergCheckpointAttestationVerifier,
            "verify",
            new=injected_failure,
        ):
            with self.assertRaises(ValueError):
                self.verify()

        self.assertEqual(
            observations,
            [(True, True)],
        )

        self.assert_released()

        self.assertEqual(
            self.fixture.root_source.events,
            ["enter", "exit"],
        )

        self.assertEqual(
            self.fixture.witness_source.events,
            ["enter", "exit"],
        )

    def test_forged_witness_verification_results_rejected(self):
        base = VerifiedCheckpointTrustWitness(
            root_id=ROOT,
            authority_id=AUTHORITY,
            universe_id=WORLD,
            checkpoint_public_key=(
                self.fixture.checkpoint.public
            ),
            minimum_generation=GENERATION - 1,
            witness_revision=REVISION,
            challenge=self.fixture.witness.challenge,
        )

        invalid = [
            None,
            object(),
            "forged",
        ]

        for attribute in (
            "root_signature_verified",
            "is_independently_trusted",
            "is_authoritative",
            "is_restorable",
            "can_republish",
        ):
            altered = replace(base)

            object.__setattr__(
                altered,
                attribute,
                (
                    False
                    if attribute == "root_signature_verified"
                    else True
                ),
            )

            invalid.append(altered)

        altered_key = replace(
            base,
            checkpoint_public_key=b"invalid",
        )
        invalid.append(altered_key)

        altered_revision = replace(
            base,
            witness_revision=REVISION - 1,
        )
        invalid.append(altered_revision)

        for forged_result in invalid:
            with self.subTest(
                result=repr(forged_result)[:75]
            ):
                with patch.object(
                    self.fixture.module,
                    "verify_signed_checkpoint_trust_witness",
                    return_value=forged_result,
                ):
                    with self.assertRaises(ValueError):
                        self.verify()

                self.assert_released()

    def test_replay_revision_rollback_and_selected_root_limits(self):
        first = self.verify()
        second = self.verify()

        self.assertTrue(first.signature_verified)
        self.assertTrue(second.signature_verified)
        self.assertEqual(
            first.generation,
            second.generation,
        )

        self.assertFalse(first.is_authoritative)
        self.assertFalse(second.is_restorable)
        self.assertFalse(second.can_republish)

        self.fixture.root_source.replace(
            (
                ROOT,
                self.fixture.witness.root_public,
                REVISION,
            )
        )

        with self.assertRaises(ValueError):
            self.verify()

        self.fixture.root_source.replace(
            (
                ROOT,
                self.fixture.witness.root_public,
                0,
            )
        )

        replay = self.verify()

        self.assertTrue(replay.signature_verified)
        self.assertFalse(replay.is_authoritative)

        attacker_root = Ed25519PrivateKey.generate()

        attacker_source = source_contract.HeldSource(
            (
                ROOT,
                witness_contract.public_bytes(
                    attacker_root
                ),
                REVISION - 1,
            )
        )

        attacker_witness = self.fixture.signed_source(
            signer=attacker_root
        )

        attacker_result = self.verify(
            root=attacker_source,
            witness=attacker_witness,
        )

        self.assertTrue(
            attacker_result.signature_verified
        )
        self.assertFalse(
            attacker_result.is_authoritative
        )
        self.assertFalse(
            attacker_result.is_restorable
        )
        self.assertFalse(
            attacker_result.can_republish
        )

        self.assert_released(
            attacker_source,
            attacker_witness,
        )


if __name__ == "__main__":
    unittest.main()
