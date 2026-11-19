"""A44 signed-witness checkpoint held binding contract.

EXPECTED RED: signed checkpoint binding module absent.

root_source.hold() yields:
    (root_id, root_public_key, minimum_witness_revision)

signed_witness_source.hold() yields:
    (signed_message_bytes, signature_bytes)

A single root-signed witness supplies BOTH the checkpoint
public key and exclusive generation floor.

Both external leases must remain active through witness
signature verification and checkpoint signature verification.

This is a consistency contract only, not an independent
root enrollment, rollback-resistant state store, or
authorization to restore or republish Universe objects.
"""

import importlib
import sys
import unittest

from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_held_trust as held_contract
import test_a44_checkpoint_source_binding as source_contract
import test_a44_checkpoint_signed_witness as witness_contract

from core.existence.history_receipt_trust_checkpoint_attestation import (
    PinnedCronenbergCheckpointAttestationVerifier,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_signed_binding"
)

ROOT = witness_contract.ROOT_ID
AUTHORITY = held_contract.AUTHORITY
WORLD = held_contract.WORLD

GENERATION = held_contract.GENERATION
REVISION = witness_contract.WITNESS_REVISION


class A44CheckpointSignedBindingContractTests(unittest.TestCase):

    def setUp(self):
        self.module = importlib.import_module(MODULE)

        self.binding_type = (
            self.module.SignedCheckpointWitnessHeldSource
        )

        self.checkpoint = (
            held_contract.A44CheckpointHeldTrustContractTests(
                "test_valid_held_snapshot_verifies_data_only"
            )
        )

        self.checkpoint.setUp()
        self.addCleanup(self.checkpoint.doCleanups)

        self.witness = (
            witness_contract.A44CheckpointSignedWitnessContractTests(
                "test_valid_signed_witness_data_only"
            )
        )

        self.witness.setUp()
        self.addCleanup(self.witness.doCleanups)

        self.root_source = source_contract.HeldSource(
            (
                ROOT,
                self.witness.root_public,
                REVISION - 1,
            )
        )

        message, signature = self.witness.signed(
            self.document()
        )

        self.witness_source = source_contract.HeldSource(
            (message, signature)
        )

    def document(self, **changes):
        values = self.witness.document(
            universe_id=WORLD,
            authority_id=AUTHORITY,
            checkpoint_public_key_hex=(
                self.checkpoint.public.hex()
            ),
            minimum_generation=GENERATION - 1,
        )

        values.update(changes)
        return values

    def signed_source(self, document=None, *, signer=None):
        message, signature = self.witness.signed(
            self.document() if document is None else document,
            signer=signer,
        )

        return source_contract.HeldSource(
            (message, signature)
        )

    def make_source(
        self,
        *,
        root_source=None,
        signed_witness_source=None,
        expected_challenge=None,
    ):
        return self.binding_type.from_sources(
            root_source=(
                self.root_source
                if root_source is None
                else root_source
            ),
            signed_witness_source=(
                self.witness_source
                if signed_witness_source is None
                else signed_witness_source
            ),
            expected_root_id=ROOT,
            expected_authority_id=AUTHORITY,
            expected_universe_id=WORLD,
            expected_challenge=(
                self.witness.challenge
                if expected_challenge is None
                else expected_challenge
            ),
        )

    def verify(self, source=None, **changes):
        return self.checkpoint.verify(
            self.make_source() if source is None else source,
            **changes,
        )

    def assert_released(self, root=None, witness=None):
        root = self.root_source if root is None else root
        witness = (
            self.witness_source
            if witness is None
            else witness
        )

        self.assertFalse(root.active)
        self.assertFalse(witness.active)

    def test_valid_single_signed_witness_checkpoint_verification(self):
        source = self.make_source()

        before = (
            len(self.checkpoint.world.entities),
            len(self.checkpoint.world.cronenbergs),
            len(self.checkpoint.world.quantum_events),
        )

        result = self.verify(source)

        self.assertTrue(result.signature_verified)
        self.assertEqual(result.authority_id, AUTHORITY)
        self.assertEqual(result.generation, GENERATION)

        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assertEqual(
            self.root_source.events,
            ["enter", "exit"],
        )

        self.assertEqual(
            self.witness_source.events,
            ["enter", "exit"],
        )

        self.assert_released()

        self.assertEqual(
            before,
            (
                len(self.checkpoint.world.entities),
                len(self.checkpoint.world.cronenbergs),
                len(self.checkpoint.world.quantum_events),
            ),
        )

    def test_both_leases_cover_witness_and_checkpoint_verification(self):
        original_witness_verify = (
            self.module.verify_signed_checkpoint_trust_witness
        )

        original_checkpoint_verify = (
            PinnedCronenbergCheckpointAttestationVerifier.verify
        )

        events = []

        def guarded_witness_verify(**kwargs):
            self.assertTrue(self.root_source.active)
            self.assertTrue(self.witness_source.active)
            events.append("witness")
            return original_witness_verify(**kwargs)

        def guarded_checkpoint_verify(verifier, **kwargs):
            self.assertTrue(self.root_source.active)
            self.assertTrue(self.witness_source.active)
            self.assertEqual(
                kwargs["minimum_generation"],
                GENERATION - 1,
            )
            events.append("checkpoint")

            return original_checkpoint_verify(
                verifier,
                **kwargs,
            )

        with patch.object(
            self.module,
            "verify_signed_checkpoint_trust_witness",
            new=guarded_witness_verify,
        ):
            with patch.object(
                PinnedCronenbergCheckpointAttestationVerifier,
                "verify",
                new=guarded_checkpoint_verify,
            ):
                result = self.verify()

        self.assertTrue(result.signature_verified)
        self.assertEqual(events, ["witness", "checkpoint"])
        self.assert_released()

    def test_witness_signature_tamper_rejected(self):
        message, signature = self.witness_source.snapshot

        changed = bytearray(message)
        changed[-2] ^= 1

        source_data = source_contract.HeldSource(
            (bytes(changed), signature)
        )

        with self.assertRaises(ValueError):
            self.verify(
                self.make_source(
                    signed_witness_source=source_data
                )
            )

        self.assertFalse(source_data.active)
        self.assertFalse(self.root_source.active)

    def test_root_public_key_or_id_mismatch_rejected(self):
        foreign_root_key = Ed25519PrivateKey.generate()

        malformed_roots = (
            (
                ROOT,
                witness_contract.public_bytes(
                    foreign_root_key
                ),
                REVISION - 1,
            ),
            (
                "foreign_root",
                self.witness.root_public,
                REVISION - 1,
            ),
        )

        for snapshot in malformed_roots:
            with self.subTest(snapshot=repr(snapshot)[:60]):
                root_source = source_contract.HeldSource(
                    snapshot
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        self.make_source(
                            root_source=root_source
                        )
                    )

                self.assertFalse(root_source.active)
                self.assertFalse(self.witness_source.active)

    def test_universe_authority_and_challenge_mismatch_rejected(self):
        wrong_challenge = bytes([
            self.witness.challenge[0] ^ 1
        ]) + self.witness.challenge[1:]

        invalid = (
            {"universe_id": "foreign_universe"},
            {"authority_id": "foreign_authority"},
            {"challenge_hex": wrong_challenge.hex()},
        )

        for changes in invalid:
            with self.subTest(changes=changes):
                source_data = self.signed_source(
                    self.document(**changes)
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        self.make_source(
                            signed_witness_source=source_data
                        )
                    )

                self.assertFalse(source_data.active)

        with self.assertRaises(ValueError):
            self.verify(
                self.make_source(
                    expected_challenge=wrong_challenge
                )
            )

    def test_stale_witness_revision_rejected(self):
        for floor in (
            REVISION,
            REVISION + 1,
        ):
            with self.subTest(floor=floor):
                root_source = source_contract.HeldSource(
                    (
                        ROOT,
                        self.witness.root_public,
                        floor,
                    )
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        self.make_source(
                            root_source=root_source
                        )
                    )

                self.assertFalse(root_source.active)

    def test_checkpoint_generation_floor_rejects_old_signature(self):
        source_data = self.signed_source(
            self.document(
                minimum_generation=GENERATION
            )
        )

        with self.assertRaises(ValueError):
            self.verify(
                self.make_source(
                    signed_witness_source=source_data
                )
            )

        self.assertFalse(source_data.active)

    def test_mixed_signed_message_and_signature_rejected(self):
        original_message, original_signature = (
            self.witness_source.snapshot
        )

        alternate_message, alternate_signature = (
            self.witness.signed(
                self.document(
                    minimum_generation=0
                )
            )
        )

        self.assertNotEqual(
            original_message,
            alternate_message,
        )

        for snapshot in (
            (
                alternate_message,
                original_signature,
            ),
            (
                original_message,
                alternate_signature,
            ),
        ):
            with self.subTest(
                message_size=len(snapshot[0])
            ):
                source_data = source_contract.HeldSource(
                    snapshot
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        self.make_source(
                            signed_witness_source=source_data
                        )
                    )

                self.assertFalse(source_data.active)

    def test_checkpoint_signer_substitution_rejected(self):
        alternative_signer = Ed25519PrivateKey.generate()

        source_data = self.signed_source(
            self.document(
                checkpoint_public_key_hex=(
                    witness_contract.public_bytes(
                        alternative_signer
                    ).hex()
                )
            )
        )

        with self.assertRaises(ValueError):
            self.verify(
                self.make_source(
                    signed_witness_source=source_data
                )
            )

        self.assertFalse(source_data.active)

    def test_malformed_provider_snapshots_fail_closed(self):
        valid_root = self.root_source.snapshot
        valid_witness = self.witness_source.snapshot

        invalid_roots = (
            None,
            (),
            [*valid_root],
            (ROOT,),
            (*valid_root, "extra"),
            (
                ROOT,
                bytearray(self.witness.root_public),
                REVISION - 1,
            ),
            (
                ROOT,
                self.witness.root_public,
                True,
            ),
            (
                ROOT,
                self.witness.root_public,
                -1,
            ),
        )

        for snapshot in invalid_roots:
            with self.subTest(root=repr(snapshot)[:55]):
                root_source = source_contract.HeldSource(
                    snapshot
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        self.make_source(
                            root_source=root_source
                        )
                    )

                self.assertFalse(root_source.active)

        invalid_witnesses = (
            None,
            (),
            [*valid_witness],
            (valid_witness[0],),
            (*valid_witness, "extra"),
            (
                bytearray(valid_witness[0]),
                valid_witness[1],
            ),
            (
                valid_witness[0],
                bytearray(valid_witness[1]),
            ),
        )

        for snapshot in invalid_witnesses:
            with self.subTest(witness=repr(snapshot)[:55]):
                source_data = source_contract.HeldSource(
                    snapshot
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        self.make_source(
                            signed_witness_source=source_data
                        )
                    )

                self.assertFalse(source_data.active)

    def test_enter_exit_and_suppressed_nested_exit_fail_closed(self):
        valid_root = self.root_source.snapshot
        valid_witness = self.witness_source.snapshot

        failures = (
            (
                source_contract.HeldSource(
                    valid_root,
                    fail_enter=ValueError("root enter"),
                ),
                source_contract.HeldSource(valid_witness),
            ),
            (
                source_contract.HeldSource(valid_root),
                source_contract.HeldSource(
                    valid_witness,
                    fail_enter=ValueError("witness enter"),
                ),
            ),
            (
                source_contract.HeldSource(
                    valid_root,
                    fail_exit=ValueError("root exit"),
                ),
                source_contract.HeldSource(valid_witness),
            ),
            (
                source_contract.HeldSource(valid_root),
                source_contract.HeldSource(
                    valid_witness,
                    fail_exit=ValueError("witness exit"),
                ),
            ),
            (
                source_contract.SuppressingSource(valid_root),
                source_contract.HeldSource(
                    valid_witness,
                    fail_exit=ValueError(
                        "masked nested witness exit"
                    ),
                ),
            ),
        )

        for root_source, witness_source in failures:
            with self.subTest(
                root_type=type(root_source).__name__,
                witness_type=type(witness_source).__name__,
                root_exit=repr(root_source.fail_exit),
                witness_exit=repr(witness_source.fail_exit),
            ):
                with self.assertRaises(ValueError):
                    self.verify(
                        self.make_source(
                            root_source=root_source,
                            signed_witness_source=witness_source,
                        )
                    )

                self.assertFalse(root_source.active)
                self.assertFalse(witness_source.active)

    def test_same_challenge_replay_and_external_root_limitations(self):
        first = self.verify()
        second = self.verify()

        self.assertTrue(first.signature_verified)
        self.assertTrue(second.signature_verified)
        self.assertEqual(first.generation, second.generation)

        # The caller-controlled revision floor can be
        # rolled back. This adapter is not a monotonic store.
        self.root_source.replace(
            (
                ROOT,
                self.witness.root_public,
                REVISION,
            )
        )

        with self.assertRaises(ValueError):
            self.verify()

        self.root_source.replace(
            (
                ROOT,
                self.witness.root_public,
                0,
            )
        )

        self.assertTrue(self.verify().signature_verified)

        # An attacker controlling both the root key and
        # witness signature can construct matching data.
        # A cryptographic match alone proves no enrollment.
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

        attacker_witness = self.signed_source(
            signer=attacker_root
        )

        result = self.verify(
            self.make_source(
                root_source=attacker_source,
                signed_witness_source=attacker_witness,
            )
        )

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)
        self.assertFalse(attacker_source.active)
        self.assertFalse(attacker_witness.active)


if __name__ == "__main__":
    unittest.main()
