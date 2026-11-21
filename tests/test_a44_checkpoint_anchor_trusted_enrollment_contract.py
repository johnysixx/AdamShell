"""A44 / 66.27B signed checkpoint anchor enrollment contract.

EXPECTED RED: trusted enrollment production module is absent.

PROPOSED API:

TrustedSignedCheckpointAnchorEnrollment.from_signed_manifest(
    manifest=canonical_ascii_json_bytes,
    signature=ed25519_signature,
    trusted_signer_id=externally_provisioned_identity,
    trusted_signer_public_key=externally_provisioned_key,
    expected_anchor_id=str,
    expected_authority_id=str,
    expected_root_id=str,
    minimum_enrollment_epoch=int,
    minimum_revision=int,
    minimum_generation=int,
    minimum_fence_token=int,
)

enrollment.read_source(provider)
    -> existing PinnedSignedCheckpointAnchorSource

enrollment.cas_client(provider)
    -> existing PinnedSignedCheckpointAnchorCASClient

enrollment.raise_floor(
    minimum_revision=int,
    minimum_generation=int,
    minimum_fence_token=int,
)
    -> new immutable enrollment with nondecreasing floors

SIGNED MANIFEST:

domain="AdamShell/A44/anchor-enrollment/v1"
version=1
operation="enroll"
signer_id
anchor_id
anchor_public_key_hex
authority_id
authority_public_key_hex
root_id
root_public_key_hex
enrollment_epoch
minimum_revision
minimum_generation
minimum_fence_token

All keys are 32-byte Ed25519 public keys, encoded as exactly
64 lowercase hexadecimal characters. The signed JSON is canonical
ASCII, has exact fields and rejects duplicate properties.

The externally supplied signer key is the trust prerequisite;
a key bundled inside the signed manifest is NOT a trust root.

SECURITY LIMITS:

- Verification does not prove trustworthy provisioning.
- Caller-controlled trusted pins can still be replaced.
- raise_floor is in-memory only; it does not persist high-water.
- A trusted signer's own malicious signature cannot be detected.
- No hardware trust, remote authority or cross-store atomicity.
- No checkpoint restore, reset or republication.
"""

import importlib
import json
import shutil
import sys
import unittest

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_anchor_cas_backend_contract as backend_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_anchor_trusted_enrollment"
)

CLASS_NAME = "TrustedSignedCheckpointAnchorEnrollment"

DOMAIN = "AdamShell/A44/anchor-enrollment/v1"
SIGNER_ID = "a44-test-provisioning-root"

OPERATION_ID = "a" * 32


