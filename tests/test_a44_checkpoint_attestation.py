"""A44 pinned Cronenberg checkpoint attestation contract.

EXPECTED RED: checkpoint attestation verifier is absent.

Unlike the existing recovery-evidence attestation, the
new signed document MUST bind both:
  projection_sha256 and checkpoint_sha256.

The verifier authenticates message bytes against a configured
Ed25519 pinset and compares identities and digests with
strictly validated detached evidence and checkpoint objects.

Test fixture keys do NOT establish independently trusted
enrollment. A caller-provided generation floor does NOT
independently guarantee rollback protection.

Verification must not restore, republish, or mutate Universe.
"""

import dataclasses
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

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)

from core.existence.history_receipt_trust_cronenberg_checkpoint import (
    CanonicalCronenbergStateCheckpoint,
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
    "history_receipt_trust_checkpoint_attestation"
)

DOMAIN = (
    "AdamShell/A44/"
    "cronenberg-state-checkpoint-attestation/v1"
)

AUTHORITY = "checkpoint_authority_v1"
WORLD = "a44_669_checkpoint_attestation"
INCIDENT = "incident-checkpoint-attestation"
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


def rehash_checkpoint(payload):
    body = {
        key: value
        for key, value in payload.items()
        if key != "checkpoint_sha256"
    }

    payload["checkpoint_sha256"] = (
        hashlib.sha256(
            canonical_bytes(body)
        ).hexdigest()
    )

    return payload


