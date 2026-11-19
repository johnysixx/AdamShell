"""A44 held checkpoint attestation trust contract.

EXPECTED RED: the held checkpoint trust gate is absent.

The test-only trust source exposes one tuple under hold():
    (authority_id, raw_ed25519_public_key, minimum_generation)

The gate must verify the complete signed checkpoint while the
hold context remains active. No caller-provided key or generation
floor may bypass that held snapshot.

The in-memory fixture is NOT an independently trusted provider.
A lock alone is not authentication, durability or rollback
protection. Verification never authorizes Universe restoration.
"""

import hashlib
import importlib
import io
import json
import tempfile
import unittest

from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from unittest.mock import patch

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
    "history_receipt_trust_checkpoint_held_gate"
)

WORLD = "a44_6610_checkpoint_held_trust"
INCIDENT = "incident-held-checkpoint"
OPERATION = "security_validation"
AUTHORITY = "checkpoint_authority_v1"
GENERATION = 8

DOMAIN = (
    "AdamShell/A44/"
    "cronenberg-state-checkpoint-attestation/v1"
)


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

    payload["checkpoint_sha256"] = hashlib.sha256(
        canonical_bytes(body)
    ).hexdigest()

    return payload


class MemoryHeldTrustSource:
    """Volatile and caller-controlled fixture, never a trust root."""

    def __init__(self, snapshot, *, failure=None):
        self.snapshot = snapshot
        self.failure = failure
        self.events = []
        self.active = False

    @contextmanager
    def hold(self):
        self.events.append("enter")

        if self.failure is not None:
            raise self.failure

        self.active = True

        try:
            yield self.snapshot
        finally:
            self.active = False
            self.events.append("exit")


