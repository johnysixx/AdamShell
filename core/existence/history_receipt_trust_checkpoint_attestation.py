"""A44 pinned Ed25519 attestation for canonical Cronenberg checkpoints.

Verifies the exact signed identity, publication projection digest and
supported entity-state checkpoint digest. A configured public-key pin
is only as trusted as its independent provisioning. The caller-supplied
generation floor does not establish rollback resistance by itself.

This module never restores, authorizes, or republishes a Universe entity.
"""

import json
from dataclasses import dataclass, field

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)
from core.existence.history_receipt_trust_cronenberg_checkpoint import (
    CanonicalCronenbergStateCheckpoint,
)
from core.existence.history_receipt_trust_incident_outbox import (
    _require_cronenberg_id,
    _require_incident_id,
    _require_operation,
)
from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)
from core.existence.history_receipt_trust_publication_witness import (
    _require_digest,
    _require_universe_id,
)

_SCHEMA_VERSION = 1
_DOMAIN = (
    "AdamShell/A44/"
    "cronenberg-state-checkpoint-attestation/v1"
)
_MAX_MESSAGE_BYTES = 4096
_DOCUMENT_KEYS = frozenset({
    "schema_version",
    "domain",
    "authority_id",
    "generation",
    "universe_id",
    "incident_id",
    "source_operation",
    "cronenberg_id",
    "projection_sha256",
    "checkpoint_sha256",
})