class A44CheckpointAttestationContractTests(
    unittest.TestCase
):

    def setUp(self):
        implementation = importlib.import_module(
            MODULE
        )

        self.Verifier = (
            implementation.PinnedCronenbergCheckpointAttestationVerifier
        )

        self.Result = (
            implementation.VerifiedCronenbergCheckpointAttestation
        )

        temporary = tempfile.TemporaryDirectory(
            prefix="a44_669_checkpoint_attestation_"
        )

        self.addCleanup(temporary.cleanup)

        root = Path(temporary.name)

        outbox = LocalDurableSecurityIncidentOutbox.create(
            root / "incident.sqlite",
            max_pending=8,
            max_total=16,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id=WORLD
            )

            coordinator = SecurityIncidentCronenbergReconciler(
                universe=self.world,
                outbox=outbox,
            )

            with self.assertRaises(SecurityAttackDetected):
                coordinator.reject(
                    incident_id=INCIDENT,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "checkpoint attestation fixture"
                    ),
                )

        self.evidence = CanonicalSecurityPublicationEvidence.capture(
            universe=self.world,
            incident_id=INCIDENT,
            source_operation=OPERATION,
        )

        self.checkpoint = CanonicalCronenbergStateCheckpoint.capture(
            universe=self.world,
            incident_id=INCIDENT,
            source_operation=OPERATION,
        )

        self.assertTrue(
            self.evidence.verify_live(self.world)
        )

        self.assertTrue(
            self.checkpoint.verify_live(self.world)
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
            "universe_id": WORLD,
            "incident_id": INCIDENT,
            "source_operation": OPERATION,
            "cronenberg_id": self.evidence.cronenberg_id,
            "projection_sha256": self.evidence.projection_sha256,
            "checkpoint_sha256": self.checkpoint.checkpoint_sha256,
        }

    def signed(self, document=None, *, key=None):
        document = (
            self.document()
            if document is None
            else document
        )

        message = canonical_bytes(
            document
        )

        signing_key = (
            self.private_key
            if key is None
            else key
        )

        return message, signing_key.sign(message)

    def verify(
        self,
        message,
        signature,
        *,
        evidence=None,
        checkpoint=None,
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
            checkpoint=(
                self.checkpoint
                if checkpoint is None
                else checkpoint
            ),
            message=message,
            signature=signature,
            expected_authority_id=authority,
            expected_universe_id=world,
            expected_incident_id=incident,
            minimum_generation=floor,
        )

    def test_valid_signature_binds_both_digests(self):
        message, signature = self.signed()

        result = self.verify(
            message,
            signature,
        )

        self.assertIs(
            type(result),
            self.Result,
        )

        self.assertIs(
            result.signature_verified,
            True,
        )

        self.assertEqual(
            result.projection_sha256,
            self.evidence.projection_sha256,
        )

        self.assertEqual(
            result.checkpoint_sha256,
            self.checkpoint.checkpoint_sha256,
        )

        self.assertEqual(
            result.generation,
            GENERATION,
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
            result.source_operation,
            OPERATION,
        )

        self.assertEqual(
            result.cronenberg_id,
            self.evidence.cronenberg_id,
        )

        self.assertEqual(
            result.authority_id,
            AUTHORITY,
        )

    def test_later_checkpoint_cannot_reuse_earlier_signature(self):
        message, signature = self.signed()

        entity = self.world.cronenbergs[0]

        entity.energy += 3.5
        entity.metabolism.pending_dark_energy += 2.0

        later_checkpoint = (
            CanonicalCronenbergStateCheckpoint.capture(
                universe=self.world,
                incident_id=INCIDENT,
                source_operation=OPERATION,
            )
        )

        self.assertEqual(
            later_checkpoint.projection_sha256,
            self.checkpoint.projection_sha256,
        )

        self.assertNotEqual(
            later_checkpoint.checkpoint_sha256,
            self.checkpoint.checkpoint_sha256,
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
                checkpoint=later_checkpoint,
            )

        self.assertTrue(
            self.verify(
                message,
                signature,
            ).signature_verified
        )

    def test_rehashed_checkpoint_forgery_rejected(self):
        message, signature = self.signed()

        forged = self.checkpoint.to_dict()
        forged["entity_state"]["energy"] += 11.0

        parsed = (
            CanonicalCronenbergStateCheckpoint.parse_untrusted(
                rehash_checkpoint(forged)
            )
        )

        self.assertNotEqual(
            parsed.checkpoint_sha256,
            self.checkpoint.checkpoint_sha256,
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
                checkpoint=parsed,
            )

    def test_rebound_checkpoint_projection_rejected(self):
        message, signature = self.signed()

        forged = self.checkpoint.to_dict()

        forged["projection_sha256"] = (
            "a" * 64
            if self.evidence.projection_sha256 != "a" * 64
            else "b" * 64
        )

        parsed = (
            CanonicalCronenbergStateCheckpoint.parse_untrusted(
                rehash_checkpoint(forged)
            )
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
                checkpoint=parsed,
            )

    def test_signed_digests_must_match_both_objects(self):
        for field in (
            "projection_sha256",
            "checkpoint_sha256",
        ):
            with self.subTest(digest=field):
                document = self.document()

                document[field] = (
                    "a" * 64
                    if document[field] != "a" * 64
                    else "b" * 64
                )

                message, signature = self.signed(
                    document
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        signature,
                    )

    def test_signed_identity_mismatches_rejected(self):
        replacements = {
            "authority_id": "foreign_checkpoint_authority",
            "universe_id": "foreign_checkpoint_world",
            "incident_id": "incident-foreign-checkpoint",
            "source_operation": "receipt_signature",
            "cronenberg_id": "cronenberg_00000000",
        }

        for name, replacement in replacements.items():
            with self.subTest(identity=name):
                document = self.document()
                document[name] = replacement

                message, signature = self.signed(
                    document
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        signature,
                    )

    def test_unpinned_signer_and_malformed_signature_rejected(self):
        message, signature = self.signed()

        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.verify(
                message,
                attacker.sign(message),
            )

        damaged = bytearray(
            signature
        )

        damaged[0] ^= 1

        invalid_signatures = (
            bytes(damaged),
            signature[:-1],
            b"",
            "not-bytes",
            bytearray(signature),
        )

        for invalid in invalid_signatures:
            with self.subTest(type=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        invalid,
                    )

    def test_pinset_is_detached_and_strict(self):
        pins = {
            AUTHORITY: self.public_key,
        }

        verifier = self.Verifier.from_pinned_keys(
            pins
        )

        pins.clear()

        message, signature = self.signed()

        self.assertTrue(
            self.verify(
                message,
                signature,
                verifier=verifier,
            ).signature_verified
        )

        invalid_pinsets = (
            {},
            {AUTHORITY: b"x" * 31},
            {AUTHORITY: "not-raw-key"},
            {AUTHORITY: bytearray(self.public_key)},
            {"": self.public_key},
        )

        for invalid in invalid_pinsets:
            with self.subTest(pinset=str(invalid)[:50]):
                with self.assertRaises(ValueError):
                    self.Verifier.from_pinned_keys(
                        invalid
                    )

    def test_domain_version_and_document_shape_rejected(self):
        variants = []

        wrong_domain = self.document()
        wrong_domain["domain"] = (
            "AdamShell/A44/"
            "recovery-evidence-attestation/v1"
        )

        variants.append(wrong_domain)

        wrong_version = self.document()
        wrong_version["schema_version"] = 2

        variants.append(wrong_version)

        unexpected = self.document()
        unexpected["unexpected"] = True

        variants.append(unexpected)

        missing_checkpoint_digest = self.document()
        del missing_checkpoint_digest["checkpoint_sha256"]

        variants.append(missing_checkpoint_digest)

        for document in variants:
            with self.subTest(
                fields=tuple(sorted(document))
            ):
                message, signature = self.signed(
                    document
                )

                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        signature,
                    )

    def test_noncanonical_and_duplicate_json_rejected(self):
        document = self.document()

        pretty_message = json.dumps(
            document,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        ).encode("utf-8")

        duplicated_message = canonical_bytes(
            document
        ).replace(
            b'"authority_id":',
            b'"authority_id":"duplicate","authority_id":',
            1,
        )

        for message in (
            pretty_message,
            duplicated_message,
        ):
            with self.subTest(length=len(message)):
                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        self.private_key.sign(message),
                    )

    def test_generation_floor_is_exclusive_and_strict(self):
        message, signature = self.signed()

        self.assertEqual(
            self.verify(
                message,
                signature,
                floor=GENERATION - 1,
            ).generation,
            GENERATION,
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
                floor=GENERATION,
            )

        for invalid in (
            -1,
            True,
            1.5,
            "7",
        ):
            with self.subTest(floor=invalid):
                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        signature,
                        floor=invalid,
                    )

        # Caller-selected floors are not trusted
        # monotonic state by themselves.
        self.assertEqual(
            self.verify(
                message,
                signature,
                floor=0,
            ).generation,
            GENERATION,
        )

    def test_verified_result_is_non_authoritative_and_no_mutation(self):
        before = (
            len(self.world.entities),
            len(self.world.cronenbergs),
            len(self.world.quantum_events),
        )

        message, signature = self.signed()

        result = self.verify(
            message,
            signature,
        )

        after = (
            len(self.world.entities),
            len(self.world.cronenbergs),
            len(self.world.quantum_events),
        )

        self.assertEqual(
            before,
            after,
        )

        self.assertTrue(
            dataclasses.is_dataclass(result)
        )

        self.assertTrue(
            type(result).__dataclass_params__.frozen
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

        fields = {
            item.name: item
            for item in dataclasses.fields(result)
        }

        for name in (
            "is_authoritative",
            "is_restorable",
            "can_republish",
        ):
            with self.subTest(field=name):
                self.assertIs(
                    fields[name].default,
                    False,
                )

                self.assertFalse(
                    fields[name].init
                )

        with self.assertRaises(
            dataclasses.FrozenInstanceError
        ):
            result.generation = 999

        for name in (
            "restore",
            "republish",
            "authorize",
        ):
            self.assertFalse(
                hasattr(result, name)
            )


if __name__ == "__main__":
    unittest.main()
