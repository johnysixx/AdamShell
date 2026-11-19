"""A44 adversarial signed checkpoint trust-witness tests.

This suite verifies cryptographic and schema boundaries.

Important intentional limitations:
- A caller-selected root key can validate attacker data.
- Repeating the SAME challenge remains possible.
- A supplied witness revision floor is not durable state.
- A verified Python result is not an authorization token.

No external trust root, protected monotonic floor,
checkpoint restoration or republication is implemented.
"""

import json
import sys
import unittest

from dataclasses import FrozenInstanceError
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_signed_witness as contract

from core.existence.history_receipt_trust_checkpoint_signed_witness import (
    VerifiedCheckpointTrustWitness,
)


class A44CheckpointSignedWitnessAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointSignedWitnessContractTests(
                "test_valid_signed_witness_data_only"
            )
        )
        self.fixture.setUp()

    def reject_signed_document(self, document):
        message, signature = self.fixture.signed(document)

        with self.assertRaises(ValueError):
            self.fixture.verify(
                message=message,
                signature=signature,
            )

    def test_signed_payload_bitflip_rejected(self):
        message, signature = self.fixture.signed()

        for field, replacement in (
            ("root_id", "foreign_root"),
            ("authority_id", "foreign_authority"),
            ("universe_id", "foreign_universe"),
            ("minimum_generation", 8),
            ("witness_revision", 14),
            ("checkpoint_public_key_hex", "0" * 64),
            ("challenge_hex", "f" * 64),
        ):
            with self.subTest(field=field):
                document = self.fixture.document()
                document[field] = replacement

                changed_message = contract.canonical(
                    document
                )

                self.assertNotEqual(
                    changed_message,
                    message,
                )

                # Reuse the original valid signature.
                with self.assertRaises(ValueError):
                    self.fixture.verify(
                        message=changed_message,
                        signature=signature,
                    )

    def test_resigned_foreign_identity_rejected(self):
        for changes in (
            {"root_id": "foreign_root"},
            {"authority_id": "foreign_authority"},
            {"universe_id": "foreign_universe"},
            {"domain": "foreign-domain"},
            {"version": 2},
        ):
            with self.subTest(changes=changes):
                self.reject_signed_document(
                    self.fixture.document(**changes)
                )

    def test_untrusted_signer_and_root_confusion(self):
        attacker = Ed25519PrivateKey.generate()

        message, _ = self.fixture.signed()

        attacker_signature = attacker.sign(message)

        with self.assertRaises(ValueError):
            self.fixture.verify(
                message=message,
                signature=attacker_signature,
            )

        with self.assertRaises(ValueError):
            self.fixture.verify(
                message=message,
                signature=self.fixture.root_private.sign(
                    message
                ),
                trusted_root_public_key=contract.public_bytes(
                    attacker
                ),
            )

        # Both key and signer are caller-selected.
        # Verification may succeed, but provenance is
        # explicitly NOT independently established.
        result = self.fixture.verify(
            message=message,
            signature=attacker_signature,
            trusted_root_public_key=contract.public_bytes(
                attacker
            ),
        )

        self.assertTrue(result.root_signature_verified)
        self.assertFalse(result.is_independently_trusted)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

    def test_malformed_root_key_inputs_rejected(self):
        for key in (
            None,
            b"",
            b"x" * 31,
            b"x" * 33,
            bytearray(self.fixture.root_public),
            "not-bytes",
            True,
        ):
            with self.subTest(type=type(key).__name__):
                with self.assertRaises(ValueError):
                    self.fixture.verify(
                        trusted_root_public_key=key
                    )

    def test_corrupted_signature_forms_rejected(self):
        message, signature = self.fixture.signed()

        corrupted = bytearray(signature)
        corrupted[-1] ^= 1

        for invalid in (
            bytes(corrupted),
            signature[:-1],
            signature + b"x",
            bytearray(signature),
            b"",
            None,
            "not-bytes",
        ):
            with self.subTest(type=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    self.fixture.verify(
                        message=message,
                        signature=invalid,
                    )

    def test_malformed_message_inputs_rejected(self):
        _, signature = self.fixture.signed()

        for invalid in (
            None,
            "",
            b"",
            b"{}",
            b"[" * 4097,
            b"\x80",
            bytearray(b"{}"),
            [],
        ):
            with self.subTest(type=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    self.fixture.verify(
                        message=invalid,
                        signature=signature,
                    )

    def test_noncanonical_duplicate_json_rejected(self):
        document = self.fixture.document()

        canonical = contract.canonical(document)

        pretty = json.dumps(
            document,
            sort_keys=True,
            indent=2,
            ensure_ascii=True,
        ).encode("ascii")

        unsorted = json.dumps(
            document,
            sort_keys=False,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("ascii")

        duplicate = canonical.replace(
            b'"version":1',
            b'"version":1,"version":1',
            1,
        )

        self.assertNotEqual(pretty, canonical)
        self.assertNotEqual(unsorted, canonical)
        self.assertNotEqual(duplicate, canonical)

        for message in (
            pretty,
            unsorted,
            duplicate,
            canonical + b"\n",
        ):
            with self.subTest(
                length=len(message)
            ):
                signature = (
                    self.fixture.root_private.sign(message)
                )

                with self.assertRaises(ValueError):
                    self.fixture.verify(
                        message=message,
                        signature=signature,
                    )

    def test_unexpected_signed_schema_rejected(self):
        variants = (
            {"unknown_field": "forbidden"},
            {"minimum_generation": None},
            {"minimum_generation": True},
            {"minimum_generation": -1},
            {"minimum_generation": "7"},
            {"root_id": True},
            {"authority_id": 7},
            {"universe_id": False},
            {"version": True},
            {"checkpoint_public_key_hex": None},
            {"challenge_hex": None},
        )

        for changes in variants:
            with self.subTest(changes=repr(changes)):
                self.reject_signed_document(
                    self.fixture.document(**changes)
                )

        missing = self.fixture.document()
        del missing["challenge_hex"]

        self.reject_signed_document(missing)

        # A signed nonfinite JSON constant must be rejected
        # rather than silently accepted by Python json.loads.
        original_message, _ = self.fixture.signed()

        nonfinite = original_message.replace(
            b'"witness_revision":13',
            b'"witness_revision":NaN',
            1,
        )

        self.assertNotEqual(
            original_message,
            nonfinite,
        )

        with self.assertRaises(ValueError):
            self.fixture.verify(
                message=nonfinite,
                signature=self.fixture.root_private.sign(
                    nonfinite
                ),
            )

    def test_revision_and_generation_boundaries(self):
        valid = self.fixture.verify(
            minimum_witness_revision=12
        )

        self.assertEqual(valid.witness_revision, 13)

        for floor in (
            13,
            14,
            -1,
            True,
            False,
            12.0,
            "12",
            None,
        ):
            with self.subTest(floor=repr(floor)):
                with self.assertRaises(ValueError):
                    self.fixture.verify(
                        minimum_witness_revision=floor
                    )

        for revision in (
            0,
            -1,
            12,
            True,
            "13",
            13.0,
        ):
            with self.subTest(revision=repr(revision)):
                self.reject_signed_document(
                    self.fixture.document(
                        witness_revision=revision
                    )
                )

        for generation in (
            -1,
            True,
            False,
            "7",
            7.0,
        ):
            with self.subTest(generation=repr(generation)):
                self.reject_signed_document(
                    self.fixture.document(
                        minimum_generation=generation
                    )
                )

    def test_checkpoint_public_key_encoding_rejected(self):
        for encoded in (
            "",
            "0" * 63,
            "0" * 65,
            "g" * 64,
            "A" * 64,
            " " + "0" * 63,
            None,
            True,
            bytearray(b"0" * 64).hex(),
        ):
            # The final variant deliberately has 128
            # hex characters after bytearray.hex().
            with self.subTest(encoded=repr(encoded)[:40]):
                self.reject_signed_document(
                    self.fixture.document(
                        checkpoint_public_key_hex=encoded
                    )
                )

    def test_challenge_scope_and_replay_limit(self):
        message, signature = self.fixture.signed()

        changed = bytearray(self.fixture.challenge)
        changed[0] ^= 1
        foreign_challenge = bytes(changed)

        self.assertNotEqual(
            foreign_challenge,
            self.fixture.challenge,
        )

        with self.assertRaises(ValueError):
            self.fixture.verify(
                message=message,
                signature=signature,
                expected_challenge=foreign_challenge,
            )

        self.reject_signed_document(
            self.fixture.document(
                challenge_hex=foreign_challenge.hex()
            )
        )

        # Same-challenge replay is deliberately allowed by
        # a stateless verifier. Do not claim single-use proof.
        first = self.fixture.verify(
            message=message,
            signature=signature,
        )

        second = self.fixture.verify(
            message=message,
            signature=signature,
        )

        self.assertTrue(first.root_signature_verified)
        self.assertTrue(second.root_signature_verified)
        self.assertEqual(
            first.witness_revision,
            second.witness_revision,
        )

        self.assertFalse(first.is_independently_trusted)
        self.assertFalse(second.is_independently_trusted)

    def test_constructible_result_is_not_authority(self):
        result = VerifiedCheckpointTrustWitness(
            root_id=contract.ROOT_ID,
            authority_id=contract.AUTHORITY_ID,
            universe_id=contract.UNIVERSE_ID,
            checkpoint_public_key=bytes(32),
            minimum_generation=999,
            witness_revision=999,
            challenge=bytes(32),
        )

        # Python dataclass construction is not cryptographic
        # proof. The result has no publication privileges.
        self.assertIs(result.root_signature_verified, True)
        self.assertIs(
            result.is_independently_trusted,
            False,
        )
        self.assertIs(result.is_authoritative, False)
        self.assertIs(result.is_restorable, False)
        self.assertIs(result.can_republish, False)

        with self.assertRaises(FrozenInstanceError):
            result.minimum_generation = 1

        self.assertFalse(
            hasattr(result, "restore")
        )
        self.assertFalse(
            hasattr(result, "republish")
        )
        self.assertFalse(
            hasattr(result, "authorize")
        )


if __name__ == "__main__":
    unittest.main()
