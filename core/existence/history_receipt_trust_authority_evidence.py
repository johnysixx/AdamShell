"""Versioned canonical payload for authority reply evidence.

This module encodes the complete semantic content of an
authority publication reply into deterministic ASCII bytes.

It does NOT sign or authenticate the resulting bytes.

The opaque `evidence` field is deliberately excluded to
avoid including a signature within its own signed message.

Future implementations must bind signatures to these bytes
and validate keys against an independently trusted root.

No authorization, rollback protection, distributed fencing
or network trust is implemented here.
"""

import json

from core.existence.history_receipt_trust_independent_authority_contract import (
    AuthorityAttestedReply,
    AuthorityReplyStatus,
    _require_identity,
    _require_integer,
    _require_snapshot,
    _require_transition,
)


AUTHORITY_REPLY_DOMAIN = (
    "adam-shell.receipt-trust.authority-reply"
)

AUTHORITY_REPLY_VERSION = 1


def _snapshot_document(snapshot):
    """Convert a validated snapshot to explicit JSON fields."""

    _require_snapshot(
        snapshot,
        "authority catalog snapshot",
    )

    return {
        "revision": snapshot[0],
        "source_ids_digest": snapshot[1],
        "catalog_digest": snapshot[2],
    }


def _validated_reply_document(reply):
    """Construct the semantic message without evidence bytes.

    Refuse structurally inconsistent replies before encoding.

    This is a local consistency check, not proof that the
    reply originated from a trusted authority.
    """

    if type(reply) is not AuthorityAttestedReply:
        raise ValueError(
            "Invalid authority reply container."
        )

    _require_identity(
        reply.authority_id,
        "authority identity",
    )

    _require_identity(
        reply.operation_id,
        "operation identity",
    )

    _require_transition(
        reply.expected_committed,
        reply.target,
    )

    _require_snapshot(
        reply.committed,
        "committed authority snapshot",
    )

    if type(reply.status) is not AuthorityReplyStatus:
        raise ValueError(
            "Invalid authority reply status."
        )

    _require_integer(
        reply.generation,
        "authority generation",
        minimum=0,
    )

    _require_integer(
        reply.fence_token,
        "authority fencing token",
        minimum=1,
    )

    if reply.status is AuthorityReplyStatus.PREPARED:
        if reply.committed != reply.expected_committed:
            raise ValueError(
                "PREPARED reply changed committed snapshot."
            )

        _require_identity(
            reply.pending_operation_id,
            "pending operation identity",
        )

        if reply.pending_operation_id != reply.operation_id:
            raise ValueError(
                "PREPARED pending operation mismatch."
            )

    elif reply.status is AuthorityReplyStatus.COMMITTED:
        if reply.committed != reply.target:
            raise ValueError(
                "COMMITTED reply does not match target."
            )

        if reply.pending_operation_id is not None:
            raise ValueError(
                "COMMITTED reply contains pending operation."
            )

    else:
        raise ValueError(
            "Unsupported authority reply status."
        )

    return {
        "domain": AUTHORITY_REPLY_DOMAIN,
        "version": AUTHORITY_REPLY_VERSION,
        "authority_id": reply.authority_id,
        "operation_id": reply.operation_id,
        "expected_committed": _snapshot_document(
            reply.expected_committed
        ),
        "target": _snapshot_document(
            reply.target
        ),
        "committed": _snapshot_document(
            reply.committed
        ),
        "pending_operation_id": reply.pending_operation_id,
        "status": reply.status.value,
        "generation": reply.generation,
        "fence_token": reply.fence_token,
    }


def canonical_authority_reply_bytes(reply):
    """Return exact version-1 bytes for the signed reply.

    Encoding contract:

    - Fixed application-specific domain.
    - Fixed integer protocol version.
    - Complete explicitly named reply fields.
    - JSON keys sorted lexicographically.
    - No optional whitespace.
    - Non-ASCII Unicode escaped in JSON.
    - No NaN or Infinity values.
    - Encoded as ASCII bytes.
    - The evidence/signature field is excluded.

    Any future change to the encoding contract must use
    a new protocol version rather than silently changing
    version-1 signed messages.

    The returned bytes are NOT authenticated.
    """

    document = _validated_reply_document(reply)

    return json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
