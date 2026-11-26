"""Pinned protected root anchor enrollment contract.

Enrollment is supplied by an independently trusted deployment
configuration. No transport-supplied key becomes trusted
implicitly.

A proof authenticates only its exact challenge and root reference.

Proof verification does not establish a live fence, remote CAS,
durability, rollback resistance or honest provider execution.

The private keys in this file are synthetic test fixtures only.
"""

import hashlib
import importlib
import json
import unittest

from dataclasses import (
    FrozenInstanceError,
    replace,
)

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root
    as root,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_"
    "protected_provisioning_witness_deployment_floor_"
    "writer_policy_protected_root_anchor_enrollment"
)

ENROLLMENT_DOMAIN = (
    "AdamShell/A44/protected-root-anchor-enrollment/v1"
)

PROOF_DOMAIN = (
    "AdamShell/A44/protected-root-anchor-enrollment-proof/v1"
)


def canonical_json(value):

    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def public_bytes(private_key):

    return private_key.public_key().public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )


class A44PinnedProtectedRootAnchorEnrollmentContractTests(
    unittest.TestCase
):

    def setUp(self):

        self.m = importlib.import_module(MODULE)

        self.signer = Ed25519PrivateKey.from_private_bytes(
            b"a" * 32
        )

        self.replacement_signer = (
            Ed25519PrivateKey.from_private_bytes(
                b"b" * 32
            )
        )

        self.identity = root.ProtectedDeploymentIdentity(
            deployment_id="anchor-enrollment-test",
            configuration_sha256="a" * 64,
            provisioning_nonce=b"n" * 32,
        )

        self.key = public_bytes(
            self.signer
        )

        self.other_key = public_bytes(
            self.replacement_signer
        )

        self.assertNotEqual(
            self.key,
            self.other_key,
        )

        self.reference = root.ProtectedRootReference(
            revision=3,
            sha256="c" * 64,
        )

        self.challenge = b"q" * 32

        self.pin = self.make_pin()

    def make_pin(self, **changes):

        parameters = {
            "identity": self.identity,
            "anchor_id": "protected-anchor-alpha",
            "anchor_public_key": self.key,
            "enrollment_epoch": 1,
        }

        parameters.update(changes)

        return (
            self.m.PinnedProtectedRootAnchorEnrollment(
                **parameters
            )
        )

    def expected_fingerprint(self, pin=None):

        if pin is None:
            pin = self.pin

        identity = pin.identity

        payload = [
            ENROLLMENT_DOMAIN,
            pin.anchor_id,
            pin.anchor_public_key.hex(),
            pin.enrollment_epoch,
            identity.deployment_id,
            identity.configuration_sha256,
            identity.provisioning_nonce.hex(),
        ]

        return hashlib.sha256(
            canonical_json(payload)
        ).hexdigest()

    def proof_message(
        self,
        *,
        pin=None,
        challenge=None,
        reference=None,
        domain=PROOF_DOMAIN,
    ):

        if pin is None:
            pin = self.pin

        if challenge is None:
            challenge = self.challenge

        if reference is None:
            reference = self.reference

        return canonical_json(
            [
                domain,
                self.expected_fingerprint(pin),
                challenge.hex(),
                reference.revision,
                reference.sha256,
            ]
        )

    def signature(self, *, signer=None, **changes):

        if signer is None:
            signer = self.signer

        return signer.sign(
            self.proof_message(
                **changes
            )
        )

    def verify(
        self,
        signature,
        *,
        pin=None,
        **changes,
    ):

        if pin is None:
            pin = self.pin

        parameters = {
            "challenge": self.challenge,
            "state_reference": self.reference,
            "signature": signature,
        }

        parameters.update(changes)

        return pin.verify_proof(
            **parameters
        )

    def test_01_canonical_enrollment_fingerprint(self):

        self.assertIs(
            type(self.pin),
            self.m.PinnedProtectedRootAnchorEnrollment,
        )

        self.assertEqual(
            self.pin.identity,
            self.identity,
        )

        self.assertEqual(
            self.pin.anchor_id,
            "protected-anchor-alpha",
        )

        self.assertEqual(
            self.pin.anchor_public_key,
            self.key,
        )

        self.assertEqual(
            self.pin.enrollment_epoch,
            1,
        )

        expected = self.expected_fingerprint()

        self.assertEqual(
            self.pin.fingerprint(),
            expected,
        )

        independently_created = self.make_pin()

        self.assertEqual(
            independently_created,
            self.pin,
        )

        self.assertEqual(
            independently_created.fingerprint(),
            expected,
        )

        self.assertNotEqual(
            self.make_pin(
                anchor_public_key=self.other_key,
            ).fingerprint(),
            expected,
        )

        self.assertNotEqual(
            self.make_pin(
                enrollment_epoch=2,
            ).fingerprint(),
            expected,
        )

    def test_02_enrollment_is_immutable_object_state(self):

        self.assertTrue(
            self.pin.__dataclass_params__.frozen
        )

        self.assertFalse(
            hasattr(self.pin, "__dict__")
        )

        for field, value in (
            ("identity", None),
            ("anchor_id", "replacement"),
            ("anchor_public_key", self.other_key),
            ("enrollment_epoch", 2),
        ):

            with self.assertRaises(FrozenInstanceError):

                setattr(
                    self.pin,
                    field,
                    value,
                )

        self.assertEqual(
            self.pin.fingerprint(),
            self.expected_fingerprint(),
        )

    def test_03_valid_pinned_ed25519_proof(self):

        signature = self.signature()

        self.assertEqual(
            len(signature),
            64,
        )

        verified = self.verify(
            signature,
        )

        self.assertIs(
            type(verified),
            root.ProtectedRootReference,
        )

        self.assertEqual(
            verified,
            self.reference,
        )

    def test_04_same_identity_replacement_key_rejected(self):

        signature = self.signature(
            signer=self.replacement_signer,
        )

        # Replacement signs the original enrollment transcript,
        # but does not possess the pinned private key.

        with self.assertRaises(ValueError):

            self.verify(signature)

        replacement_pin = self.make_pin(
            anchor_public_key=self.other_key,
        )

        self.assertEqual(
            replacement_pin.identity,
            self.pin.identity,
        )

        self.assertEqual(
            replacement_pin.anchor_id,
            self.pin.anchor_id,
        )

        self.assertNotEqual(
            replacement_pin.fingerprint(),
            self.pin.fingerprint(),
        )

        replacement_proof = self.signature(
            signer=self.replacement_signer,
            pin=replacement_pin,
        )

        # A self-consistent proof for another enrollment
        # cannot replace the independently trusted pin.

        with self.assertRaises(ValueError):

            self.verify(
                replacement_proof,
            )

        self.assertEqual(
            self.verify(self.signature()),
            self.reference,
        )

    def test_05_anchor_id_is_bound_to_proof(self):

        alternative = self.make_pin(
            anchor_id="protected-anchor-beta",
        )

        self.assertNotEqual(
            alternative.fingerprint(),
            self.pin.fingerprint(),
        )

        with self.assertRaises(ValueError):

            self.verify(
                self.signature(pin=alternative),
            )

        with self.assertRaises(ValueError):

            self.verify(
                self.signature(),
                pin=alternative,
            )

    def test_06_enrollment_epoch_is_bound_to_proof(self):

        alternative = self.make_pin(
            enrollment_epoch=2,
        )

        self.assertNotEqual(
            alternative.fingerprint(),
            self.pin.fingerprint(),
        )

        with self.assertRaises(ValueError):

            self.verify(
                self.signature(),
                pin=alternative,
            )

        with self.assertRaises(ValueError):

            self.verify(
                self.signature(pin=alternative),
            )

    def test_07_full_deployment_identity_is_bound_to_proof(self):

        alternatives = (
            replace(
                self.identity,
                deployment_id="another-deployment",
            ),
            replace(
                self.identity,
                configuration_sha256="b" * 64,
            ),
            replace(
                self.identity,
                provisioning_nonce=b"x" * 32,
            ),
        )

        for identity in alternatives:

            alternative = self.make_pin(
                identity=identity,
            )

            self.assertNotEqual(
                alternative.fingerprint(),
                self.pin.fingerprint(),
            )

            with self.assertRaises(ValueError):

                self.verify(
                    self.signature(),
                    pin=alternative,
                )

            with self.assertRaises(ValueError):

                self.verify(
                    self.signature(pin=alternative),
                )

    def test_08_replayed_proof_rejected_for_new_challenge(self):

        original = self.signature()

        self.assertEqual(
            self.verify(original),
            self.reference,
        )

        fresh = b"r" * 32

        with self.assertRaises(ValueError):

            self.verify(
                original,
                challenge=fresh,
            )

        fresh_signature = self.signature(
            challenge=fresh,
        )

        self.assertEqual(
            self.verify(
                fresh_signature,
                challenge=fresh,
            ),
            self.reference,
        )

    def test_09_root_revision_and_digest_are_bound_to_proof(self):

        signature = self.signature()

        alternatives = (
            replace(
                self.reference,
                revision=4,
            ),
            replace(
                self.reference,
                sha256="d" * 64,
            ),
        )

        for alternative in alternatives:

            with self.assertRaises(ValueError):

                self.verify(
                    signature,
                    state_reference=alternative,
                )

            with self.assertRaises(ValueError):

                self.verify(
                    self.signature(
                        reference=alternative,
                    ),
                )

            self.assertEqual(
                self.verify(
                    self.signature(
                        reference=alternative,
                    ),
                    state_reference=alternative,
                ),
                alternative,
            )

    def test_10_signature_domains_are_not_interchangeable(self):

        for domain in (
            ENROLLMENT_DOMAIN,
            "AdamShell/A44/protected-root-anchor-cas/v1",
            "AdamShell/A44/protected-root-anchor-read/v1",
            "",
        ):

            signature = self.signature(
                domain=domain,
            )

            with self.assertRaises(ValueError):

                self.verify(signature)

        self.assertEqual(
            self.verify(self.signature()),
            self.reference,
        )

    def test_11_noncanonical_enrollment_inputs_rejected(self):

        cases = (
            {"identity": None},
            {"identity": {}},
            {"anchor_id": ""},
            {"anchor_id": " "},
            {"anchor_id": b"anchor"},
            {"anchor_public_key": bytearray(self.key)},
            {"anchor_public_key": memoryview(self.key)},
            {"anchor_public_key": self.key.hex()},
            {"anchor_public_key": b""},
            {"anchor_public_key": b"a" * 31},
            {"anchor_public_key": b"a" * 33},
            {"enrollment_epoch": True},
            {"enrollment_epoch": False},
            {"enrollment_epoch": 0},
            {"enrollment_epoch": -1},
            {"enrollment_epoch": 1.0},
            {"enrollment_epoch": "1"},
            {"enrollment_epoch": 1 << 63},
        )

        for changes in cases:

            with self.assertRaises(ValueError):

                self.make_pin(
                    **changes
                )

        largest = self.make_pin(
            enrollment_epoch=(1 << 63) - 1,
        )

        self.assertEqual(
            largest.enrollment_epoch,
            (1 << 63) - 1,
        )

        self.assertEqual(
            largest.fingerprint(),
            self.expected_fingerprint(largest),
        )

    def test_12_noncanonical_proof_inputs_rejected(self):

        signature = self.signature()

        cases = (
            {"challenge": None},
            {"challenge": b""},
            {"challenge": b"q" * 31},
            {"challenge": b"q" * 33},
            {"challenge": bytearray(self.challenge)},
            {"challenge": self.challenge.hex()},
            {"state_reference": None},
            {"state_reference": {}},
            {
                "state_reference": (
                    self.reference.revision,
                    self.reference.sha256,
                ),
            },
        )

        for changes in cases:

            with self.assertRaises(ValueError):

                self.verify(
                    signature,
                    **changes,
                )

        malformed_signatures = (
            None,
            b"",
            signature[:-1],
            signature + b"x",
            bytearray(signature),
            memoryview(signature),
            signature.hex(),
            bytes([signature[0] ^ 1]) + signature[1:],
        )

        for malformed in malformed_signatures:

            with self.assertRaises(ValueError):

                self.verify(
                    malformed,
                )

        self.assertEqual(
            self.verify(signature),
            self.reference,
        )


if __name__ == "__main__":
    unittest.main()
