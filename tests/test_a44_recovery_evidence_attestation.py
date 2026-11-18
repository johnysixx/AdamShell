"""A44 pinned recovery evidence attestation contract.

EXPECTED RED: the attestation implementation is absent.

A valid signature attests only to a signed canonical
evidence projection, not the historical truth of a
publication or the completeness of Cronenberg object state.

It MUST NOT authorize Universe restoration or republication.

The test's ephemeral Ed25519 keys are controlled fixtures,
not a production trusted-root enrollment mechanism.

The minimum generation must come from an independently
protected monotonic trust source in a real deployment.
"""

import hashlib
import importlib
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

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergReconciler,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)

from universe.universe import Universe


MODULE = (
    "core.existence."
    "history_receipt_trust_recovery_attestation"
)

DOMAIN = (
    "AdamShell/A44/"
    "recovery-evidence-attestation/v1"
)

AUTHORITY = "recovery_authority_v1"

WORLD = "a44_667_recovery_attestation"
INCIDENT = "incident-recovery-attestation"
OPERATION = "security_validation"

GENERATION = 8
TRUSTED_FLOOR = 7


def canonical_bytes(document):
    return json.dumps(
        document,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def projection_digest(payload):
    body = {
        key: value
        for key, value in payload.items()
        if key != "projection_sha256"
    }

    return hashlib.sha256(
        canonical_bytes(body)
    ).hexdigest()


class A44RecoveryEvidenceAttestationContractTests(
    unittest.TestCase
):

    def setUp(self):
        implementation = importlib.import_module(
            MODULE
        )

        self.Verifier = (
            implementation.PinnedRecoveryEvidenceAttestationVerifier
        )

        self.Result = (
            implementation.VerifiedRecoveryEvidenceAttestation
        )

        directory = tempfile.TemporaryDirectory(
            prefix="a44_667_attestation_"
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
                        "recovery attestation test"
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

        self.assertIsInstance(
            self.evidence,
            CanonicalSecurityPublicationEvidence,
        )

        self.private_key = Ed25519PrivateKey.generate()

        self.public_key = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        self.verifier = self.Verifier.from_pinned_keys({
            AUTHORITY: self.public_key,
        })

    def document(self):
        return {
            "schema_version": 1,
            "domain": DOMAIN,
            "authority_id": AUTHORITY,
            "generation": GENERATION,
            "universe_id": self.evidence.universe_id,
            "incident_id": self.evidence.incident_id,
            "source_operation": self.evidence.source_operation,
            "cronenberg_id": self.evidence.cronenberg_id,
            "projection_sha256": self.evidence.projection_sha256,
        }

    def signed(self, document=None, *, key=None):
        body = (
            self.document()
            if document is None
            else document
        )

        message = canonical_bytes(body)

        signing_key = (
            self.private_key
            if key is None
            else key
        )

        return (
            message,
            signing_key.sign(message),
        )

    def verify(
        self,
        message,
        signature,
        *,
        evidence=None,
        verifier=None,
        authority=AUTHORITY,
        world=WORLD,
        incident=INCIDENT,
        floor=TRUSTED_FLOOR,
    ):
        return (
            self.verifier
            if verifier is None
            else verifier
        ).verify(
            evidence=(
                self.evidence
                if evidence is None
                else evidence
            ),
            message=message,
            signature=signature,
            expected_authority_id=authority,
            expected_universe_id=world,
            expected_incident_id=incident,
            minimum_generation=floor,
        )

    def test_valid_signature_attests_data_only(self):
        message, signature = self.signed()

        result = self.verify(
            message,
            signature,
        )

        self.assertIs(type(result), self.Result)

        self.assertIs(
            result.signature_verified,
            True,
        )

        self.assertEqual(
            result.authority_id,
            AUTHORITY,
        )

        self.assertEqual(
            result.universe_id,
            WORLD,
        )

        self.assertEqual(
            result.incident_id,
            INCIDENT,
        )

        self.assertEqual(
            result.projection_sha256,
            self.evidence.projection_sha256,
        )

        self.assertEqual(
            result.generation,
            GENERATION,
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

    def test_pinned_public_keys_are_detached_and_validated(self):
        pins = {
            AUTHORITY: self.public_key,
        }

        verifier = self.Verifier.from_pinned_keys(
            pins
        )

        pins.clear()

        message, signature = self.signed()

        result = self.verify(
            message,
            signature,
            verifier=verifier,
        )

        self.assertTrue(
            result.signature_verified
        )

        for invalid in (
            {},
            {AUTHORITY: b"x" * 31},
            {AUTHORITY: "not-bytes"},
            {"": self.public_key},
            {AUTHORITY: bytearray(self.public_key)},
        ):
            with self.subTest(invalid=str(invalid)[:40]):
                with self.assertRaises(ValueError):
                    self.Verifier.from_pinned_keys(
                        invalid
                    )

    def test_unpinned_attacker_signing_key_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        message, signature = self.signed(
            key=attacker
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
            )

    def test_modified_signature_and_invalid_length_rejected(self):
        message, signature = self.signed()

        corrupted = bytearray(signature)
        corrupted[0] ^= 1

        for invalid in (
            bytes(corrupted),
            signature[:-1],
            b"",
            "not-signature-bytes",
        ):
            with self.subTest(signature=str(invalid)[:32]):
                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        invalid,
                    )

    def test_signed_wrong_domain_rejected(self):
        document = self.document()

        document["domain"] = (
            "AdamShell/A44/"
            "authority-reply/v1"
        )

        message, signature = self.signed(
            document
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
            )

    def test_signed_foreign_universe_rejected(self):
        document = self.document()

        document["universe_id"] = (
            "a44_foreign_recovery_universe"
        )

        message, signature = self.signed(
            document
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
            )

    def test_signed_foreign_incident_rejected(self):
        document = self.document()

        document["incident_id"] = (
            "incident-foreign-recovery"
        )

        message, signature = self.signed(
            document
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
            )

    def test_signed_wrong_authority_rejected(self):
        document = self.document()

        document["authority_id"] = (
            "untrusted_recovery_authority"
        )

        message, signature = self.signed(
            document
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
            )

    def test_stale_generation_and_invalid_floor_rejected(self):
        message, signature = self.signed()

        for floor in (
            GENERATION,
            GENERATION + 1,
            True,
            -1,
            "7",
        ):
            with self.subTest(floor=floor):
                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        signature,
                        floor=floor,
                    )

    def test_signed_malformed_or_noncanonical_messages_rejected(self):
        document = self.document()

        original = canonical_bytes(
            document
        )

        marker = b'"schema_version":1'

        self.assertEqual(
            original.count(marker),
            1,
        )

        duplicate_key = original.replace(
            marker,
            (
                b'"schema_version":1,'
                b'"schema_version":1'
            ),
            1,
        )

        with_extra = self.document()
        with_extra["unexpected"] = "injected"

        bool_generation = self.document()
        bool_generation["generation"] = True

        invalid_messages = (
            duplicate_key,
            canonical_bytes(with_extra),
            canonical_bytes(bool_generation),
            b"{ " + original[1:],
        )

        for message in invalid_messages:
            signature = self.private_key.sign(
                message
            )

            with self.subTest(
                message=repr(message[:45])
            ):
                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        signature,
                    )

    def test_signed_message_cannot_bind_altered_projection(self):
        original_message, original_signature = (
            self.signed()
        )

        forged_payload = (
            self.evidence.to_dict()
        )

        forged_payload["manifestation"][
            "quantum_tick"
        ] += 1

        forged_payload["projection_sha256"] = (
            projection_digest(forged_payload)
        )

        forged_evidence = (
            CanonicalSecurityPublicationEvidence
            .parse_untrusted(forged_payload)
        )

        self.assertFalse(
            forged_evidence.is_authoritative
        )

        self.assertFalse(
            forged_evidence.is_restorable
        )

        with self.assertRaises(ValueError):
            self.verify(
                original_message,
                original_signature,
                evidence=forged_evidence,
            )

        self.assertTrue(
            self.evidence.verify_live(
                self.world
            )
        )

    def test_valid_signature_cannot_restore_empty_universe(self):
        message, signature = self.signed()

        verified = self.verify(
            message,
            signature,
        )

        with redirect_stdout(io.StringIO()):
            fresh = Universe(
                universe_id=WORLD
            )

        self.assertEqual(
            len(fresh.cronenbergs),
            0,
        )

        self.assertEqual(
            len(fresh.entities),
            0,
        )

        self.assertEqual(
            len(fresh.quantum_events),
            0,
        )

        with self.assertRaises(ValueError):
            self.evidence.verify_live(
                fresh
            )

        self.assertTrue(
            verified.signature_verified
        )

        self.assertFalse(
            verified.is_authoritative
        )

        self.assertFalse(
            verified.is_restorable
        )

        self.assertFalse(
            verified.can_republish
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
