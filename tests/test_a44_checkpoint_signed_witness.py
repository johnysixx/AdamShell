"""A44 signed checkpoint trust witness contract.

EXPECTED RED: signed witness verifier is absent.

A signed external witness binds:
- root identity
- checkpoint authority identity
- Universe identity
- checkpoint Ed25519 public key
- minimum accepted checkpoint generation
- monotonically intended witness revision
- caller-generated challenge

The signer is authenticated ONLY relative to the supplied
root public key. Supplying a key does not prove that the
root was independently enrolled.

Challenge verification prevents replay against a DIFFERENT
challenge, not repeated use of the SAME challenge.

An externally protected revision floor is still required
for real anti-rollback enforcement. No restore or
republication authority is granted.
"""

import importlib
import json
import os
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_signed_witness"
)

ROOT_ID = "checkpoint_trust_root_v1"
AUTHORITY_ID = "checkpoint_authority_v1"
UNIVERSE_ID = "a44_6612_checkpoint_witness"

DOMAIN = "AdamShell/A44/checkpoint-trust-witness/v1"

WITNESS_REVISION = 13
GENERATION_FLOOR = 7


def public_bytes(private_key):
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def canonical(document):
    return json.dumps(
        document,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


class A44CheckpointSignedWitnessContractTests(unittest.TestCase):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.verify_witness = (
            module.verify_signed_checkpoint_trust_witness
        )

        self.result_type = (
            module.VerifiedCheckpointTrustWitness
        )

        self.root_private = Ed25519PrivateKey.generate()
        self.root_public = public_bytes(self.root_private)

        self.checkpoint_private = Ed25519PrivateKey.generate()
        self.checkpoint_public = public_bytes(
            self.checkpoint_private
        )

        self.challenge = os.urandom(32)

    def document(self, **changes):
        payload = {
            "domain": DOMAIN,
            "version": 1,
            "root_id": ROOT_ID,
            "authority_id": AUTHORITY_ID,
            "universe_id": UNIVERSE_ID,
            "checkpoint_public_key_hex":
                self.checkpoint_public.hex(),
            "minimum_generation": GENERATION_FLOOR,
            "witness_revision": WITNESS_REVISION,
            "challenge_hex": self.challenge.hex(),
        }

        payload.update(changes)
        return payload

    def signed(self, document=None, *, signer=None):
        message = canonical(
            self.document() if document is None else document
        )

        private = (
            self.root_private if signer is None else signer
        )

        return message, private.sign(message)

    def verify(self, *, message=None, signature=None, **changes):
        if message is None and signature is None:
            message, signature = self.signed()

        arguments = {
            "message": message,
            "signature": signature,
            "trusted_root_id": ROOT_ID,
            "trusted_root_public_key": self.root_public,
            "expected_authority_id": AUTHORITY_ID,
            "expected_universe_id": UNIVERSE_ID,
            "expected_challenge": self.challenge,
            "minimum_witness_revision": WITNESS_REVISION - 1,
        }

        arguments.update(changes)

        return self.verify_witness(**arguments)

    def test_valid_signed_witness_data_only(self):
        result = self.verify()

        self.assertIs(type(result), self.result_type)

        self.assertEqual(result.root_id, ROOT_ID)
        self.assertEqual(result.authority_id, AUTHORITY_ID)
        self.assertEqual(result.universe_id, UNIVERSE_ID)

        self.assertEqual(
            result.checkpoint_public_key,
            self.checkpoint_public,
        )

        self.assertIs(
            type(result.checkpoint_public_key),
            bytes,
        )

        self.assertEqual(
            result.minimum_generation,
            GENERATION_FLOOR,
        )

        self.assertEqual(
            result.witness_revision,
            WITNESS_REVISION,
        )

        self.assertEqual(
            result.challenge,
            self.challenge,
        )

        self.assertIs(result.root_signature_verified, True)
        self.assertIs(result.is_independently_trusted, False)
        self.assertIs(result.is_authoritative, False)
        self.assertIs(result.is_restorable, False)
        self.assertIs(result.can_republish, False)

    def test_foreign_pinned_root_public_key_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.verify(
                trusted_root_public_key=public_bytes(attacker)
            )

    def test_untrusted_signer_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        message, signature = self.signed(
            signer=attacker
        )

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

    def test_malformed_signature_rejected(self):
        message, signature = self.signed()

        corrupted = bytearray(signature)
        corrupted[0] ^= 1

        for invalid in (
            bytes(corrupted),
            signature[:-1],
            bytearray(signature),
            b"",
            None,
        ):
            with self.subTest(type=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    self.verify(
                        message=message,
                        signature=invalid,
                    )

    def test_foreign_root_identity_rejected(self):
        message, signature = self.signed(
            self.document(root_id="foreign_root")
        )

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

    def test_foreign_checkpoint_authority_rejected(self):
        message, signature = self.signed(
            self.document(authority_id="foreign_authority")
        )

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

    def test_wrong_universe_scope_rejected(self):
        message, signature = self.signed(
            self.document(universe_id="foreign_universe")
        )

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

    def test_wrong_challenge_rejected(self):
        wrong_challenge = os.urandom(32)

        self.assertNotEqual(
            wrong_challenge,
            self.challenge,
        )

        with self.assertRaises(ValueError):
            self.verify(
                expected_challenge=wrong_challenge
            )

        message, signature = self.signed(
            self.document(
                challenge_hex=wrong_challenge.hex()
            )
        )

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

    def test_exclusive_witness_revision_floor(self):
        with self.assertRaises(ValueError):
            self.verify(
                minimum_witness_revision=WITNESS_REVISION
            )

        with self.assertRaises(ValueError):
            self.verify(
                minimum_witness_revision=WITNESS_REVISION + 1
            )

        result = self.verify(
            minimum_witness_revision=WITNESS_REVISION - 1
        )

        self.assertEqual(
            result.witness_revision,
            WITNESS_REVISION,
        )

    def test_malformed_external_trust_inputs_rejected(self):
        invalid_inputs = (
            {"trusted_root_id": ""},
            {"trusted_root_id": " foreign_root"},
            {"trusted_root_public_key": b""},
            {"trusted_root_public_key": bytearray(self.root_public)},
            {"expected_authority_id": ""},
            {"expected_universe_id": ""},
            {"expected_challenge": b""},
            {"expected_challenge": bytearray(self.challenge)},
            {"minimum_witness_revision": -1},
            {"minimum_witness_revision": True},
            {"minimum_witness_revision": 12.0},
        )

        for changes in invalid_inputs:
            with self.subTest(changes=repr(changes)[:80]):
                with self.assertRaises(ValueError):
                    self.verify(**changes)

    def test_malformed_signed_witness_schema_rejected(self):
        variants = (
            {"minimum_generation": -1},
            {"minimum_generation": True},
            {"minimum_generation": "7"},
            {"witness_revision": 0},
            {"witness_revision": True},
            {"checkpoint_public_key_hex": "00"},
            {"checkpoint_public_key_hex": "g" * 64},
            {"challenge_hex": "x" * 64},
            {"version": 2},
            {"domain": "wrong-domain"},
            {"unknown_field": "not-permitted"},
        )

        for changes in variants:
            with self.subTest(changes=changes):
                message, signature = self.signed(
                    self.document(**changes)
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        message=message,
                        signature=signature,
                    )

        document = self.document()
        del document["authority_id"]

        message, signature = self.signed(document)

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

    def test_noncanonical_duplicate_replay_and_root_limit(self):
        document = self.document()

        noncanonical = json.dumps(
            document,
            indent=2,
            ensure_ascii=True,
        ).encode("ascii")

        with self.assertRaises(ValueError):
            self.verify(
                message=noncanonical,
                signature=self.root_private.sign(noncanonical),
            )

        duplicate = canonical(document).replace(
            b'"version":1',
            b'"version":1,"version":1',
            1,
        )

        self.assertNotEqual(duplicate, canonical(document))

        with self.assertRaises(ValueError):
            self.verify(
                message=duplicate,
                signature=self.root_private.sign(duplicate),
            )

        message, signature = self.signed()

        first = self.verify(
            message=message,
            signature=signature,
        )

        # Reusing exactly the same challenge is not prevented
        # by this stateless signed-witness verifier.
        second = self.verify(
            message=message,
            signature=signature,
        )

        self.assertTrue(first.root_signature_verified)
        self.assertTrue(second.root_signature_verified)

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
                expected_challenge=os.urandom(32),
            )

        # An attacker choosing both the signing key and the
        # supposed root pin can still verify their own data.
        # The result must never claim independent trust.
        attacker = Ed25519PrivateKey.generate()

        attacker_message, attacker_signature = self.signed(
            signer=attacker
        )

        attacker_result = self.verify(
            message=attacker_message,
            signature=attacker_signature,
            trusted_root_public_key=public_bytes(attacker),
        )

        self.assertTrue(
            attacker_result.root_signature_verified
        )
        self.assertFalse(
            attacker_result.is_independently_trusted
        )
        self.assertFalse(attacker_result.is_authoritative)
        self.assertFalse(attacker_result.is_restorable)
        self.assertFalse(attacker_result.can_republish)


if __name__ == "__main__":
    unittest.main()
