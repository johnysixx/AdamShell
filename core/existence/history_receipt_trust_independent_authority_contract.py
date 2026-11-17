"""Experimental independent-authority reply contract.

This module validates publication intent and the structure of
authority responses, then calls an injected attestation verifier.

It does NOT implement authentication, signature verification,
a trusted key store, a remote service, rollback protection,
linearizable CAS, or cross-process fencing.

A caller-provided verifier is NOT automatically trustworthy.
Generation and fencing thresholds must originate from an
independently trusted source to provide replay protection.

No receipt is authorized for execution by this module.
"""

import hmac

from dataclasses import dataclass
from enum import Enum

from core.existence.history_receipt_trust_publication_state import (
    _valid_snapshot,
)


class AuthorityReplyStatus(str, Enum):
    PREPARED = "prepared"
    COMMITTED = "committed"


def _require_identity(value, name):
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > 256
        or any(
            ord(character) < 32
            or ord(character) == 127
            for character in value
        )
    ):
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _require_snapshot(value, name):
    if (
        type(value) is not tuple
        or not _valid_snapshot(value)
    ):
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _require_integer(value, name, *, minimum):
    if (
        type(value) is not int
        or value < minimum
    ):
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _require_transition(predecessor, target):
    _require_snapshot(
        predecessor,
        "expected committed snapshot",
    )

    _require_snapshot(
        target,
        "target snapshot",
    )

    if target[0] <= predecessor[0]:
        raise ValueError(
            "Publication target must increase the revision."
        )

    if not hmac.compare_digest(
        predecessor[1],
        target[1],
    ):
        raise ValueError(
            "Pinned provider identities cannot change."
        )


@dataclass(frozen=True, slots=True)
class AuthorityPublicationIntent:
    """Identity and preconditions for one publication operation."""

    authority_id: str
    operation_id: str
    expected_committed: tuple
    target: tuple
    expected_generation: int
    fence_token: int

    def __post_init__(self):
        _require_identity(
            self.authority_id,
            "authority identity",
        )

        _require_identity(
            self.operation_id,
            "operation identity",
        )

        _require_transition(
            self.expected_committed,
            self.target,
        )

        _require_integer(
            self.expected_generation,
            "expected generation",
            minimum=0,
        )

        _require_integer(
            self.fence_token,
            "fencing token",
            minimum=1,
        )


@dataclass(frozen=True, slots=True)
class AuthorityAttestedReply:
    """Untrusted response container.

    Instances are deliberately constructible with invalid values,
    so that malformed transport responses can be tested. All
    fields must be validated before the reply is accepted.

    The evidence field is opaque. Its authenticity is NOT
    established merely by storing bytes here.
    """

    authority_id: str
    operation_id: str
    expected_committed: tuple
    target: tuple
    committed: tuple
    pending_operation_id: str | None
    status: AuthorityReplyStatus
    generation: int
    fence_token: int
    evidence: bytes


def require_attested_publication_reply(
    intent,
    reply,
    *,
    verifier,
    minimum_generation,
    minimum_fence_token,
):
    """Validate a reply and require verifier approval.

    Returns only the PREPARED or COMMITTED status. This is
    NOT a receipt authorization decision.

    minimum_generation is an EXCLUSIVE lower bound.
    minimum_fence_token is an INCLUSIVE lower bound.

    Supplying an untrusted verifier, identity, or generation
    floor defeats the corresponding security property.
    """

    if type(intent) is not AuthorityPublicationIntent:
        raise ValueError(
            "Invalid publication intent."
        )

    # Revalidate the frozen object at the boundary.
    # Python frozen dataclasses are not a security
    # boundary against malicious in-process code.
    intent.__post_init__()

    if type(reply) is not AuthorityAttestedReply:
        raise ValueError(
            "Invalid authority reply."
        )

    _require_integer(
        minimum_generation,
        "minimum trusted generation",
        minimum=0,
    )

    _require_integer(
        minimum_fence_token,
        "minimum trusted fencing token",
        minimum=1,
    )

    _require_identity(
        reply.authority_id,
        "reply authority identity",
    )

    _require_identity(
        reply.operation_id,
        "reply operation identity",
    )

    _require_snapshot(
        reply.expected_committed,
        "reply predecessor",
    )

    _require_snapshot(
        reply.target,
        "reply target",
    )

    _require_snapshot(
        reply.committed,
        "reply committed snapshot",
    )

    if reply.authority_id != intent.authority_id:
        raise ValueError(
            "Authority identity mismatch."
        )

    if reply.operation_id != intent.operation_id:
        raise ValueError(
            "Publication operation identity mismatch."
        )

    if reply.expected_committed != intent.expected_committed:
        raise ValueError(
            "Publication predecessor mismatch."
        )

    if reply.target != intent.target:
        raise ValueError(
            "Publication target mismatch."
        )

    if type(reply.status) is not AuthorityReplyStatus:
        raise ValueError(
            "Invalid authority reply status."
        )

    _require_integer(
        reply.generation,
        "reply generation",
        minimum=0,
    )

    if (
        reply.generation <= intent.expected_generation
        or reply.generation <= minimum_generation
    ):
        raise ValueError(
            "Stale authority generation."
        )

    _require_integer(
        reply.fence_token,
        "reply fencing token",
        minimum=1,
    )

    if (
        reply.fence_token != intent.fence_token
        or reply.fence_token < minimum_fence_token
    ):
        raise ValueError(
            "Publication fencing token mismatch."
        )

    if (
        type(reply.evidence) is not bytes
        or not reply.evidence
    ):
        raise ValueError(
            "Missing or invalid attestation evidence."
        )

    if reply.status is AuthorityReplyStatus.PREPARED:
        if reply.committed != intent.expected_committed:
            raise ValueError(
                "PREPARED reply changed committed catalog."
            )

        if reply.pending_operation_id != intent.operation_id:
            raise ValueError(
                "PREPARED reply does not bind pending operation."
            )

    elif reply.status is AuthorityReplyStatus.COMMITTED:
        if reply.committed != intent.target:
            raise ValueError(
                "COMMITTED reply does not match target."
            )

        if reply.pending_operation_id is not None:
            raise ValueError(
                "COMMITTED reply still contains pending operation."
            )

    else:
        raise ValueError(
            "Unsupported publication reply status."
        )

    try:
        verify = getattr(
            verifier,
            "verify_attestation",
            None,
        )

        if not callable(verify):
            raise ValueError(
                "Attestation verifier is unavailable."
            )

        verified = verify(reply)

    except Exception as exc:
        raise ValueError(
            "Authority attestation verification failed."
        ) from exc

    # Require an actual boolean True; a truthy object
    # or string is not sufficient.
    if verified is not True:
        raise ValueError(
            "Authority attestation was not verified."
        )

    return reply.status
