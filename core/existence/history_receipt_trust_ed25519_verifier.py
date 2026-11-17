"""Experimental pinned Ed25519 authority reply verifier.

The verifier checks an Ed25519 signature over the
canonical version-1 authority reply payload.

The public-key catalog must be provisioned and protected
outside the attacker's control. Constructing this verifier
from attacker-supplied keys defeats its trust boundary.

This module implements no private-key management,
trusted key distribution, rotation, revocation,
persistent monotonic state, or distributed fencing.

It does not authorize receipt execution.
"""

from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from core.existence.history_receipt_trust_authority_evidence import (
    canonical_authority_reply_bytes,
)

from core.existence.history_receipt_trust_independent_authority_contract import (
    AuthorityAttestedReply,
    _require_identity,
)


@dataclass(frozen=True, slots=True)
class PinnedEd25519AuthorityVerifier:
    """Verifier configured with a detached pinned-key catalog.

    _pinned_keys contains immutable (authority_id, key_bytes)
    pairs. The factory validates and snapshots the input.

    Python object immutability is not a security boundary
    against malicious code running in the same process.
    """

    _pinned_keys: tuple[tuple[str, bytes], ...]

    @classmethod
    def from_pinned_keys(cls, keys):
        """Accept an explicitly provisioned nonempty pin catalog.

        Version 1 uses one 32-byte raw Ed25519 public key
        per authority identity. Key rotation and revocation
        require a separate trusted protocol.
        """

        if type(keys) is not dict or not keys:
            raise ValueError(
                "Expected a nonempty pinned-key dictionary."
            )

        validated = []

        for authority_id, raw_key in keys.items():
            _require_identity(
                authority_id,
                "pinned authority identity",
            )

            if (
                type(raw_key) is not bytes
                or len(raw_key) != 32
            ):
                raise ValueError(
                    "Pinned Ed25519 public key must be "
                    "exactly 32 immutable bytes."
                )

            try:
                Ed25519PublicKey.from_public_bytes(raw_key)
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    "Invalid pinned Ed25519 public key."
                ) from exc

            validated.append(
                (authority_id, bytes(raw_key))
            )

        # The caller may later mutate or clear the original
        # dictionary. Its changes must not alter this pinset.
        return cls(
            tuple(
                sorted(
                    validated,
                    key=lambda entry: entry[0],
                )
            )
        )

    def verify_attestation(self, reply):
        """Return exactly True or False.

        A reply is accepted only when:
        - its container type is correct;
        - its evidence is an exact 64-byte signature;
        - its authority identity exists in the pinset;
        - its semantic payload is structurally valid;
        - Ed25519 verification succeeds over canonical bytes.

        Missing keys, invalid evidence and backend errors
        fail closed. No alternative algorithm is attempted.

        A valid signature does NOT independently establish
        freshness, revocation status or trusted key origin.
        """

        if type(reply) is not AuthorityAttestedReply:
            return False

        if (
            type(reply.evidence) is not bytes
            or len(reply.evidence) != 64
        ):
            return False

        if type(reply.authority_id) is not str:
            return False

        pinned_key = None

        for authority_id, raw_key in self._pinned_keys:
            if authority_id == reply.authority_id:
                pinned_key = raw_key
                break

        if pinned_key is None:
            return False

        try:
            payload = canonical_authority_reply_bytes(
                reply
            )

            public_key = (
                Ed25519PublicKey.from_public_bytes(
                    pinned_key
                )
            )

            public_key.verify(
                reply.evidence,
                payload,
            )

        except Exception:
            # Fail closed for malformed data, signature
            # failures, and unavailable crypto operations.
            #
            # This does not replace operational logging
            # at a future authenticated authority boundary.
            return False

        return True