def _reject_duplicate_properties(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate checkpoint attestation JSON property.")
        result[key] = value
    return result


def _reject_nonfinite_constant(value):
    raise ValueError("Non-finite checkpoint attestation JSON constant.")


def _canonical_json_bytes(document):
    try:
        return json.dumps(
            document,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ValueError("Invalid checkpoint attestation JSON.") from exc


def _parse_canonical_message(message):
    if (
        type(message) is not bytes
        or not message
        or len(message) > _MAX_MESSAGE_BYTES
    ):
        raise ValueError("Invalid checkpoint attestation message bytes.")

    try:
        document = json.loads(
            message.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_properties,
            parse_constant=_reject_nonfinite_constant,
        )
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise ValueError("Malformed checkpoint attestation message.") from exc

    if type(document) is not dict or set(document) != _DOCUMENT_KEYS:
        raise ValueError("Unexpected checkpoint attestation document schema.")

    if (
        type(document["schema_version"]) is not int
        or document["schema_version"] != _SCHEMA_VERSION
    ):
        raise ValueError("Unsupported checkpoint attestation schema.")

    if type(document["domain"]) is not str or document["domain"] != _DOMAIN:
        raise ValueError("Checkpoint attestation domain mismatch.")

    _require_identity(document["authority_id"], "checkpoint attestation authority")

    if type(document["generation"]) is not int or document["generation"] < 1:
        raise ValueError("Invalid checkpoint attestation generation.")

    _require_universe_id(document["universe_id"])
    _require_incident_id(document["incident_id"])
    _require_operation(document["source_operation"])
    _require_cronenberg_id(document["cronenberg_id"])
    _require_digest(document["projection_sha256"])
    _require_digest(document["checkpoint_sha256"])

    if _canonical_json_bytes(document) != message:
        raise ValueError("Noncanonical checkpoint attestation serialization.")

    return document


@dataclass(frozen=True, slots=True)
class VerifiedCronenbergCheckpointAttestation:
    """A signed-data verification report, never an authority token.

    Python callers can construct an instance directly. Security-sensitive
    operations must not trust this result as authorization.
    """

    authority_id: str
    generation: int
    universe_id: str
    incident_id: str
    source_operation: str
    cronenberg_id: str
    projection_sha256: str
    checkpoint_sha256: str

    signature_verified: bool = field(default=True, init=False)
    is_authoritative: bool = field(default=False, init=False)
    is_restorable: bool = field(default=False, init=False)
    can_republish: bool = field(default=False, init=False)


@dataclass(frozen=True, slots=True)
class PinnedCronenbergCheckpointAttestationVerifier:
    """Detaches pinned Ed25519 public keys; never manages private keys.

    A pinset supplied by an attacker is not independently trusted.
    The exclusive minimum_generation floor also requires an independent
    trusted source for real anti-rollback protection.
    """

    _pinned_keys: tuple[tuple[str, bytes], ...]

    @classmethod
    def from_pinned_keys(cls, keys):
        if type(keys) is not dict or not keys:
            raise ValueError("Expected a nonempty pinned checkpoint key map.")

        validated = []
        for authority_id, raw_key in keys.items():
            _require_identity(authority_id, "pinned checkpoint authority")
            if type(raw_key) is not bytes or len(raw_key) != 32:
                raise ValueError("Pinned checkpoint Ed25519 key must be 32 immutable bytes.")
            try:
                Ed25519PublicKey.from_public_bytes(raw_key)
            except (TypeError, ValueError) as exc:
                raise ValueError("Invalid checkpoint Ed25519 public key.") from exc
            validated.append((authority_id, bytes(raw_key)))

        return cls(tuple(sorted(validated, key=lambda item: item[0])))

    def verify(
        self,
        *,
        evidence,
        checkpoint,
        message,
        signature,
        expected_authority_id,
        expected_universe_id,
        expected_incident_id,
        minimum_generation,
    ):
        """Verify signed publication/checkpoint data only; no live mutation."""

        _require_identity(expected_authority_id, "expected checkpoint authority")
        _require_universe_id(expected_universe_id)
        _require_incident_id(expected_incident_id)

        if type(minimum_generation) is not int or minimum_generation < 0:
            raise ValueError("Invalid trusted checkpoint generation floor.")

        if type(signature) is not bytes or len(signature) != 64:
            raise ValueError("Invalid checkpoint attestation signature.")

        if type(evidence) is not CanonicalSecurityPublicationEvidence:
            raise ValueError("Canonical publication evidence is required.")
        if type(checkpoint) is not CanonicalCronenbergStateCheckpoint:
            raise ValueError("Canonical Cronenberg checkpoint is required.")

        # Re-parse detached serializations. Neither a frozen dataclass nor
        # a caller-constructed object is a security authority by itself.
        try:
            verified_evidence = CanonicalSecurityPublicationEvidence.parse_untrusted(
                evidence.to_dict()
            )
            verified_checkpoint = CanonicalCronenbergStateCheckpoint.parse_untrusted(
                checkpoint.to_dict()
            )
        except Exception as exc:
            raise ValueError("Invalid checkpoint attestation input objects.") from exc

        if (
            verified_evidence.is_authoritative is not False
            or verified_evidence.is_restorable is not False
            or verified_checkpoint.is_authoritative is not False
            or verified_checkpoint.is_restorable is not False
            or verified_checkpoint.can_republish is not False
        ):
            raise ValueError("Checkpoint inputs cannot confer authority.")

        # Check every shared publication identity, not only the digest.
        for name in (
            "universe_id",
            "incident_id",
            "source_operation",
            "cronenberg_id",
            "projection_sha256",
        ):
            if getattr(verified_evidence, name) != getattr(verified_checkpoint, name):
                raise ValueError("Checkpoint/publication identity mismatch.")

        document = _parse_canonical_message(message)
        if document["authority_id"] != expected_authority_id:
            raise ValueError("Checkpoint attestation authority mismatch.")
        if (
            document["universe_id"] != expected_universe_id
            or document["incident_id"] != expected_incident_id
        ):
            raise ValueError("Checkpoint attestation target mismatch.")
        if document["generation"] <= minimum_generation:
            raise ValueError("Stale checkpoint attestation generation.")

        for name in (
            "universe_id",
            "incident_id",
            "source_operation",
            "cronenberg_id",
            "projection_sha256",
        ):
            if document[name] != getattr(verified_evidence, name):
                raise ValueError("Signed checkpoint publication identity mismatch.")

        if document["checkpoint_sha256"] != verified_checkpoint.checkpoint_sha256:
            raise ValueError("Signed checkpoint state digest mismatch.")

        pinned_key = None
        for authority_id, raw_key in self._pinned_keys:
            if authority_id == expected_authority_id:
                pinned_key = raw_key
                break

        if pinned_key is None:
            raise ValueError("Checkpoint authority has no configured pin.")

        try:
            Ed25519PublicKey.from_public_bytes(pinned_key).verify(
                signature,
                message,
            )
        except Exception as exc:
            raise ValueError("Checkpoint Ed25519 signature verification failed.") from exc

        # The result verifies signed bytes under caller-configured trust inputs,
        # but proves neither historic publication nor restorable checkpoint.
        return VerifiedCronenbergCheckpointAttestation(
            authority_id=document["authority_id"],
            generation=document["generation"],
            universe_id=document["universe_id"],
            incident_id=document["incident_id"],
            source_operation=document["source_operation"],
            cronenberg_id=document["cronenberg_id"],
            projection_sha256=document["projection_sha256"],
            checkpoint_sha256=document["checkpoint_sha256"],
        )