class A44CheckpointHeldTrustContractTests(
    unittest.TestCase
):

    def setUp(self):
        gate_module = importlib.import_module(MODULE)

        self.held_verify = (
            gate_module.verify_checkpoint_attestation_with_held_trust
        )

        temporary = tempfile.TemporaryDirectory(
            prefix="a44_6610_held_checkpoint_"
        )
        self.addCleanup(temporary.cleanup)

        root = Path(temporary.name)

        outbox = LocalDurableSecurityIncidentOutbox.create(
            root / "incident.sqlite",
            max_pending=8,
            max_total=16,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(universe_id=WORLD)

            reconciler = SecurityIncidentCronenbergReconciler(
                universe=self.world,
                outbox=outbox,
            )

            with self.assertRaises(SecurityAttackDetected):
                reconciler.reject(
                    incident_id=INCIDENT,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "held checkpoint fixture"
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

        self.source = MemoryHeldTrustSource(
            (AUTHORITY, self.public, GENERATION - 1)
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
            "checkpoint_sha256": self.checkpoint.checkpoint_sha256,
        }

    def signed(self, document=None, *, key=None):
        message = canonical_bytes(
            self.document() if document is None else document
        )
        signer = self.key if key is None else key
        return message, signer.sign(message)

    def verify(
        self,
        source=None,
        *,
        message=None,
        signature=None,
        checkpoint=None,
    ):
        if message is None and signature is None:
            message, signature = self.signed()

        return self.held_verify(
            evidence=self.evidence,
            checkpoint=(
                self.checkpoint if checkpoint is None else checkpoint
            ),
            message=message,
            signature=signature,
            trusted_source=(
                self.source if source is None else source
            ),
            expected_authority_id=AUTHORITY,
            expected_universe_id=WORLD,
            expected_incident_id=INCIDENT,
        )

    def test_valid_held_snapshot_verifies_data_only(self):
        before = (
            len(self.world.entities),
            len(self.world.cronenbergs),
            len(self.world.quantum_events),
        )

        result = self.verify()

        self.assertTrue(result.signature_verified)
        self.assertEqual(result.authority_id, AUTHORITY)
        self.assertEqual(result.generation, GENERATION)
        self.assertEqual(
            result.checkpoint_sha256,
            self.checkpoint.checkpoint_sha256,
        )
        self.assertEqual(
            result.projection_sha256,
            self.evidence.projection_sha256,
        )

        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assertEqual(
            self.source.events,
            ["enter", "exit"],
        )
        self.assertFalse(self.source.active)

        self.assertEqual(
            before,
            (
                len(self.world.entities),
                len(self.world.cronenbergs),
                len(self.world.quantum_events),
            ),
        )

    def test_signature_verification_occurs_inside_held_lease(self):
        original_verify = (
            PinnedCronenbergCheckpointAttestationVerifier.verify
        )

        observations = []

        def guarded_verify(verifier_instance, **kwargs):
            observations.append(
                (
                    self.source.active,
                    tuple(self.source.events),
                    kwargs["minimum_generation"],
                )
            )

            if not self.source.active:
                raise AssertionError(
                    "Signature verifier ran outside held trust lease."
                )

            return original_verify(
                verifier_instance,
                **kwargs,
            )

        with patch.object(
            PinnedCronenbergCheckpointAttestationVerifier,
            "verify",
            new=guarded_verify,
        ):
            result = self.verify()

        self.assertTrue(result.signature_verified)
        self.assertEqual(
            observations,
            [(True, ("enter",), 7)],
        )
        self.assertEqual(
            self.source.events,
            ["enter", "exit"],
        )

    def test_missing_or_unusable_trust_source_rejected(self):
        class MissingHold:
            pass

        class InvalidHold:
            hold = None

        class NotAContextManager:
            def hold(self):
                return ("not", "a", "context-manager")

        for source in (
            None,
            object(),
            {},
            MissingHold(),
            InvalidHold(),
            NotAContextManager(),
        ):
            with self.subTest(source=type(source).__name__):
                # None explicitly denotes an absent source.
                if source is None:
                    with self.assertRaises(ValueError):
                        self.held_verify(
                            evidence=self.evidence,
                            checkpoint=self.checkpoint,
                            message=self.signed()[0],
                            signature=self.signed()[1],
                            trusted_source=None,
                            expected_authority_id=AUTHORITY,
                            expected_universe_id=WORLD,
                            expected_incident_id=INCIDENT,
                        )
                else:
                    with self.assertRaises(ValueError):
                        self.verify(source)

    def test_malformed_snapshot_shapes_rejected(self):
        for snapshot in (
            None,
            {},
            [],
            (),
            (AUTHORITY, self.public),
            (AUTHORITY, self.public, 7, "extra"),
            [AUTHORITY, self.public, 7],
            "not-a-snapshot",
        ):
            with self.subTest(snapshot=repr(snapshot)[:60]):
                source = MemoryHeldTrustSource(snapshot)

                with self.assertRaises(ValueError):
                    self.verify(source)

                self.assertEqual(
                    source.events,
                    ["enter", "exit"],
                )
                self.assertFalse(source.active)

    def test_invalid_or_foreign_authority_rejected(self):
        for authority in (
            "",
            None,
            True,
            " checkpoint_authority_v1",
            "foreign_checkpoint_authority",
        ):
            with self.subTest(authority=repr(authority)):
                source = MemoryHeldTrustSource(
                    (authority, self.public, 7)
                )

                with self.assertRaises(ValueError):
                    self.verify(source)

                self.assertFalse(source.active)

        document = self.document()
        document["authority_id"] = "foreign_checkpoint_authority"
        message, signature = self.signed(document)

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

    def test_invalid_key_type_or_length_rejected(self):
        for key in (
            None,
            "not-a-key",
            bytearray(self.public),
            self.public[:-1],
            b"",
        ):
            with self.subTest(type=type(key).__name__):
                source = MemoryHeldTrustSource(
                    (AUTHORITY, key, 7)
                )

                with self.assertRaises(ValueError):
                    self.verify(source)

                self.assertFalse(source.active)

    def test_invalid_generation_floor_rejected(self):
        for floor in (
            None,
            -1,
            True,
            False,
            7.0,
            "7",
        ):
            with self.subTest(floor=repr(floor)):
                source = MemoryHeldTrustSource(
                    (AUTHORITY, self.public, floor)
                )

                with self.assertRaises(ValueError):
                    self.verify(source)

                self.assertFalse(source.active)

    def test_stale_generation_rejected_by_held_floor(self):
        source = MemoryHeldTrustSource(
            (AUTHORITY, self.public, GENERATION)
        )

        with self.assertRaises(ValueError):
            self.verify(source)

        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )

        fresh = MemoryHeldTrustSource(
            (AUTHORITY, self.public, GENERATION - 1)
        )

        result = self.verify(fresh)
        self.assertEqual(result.generation, GENERATION)

    def test_wrong_signer_rejected_against_held_key(self):
        attacker = Ed25519PrivateKey.generate()

        message, signature = self.signed(
            key=attacker
        )

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
            )

        self.assertEqual(
            self.source.events,
            ["enter", "exit"],
        )
        self.assertFalse(self.source.active)

    def test_rehashed_checkpoint_substitution_rejected(self):
        message, signature = self.signed()

        payload = self.checkpoint.to_dict()
        payload["entity_state"]["energy"] += 5.0

        forged = CanonicalCronenbergStateCheckpoint.parse_untrusted(
            rehash_checkpoint(payload)
        )

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=signature,
                checkpoint=forged,
            )

        self.assertFalse(self.source.active)
        self.assertFalse(forged.is_authoritative)

    def test_lease_failure_and_bad_signature_release_trust(self):
        unavailable = MemoryHeldTrustSource(
            (AUTHORITY, self.public, 7),
            failure=OSError("Injected trust backend outage"),
        )

        with self.assertRaises(ValueError):
            self.verify(unavailable)

        self.assertFalse(unavailable.active)

        message, signature = self.signed()
        corrupted = bytearray(signature)
        corrupted[0] ^= 1

        source = MemoryHeldTrustSource(
            (AUTHORITY, self.public, 7)
        )

        with self.assertRaises(ValueError):
            self.verify(
                source,
                message=message,
                signature=bytes(corrupted),
            )

        self.assertEqual(source.events, ["enter", "exit"])
        self.assertFalse(source.active)

    def test_caller_selected_source_is_not_independent_trust(self):
        attacker = Ed25519PrivateKey.generate()

        attacker_public = attacker.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        message, _ = self.signed()
        attacker_signature = attacker.sign(message)

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=attacker_signature,
            )

        malicious_source = MemoryHeldTrustSource(
            (AUTHORITY, attacker_public, 0)
        )

        # A caller-controlled source can lie about both the
        # public key and the generation floor. This result
        # MUST NOT be represented as independent trust.
        result = self.verify(
            malicious_source,
            message=message,
            signature=attacker_signature,
        )

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assertEqual(
            malicious_source.events,
            ["enter", "exit"],
        )


if __name__ == "__main__":
    unittest.main()
