"""A44 adversarial checkpoint attestation tests.

Tests distinguish cryptographic signed-byte consistency
from externally established trust in authority enrollment,
generation freshness, or historical Universe publication.

No test authorizes entity restoration or republication.
All signing keys are ephemeral test fixtures.
"""

import dataclasses
import hashlib
import io
import json
import subprocess
import sys
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
from core.existence.history_receipt_trust_checkpoint_attestation import (
    PinnedCronenbergCheckpointAttestationVerifier,
    VerifiedCronenbergCheckpointAttestation,
)
from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergReconciler,
)
from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)
from universe.universe import Universe


WORLD = "a44_669_checkpoint_attestation_adversarial"
INCIDENT = "incident-checkpoint-attestation-adversarial"
OPERATION = "security_validation"
AUTHORITY = "checkpoint_authority_v1"

DOMAIN = (
    "AdamShell/A44/"
    "cronenberg-state-checkpoint-attestation/v1"
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


def rehash(payload):
    body = {
        key: value
        for key, value in payload.items()
        if key != "checkpoint_sha256"
    }
    payload["checkpoint_sha256"] = hashlib.sha256(
        canonical_bytes(body)
    ).hexdigest()
    return payload


CHILD = r"""
import io
import json
import sys

from contextlib import redirect_stdout
from pathlib import Path

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)
from core.existence.history_receipt_trust_cronenberg_checkpoint import (
    CanonicalCronenbergStateCheckpoint,
)
from core.existence.history_receipt_trust_checkpoint_attestation import (
    PinnedCronenbergCheckpointAttestationVerifier,
)
from universe.universe import Universe

root = Path(sys.argv[1])

evidence = CanonicalSecurityPublicationEvidence.parse_untrusted(
    json.loads((root / "evidence.json").read_text(encoding="utf-8"))
)
checkpoint = CanonicalCronenbergStateCheckpoint.parse_untrusted(
    json.loads((root / "checkpoint.json").read_text(encoding="utf-8"))
)

verifier = PinnedCronenbergCheckpointAttestationVerifier.from_pinned_keys({
    "checkpoint_authority_v1": (root / "public.key").read_bytes(),
})

result = verifier.verify(
    evidence=evidence,
    checkpoint=checkpoint,
    message=(root / "message.bin").read_bytes(),
    signature=(root / "signature.bin").read_bytes(),
    expected_authority_id="checkpoint_authority_v1",
    expected_universe_id="a44_669_checkpoint_attestation_adversarial",
    expected_incident_id="incident-checkpoint-attestation-adversarial",
    minimum_generation=7,
)

with redirect_stdout(io.StringIO()):
    fresh = Universe(
        universe_id="a44_669_checkpoint_attestation_adversarial"
    )

denied = False
try:
    checkpoint.verify_live(fresh)
except ValueError:
    denied = True

assert denied
assert result.signature_verified is True
assert result.is_authoritative is False
assert result.is_restorable is False
assert result.can_republish is False
assert len(fresh.entities) == 0
assert len(fresh.cronenbergs) == 0
assert len(fresh.quantum_events) == 0

print(json.dumps({
    "signature_verified": result.signature_verified,
    "is_authoritative": result.is_authoritative,
    "is_restorable": result.is_restorable,
    "can_republish": result.can_republish,
    "missing_live_denied": denied,
    "entities": len(fresh.entities),
    "cronenbergs": len(fresh.cronenbergs),
    "events": len(fresh.quantum_events),
}))
"""


class A44CheckpointAttestationAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a44_669_checkpoint_attestation_attack_"
        )
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

        outbox = LocalDurableSecurityIncidentOutbox.create(
            self.root / "incident.sqlite",
            max_pending=8,
            max_total=16,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(
                universe_id=WORLD
            )
            reconciler = SecurityIncidentCronenbergReconciler(
                universe=self.world,
                outbox=outbox,
            )
            with self.assertRaises(SecurityAttackDetected):
                reconciler.reject(
                    incident_id=INCIDENT,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "checkpoint attestation attack fixture"
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

        self.key = Ed25519PrivateKey.generate()
        self.public = self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        self.Verifier = PinnedCronenbergCheckpointAttestationVerifier
        self.verifier = self.Verifier.from_pinned_keys({
            AUTHORITY: self.public,
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

    def signed(self, document=None, key=None):
        message = canonical_bytes(
            self.document() if document is None else document
        )
        signer = self.key if key is None else key
        return message, signer.sign(message)

    def verify(
        self,
        message,
        signature,
        *,
        checkpoint=None,
        verifier=None,
        floor=7,
    ):
        return (
            self.verifier if verifier is None else verifier
        ).verify(
            evidence=self.evidence,
            checkpoint=(
                self.checkpoint if checkpoint is None else checkpoint
            ),
            message=message,
            signature=signature,
            expected_authority_id=AUTHORITY,
            expected_universe_id=WORLD,
            expected_incident_id=INCIDENT,
            minimum_generation=floor,
        )

    def test_valid_attestation_never_mutates_universe(self):
        before = (
            len(self.world.entities),
            len(self.world.cronenbergs),
            len(self.world.quantum_events),
        )

        message, signature = self.signed()
        result = self.verify(message, signature)

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assertEqual(
            before,
            (
                len(self.world.entities),
                len(self.world.cronenbergs),
                len(self.world.quantum_events),
            ),
        )

    def test_unpinned_attacker_signature_rejected(self):
        message, _ = self.signed()
        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.verify(
                message,
                attacker.sign(message),
            )

    def test_corrupted_signature_rejected(self):
        message, signature = self.signed()

        corrupted = bytearray(signature)
        corrupted[0] ^= 1

        with self.assertRaises(ValueError):
            self.verify(message, bytes(corrupted))

    def test_modified_message_without_resigning_rejected(self):
        message, signature = self.signed()

        document = self.document()
        document["generation"] += 1

        changed_message = canonical_bytes(document)

        with self.assertRaises(ValueError):
            self.verify(changed_message, signature)

    def test_cross_domain_signed_message_rejected(self):
        document = self.document()
        document["domain"] = (
            "AdamShell/A44/"
            "recovery-evidence-attestation/v1"
        )
        message, signature = self.signed(document)

        with self.assertRaises(ValueError):
            self.verify(message, signature)

    def test_duplicate_and_extra_properties_rejected(self):
        standard = self.document()

        extra = dict(standard)
        extra["attacker_field"] = True

        ordinary_message = canonical_bytes(standard)
        duplicate_message = ordinary_message.replace(
            b'"authority_id":',
            b'"authority_id":"attacker","authority_id":',
            1,
        )

        for message in (
            canonical_bytes(extra),
            duplicate_message,
        ):
            with self.subTest(message_length=len(message)):
                with self.assertRaises(ValueError):
                    self.verify(
                        message,
                        self.key.sign(message),
                    )

    def test_old_signature_rejects_new_state_checkpoint(self):
        message, signature = self.signed()

        entity = self.world.cronenbergs[0]
        entity.energy += 4.0
        entity.metabolism.pending_dark_energy += 1.0

        newer = CanonicalCronenbergStateCheckpoint.capture(
            universe=self.world,
            incident_id=INCIDENT,
            source_operation=OPERATION,
        )

        self.assertEqual(
            newer.projection_sha256,
            self.checkpoint.projection_sha256,
        )
        self.assertNotEqual(
            newer.checkpoint_sha256,
            self.checkpoint.checkpoint_sha256,
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
                checkpoint=newer,
            )

        # New signed bytes can describe the newer state;
        # this alone does not attest historical truth.
        document = self.document()
        document["checkpoint_sha256"] = newer.checkpoint_sha256
        new_message, new_signature = self.signed(document)

        result = self.verify(
            new_message,
            new_signature,
            checkpoint=newer,
        )
        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)

    def test_rehashed_checkpoint_forgery_rejected(self):
        message, signature = self.signed()

        forged = self.checkpoint.to_dict()
        forged["entity_state"]["energy"] += 9.0

        parsed = CanonicalCronenbergStateCheckpoint.parse_untrusted(
            rehash(forged)
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
                checkpoint=parsed,
            )

        self.assertFalse(parsed.is_authoritative)

    def test_projection_rebinding_rejected(self):
        message, signature = self.signed()

        forged = self.checkpoint.to_dict()
        forged["projection_sha256"] = (
            "f" * 64
            if forged["projection_sha256"] != "f" * 64
            else "e" * 64
        )

        parsed = CanonicalCronenbergStateCheckpoint.parse_untrusted(
            rehash(forged)
        )

        with self.assertRaises(ValueError):
            self.verify(
                message,
                signature,
                checkpoint=parsed,
            )

    def test_signed_identity_and_digest_substitution_rejected(self):
        substitutions = {
            "universe_id": "foreign_checkpoint_world",
            "incident_id": "incident-foreign-checkpoint",
            "source_operation": "receipt_signature",
            "cronenberg_id": "cronenberg_00000000",
            "projection_sha256": "a" * 64,
            "checkpoint_sha256": "b" * 64,
        }

        for name, replacement in substitutions.items():
            document = self.document()
            if document[name] == replacement:
                replacement = "c" * 64

            document[name] = replacement
            message, signature = self.signed(document)

            with self.subTest(field=name):
                with self.assertRaises(ValueError):
                    self.verify(message, signature)

    def test_replay_floor_and_selected_pin_are_not_trust_roots(self):
        message, signature = self.signed()

        self.assertTrue(
            self.verify(message, signature, floor=7).signature_verified
        )

        with self.assertRaises(ValueError):
            self.verify(message, signature, floor=8)

        # An old caller-provided floor cannot independently
        # establish freshness; the result remains data only.
        old_floor = self.verify(message, signature, floor=0)
        self.assertFalse(old_floor.is_authoritative)

        attacker = Ed25519PrivateKey.generate()
        attacker_public = attacker.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        attacker_verifier = self.Verifier.from_pinned_keys({
            AUTHORITY: attacker_public,
        })

        attacker_result = self.verify(
            message,
            attacker.sign(message),
            verifier=attacker_verifier,
        )

        self.assertTrue(attacker_result.signature_verified)
        self.assertFalse(attacker_result.is_authoritative)

        # Even an explicitly constructed report is no
        # restoration authority or independent proof.
        synthetic = VerifiedCronenbergCheckpointAttestation(
            authority_id=AUTHORITY,
            generation=GENERATION,
            universe_id=WORLD,
            incident_id=INCIDENT,
            source_operation=OPERATION,
            cronenberg_id=self.evidence.cronenberg_id,
            projection_sha256=self.evidence.projection_sha256,
            checkpoint_sha256=self.checkpoint.checkpoint_sha256,
        )

        self.assertTrue(dataclasses.is_dataclass(synthetic))
        self.assertFalse(synthetic.is_authoritative)
        self.assertFalse(synthetic.is_restorable)
        self.assertFalse(synthetic.can_republish)

    def test_fresh_process_verification_never_restores(self):
        message, signature = self.signed()

        (self.root / "evidence.json").write_bytes(
            canonical_bytes(self.evidence.to_dict())
        )
        (self.root / "checkpoint.json").write_bytes(
            canonical_bytes(self.checkpoint.to_dict())
        )
        (self.root / "message.bin").write_bytes(message)
        (self.root / "signature.bin").write_bytes(signature)
        (self.root / "public.key").write_bytes(self.public)

        child = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                CHILD,
                str(self.root),
            ],
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            timeout=60,
        )

        self.assertEqual(
            child.returncode,
            0,
            msg=child.stdout + "\n" + child.stderr,
        )

        report = json.loads(child.stdout.strip())

        self.assertTrue(report["signature_verified"])
        self.assertFalse(report["is_authoritative"])
        self.assertFalse(report["is_restorable"])
        self.assertFalse(report["can_republish"])
        self.assertTrue(report["missing_live_denied"])
        self.assertEqual(report["entities"], 0)
        self.assertEqual(report["cronenbergs"], 0)
        self.assertEqual(report["events"], 0)


if __name__ == "__main__":
    unittest.main()
