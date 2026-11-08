"""Regression tests for opt-in Ed25519 symbolic replay witnesses.

Private keys are generated only for ephemeral test fixtures.
The authenticated adapter does not claim to prove freshness, or that
a signer really persisted its signed response.
"""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from universe.symbolic_replay_receipt_witness import (
    SymbolicReplayReceiptWitness,
)
from universe.symbolic_replay_witness_authority import (
    SymbolicReplayWitnessAuthority,
    SymbolicReplayWitnessRevision,
)

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )
    from universe.symbolic_replay_authenticated_witness import (
        AuthenticatedSymbolicReplayWitnessAuthority,
        SignedSymbolicReplayWitnessRevision,
        SignedSymbolicReplayWitnessSource,
        witness_key_id,
        witness_signature_payload,
    )
except ImportError:
    _HAS_ED25519 = False
else:
    _HAS_ED25519 = True


if _HAS_ED25519:
    class MemorySignedSource(SignedSymbolicReplayWitnessSource):
        """In-memory signed test source; never a trusted service."""

        def __init__(self, private_key, initial):
            self.private_key = private_key
            self.key_id = witness_key_id(
                private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            )
            self.current = initial
            self.read_override = None
            self.publish_override = None
            self.fake_success = False
            self.reads = 0
            self.publications = 0

        def sign(self, revision):
            return SignedSymbolicReplayWitnessRevision(
                revision=revision,
                key_id=self.key_id,
                signature=self.private_key.sign(
                    witness_signature_payload(revision, self.key_id)
                ),
            )

        def read_current(self, *, universe_id, batch_sha256):
            self.reads += 1
            if self.read_override is not None:
                return self.read_override
            return self.sign(self.current)

        def publish(self, witness, *, expected_revision):
            self.publications += 1
            if self.publish_override is not None:
                return self.publish_override

            proposed = self.transition(
                self.current,
                witness,
                expected_revision=expected_revision,
            )
            if not self.fake_success:
                self.current = proposed
            return self.sign(proposed)

        transition = staticmethod(
            SymbolicReplayWitnessAuthority.transition
        )


