"""A44 adversarial recovery-evidence attestation.

These tests distinguish signature verification from
trusted enrollment, independent freshness, and authority
to reconstruct or republish Universe entities.

The test signing keys are ephemeral fixtures.
They are NOT production trust-root credentials.

Direct construction of public Python result objects is
not cryptographic provenance.

No test authorizes restoration or republication.
"""

import io
import json
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_canonical_archive import (
    LocalDurableCanonicalEvidenceArchive,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergReconciler,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)

from core.existence.history_receipt_trust_recovery_attestation import (
    PinnedRecoveryEvidenceAttestationVerifier,
    VerifiedRecoveryEvidenceAttestation,
)

from universe.universe import Universe


WORLD = "a44_667_adversarial_attestation"
INCIDENT = "incident-adversarial-attestation"
OPERATION = "security_validation"
AUTHORITY = "recovery_authority_v1"

DOMAIN = (
    "AdamShell/A44/"
    "recovery-evidence-attestation/v1"
)

GENERATION = 8


def canonical_bytes(value):
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def public_bytes(private_key):
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class A44RecoveryEvidenceAttestationAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_667_adversarial_attestation_"
        )

        self.addCleanup(directory.cleanup)

        self.root = Path(directory.name)

        self.outbox = LocalDurableSecurityIncidentOutbox.create(
            self.root / "incident.sqlite",
            max_pending=8,
            max_total=16,
        )

        self.archive = LocalDurableCanonicalEvidenceArchive.create(
            self.root / "archive.sqlite",
            universe_id=WORLD,
            max_entries=8,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id=WORLD
            )

            coordinator = SecurityIncidentCronenbergReconciler(
                universe=self.world,
                outbox=self.outbox,
            )

            with self.assertRaises(SecurityAttackDetected):
                coordinator.reject(
                    incident_id=INCIDENT,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "adversarial recovery attestation"
                    ),
                )

        self.assertTrue(
            self.archive.capture_live(
                universe=self.world,
                incident_id=INCIDENT,
                source_operation=OPERATION,
            )
        )

        self.evidence = self.archive.get_untrusted(
            INCIDENT
        )

        self.key = Ed25519PrivateKey.generate()

        self.verifier = (
            PinnedRecoveryEvidenceAttestationVerifier
            .from_pinned_keys({
                AUTHORITY: public_bytes(self.key),
            })
        )

    def document(self):
        return {
            "schema_version": 1,
            "domain": DOMAIN,
            "authority_id": AUTHORITY,
            "generation": GENERATION,
            "universe_id": WORLD,
            "incident_id": INCIDENT,
            "source_operation": OPERATION,
            "cronenberg_id": self.evidence.cronenberg_id,
            "projection_sha256": self.evidence.projection_sha256,
        }

    def sign(self, document=None, *, signing_key=None):
        document = (
            self.document()
            if document is None
            else document
        )

        message = canonical_bytes(document)

        key = (
            self.key
            if signing_key is None
            else signing_key
        )

        return message, key.sign(message)

    def verify(
        self,
        message,
        signature,
        *,
        verifier=None,
        evidence=None,
        floor=7,
        **overrides,
    ):
        arguments = {
            "evidence": (
                self.evidence
                if evidence is None
                else evidence
            ),
            "message": message,
            "signature": signature,
            "expected_authority_id": AUTHORITY,
            "expected_universe_id": WORLD,
            "expected_incident_id": INCIDENT,
            "minimum_generation": floor,
        }

        arguments.update(overrides)

        target = (
            self.verifier
            if verifier is None
            else verifier
        )

        return target.verify(**arguments)

    def test_signed_wrong_source_operation_denied(self):
        document = self.document()
        document["source_operation"] = "receipt_signature"

        message, signature = self.sign(document)

        with self.assertRaises(ValueError):
            self.verify(message, signature)

    def test_signed_wrong_cronenberg_denied(self):
        document = self.document()
        document["cronenberg_id"] = "cronenberg_deadbeef"

        message, signature = self.sign(document)

        with self.assertRaises(ValueError):
            self.verify(message, signature)

    def test_signed_rehashed_projection_claim_denied(self):
        document = self.document()
        document["projection_sha256"] = "a" * 64

        if document["projection_sha256"] == (
            self.evidence.projection_sha256
        ):
            document["projection_sha256"] = "b" * 64

        message, signature = self.sign(document)

        with self.assertRaises(ValueError):
            self.verify(message, signature)

        self.assertTrue(
            self.evidence.verify_live(self.world)
        )

    def test_signature_cannot_be_spliced_to_new_message(self):
        message, signature = self.sign()

        altered = self.document()
        altered["generation"] = GENERATION + 1

        altered_message = canonical_bytes(altered)

        self.assertNotEqual(
            message,
            altered_message,
        )

        with self.assertRaises(ValueError):
            self.verify(altered_message, signature)

    def test_signed_foreign_world_and_incident_denied(self):
        changes = (
            ("universe_id", "a44_foreign_world"),
            ("incident_id", "incident-foreign-attestation"),
        )

        for field, value in changes:
            with self.subTest(field=field):
                document = self.document()
                document[field] = value

                message, signature = self.sign(document)

                with self.assertRaises(ValueError):
                    self.verify(message, signature)

    def test_unpinned_foreign_signing_key_denied(self):
        foreign_key = Ed25519PrivateKey.generate()

        message, signature = self.sign(
            signing_key=foreign_key
        )

        with self.assertRaises(ValueError):
            self.verify(message, signature)

    def test_attacker_controlled_pin_is_not_independent_trust(self):
        """A caller-selected pinset can validate attacker signatures.

        This is a documented external trust-provisioning gap,
        NOT a claim that the verification algorithm is broken.
        """

        foreign_key = Ed25519PrivateKey.generate()

        attacker_configured_verifier = (
            PinnedRecoveryEvidenceAttestationVerifier
            .from_pinned_keys({
                AUTHORITY: public_bytes(foreign_key),
            })
        )

        message, signature = self.sign(
            signing_key=foreign_key
        )

        result = self.verify(
            message,
            signature,
            verifier=attacker_configured_verifier,
        )

        self.assertIs(
            result.signature_verified,
            True,
        )

        self.assertIs(
            result.is_authoritative,
            False,
        )

        self.assertIs(
            result.is_restorable,
            False,
        )

        self.assertIs(
            result.can_republish,
            False,
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
                verifier=self.verifier,
            )

    def test_generation_floor_requires_independent_protection(self):
        message, signature = self.sign()

        for floor in (0, 7):
            with self.subTest(accepted_floor=floor):
                result = self.verify(
                    message,
                    signature,
                    floor=floor,
                )

                self.assertTrue(
                    result.signature_verified
                )

        for floor in (8, 9, -1, True, "7", 7.0):
            with self.subTest(rejected_floor=floor):
                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        signature,
                        floor=floor,
                    )

    def test_signed_noncanonical_messages_denied(self):
        document = self.document()
        canonical = canonical_bytes(document)

        marker = b'"schema_version":1'

        self.assertEqual(
            canonical.count(marker),
            1,
        )

        duplicates = canonical.replace(
            marker,
            (
                b'"schema_version":1,'
                b'"schema_version":1'
            ),
            1,
        )

        pretty = json.dumps(
            document,
            sort_keys=True,
            indent=2,
        ).encode("utf-8")

        with_extra = self.document()
        with_extra["unexpected"] = "injected"

        samples = (
            duplicates,
            pretty,
            canonical + b"\n",
            canonical_bytes(with_extra),
        )

        for message in samples:
            with self.subTest(message=repr(message[:40])):
                signature = self.key.sign(message)

                with self.assertRaises(ValueError):
                    self.verify(message, signature)

    def test_type_confusion_denied(self):
        message, signature = self.sign()

        samples = (
            {
                "message": message.decode("utf-8"),
            },
            {
                "message": bytearray(message),
            },
            {
                "signature": bytearray(signature),
            },
            {
                "signature": signature[:-1],
            },
            {
                "expected_authority_id": True,
            },
            {
                "expected_universe_id": True,
            },
            {
                "expected_incident_id": True,
            },
            {
                "minimum_generation": True,
            },
        )

        for changes in samples:
            with self.subTest(changes=str(changes)[:55]):
                arguments = {
                    "evidence": self.evidence,
                    "message": message,
                    "signature": signature,
                    "expected_authority_id": AUTHORITY,
                    "expected_universe_id": WORLD,
                    "expected_incident_id": INCIDENT,
                    "minimum_generation": 7,
                }

                arguments.update(changes)

                with self.assertRaises(ValueError):
                    self.verifier.verify(**arguments)

    def test_directly_constructed_result_is_not_authority(self):
        """A Python dataclass is not cryptographic provenance."""

        forged = VerifiedRecoveryEvidenceAttestation(
            authority_id=AUTHORITY,
            generation=GENERATION,
            universe_id=WORLD,
            incident_id=INCIDENT,
            source_operation=OPERATION,
            cronenberg_id=self.evidence.cronenberg_id,
            projection_sha256=self.evidence.projection_sha256,
        )

        self.assertTrue(
            forged.signature_verified
        )

        self.assertFalse(
            forged.is_authoritative
        )

        self.assertFalse(
            forged.is_restorable
        )

        self.assertFalse(
            forged.can_republish
        )

        self.assertFalse(
            hasattr(forged, "restore")
        )

        self.assertFalse(
            hasattr(forged, "republish")
        )

    def test_valid_attestation_cannot_restore_fresh_universe(self):
        message, signature = self.sign()

        result = self.verify(
            message,
            signature,
        )

        with redirect_stdout(io.StringIO()):
            fresh = Universe(
                universe_id=WORLD
            )

        self.assertTrue(
            result.signature_verified
        )

        self.assertFalse(
            result.is_authoritative
        )

        self.assertFalse(
            result.is_restorable
        )

        self.assertFalse(
            result.can_republish
        )

        with self.assertRaises(ValueError):
            self.evidence.verify_live(fresh)

        self.assertEqual(
            len(fresh.entities),
            0,
        )

        self.assertEqual(
            len(fresh.cronenbergs),
            0,
        )

        self.assertEqual(
            len(fresh.quantum_events),
            0,
        )


if __name__ == "__main__":
    unittest.main()
