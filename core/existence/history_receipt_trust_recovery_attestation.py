"""A44 pinned Ed25519 recovery-evidence attestation.

This module verifies a signature over an exact, versioned,
domain-separated canonical evidence identity document.

A successful result establishes only that the supplied
bytes verify under the configured pinned public key.

It DOES NOT prove:
- trusted enrollment or provenance of that pinset;
- authenticated historical Universe publication;
- completeness of the Cronenberg object state;
- freshness without an independent generation floor;
- revocation or key-rotation status;
- checkpoint restorability;
- authorization to republish or create entities;
- atomicity or cross-process exactly-once behavior.

A Python result object can be constructed by a caller and
must never be treated as an independent security authority.

No private keys are accepted or stored by this module.
"""

import json

from dataclasses import dataclass, field

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
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
    "recovery-evidence-attestation/v1"
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
})


def _reject_duplicate_properties(pairs):
    """Reject duplicates even inside nested JSON objects."""

    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                "Duplicate recovery attestation JSON property."
            )

        result[key] = value

    return result


def _reject_nonfinite_constant(value):
    raise ValueError(
        "Non-finite recovery attestation JSON constant."
    )


def _canonical_json_bytes(document):
    try:
        return json.dumps(
            document,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            "Invalid recovery attestation JSON."
        ) from exc


def _parse_canonical_message(message):
    """Require exact canonical JSON with no extra properties."""

    if (
        type(message) is not bytes
        or not message
        or len(message) > _MAX_MESSAGE_BYTES
    ):
        raise ValueError(
            "Invalid recovery attestation message bytes."
        )

    try:
        document = json.loads(
            message.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_properties,
            parse_constant=_reject_nonfinite_constant,
        )

    except (
        UnicodeError,
        ValueError,
        TypeError,
        RecursionError,
    ) as exc:
        raise ValueError(
            "Malformed recovery attestation message."
        ) from exc

    if (
        type(document) is not dict
        or set(document) != _DOCUMENT_KEYS
    ):
        raise ValueError(
            "Unexpected recovery attestation document schema."
        )

    if (
        type(document["schema_version"]) is not int
        or document["schema_version"] != _SCHEMA_VERSION
    ):
        raise ValueError(
            "Unsupported recovery attestation schema."
        )

    if (
        type(document["domain"]) is not str
        or document["domain"] != _DOMAIN
    ):
        raise ValueError(
            "Recovery attestation domain mismatch."
        )

    _require_identity(
        document["authority_id"],
        "recovery attestation authority",
    )

    if (
        type(document["generation"]) is not int
        or document["generation"] < 1
    ):
        raise ValueError(
            "Invalid recovery attestation generation."
        )

    _require_universe_id(
        document["universe_id"]
    )

    _require_incident_id(
        document["incident_id"]
    )

    _require_operation(
        document["source_operation"]
    )

    _require_cronenberg_id(
        document["cronenberg_id"]
    )

    _require_digest(
        document["projection_sha256"]
    )

    if _canonical_json_bytes(document) != message:
        raise ValueError(
            "Noncanonical recovery attestation serialization."
        )

    return document