@unittest.skipUnless(
    _HAS_ED25519,
    "Optional A33 cryptography dependency is not installed.",
)
class AuthenticatedWitnessTests(unittest.TestCase):

    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.witness = SymbolicReplayReceiptWitness(
            universe_id="a33_universe",
            batch_sha256="a" * 64,
            receipt_ids=(),
        )
        self.initial = SymbolicReplayWitnessRevision(
            revision=0,
            witness=self.witness,
        )
        self.source = MemorySignedSource(
            self.private, self.initial,
        )
        self.floor = self.source.sign(self.initial)

    def authority(self, *, source=None, floor=None, key=None):
        return AuthenticatedSymbolicReplayWitnessAuthority(
            self.source if source is None else source,
            public_key_bytes=self.public if key is None else key,
            trusted_signed_floor=self.floor if floor is None else floor,
        )

    def next_witness(self, ids=("receipt_1",)):
        return SymbolicReplayReceiptWitness(
            universe_id=self.witness.universe_id,
            batch_sha256=self.witness.batch_sha256,
            receipt_ids=ids,
        )

    def test_valid_signed_read_and_cas_publication(self):
        authority = self.authority()
        self.assertIsInstance(
            authority, SymbolicReplayWitnessAuthority,
        )
        self.assertEqual(
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            ),
            self.initial,
        )
        updated = authority.publish(
            self.next_witness(),
            expected_revision=0,
        )
        self.assertEqual(updated.revision, 1)
        self.assertEqual(updated.witness.receipt_ids, ("receipt_1",))
        self.assertEqual(self.source.current, updated)
        self.assertGreater(self.source.reads, 0)

    def test_missing_signed_floor_rejected(self):
        with self.assertRaisesRegex(
            TypeError, "Signed witness evidence must be canonical"
        ):
            AuthenticatedSymbolicReplayWitnessAuthority(
                self.source,
                public_key_bytes=self.public,
                trusted_signed_floor=None,
            )

    def test_invalid_public_key_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "32 bytes"
        ):
            self.authority(key=b"wrong")

    def test_different_signing_key_rejected(self):
        other = Ed25519PrivateKey.generate()
        other_key = other.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        with self.assertRaisesRegex(
            ValueError, "key mismatch"
        ):
            self.authority(key=other_key)

    def test_tampered_signature_rejected(self):
        authority = self.authority()
        original = self.source.sign(self.initial)
        invalid = SignedSymbolicReplayWitnessRevision(
            revision=original.revision,
            key_id=original.key_id,
            signature=bytes([original.signature[0] ^ 1])
            + original.signature[1:],
        )
        self.source.read_override = invalid

        with self.assertRaisesRegex(
            ValueError, "signature verification failed"
        ):
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            )

    def test_tampered_revision_payload_rejected(self):
        authority = self.authority()
        valid = self.source.sign(self.initial)
        tampered = SignedSymbolicReplayWitnessRevision(
            revision=SymbolicReplayWitnessRevision(
                revision=1,
                witness=self.next_witness(),
            ),
            key_id=valid.key_id,
            signature=valid.signature,
        )
        self.source.read_override = tampered

        with self.assertRaisesRegex(
            ValueError, "signature verification failed"
        ):
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            )

    def test_unsigned_canonical_response_rejected(self):
        authority = self.authority()
        self.source.read_override = self.initial

        with self.assertRaisesRegex(
            TypeError, "Signed witness evidence must be canonical"
        ):
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            )

    def test_wrong_scope_signed_response_rejected(self):
        authority = self.authority()
        foreign = SymbolicReplayWitnessRevision(
            revision=1,
            witness=SymbolicReplayReceiptWitness(
                universe_id="foreign",
                batch_sha256="a" * 64,
                receipt_ids=(),
            ),
        )
        self.source.read_override = self.source.sign(foreign)

        with self.assertRaisesRegex(
            ValueError, "scope mismatch"
        ):
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            )

    def test_stale_valid_signature_below_signed_floor_rejected(self):
        advanced = SymbolicReplayWitnessRevision(
            revision=1,
            witness=self.next_witness(),
        )
        authority = self.authority(
            floor=self.source.sign(advanced),
        )

        with self.assertRaisesRegex(
            ValueError, "below trusted floor"
        ):
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            )

    def test_signed_floor_receipt_revocation_rejected(self):
        advanced = SymbolicReplayWitnessRevision(
            revision=1,
            witness=self.next_witness(),
        )
        authority = self.authority(
            floor=self.source.sign(advanced),
        )
        # The response has the same revision but removes a receipt.
        self.source.current = SymbolicReplayWitnessRevision(
            revision=1,
            witness=self.witness,
        )

        with self.assertRaisesRegex(
            ValueError, "contradicts trusted floor"
        ):
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            )

    def test_wrong_scope_signed_floor_rejected_on_read(self):
        foreign = SymbolicReplayWitnessRevision(
            revision=0,
            witness=SymbolicReplayReceiptWitness(
                universe_id="foreign",
                batch_sha256="a" * 64,
                receipt_ids=(),
            ),
        )
        authority = self.authority(
            floor=self.source.sign(foreign),
        )

        with self.assertRaisesRegex(
            ValueError, "Trusted witness floor scope mismatch"
        ):
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            )

    def test_unsigned_publish_response_rejected(self):
        authority = self.authority()
        self.source.publish_override = self.initial

        with self.assertRaisesRegex(
            TypeError, "Signed witness evidence must be canonical"
        ):
            authority.publish(
                self.next_witness(),
                expected_revision=0,
            )

    def test_signed_publish_without_receipt_rejected(self):
        authority = self.authority()
        self.source.publish_override = self.source.sign(self.initial)

        with self.assertRaisesRegex(
            ValueError, "publication not confirmed"
        ):
            authority.publish(
                self.next_witness(),
                expected_revision=0,
            )

    def test_wrong_scope_publication_stops_before_network(self):
        authority = self.authority()
        foreign = SymbolicReplayReceiptWitness(
            universe_id="foreign",
            batch_sha256="a" * 64,
            receipt_ids=("receipt_1",),
        )
        with self.assertRaisesRegex(
            ValueError, "Trusted witness floor scope mismatch"
        ):
            authority.publish(foreign, expected_revision=0)
        self.assertEqual(self.source.publications, 0)

    def test_signed_forgery_from_real_issuer_is_not_durability_proof(self):
        authority = self.authority()
        self.source.fake_success = True

        reported = authority.publish(
            self.next_witness(),
            expected_revision=0,
        )
        self.assertEqual(reported.revision, 1)
        self.assertEqual(self.source.current.revision, 0)

        # A31's caller-side read-back will see the unchanged
        # revision and reject ACK. This adapter makes no
        # guarantee about a dishonest holder of the real key.
        self.assertEqual(
            authority.read_current(
                universe_id="a33_universe",
                batch_sha256="a" * 64,
            ).revision,
            0,
        )

    def test_canonical_payload_is_domain_separated(self):
        expected = witness_signature_payload(
            self.initial, witness_key_id(self.public),
        )
        self.assertTrue(
            expected.startswith(
                b"adamshell:symbolic-replay:witness:ed25519:v1\x00"
            )
        )
        self.assertIn(b'"revision":0', expected)
        self.assertIn(b'"batch_sha256"', expected)


if __name__ == "__main__":
    unittest.main()