def canonical(document):
    return json.dumps(
        document,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


class A44CheckpointAnchorTrustedEnrollmentContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)
        self.enrollment_type = getattr(
            module,
            CLASS_NAME,
        )

        self.fixture = (
            backend_contract.A44AnchorCASBackendAtomicRecoveryContractTests(
                "test_01_bootstrap_supports_pinned_signed_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.signer = Ed25519PrivateKey.generate()
        self.signer_key = backend_contract.public_key(
            self.signer
        )

        self.document = {
            "domain": DOMAIN,
            "version": 1,
            "operation": "enroll",
            "signer_id": SIGNER_ID,
            "anchor_id": self.fixture.anchor_id,
            "anchor_public_key_hex": self.fixture.anchor_key.hex(),
            "authority_id": self.fixture.authority_id,
            "authority_public_key_hex": (
                self.fixture.authority_key.hex()
            ),
            "root_id": self.fixture.root_id,
            "root_public_key_hex": (
                self.fixture.root_key.hex()
            ),
            "enrollment_epoch": self.fixture.epoch,
            "minimum_revision": self.fixture.initial[5],
            "minimum_generation": self.fixture.initial[6],
            "minimum_fence_token": self.fixture.initial[7],
        }

    def payload(self, changes=None):
        document = dict(self.document)

        if changes:
            document.update(changes)

        return canonical(document)

    def enrollment_arguments(self):
        return {
            "trusted_signer_id": SIGNER_ID,
            "trusted_signer_public_key": self.signer_key,
            "expected_anchor_id": self.fixture.anchor_id,
            "expected_authority_id": self.fixture.authority_id,
            "expected_root_id": self.fixture.root_id,
            "minimum_enrollment_epoch": self.fixture.epoch,
            "minimum_revision": self.fixture.initial[5],
            "minimum_generation": self.fixture.initial[6],
            "minimum_fence_token": self.fixture.initial[7],
        }

    def enrolled(
        self,
        changes=None,
        *,
        payload=None,
        signature=None,
        signer=None,
        **overrides,
    ):
        if payload is None:
            payload = self.payload(changes)

        if signer is None:
            signer = self.signer

        if signature is None:
            signature = signer.sign(payload)

        arguments = self.enrollment_arguments()
        arguments.update(overrides)

        return self.enrollment_type.from_signed_manifest(
            manifest=payload,
            signature=signature,
            **arguments,
        )

    def read(self, enrollment, provider=None):
        if provider is None:
            provider = self.fixture.backend

        with enrollment.read_source(provider).hold() as snapshot:
            return snapshot

    def advance(self, enrollment, provider=None):
        if provider is None:
            provider = self.fixture.backend

        return enrollment.cas_client(
            provider
        ).advance_if_current(
            operation_id=OPERATION_ID,
            expected_revision=10,
            next_revision=11,
            expected_generation=20,
            expected_fence_token=30,
        )

    def test_01_signed_enrollment_binds_read_and_cas(self):
        enrollment = self.enrolled()

        self.assertEqual(
            self.read(enrollment),
            self.fixture.initial,
        )

        self.assertEqual(
            self.advance(enrollment),
            self.fixture.first,
        )

        self.assertEqual(
            self.read(enrollment),
            self.fixture.first,
        )

        self.assertEqual(
            enrollment.cas_client(
                self.fixture.backend
            ).lookup_operation(
                operation_id=OPERATION_ID
            ),
            ("committed", self.fixture.first),
        )

    def test_02_enrollment_is_usable_after_backend_reopen(self):
        enrollment = self.enrolled()

        self.assertEqual(
            self.advance(enrollment),
            self.fixture.first,
        )

        restarted = self.fixture.reopened()

        self.assertEqual(
            self.read(enrollment, restarted),
            self.fixture.first,
        )

        self.assertEqual(
            enrollment.cas_client(
                restarted
            ).lookup_operation(
                operation_id=OPERATION_ID
            ),
            ("committed", self.fixture.first),
        )

    def test_03_wrong_trusted_signer_key_rejected(self):
        wrong = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.enrolled(
                trusted_signer_public_key=(
                    backend_contract.public_key(wrong)
                ),
            )

    def test_04_forged_manifest_signed_by_attacker_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.enrolled(
                signer=attacker
            )

    def test_05_wrong_trusted_signer_identity_rejected(self):
        with self.assertRaises(ValueError):
            self.enrolled(
                trusted_signer_id="wrong-provisioning-root",
            )

        with self.assertRaises(ValueError):
            self.enrolled(
                changes={"signer_id": "wrong-provisioning-root"},
            )

    def test_06_unsigned_anchor_key_replacement_rejected(self):
        original_signature = self.signer.sign(
            self.payload()
        )

        with self.assertRaises(ValueError):
            self.enrolled(
                changes={
                    "anchor_public_key_hex": "01" * 32
                },
                signature=original_signature,
            )

    def test_07_unsigned_authority_key_replacement_rejected(self):
        original_signature = self.signer.sign(
            self.payload()
        )

        with self.assertRaises(ValueError):
            self.enrolled(
                changes={
                    "authority_public_key_hex": "02" * 32
                },
                signature=original_signature,
            )

    def test_08_unsigned_root_key_replacement_rejected(self):
        original_signature = self.signer.sign(
            self.payload()
        )

        with self.assertRaises(ValueError):
            self.enrolled(
                changes={
                    "root_public_key_hex": "03" * 32
                },
                signature=original_signature,
            )

    def test_09_malformed_signatures_fail_closed(self):
        valid_signature = self.signer.sign(
            self.payload()
        )

        attacks = (
            b"",
            b"\x00" * 63,
            b"\x00" * 64,
            valid_signature[:-1]
            + bytes((valid_signature[-1] ^ 1,)),
            bytearray(valid_signature),
        )

        for attack in attacks:
            with self.subTest(signature_type=type(attack).__name__):
                with self.assertRaises(ValueError):
                    self.enrolled(
                        signature=attack
                    )

    def test_10_signed_duplicate_json_property_rejected(self):
        payload = (
            b'{"version":1,'
            + self.payload()[1:]
        )

        with self.assertRaises(ValueError):
            self.enrolled(
                payload=payload
            )

    def test_11_signed_noncanonical_json_rejected(self):
        payload = json.dumps(
            self.document,
            sort_keys=True,
            indent=2,
            ensure_ascii=True,
        ).encode("ascii")

        with self.assertRaises(ValueError):
            self.enrolled(
                payload=payload
            )

    def test_12_signed_unexpected_property_rejected(self):
        with self.assertRaises(ValueError):
            self.enrolled(
                changes={"unexpected_property": True},
            )

    def test_13_wrong_signed_domain_operation_version(self):
        attacks = (
            {"domain": "wrong-domain"},
            {"operation": "rotate"},
            {"version": 2},
            {"version": True},
        )

        for changes in attacks:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.enrolled(changes=changes)

    def test_14_wrong_expected_identities_rejected(self):
        attacks = (
            {"expected_anchor_id": "wrong-anchor"},
            {"expected_authority_id": "wrong-authority"},
            {"expected_root_id": "wrong-root"},
        )

        for changes in attacks:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.enrolled(**changes)

    def test_15_enrollment_epoch_below_external_floor_rejected(self):
        with self.assertRaises(ValueError):
            self.enrolled(
                minimum_enrollment_epoch=(
                    self.fixture.epoch + 1
                )
            )

        with self.assertRaises(ValueError):
            self.enrolled(
                changes={
                    "enrollment_epoch": self.fixture.epoch - 1
                },
            )

    def test_16_counters_below_external_floors_rejected(self):
        for field in (
            "minimum_revision",
            "minimum_generation",
            "minimum_fence_token",
        ):
            original = self.document[field]

            with self.subTest(
                field=field,
                mode="raised_external_floor",
            ):
                with self.assertRaises(ValueError):
                    self.enrolled(
                        **{field: original + 1}
                    )

            with self.subTest(
                field=field,
                mode="lower_signed_floor",
            ):
                with self.assertRaises(ValueError):
                    self.enrolled(
                        changes={field: original - 1}
                    )

    def test_17_malformed_signed_manifest_values_rejected(self):
        attacks = (
            {"anchor_public_key_hex": "a" * 63},
            {"authority_public_key_hex": "A" * 64},
            {"root_public_key_hex": "z" * 64},
            {"enrollment_epoch": True},
            {"minimum_revision": False},
            {"minimum_generation": -1},
            {"minimum_fence_token": 1 << 63},
            {"anchor_id": ""},
            {"authority_id": " leading-space"},
        )

        for changes in attacks:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.enrolled(changes=changes)

    def test_18_malformed_external_trust_inputs_rejected(self):
        attacks = (
            {"trusted_signer_id": ""},
            {"trusted_signer_public_key": b"\x01" * 31},
            {"trusted_signer_public_key": bytearray(b"\x01" * 32)},
            {"minimum_enrollment_epoch": True},
            {"minimum_revision": -1},
            {"minimum_generation": False},
            {"minimum_fence_token": 1 << 63},
        )

        for changes in attacks:
            with self.subTest(changes=tuple(changes)):
                with self.assertRaises(ValueError):
                    self.enrolled(**changes)

    def test_19_floor_advancement_is_immutable_and_monotonic(self):
        original = self.enrolled()

        self.assertEqual(
            self.advance(original),
            self.fixture.first,
        )

        advanced = original.raise_floor(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
        )

        self.assertIsNot(
            advanced,
            original,
        )

        self.assertEqual(
            original.minimum_revision,
            10,
        )

        self.assertEqual(
            advanced.minimum_revision,
            11,
        )

        self.assertEqual(
            self.read(advanced),
            self.fixture.first,
        )

        with self.assertRaises(ValueError):
            advanced.raise_floor(
                minimum_revision=10,
                minimum_generation=21,
                minimum_fence_token=31,
            )

        with self.assertRaises(AttributeError):
            advanced.expected_anchor_id = "attacker-anchor"

    def test_20_external_floor_detects_reference_store_rollback(self):
        """KNOWN LIMIT: floors are not durably stored here."""

        enrollment = self.enrolled()

        backup = (
            Path(self.fixture.temp.name)
            / "pre-publication-anchor.sqlite3"
        )

        shutil.copyfile(
            self.fixture.path,
            backup,
        )

        self.assertEqual(
            self.advance(enrollment),
            self.fixture.first,
        )

        advanced = enrollment.raise_floor(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
        )

        self.assertEqual(
            self.read(advanced),
            self.fixture.first,
        )

        shutil.copyfile(
            backup,
            self.fixture.path,
        )

        reopened = self.fixture.reopened()

        # A client with the old, still-valid signed floor
        # can accept the rolled-back database.
        self.assertEqual(
            self.read(enrollment, reopened),
            self.fixture.initial,
        )

        # A caller that preserved a higher trusted floor
        # can detect this rollback.
        with self.assertRaises(ValueError):
            self.read(advanced, reopened)

        self.assertEqual(
            enrollment.cas_client(
                reopened
            ).lookup_operation(
                operation_id=OPERATION_ID
            ),
            ("unknown", self.fixture.initial),
        )


if __name__ == "__main__":
    unittest.main()
