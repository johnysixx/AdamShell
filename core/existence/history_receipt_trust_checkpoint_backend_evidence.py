"""A44 signed checkpoint root-backend evidence verifier.

This module verifies Ed25519 signatures over strictly canonical,
domain-separated read and CAS evidence messages.

SECURITY LIMITATIONS:

- Both backend and root public keys are caller-supplied pins.
- Successful verification does not independently enroll keys.
- No transport authentication or external backend is provided.
- A signed response does not prove a real CAS occurred.
- A signed response does not prove durability or linearizability.
- A repeated challenge may admit replay of the same evidence.
- No persistent anti-rollback or restart guarantee is provided.
- There is no cross-backend atomicity.
- Result objects carry DATA ONLY, not authorization.
- No checkpoint restoration or republication is authorized.
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


_DOMAIN = "AdamShell/A44/checkpoint-backend-evidence/v1"
_VERSION = 1
_MAX_MESSAGE_BYTES = 4096

_HEX32 = re.compile(r"[0-9a-f]{64}\Z")

_COMMON_FIELDS = frozenset({
    "domain",
    "version",
    "operation",
    "backend_id",
    "root_id",
    "root_public_key_hex",
    "revision",
    "challenge_hex",
})

_CAS_FIELDS = frozenset({
    "expected_revision",
    "next_revision",
})


def _require_public_key(value, name):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(
            f"Invalid {name}: expected 32 immutable bytes."
        )

    return bytes(value)


def _require_challenge(value):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(
            "Backend evidence challenge must be "
            "32 immutable bytes."
        )

    return bytes(value)


def _require_revision(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _require_message_and_signature(message, signature):
    if (
        type(message) is not bytes
        or not message
        or len(message) > _MAX_MESSAGE_BYTES
    ):
        raise ValueError(
            "Invalid signed backend evidence message."
        )

    if type(signature) is not bytes or len(signature) != 64:
        raise ValueError(
            "Invalid backend evidence Ed25519 signature."
        )

    return bytes(message), bytes(signature)


def _reject_duplicate_properties(pairs):
    result = {}

    for name, value in pairs:
        if name in result:
            raise ValueError(
                "Duplicate backend evidence JSON property."
            )

        result[name] = value

    return result


def _reject_nonfinite_constant(value):
    raise ValueError(
        "Non-finite backend evidence JSON value."
    )


def _parse_canonical_document(message, operation):
    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=_reject_duplicate_properties,
            parse_constant=_reject_nonfinite_constant,
        )

        canonical = json.dumps(
            document,
            ensure_ascii=True,
            sort_keys=True,
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
            "Invalid canonical backend evidence JSON."
        ) from exc

    if canonical != message:
        raise ValueError(
            "Noncanonical backend evidence message."
        )

    expected_fields = (
        _COMMON_FIELDS
        if operation == "read"
        else _COMMON_FIELDS | _CAS_FIELDS
    )

    if (
        type(document) is not dict
        or set(document) != expected_fields
    ):
        raise ValueError(
            "Unexpected backend evidence schema."
        )

    if (
        type(document["domain"]) is not str
        or document["domain"] != _DOMAIN
    ):
        raise ValueError(
            "Backend evidence domain mismatch."
        )

    if (
        type(document["version"]) is not int
        or document["version"] != _VERSION
    ):
        raise ValueError(
            "Unsupported backend evidence version."
        )

    if (
        type(document["operation"]) is not str
        or document["operation"] != operation
    ):
        raise ValueError(
            "Backend evidence operation mismatch."
        )

    return document


def _require_hex32(value, name):
    if (
        type(value) is not str
        or _HEX32.fullmatch(value) is None
    ):
        raise ValueError(
            f"Invalid {name} hex encoding."
        )

    return bytes.fromhex(value)


@dataclass(frozen=True, slots=True)
class VerifiedCheckpointRootBackendEvidence:
    """Verified signed data relative to supplied key pins."""

    operation: str
    backend_id: str
    backend_public_key: bytes
    root_id: str
    root_public_key: bytes
    revision: int
    challenge: bytes

    expected_revision: int | None = None
    next_revision: int | None = None

    signature_verified: bool = field(
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
    is_durable: bool = field(
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
class CheckpointRootBackendEvidenceVerifier:
    """Strict signed-evidence verifier; no backend connection."""

    expected_backend_id: str
    expected_backend_public_key: bytes
    expected_root_id: str
    expected_root_public_key: bytes

    def __post_init__(self):
        _require_identity(
            self.expected_backend_id,
            "expected backend identity",
        )

        _require_identity(
            self.expected_root_id,
            "expected root identity",
        )

        _require_public_key(
            self.expected_backend_public_key,
            "expected backend public key",
        )

        _require_public_key(
            self.expected_root_public_key,
            "expected root public key",
        )

    @classmethod
    def from_pinned_key(
        cls,
        *,
        expected_backend_id,
        expected_backend_public_key,
        expected_root_id,
        expected_root_public_key,
    ):
        try:
            return cls(
                expected_backend_id=expected_backend_id,
                expected_backend_public_key=(
                    expected_backend_public_key
                ),
                expected_root_id=expected_root_id,
                expected_root_public_key=(
                    expected_root_public_key
                ),
            )

        except Exception as exc:
            raise ValueError(
                "Checkpoint backend evidence pinning failed."
            ) from exc

    def _verify(
        self,
        *,
        message,
        signature,
        expected_challenge,
        operation,
    ):
        """Verify syntax, signed fields and Ed25519 signature."""

        self.__post_init__()

        canonical_message, signed_signature = (
            _require_message_and_signature(
                message,
                signature,
            )
        )

        challenge = _require_challenge(
            expected_challenge
        )

        document = _parse_canonical_document(
            canonical_message,
            operation,
        )

        backend_id = _require_identity(
            document["backend_id"],
            "signed backend identity",
        )

        root_id = _require_identity(
            document["root_id"],
            "signed root identity",
        )

        if backend_id != self.expected_backend_id:
            raise ValueError(
                "Signed backend identity mismatch."
            )

        if root_id != self.expected_root_id:
            raise ValueError(
                "Signed root identity mismatch."
            )

        document_root_key = _require_hex32(
            document["root_public_key_hex"],
            "signed root public key",
        )

        if not hmac.compare_digest(
            document_root_key,
            self.expected_root_public_key,
        ):
            raise ValueError(
                "Signed root key differs from supplied pin."
            )

        document_challenge = _require_hex32(
            document["challenge_hex"],
            "signed challenge",
        )

        if not hmac.compare_digest(
            document_challenge,
            challenge,
        ):
            raise ValueError(
                "Backend evidence challenge mismatch."
            )

        revision = _require_revision(
            document["revision"],
            "signed backend revision",
        )

        try:
            Ed25519PublicKey.from_public_bytes(
                self.expected_backend_public_key
            ).verify(
                signed_signature,
                canonical_message,
            )

        except Exception as exc:
            raise ValueError(
                "Backend evidence Ed25519 verification failed."
            ) from exc

        return document, revision, challenge

    def verify_read(
        self,
        *,
        message,
        signature,
        expected_challenge,
        minimum_revision,
    ):
        """Verify an exact canonical signed read response.

        The caller-supplied revision floor must itself come
        from trusted monotonic state to prevent rollback.
        """

        try:
            minimum = _require_revision(
                minimum_revision,
                "minimum read revision",
            )

            _, revision, challenge = self._verify(
                message=message,
                signature=signature,
                expected_challenge=expected_challenge,
                operation="read",
            )

            if revision < minimum:
                raise ValueError(
                    "Signed backend read is below minimum revision."
                )

            return VerifiedCheckpointRootBackendEvidence(
                operation="read",
                backend_id=self.expected_backend_id,
                backend_public_key=(
                    self.expected_backend_public_key
                ),
                root_id=self.expected_root_id,
                root_public_key=self.expected_root_public_key,
                revision=revision,
                challenge=challenge,
            )

        except Exception as exc:
            raise ValueError(
                "Checkpoint backend signed read verification failed."
            ) from exc

    def verify_cas(
        self,
        *,
        message,
        signature,
        expected_challenge,
        expected_revision,
        next_revision,
    ):
        """Verify an exact canonical signed CAS response.

        This method checks cryptographic evidence only.
        It does not establish that CAS actually committed.
        """

        try:
            previous = _require_revision(
                expected_revision,
                "expected CAS revision",
            )

            target = _require_revision(
                next_revision,
                "next CAS revision",
            )

            if target <= previous:
                raise ValueError(
                    "CAS revision must increase."
                )

            document, revision, challenge = self._verify(
                message=message,
                signature=signature,
                expected_challenge=expected_challenge,
                operation="cas",
            )

            signed_previous = _require_revision(
                document["expected_revision"],
                "signed CAS predecessor",
            )

            signed_target = _require_revision(
                document["next_revision"],
                "signed CAS target",
            )

            if (
                signed_previous != previous
                or signed_target != target
                or revision != target
                or signed_target <= signed_previous
            ):
                raise ValueError(
                    "Signed backend CAS transition mismatch."
                )

            return VerifiedCheckpointRootBackendEvidence(
                operation="cas",
                backend_id=self.expected_backend_id,
                backend_public_key=(
                    self.expected_backend_public_key
                ),
                root_id=self.expected_root_id,
                root_public_key=self.expected_root_public_key,
                revision=revision,
                challenge=challenge,
                expected_revision=previous,
                next_revision=target,
            )

        except Exception as exc:
            raise ValueError(
                "Checkpoint backend signed CAS verification failed."
            ) from exc