@dataclass(frozen=True, slots=True)
class VerifiedRecoveryEvidenceAttestation:
    """Detached result of signature verification only.

    This object is not protected against direct construction
    by arbitrary Python code. It is never an authority
    token and cannot authorize Universe restoration.
    """

    authority_id: str
    generation: int
    universe_id: str
    incident_id: str
    source_operation: str
    cronenberg_id: str
    projection_sha256: str

    signature_verified: bool = field(
        default=True,
        init=False,
    )

    is_authoritative: bool = field(
        default=False,
        init=False,
    )

    is_restorable: bool = field(
        default=False,
        init=False,
    )

    can_republish: bool = field(
        default=False,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class PinnedRecoveryEvidenceAttestationVerifier:
    """Verifier with a detached immutable public-key pinset.

    The factory validates keys, but cannot determine
    whether their source is independently trusted.

    Only explicit provisioning from a trusted boundary
    can establish that provenance.
    """

    _pinned_keys: tuple[tuple[str, bytes], ...]

    @classmethod
    def from_pinned_keys(cls, keys):
        """Accept a nonempty map of identity -> raw Ed25519 key."""

        if type(keys) is not dict or not keys:
            raise ValueError(
                "Expected a nonempty pinned recovery key map."
            )

        validated = []

        for authority_id, raw_key in keys.items():
            _require_identity(
                authority_id,
                "pinned recovery authority",
            )

            if (
                type(raw_key) is not bytes
                or len(raw_key) != 32
            ):
                raise ValueError(
                    "Pinned recovery Ed25519 key must be "
                    "exactly 32 immutable bytes."
                )

            try:
                Ed25519PublicKey.from_public_bytes(
                    raw_key
                )

            except (ValueError, TypeError) as exc:
                raise ValueError(
                    "Invalid recovery Ed25519 public key."
                ) from exc

            validated.append(
                (
                    authority_id,
                    bytes(raw_key),
                )
            )

        return cls(
            tuple(
                sorted(
                    validated,
                    key=lambda entry: entry[0],
                )
            )
        )

    def verify(
        self,
        *,
        evidence,
        message,
        signature,
        expected_authority_id,
        expected_universe_id,
        expected_incident_id,
        minimum_generation,
    ):
        """Verify signed data; never authorize recovery.

        minimum_generation is an EXCLUSIVE lower bound.
        It must be supplied by an independently trusted
        monotonic source to provide replay protection.

        The signed projection is identity-and-event evidence
        only. No live Universe mutation occurs here.
        """

        _require_identity(
            expected_authority_id,
            "expected recovery authority",
        )

        _require_universe_id(
            expected_universe_id
        )

        _require_incident_id(
            expected_incident_id
        )

        if (
            type(minimum_generation) is not int
            or minimum_generation < 0
        ):
            raise ValueError(
                "Invalid trusted recovery generation floor."
            )

        if (
            type(signature) is not bytes
            or len(signature) != 64
        ):
            raise ValueError(
                "Invalid recovery attestation signature."
            )

        if type(evidence) is not CanonicalSecurityPublicationEvidence:
            raise ValueError(
                "Canonical publication evidence is required."
            )

        # Revalidate evidence rather than trusting a frozen
        # Python instance or its claimed digest.
        try:
            validated_evidence = (
                CanonicalSecurityPublicationEvidence
                .parse_untrusted(
                    evidence.to_dict()
                )
            )

        except Exception as exc:
            raise ValueError(
                "Invalid recovery evidence projection."
            ) from exc

        if (
            validated_evidence.is_authoritative is not False
            or validated_evidence.is_restorable is not False
        ):
            raise ValueError(
                "Recovery evidence cannot grant authority."
            )

        document = _parse_canonical_message(
            message
        )

        if (
            document["authority_id"]
            != expected_authority_id
        ):
            raise ValueError(
                "Recovery attestation authority mismatch."
            )

        if (
            document["universe_id"]
            != expected_universe_id
            or document["incident_id"]
            != expected_incident_id
        ):
            raise ValueError(
                "Recovery attestation target identity mismatch."
            )

        if (
            document["generation"]
            <= minimum_generation
        ):
            raise ValueError(
                "Stale recovery attestation generation."
            )

        if (
            document["universe_id"]
            != validated_evidence.universe_id
            or document["incident_id"]
            != validated_evidence.incident_id
            or document["source_operation"]
            != validated_evidence.source_operation
            or document["cronenberg_id"]
            != validated_evidence.cronenberg_id
            or document["projection_sha256"]
            != validated_evidence.projection_sha256
        ):
            raise ValueError(
                "Signed recovery identity/projection mismatch."
            )

        pinned_key = None

        for authority_id, raw_key in self._pinned_keys:
            if authority_id == expected_authority_id:
                pinned_key = raw_key
                break

        if pinned_key is None:
            raise ValueError(
                "Recovery authority has no trusted pin."
            )

        try:
            public_key = (
                Ed25519PublicKey.from_public_bytes(
                    pinned_key
                )
            )

            public_key.verify(
                signature,
                message,
            )

        except Exception as exc:
            raise ValueError(
                "Recovery Ed25519 signature verification failed."
            ) from exc

        # A verified signature establishes only signed
        # data consistency under the configured pinset.
        # It does not restore, authorize or republish.
        return VerifiedRecoveryEvidenceAttestation(
            authority_id=document["authority_id"],
            generation=document["generation"],
            universe_id=document["universe_id"],
            incident_id=document["incident_id"],
            source_operation=document["source_operation"],
            cronenberg_id=document["cronenberg_id"],
            projection_sha256=document["projection_sha256"],
        )
