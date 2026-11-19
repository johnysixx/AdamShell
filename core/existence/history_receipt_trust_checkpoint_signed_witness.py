"""A44 signed checkpoint trust-witness verification.

Verifies a canonical, root-signed Ed25519 trust witness
binding checkpoint authority, Universe, checkpoint key,
minimum generation, witness revision and challenge.

SECURITY LIMITATIONS:

- A supplied root public key is not independently enrolled.
- A supplied witness revision floor is not rollback-resistant.
- Challenge validation does not prevent reuse of the same
  challenge or establish remote service authenticity.
- This module does not store or advance monotonic state.
- Python result objects are not authorization tokens.
- This module never restores, creates or republishes
  Universe entities or checkpoint state.
"""

import hmac
import json
import re

from dataclasses import dataclass, field

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)

from core.existence.history_receipt_trust_publication_witness import (
    _require_universe_id,
)


_DOMAIN = "AdamShell/A44/checkpoint-trust-witness/v1"
_VERSION = 1
_MAX_MESSAGE_BYTES = 4096

_HEX32 = re.compile(r"[0-9a-f]{64}\Z")

_REQUIRED_FIELDS = frozenset({
    "domain",
    "version",
    "root_id",
    "authority_id",
    "universe_id",
    "checkpoint_public_key_hex",
    "minimum_generation",
    "witness_revision",
    "challenge_hex",
})


def _reject_duplicate_properties(pairs):
    """Reject duplicated JSON names at every object depth."""

    result = {}

    for name, value in pairs:
        if name in result:
            raise ValueError(
                "Duplicate checkpoint trust witness property."
            )

        result[name] = value

    return result


def _reject_nonfinite_constant(value):
    raise ValueError(
        "Non-finite checkpoint trust witness JSON value."
    )


