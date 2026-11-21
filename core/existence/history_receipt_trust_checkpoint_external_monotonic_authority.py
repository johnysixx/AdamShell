"""A44 signed external monotonic checkpoint authority client.

This module validates a caller-pinned Ed25519 identity and signed
canonical authority responses to fresh read and CAS challenges.
It provides an independently challenged signed CAS readback.

SECURITY BOUNDARY:

- A caller-selected signer is not independently enrolled.
- This module is a CLIENT, not an external authority service.
- A malicious signer can sign false read and publication claims.
- Revision/generation/fencing minima are caller supplied, not stored.
- Signed replies cannot prove durability, honest CAS or isolation.
- No cross-system atomicity, transport authentication or rollback
  resistant state is implemented.
- Failure after CAS may mean publication succeeded; never auto-retry.
- No checkpoint restoration or republication is authorized.
"""

import hmac
import json
import os
import re

from contextlib import contextmanager
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)


_DOMAIN = "AdamShell/A44/checkpoint-monotonic-authority/v1"
_VERSION = 1
_MAX_MESSAGE_BYTES = 4096
_HEX32 = re.compile(r"[0-9a-f]{64}\Z")

_READ_FIELDS = frozenset({
    "domain",
    "version",
    "operation",
    "authority_id",
    "root_id",
    "root_public_key_hex",
    "enrollment_epoch",
    "revision",
    "generation",
    "fence_token",
    "challenge_hex",
})

_CAS_FIELDS = _READ_FIELDS | frozenset({
    "expected_revision",
    "next_revision",
    "expected_generation",
    "expected_fence_token",
})


def _require_authority(authority):
    hold = getattr(
        authority,
        "hold",
        None,
    )

    advance = getattr(
        authority,
        "advance_if_current",
        None,
    )

    if not callable(hold) or not callable(advance):
        raise ValueError(
            "Signed external authority capabilities unavailable."
        )

    return authority


def _require_public_key(value, name):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(
            f"Invalid {name}: expected 32 immutable bytes."
        )

    return bytes(value)


def _require_integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _require_signed_pair(response):
    if type(response) is not tuple or len(response) != 2:
        raise ValueError(
            "Malformed external authority response pair."
        )

    message, signature = response

    if (
        type(message) is not bytes
        or not message
        or len(message) > _MAX_MESSAGE_BYTES
        or type(signature) is not bytes
        or len(signature) != 64
    ):
        raise ValueError(
            "Invalid signed external authority response."
        )

    return bytes(message), bytes(signature)


def _reject_duplicate_properties(pairs):
    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                "Duplicate external authority JSON field."
            )

        result[key] = value

    return result


def _reject_constant(value):
    raise ValueError(
        "Nonfinite external authority JSON constant."
    )


