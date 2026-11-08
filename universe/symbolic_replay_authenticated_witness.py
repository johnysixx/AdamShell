"""Opt-in Ed25519 authentication of symbolic replay witness evidence.

A caller must pin a genuine public key and retain an independently
obtained, signed revision floor outside the local rollback domain.

Signatures authenticate origin/integrity, not freshness or durability.
The remote service must still provide linearizable reads and durable CAS.
This module does not store, generate, or receive private signing keys.
"""

import hashlib
import json
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from universe.symbolic_replay_receipt_witness import (
    SymbolicReplayReceiptWitness,
)
from universe.symbolic_replay_witness_authority import (
    SymbolicReplayWitnessAuthority,
    SymbolicReplayWitnessRevision,
    enforce_trusted_floor,
)


_SIGNATURE_DOMAIN = b"adamshell:symbolic-replay:witness:ed25519:v1\x00"


def witness_key_id(public_key_bytes):
    """Fingerprint of a pinned Ed25519 raw public key."""
    if type(public_key_bytes) is not bytes or len(public_key_bytes) != 32:
        raise ValueError("Ed25519 public key must contain 32 bytes.")

    return hashlib.sha256(public_key_bytes).hexdigest()


def witness_signature_payload(revision, key_id):
    """Deterministic, domain-separated bytes for a signed revision."""
    if type(revision) is not SymbolicReplayWitnessRevision:
        raise TypeError("Signed witness revision must be canonical.")

    if (
        type(key_id) is not str
        or len(key_id) != 64
        or any(char not in "0123456789abcdef" for char in key_id)
    ):
        raise ValueError("Invalid witness signing key ID.")

    witness = revision.witness
    payload = {
        "format": "adamshell.symbolic_replay_signed_witness",
        "version": 1,
        "algorithm": "Ed25519",
        "key_id": key_id,
        "revision": revision.revision,
        "witness": {
            "universe_id": witness.universe_id,
            "batch_sha256": witness.batch_sha256,
            "receipt_ids": list(witness.receipt_ids),
        },
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return _SIGNATURE_DOMAIN + canonical


@dataclass(frozen=True, slots=True)
class SignedSymbolicReplayWitnessRevision:
    revision: SymbolicReplayWitnessRevision
    key_id: str
    signature: bytes

    def __post_init__(self):
        if type(self.revision) is not SymbolicReplayWitnessRevision:
            raise TypeError("Signed witness requires canonical revision.")

        if (
            type(self.key_id) is not str
            or len(self.key_id) != 64
            or any(char not in "0123456789abcdef" for char in self.key_id)
        ):
            raise ValueError("Invalid signed witness key ID.")

        if type(self.signature) is not bytes or len(self.signature) != 64:
            raise ValueError("Invalid Ed25519 witness signature.")


class SignedSymbolicReplayWitnessSource:
    """Untrusted transport interface for signed authority responses.

    Implementations must supply durable compare-and-swap publication and
    current linearizable reads. This interface does not implement either.
    """

    def read_current(self, *, universe_id, batch_sha256):
        raise NotImplementedError

    def publish(self, witness, *, expected_revision):
        raise NotImplementedError


class AuthenticatedSymbolicReplayWitnessAuthority(
    SymbolicReplayWitnessAuthority
):
    """Verify every response with one pinned issuer public key.

    An independently retained signed floor is mandatory. The adapter
    exposes only verified canonical revisions to existing A28-A32 APIs.
    """

    def __init__(
        self,
        source,
        *,
        public_key_bytes,
        trusted_signed_floor,
    ):
        if not isinstance(source, SignedSymbolicReplayWitnessSource):
            raise TypeError("Authenticated authority requires signed source.")

        self.key_id = witness_key_id(public_key_bytes)
        self._public_key = Ed25519PublicKey.from_public_bytes(
            public_key_bytes
        )
        self._source = source
        self.trusted_floor = self._verify(trusted_signed_floor)

    def _verify(self, signed):
        if type(signed) is not SignedSymbolicReplayWitnessRevision:
            raise TypeError("Signed witness evidence must be canonical.")

        if signed.key_id != self.key_id:
            raise ValueError("Witness signing key mismatch.")

        payload = witness_signature_payload(
            signed.revision, signed.key_id
        )

        try:
            self._public_key.verify(signed.signature, payload)
        except InvalidSignature as error:
            raise ValueError(
                "Witness signature verification failed."
            ) from error

        return signed.revision

    def _trusted(self, signed, *, universe_id, batch_sha256):
        current = self._verify(signed)
        enforce_trusted_floor(
            current,
            self.trusted_floor,
            universe_id=universe_id,
            batch_sha256=batch_sha256,
        )
        return current

    def read_current(self, *, universe_id, batch_sha256):
        signed = self._source.read_current(
            universe_id=universe_id,
            batch_sha256=batch_sha256,
        )
        return self._trusted(
            signed,
            universe_id=universe_id,
            batch_sha256=batch_sha256,
        )

    def publish(self, witness, *, expected_revision):
        if type(witness) is not SymbolicReplayReceiptWitness:
            raise TypeError("Proposed witness must be canonical.")
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("Invalid expected witness revision.")

        # Reject a wrong scope before invoking the external service.
        enforce_trusted_floor(
            SymbolicReplayWitnessRevision(expected_revision, witness),
            self.trusted_floor,
            universe_id=witness.universe_id,
            batch_sha256=witness.batch_sha256,
        )

        signed = self._source.publish(
            witness, expected_revision=expected_revision
        )
        result = self._trusted(
            signed,
            universe_id=witness.universe_id,
            batch_sha256=witness.batch_sha256,
        )

        # A canonical signature alone is not proof of a successful CAS.
        if (
            result.revision not in (
                expected_revision,
                expected_revision + 1,
            )
            or not set(witness.receipt_ids).issubset(
                result.witness.receipt_ids
            )
            or (
                result.revision == expected_revision
                and result.witness != witness
            )
        ):
            raise ValueError(
                "Signed witness publication not confirmed."
            )

        return result
