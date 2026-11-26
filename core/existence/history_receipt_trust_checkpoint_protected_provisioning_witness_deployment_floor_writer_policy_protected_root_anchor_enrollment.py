"""Pinned protected root anchor enrollment.

Enrollment must originate from independently trusted deployment
configuration. Transport-provided keys are not implicitly trusted.

A verified proof authenticates its exact enrollment fingerprint,
challenge and protected root reference.

This module does not establish remote execution honesty, live
fencing, CAS linearizability, durability or rollback resistance."""


import hashlib
import json

from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root import (
    ProtectedDeploymentIdentity,
    ProtectedRootReference,
)


ENROLLMENT_DOMAIN = (
    "AdamShell/A44/protected-root-anchor-enrollment/v1"
)

PROOF_DOMAIN = (
    "AdamShell/A44/protected-root-anchor-enrollment-proof/v1"
)

_MAX_ENROLLMENT_EPOCH = (1 << 63) - 1


def _canonical_json(value):
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


@dataclass(frozen=True, slots=True)
class PinnedProtectedRootAnchorEnrollment:
    """Independently trusted immutable anchor enrollment."""

    identity: ProtectedDeploymentIdentity
    anchor_id: str
    anchor_public_key: bytes
    enrollment_epoch: int

    def __post_init__(self):
        if type(self.identity) is not ProtectedDeploymentIdentity:
            raise ValueError(
                "Canonical protected deployment identity required."
            )

        if (
            type(self.anchor_id) is not str
            or not self.anchor_id.strip()
        ):
            raise ValueError(
                "Nonempty anchor identity required."
            )

        if (
            type(self.anchor_public_key) is not bytes
            or len(self.anchor_public_key) != 32
        ):
            raise ValueError(
                "Canonical 32-byte Ed25519 public key required."
            )

        if (
            type(self.enrollment_epoch) is not int
            or not 1 <= self.enrollment_epoch <= _MAX_ENROLLMENT_EPOCH
        ):
            raise ValueError(
                "Invalid enrollment epoch."
            )

        Ed25519PublicKey.from_public_bytes(
            self.anchor_public_key
        )

    def fingerprint(self) -> str:
        """Return the canonical enrollment SHA-256 fingerprint."""

        identity = self.identity

        payload = [
            ENROLLMENT_DOMAIN,
            self.anchor_id,
            self.anchor_public_key.hex(),
            self.enrollment_epoch,
            identity.deployment_id,
            identity.configuration_sha256,
            identity.provisioning_nonce.hex(),
        ]

        return hashlib.sha256(
            _canonical_json(payload)
        ).hexdigest()

    def verify_proof(
        self,
        *,
        challenge: bytes,
        state_reference: ProtectedRootReference,
        signature: bytes,
    ) -> ProtectedRootReference:
        """Authenticate the exact challenge and root reference."""

        if (
            type(challenge) is not bytes
            or len(challenge) != 32
        ):
            raise ValueError(
                "Canonical 32-byte challenge required."
            )

        if type(state_reference) is not ProtectedRootReference:
            raise ValueError(
                "Canonical protected root reference required."
            )

        if (
            type(signature) is not bytes
            or len(signature) != 64
        ):
            raise ValueError(
                "Canonical 64-byte Ed25519 signature required."
            )

        message = _canonical_json(
            [
                PROOF_DOMAIN,
                self.fingerprint(),
                challenge.hex(),
                state_reference.revision,
                state_reference.sha256,
            ]
        )

        public_key = Ed25519PublicKey.from_public_bytes(
            self.anchor_public_key
        )

        try:
            public_key.verify(
                signature,
                message,
            )
        except InvalidSignature as exc:
            raise ValueError(
                "Invalid pinned protected root anchor proof."
            ) from exc

        return state_reference