def _parse_document(message, operation):
    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=_reject_duplicate_properties,
            parse_constant=_reject_constant,
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
            "Invalid canonical external authority JSON."
        ) from exc

    if canonical != message:
        raise ValueError(
            "Noncanonical external authority message."
        )

    required = (
        _READ_FIELDS
        if operation == "read"
        else _CAS_FIELDS
    )

    if (
        type(document) is not dict
        or set(document) != required
    ):
        raise ValueError(
            "Unexpected external authority message schema."
        )

    if (
        type(document["domain"]) is not str
        or document["domain"] != _DOMAIN
        or type(document["version"]) is not int
        or document["version"] != _VERSION
        or type(document["operation"]) is not str
        or document["operation"] != operation
    ):
        raise ValueError(
            "External authority domain/version/operation mismatch."
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


def _new_challenge(*, different_from=None):
    for _ in range(8):
        candidate = os.urandom(32)

        if (
            type(candidate) is bytes
            and len(candidate) == 32
            and candidate != different_from
        ):
            return candidate

    raise ValueError(
        "Fresh external authority challenge unavailable."
    )


@dataclass(frozen=True, slots=True)
class SignedCheckpointExternalMonotonicAuthoritySource:
    """Verify externally supplied signed claims; no trusted store."""

    authority: object
    expected_authority_id: str
    expected_authority_public_key: bytes
    expected_root_id: str
    expected_root_public_key: bytes
    expected_enrollment_epoch: int
    minimum_revision: int
    minimum_generation: int
    minimum_fence_token: int

    def __post_init__(self):
        _require_authority(self.authority)

        _require_identity(
            self.expected_authority_id,
            "authority identity",
        )

        _require_public_key(
            self.expected_authority_public_key,
            "external authority public key",
        )

        _require_identity(
            self.expected_root_id,
            "checkpoint root identity",
        )

        _require_public_key(
            self.expected_root_public_key,
            "checkpoint root public key",
        )

        _require_integer(
            self.expected_enrollment_epoch,
            "enrollment epoch",
        )

        _require_integer(
            self.minimum_revision,
            "minimum revision",
        )

        _require_integer(
            self.minimum_generation,
            "minimum generation",
        )

        _require_integer(
            self.minimum_fence_token,
            "minimum fence token",
        )

    @classmethod
    def from_authority(
        cls,
        *,
        authority,
        expected_authority_id,
        expected_authority_public_key,
        expected_root_id,
        expected_root_public_key,
        expected_enrollment_epoch,
        minimum_revision,
        minimum_generation,
        minimum_fence_token,
    ):
        try:
            return cls(
                authority=authority,
                expected_authority_id=expected_authority_id,
                expected_authority_public_key=(
                    expected_authority_public_key
                ),
                expected_root_id=expected_root_id,
                expected_root_public_key=expected_root_public_key,
                expected_enrollment_epoch=(
                    expected_enrollment_epoch
                ),
                minimum_revision=minimum_revision,
                minimum_generation=minimum_generation,
                minimum_fence_token=minimum_fence_token,
            )

        except Exception as exc:
            raise ValueError(
                "External monotonic authority binding failed."
            ) from exc

    def _verify(
        self,
        *,
        response,
        operation,
        challenge,
        expected_revision=None,
        next_revision=None,
        expected_generation=None,
        expected_fence_token=None,
    ):
        self.__post_init__()

        if type(challenge) is not bytes or len(challenge) != 32:
            raise ValueError(
                "Invalid external authority challenge."
            )

        message, signature = _require_signed_pair(
            response
        )

        document = _parse_document(
            message,
            operation,
        )

        authority_id = _require_identity(
            document["authority_id"],
            "signed authority id",
        )

        root_id = _require_identity(
            document["root_id"],
            "signed root id",
        )

        if (
            authority_id != self.expected_authority_id
            or root_id != self.expected_root_id
        ):
            raise ValueError(
                "Signed external authority identity mismatch."
            )

        key = _require_hex32(
            document["root_public_key_hex"],
            "signed root public key",
        )

        if not hmac.compare_digest(
            key,
            self.expected_root_public_key,
        ):
            raise ValueError(
                "Signed external root key mismatch."
            )

        signed_challenge = _require_hex32(
            document["challenge_hex"],
            "signed challenge",
        )

        if not hmac.compare_digest(
            signed_challenge,
            challenge,
        ):
            raise ValueError(
                "Signed external authority challenge mismatch."
            )

        epoch = _require_integer(
            document["enrollment_epoch"],
            "signed enrollment epoch",
        )

        revision = _require_integer(
            document["revision"],
            "signed revision",
        )

        generation = _require_integer(
            document["generation"],
            "signed generation",
        )

        fence = _require_integer(
            document["fence_token"],
            "signed fence token",
        )

        if epoch != self.expected_enrollment_epoch:
            raise ValueError(
                "Signed external authority enrollment epoch mismatch."
            )

        if (
            revision < self.minimum_revision
            or generation < self.minimum_generation
            or fence < self.minimum_fence_token
        ):
            raise ValueError(
                "Signed external state below caller-supplied floors."
            )

        if operation == "cas":
            signed_previous = _require_integer(
                document["expected_revision"],
                "signed expected revision",
            )

            signed_next = _require_integer(
                document["next_revision"],
                "signed next revision",
            )

            signed_generation = _require_integer(
                document["expected_generation"],
                "signed expected generation",
            )

            signed_fence = _require_integer(
                document["expected_fence_token"],
                "signed expected fence",
            )

            if (
                signed_previous != expected_revision
                or signed_next != next_revision
                or signed_generation != expected_generation
                or signed_fence != expected_fence_token
                or revision != next_revision
                or generation != expected_generation + 1
                or fence != expected_fence_token + 1
            ):
                raise ValueError(
                    "Signed external CAS transition mismatch."
                )

        try:
            Ed25519PublicKey.from_public_bytes(
                self.expected_authority_public_key
            ).verify(
                signature,
                message,
            )

        except Exception as exc:
            raise ValueError(
                "External authority Ed25519 verification failed."
            ) from exc

        return (
            root_id,
            bytes(key),
            epoch,
            revision,
            generation,
            fence,
        )

    @contextmanager
    def _held_read(
        self,
        *,
        different_from=None,
        required_snapshot=None,
    ):
        caller_completed = False
        provider_released = False

        try:
            self.__post_init__()

            challenge = _new_challenge(
                different_from=different_from
            )

            with self.authority.hold(
                challenge=challenge
            ) as response:

                snapshot = self._verify(
                    response=response,
                    operation="read",
                    challenge=challenge,
                )

                if (
                    required_snapshot is not None
                    and snapshot != required_snapshot
                ):
                    raise ValueError(
                        "Signed authority readback differs "
                        "from CAS result."
                    )

                yield snapshot

                caller_completed = True

            provider_released = True

            if not (
                caller_completed
                and provider_released
            ):
                raise ValueError(
                    "External authority hold "
                    "did not complete safely."
                )

        except Exception as exc:
            raise ValueError(
                "Signed external authority held read failed."
            ) from exc

    @contextmanager
    def hold(self):
        with self._held_read() as snapshot:
            yield snapshot

    def advance_if_current(
        self,
        *,
        expected_revision,
        next_revision,
        expected_generation,
        expected_fence_token,
    ):
        try:
            self.__post_init__()

            old = _require_integer(
                expected_revision,
                "expected revision",
            )

            target = _require_integer(
                next_revision,
                "next revision",
            )

            old_generation = _require_integer(
                expected_generation,
                "expected generation",
            )

            old_fence = _require_integer(
                expected_fence_token,
                "expected fence token",
            )

            if (
                target <= old
                or old < self.minimum_revision
                or old_generation < self.minimum_generation
                or old_fence < self.minimum_fence_token
            ):
                raise ValueError(
                    "Invalid external authority CAS preconditions."
                )

            cas_challenge = _new_challenge()

            response = self.authority.advance_if_current(
                expected_revision=old,
                next_revision=target,
                expected_generation=old_generation,
                expected_fence_token=old_fence,
                challenge=cas_challenge,
            )

            signed = self._verify(
                response=response,
                operation="cas",
                challenge=cas_challenge,
                expected_revision=old,
                next_revision=target,
                expected_generation=old_generation,
                expected_fence_token=old_fence,
            )

            with self._held_read(
                different_from=cas_challenge,
                required_snapshot=signed,
            ) as observed:
                if observed != signed:
                    raise ValueError(
                        "Signed CAS readback disagreement."
                    )

            return signed

        except Exception as exc:
            # The authority may have committed before this
            # failure. Never infer rollback or auto-retry.
            raise ValueError(
                "Signed external authority CAS failed "
                "or is uncertain."
            ) from exc
