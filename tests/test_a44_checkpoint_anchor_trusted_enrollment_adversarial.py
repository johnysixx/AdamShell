"""A44 / 66.27D signed anchor enrollment adversarial coverage.

The trusted provisioning signer ID and public key are assumed to
come from outside the signed manifest and local anchor database.

These tests verify signed-data validation and immutable client
binding. They do NOT establish independently trusted provisioning,
durable high-water floors, remote authority isolation or rollback
resistance.

A caller who substitutes the trusted signer key can enroll an
attacker-signed manifest. This is an explicitly tested limitation.
"""

import json
import shutil
import sys
import unittest

from dataclasses import fields, replace
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_anchor_trusted_enrollment_contract as contract
import test_a44_checkpoint_anchor_cas_backend_contract as backend_contract


class A44CheckpointAnchorTrustedEnrollmentAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointAnchorTrustedEnrollmentContractTests(
                "test_01_signed_enrollment_binds_read_and_cas"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_01_public_constructor_does_not_skip_validation(self):
        enrollment = self.fixture.enrolled()

        arguments = {
            field.name: getattr(
                enrollment,
                field.name,
            )
            for field in fields(enrollment)
        }

        with self.assertRaises(ValueError):
            type(enrollment)(**arguments)

    def test_02_plain_dataclass_replace_is_not_verified(self):
        enrollment = self.fixture.enrolled()

        with self.assertRaises(ValueError):
            replace(
                enrollment,
                expected_anchor_id="forged-anchor",
            )

        self.assertEqual(
            self.fixture.read(enrollment),
            self.fixture.fixture.initial,
        )

    def test_03_unsigned_root_identity_replacement_rejected(self):
        original = self.fixture.payload()
        original_signature = self.fixture.signer.sign(
            original
        )

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                changes={
                    "root_id": "forged-root"
                },
                signature=original_signature,
            )

    def test_04_valid_signer_wrong_signed_identity_rejected(self):
        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                changes={
                    "signer_id": "different-provisioning-root"
                }
            )

    def test_05_attacker_signer_without_trust_pin_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                signer=attacker
            )

    def test_06_caller_substituted_trust_root_is_known_limit(self):
        """KNOWN LIMIT: caller-controlled trust roots are not secure."""

        attacker = Ed25519PrivateKey.generate()

        attacker_public_key = (
            backend_contract.public_key(attacker)
        )

        attacker_id = "attacker-provisioning-root"

        # This succeeds ONLY because the caller itself supplies
        # a replacement trusted signer identity and public key.
        enrollment = self.fixture.enrolled(
            changes={
                "signer_id": attacker_id
            },
            signer=attacker,
            trusted_signer_id=attacker_id,
            trusted_signer_public_key=attacker_public_key,
        )

        self.assertEqual(
            enrollment.trusted_signer_id,
            attacker_id,
        )

        self.assertEqual(
            enrollment.trusted_signer_public_key,
            attacker_public_key,
        )

        self.assertEqual(
            self.fixture.read(enrollment),
            self.fixture.fixture.initial,
        )

    def test_07_signed_read_response_cannot_be_replayed_as_enrollment(self):
        with self.fixture.fixture.backend.hold(
            challenge=b"\x11" * 32
        ) as response:
            message, signature = response

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                payload=message,
                signature=signature,
            )

    def test_08_signed_cas_response_cannot_be_replayed_as_enrollment(self):
        response = (
            self.fixture.fixture.backend.advance_if_current(
                operation_id=contract.OPERATION_ID,
                expected_revision=10,
                next_revision=11,
                expected_generation=20,
                expected_fence_token=30,
                challenge=b"\x22" * 32,
            )
        )

        message, signature = response

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                payload=message,
                signature=signature,
            )

    def test_09_signed_nonfinite_json_constant_rejected(self):
        original = self.fixture.payload()

        malicious = original.replace(
            b'"minimum_revision":10',
            b'"minimum_revision":NaN',
            1,
        )

        self.assertNotEqual(
            malicious,
            original,
        )

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                payload=malicious
            )

    def test_10_signed_duplicate_json_key_rejected(self):
        original = self.fixture.payload()

        malicious = (
            b'{"version":1,'
            + original[1:]
        )

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                payload=malicious
            )

    def test_11_raw_utf8_signed_manifest_rejected(self):
        document = dict(self.fixture.document)

        document["signer_id"] = (
            contract.SIGNER_ID + "-é"
        )

        non_ascii = json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                payload=non_ascii
            )

    def test_12_signed_noncanonical_key_order_rejected(self):
        noncanonical = json.dumps(
            self.fixture.document,
            sort_keys=False,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("ascii")

        self.assertNotEqual(
            noncanonical,
            self.fixture.payload(),
        )

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                payload=noncanonical
            )

    def test_13_mutable_external_trust_data_rejected(self):
        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                trusted_signer_public_key=bytearray(
                    self.fixture.signer_key
                )
            )

        original = self.fixture.payload()

        original_signature = self.fixture.signer.sign(
            original
        )

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                payload=bytearray(original),
                signature=original_signature,
            )

    def test_14_boolean_and_overflow_counters_rejected(self):
        attacks = (
            {
                "minimum_revision": True
            },
            {
                "minimum_generation": False
            },
            {
                "minimum_fence_token": 1 << 63
            },
        )

        for changes in attacks:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.fixture.enrolled(
                        changes=changes
                    )

        with self.assertRaises(ValueError):
            self.fixture.enrolled(
                minimum_revision=True
            )

    def test_15_partial_floor_raise_remains_immutable(self):
        original = self.fixture.enrolled()

        advanced = original.raise_floor(
            minimum_revision=11,
            minimum_generation=20,
            minimum_fence_token=30,
        )

        self.assertIsNot(original, advanced)

        self.assertEqual(
            (
                original.minimum_revision,
                original.minimum_generation,
                original.minimum_fence_token,
            ),
            (10, 20, 30),
        )

        self.assertEqual(
            (
                advanced.minimum_revision,
                advanced.minimum_generation,
                advanced.minimum_fence_token,
            ),
            (11, 20, 30),
        )

        self.assertEqual(
            advanced.expected_anchor_public_key,
            original.expected_anchor_public_key,
        )

        with self.assertRaises(ValueError):
            advanced.raise_floor(
                minimum_revision=10,
                minimum_generation=20,
                minimum_fence_token=30,
            )

    def test_16_advanced_floor_rejects_stale_cas_request(self):
        original = self.fixture.enrolled()

        self.assertEqual(
            self.fixture.advance(original),
            self.fixture.fixture.first,
        )

        advanced = original.raise_floor(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
        )

        with self.assertRaises(ValueError):
            advanced.cas_client(
                self.fixture.fixture.backend
            ).advance_if_current(
                operation_id="b" * 32,
                expected_revision=10,
                next_revision=12,
                expected_generation=20,
                expected_fence_token=30,
            )

        self.assertEqual(
            self.fixture.read(advanced),
            self.fixture.fixture.first,
        )

    def test_17_preserved_high_water_detects_database_rollback(self):
        """KNOWN LIMIT: the higher floor must survive elsewhere."""

        original = self.fixture.enrolled()

        backup = (
            Path(self.fixture.fixture.temp.name)
            / "before-enrollment-rollback.sqlite3"
        )

        shutil.copyfile(
            self.fixture.fixture.path,
            backup,
        )

        self.assertEqual(
            self.fixture.advance(original),
            self.fixture.fixture.first,
        )

        advanced = original.raise_floor(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
        )

        shutil.copyfile(
            backup,
            self.fixture.fixture.path,
        )

        reopened = self.fixture.fixture.reopened()

        # An old legitimate floor accepts the old signed state.
        self.assertEqual(
            self.fixture.read(
                original,
                reopened,
            ),
            self.fixture.fixture.initial,
        )

        # A separately preserved higher floor detects it.
        with self.assertRaises(ValueError):
            self.fixture.read(
                advanced,
                reopened,
            )

    def test_18_higher_signed_floor_rejects_older_backend_state(self):
        # A correctly signed manifest may set minima higher
        # than the backend's current locally stored state.
        enrollment = self.fixture.enrolled(
            changes={
                "minimum_revision": 11,
                "minimum_generation": 21,
                "minimum_fence_token": 31,
            }
        )

        self.assertEqual(
            (
                enrollment.minimum_revision,
                enrollment.minimum_generation,
                enrollment.minimum_fence_token,
            ),
            (11, 21, 31),
        )

        with self.assertRaises(ValueError):
            self.fixture.read(enrollment)

        with self.assertRaises(ValueError):
            enrollment.cas_client(
                self.fixture.fixture.backend
            ).lookup_operation(
                operation_id=contract.OPERATION_ID
            )


if __name__ == "__main__":
    unittest.main()