def _parse_canonical_document(message):
    """Accept only exact canonical ASCII JSON with fixed fields."""

    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=_reject_duplicate_properties,
            parse_constant=_reject_nonfinite_constant,
        )

        canonical = json.dumps(
            document,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")

    except (
        ValueError,
        TypeError,
        UnicodeError,
        OverflowError,
        RecursionError,
    ) as exc:
        raise ValueError(
            "Invalid checkpoint trust witness JSON."
        ) from exc

    if canonical != message:
        raise ValueError(
            "Checkpoint trust witness JSON is not canonical."
        )

    if (
        type(document) is not dict
        or set(document) != _REQUIRED_FIELDS
    ):
        raise ValueError(
            "Unexpected checkpoint trust witness schema."
        )

    if (
        type(document["domain"]) is not str
        or document["domain"] != _DOMAIN
    ):
        raise ValueError(
            "Checkpoint trust witness domain mismatch."
        )

    if (
        type(document["version"]) is not int
        or document["version"] != _VERSION
    ):
        raise ValueError(
            "Unsupported checkpoint trust witness version."
        )

    return document


def _require_hex32(value, name):
    if (
        type(value) is not str
        or _HEX32.fullmatch(value) is None
    ):
        raise ValueError(
            f"Invalid {name} encoding."
        )

    return bytes.fromhex(value)


@dataclass(frozen=True, slots=True)
class VerifiedCheckpointTrustWitness:
    """Signed-data verification report, not trusted provenance.

    Direct Python construction is possible and must never
    confer authorization to a security-sensitive operation.
    """

    root_id: str
    authority_id: str
    universe_id: str
    checkpoint_public_key: bytes
    minimum_generation: int
    witness_revision: int
    challenge: bytes

    root_signature_verified: bool = field(
        default=True,
        init=False,
    )
    is_independently_trusted: bool = field(
        default=False,
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


def verify_signed_checkpoint_trust_witness(
    *,
    message,
    signature,
    trusted_root_id,
    trusted_root_public_key,
    expected_authority_id,
    expected_universe_id,
    expected_challenge,
    minimum_witness_revision,
):
    """Verify one signed trust witness against supplied inputs.

    minimum_witness_revision is EXCLUSIVE.

    A successful verification authenticates signed bytes
    relative to the supplied root key. It does not prove
    that the supplied root was independently enrolled,
    nor that the revision floor is protected from rollback.
    """

    try:
        _require_identity(
            trusted_root_id,
            "trusted checkpoint root identity",
        )

        _require_identity(
            expected_authority_id,
            "expected checkpoint authority identity",
        )

        _require_universe_id(
            expected_universe_id
        )

        if (
            type(trusted_root_public_key) is not bytes
            or len(trusted_root_public_key) != 32
        ):
            raise ValueError(
                "Trusted root Ed25519 key must be "
                "exactly 32 immutable bytes."
            )

        if (
            type(expected_challenge) is not bytes
            or len(expected_challenge) != 32
        ):
            raise ValueError(
                "Expected challenge must be "
                "exactly 32 immutable bytes."
            )

        if (
            type(minimum_witness_revision) is not int
            or minimum_witness_revision < 0
        ):
            raise ValueError(
                "Invalid minimum witness revision."
            )

        if (
            type(message) is not bytes
            or not message
            or len(message) > _MAX_MESSAGE_BYTES
        ):
            raise ValueError(
                "Invalid checkpoint witness message bytes."
            )

        if (
            type(signature) is not bytes
            or len(signature) != 64
        ):
            raise ValueError(
                "Invalid checkpoint witness signature."
            )

        # Authenticate the exact raw bytes before parsing.
        # This authenticates against the supplied root only.
        root_public_key = (
            Ed25519PublicKey.from_public_bytes(
                trusted_root_public_key
            )
        )

        root_public_key.verify(
            signature,
            message,
        )

        document = _parse_canonical_document(
            message
        )

        root_id = _require_identity(
            document["root_id"],
            "witness root identity",
        )

        authority_id = _require_identity(
            document["authority_id"],
            "witness checkpoint authority",
        )

        universe_id = _require_universe_id(
            document["universe_id"]
        )

        if root_id != trusted_root_id:
            raise ValueError(
                "Checkpoint witness root identity mismatch."
            )

        if authority_id != expected_authority_id:
            raise ValueError(
                "Checkpoint witness authority mismatch."
            )

        if universe_id != expected_universe_id:
            raise ValueError(
                "Checkpoint witness Universe mismatch."
            )

        checkpoint_public_key = _require_hex32(
            document["checkpoint_public_key_hex"],
            "checkpoint Ed25519 public key",
        )

        # Verify that the byte string is accepted as
        # an Ed25519 public key by the crypto backend.
        Ed25519PublicKey.from_public_bytes(
            checkpoint_public_key
        )

        minimum_generation = document["minimum_generation"]

        if (
            type(minimum_generation) is not int
            or minimum_generation < 0
        ):
            raise ValueError(
                "Invalid checkpoint generation floor."
            )

        witness_revision = document["witness_revision"]

        if (
            type(witness_revision) is not int
            or witness_revision < 1
            or witness_revision <= minimum_witness_revision
        ):
            raise ValueError(
                "Stale or invalid checkpoint witness revision."
            )

        challenge = _require_hex32(
            document["challenge_hex"],
            "checkpoint challenge",
        )

        if not hmac.compare_digest(
            challenge,
            expected_challenge,
        ):
            raise ValueError(
                "Checkpoint trust witness challenge mismatch."
            )

        return VerifiedCheckpointTrustWitness(
            root_id=root_id,
            authority_id=authority_id,
            universe_id=universe_id,
            checkpoint_public_key=checkpoint_public_key,
            minimum_generation=minimum_generation,
            witness_revision=witness_revision,
            challenge=challenge,
        )

    except Exception as exc:
        raise ValueError(
            "Signed checkpoint trust witness verification failed."
        ) from exc
