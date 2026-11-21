"""A44 pinned signed checkpoint anchor read client.

Verifies caller-pinned Ed25519 anchor responses to fresh challenges.

SECURITY LIMITATIONS:
- All trust pins and minimum counters are caller supplied.
- No independent anchor enrollment or protected key store.
- Signatures cannot prove honest remote execution or durability.
- No rollback-resistant backend, remote lease, or monotonic CAS.
- No cross-store atomicity, checkpoint restoration or republication.
- Python frozen objects are not in-process security boundaries.

This module provides read-only authenticated-data validation.
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


_DOMAIN = "AdamShell/A44/independent-anchor/v1"
_VERSION = 1
_MAX_MESSAGE_BYTES = 4096
_MAX_INTEGER = (1 << 63) - 1

_HEX32 = re.compile(r"[0-9a-f]{64}\Z")

_FIELDS = frozenset({
    "domain",
    "version",
    "operation",
    "anchor_id",
    "authority_id",
    "authority_public_key_hex",
    "root_id",
    "root_public_key_hex",
    "enrollment_epoch",
    "revision",
    "generation",
    "fence_token",
    "challenge_hex",
})


def _require_provider(provider):
    if not callable(getattr(provider, "hold", None)):
        raise ValueError("Signed anchor provider unavailable.")

    return provider


def _require_key(value, name):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(
            f"Invalid {name}: expected 32 immutable bytes."
        )

    return bytes(value)


def _require_integer(value, name):
    if (
        type(value) is not int
        or not 0 <= value <= _MAX_INTEGER
    ):
        raise ValueError(f"Invalid {name}.")

    return value


def _require_hex32(value, name):
    if (
        type(value) is not str
        or _HEX32.fullmatch(value) is None
    ):
        raise ValueError(
            f"Invalid {name} hexadecimal encoding."
        )

    return bytes.fromhex(value)


def _reject_duplicate_properties(pairs):
    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                "Duplicate signed anchor JSON property."
            )

        result[key] = value

    return result


def _reject_json_constant(value):
    raise ValueError(
        "Nonfinite signed anchor JSON constant."
    )


def _require_signed_pair(response):
    if type(response) is not tuple or len(response) != 2:
        raise ValueError(
            "Malformed signed anchor response pair."
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
            "Invalid signed anchor response encoding."
        )

    return bytes(message), bytes(signature)


def _parse_document(message):
    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=_reject_duplicate_properties,
            parse_constant=_reject_json_constant,
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
            "Invalid signed anchor canonical JSON."
        ) from exc

    if (
        type(document) is not dict
        or set(document) != _FIELDS
        or canonical != message
    ):
        raise ValueError(
            "Noncanonical or unexpected signed anchor document."
        )

    if (
        type(document["domain"]) is not str
        or document["domain"] != _DOMAIN
        or type(document["version"]) is not int
        or document["version"] != _VERSION
        or type(document["operation"]) is not str
        or document["operation"] != "read"
    ):
        raise ValueError(
            "Signed anchor domain, version or operation mismatch."
        )

    return document


def _fresh_challenge():
    challenge = os.urandom(32)

    if type(challenge) is not bytes or len(challenge) != 32:
        raise ValueError(
            "Fresh signed anchor challenge unavailable."
        )

    return challenge


@dataclass(frozen=True, slots=True)
class PinnedSignedCheckpointAnchorSource:
    """Read-only signed anchor client with caller-selected pins."""

    provider: object

    expected_anchor_id: str
    expected_anchor_public_key: bytes

    expected_authority_id: str
    expected_authority_public_key: bytes

    expected_root_id: str
    expected_root_public_key: bytes

    expected_enrollment_epoch: int

    minimum_revision: int
    minimum_generation: int
    minimum_fence_token: int

    def __post_init__(self):
        _require_provider(self.provider)

        _require_identity(
            self.expected_anchor_id,
            "expected anchor identity",
        )

        _require_key(
            self.expected_anchor_public_key,
            "expected anchor public key",
        )

        _require_identity(
            self.expected_authority_id,
            "expected authority identity",
        )

        _require_key(
            self.expected_authority_public_key,
            "expected authority public key",
        )

        _require_identity(
            self.expected_root_id,
            "expected root identity",
        )

        _require_key(
            self.expected_root_public_key,
            "expected root public key",
        )

        _require_integer(
            self.expected_enrollment_epoch,
            "expected enrollment epoch",
        )

        _require_integer(
            self.minimum_revision,
            "minimum anchor revision",
        )

        _require_integer(
            self.minimum_generation,
            "minimum anchor generation",
        )

        _require_integer(
            self.minimum_fence_token,
            "minimum anchor fencing token",
        )

    @classmethod
    def from_provider(
        cls,
        *,
        provider,
        expected_anchor_id,
        expected_anchor_public_key,
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
                provider=provider,
                expected_anchor_id=expected_anchor_id,
                expected_anchor_public_key=expected_anchor_public_key,
                expected_authority_id=expected_authority_id,
                expected_authority_public_key=expected_authority_public_key,
                expected_root_id=expected_root_id,
                expected_root_public_key=expected_root_public_key,
                expected_enrollment_epoch=expected_enrollment_epoch,
                minimum_revision=minimum_revision,
                minimum_generation=minimum_generation,
                minimum_fence_token=minimum_fence_token,
            )

        except Exception as exc:
            raise ValueError(
                "Pinned signed anchor client binding failed."
            ) from exc

    def _verify(self, *, response, challenge):
        self.__post_init__()

        if type(challenge) is not bytes or len(challenge) != 32:
            raise ValueError("Invalid signed anchor challenge.")

        message, signature = _require_signed_pair(
            response
        )

        document = _parse_document(
            message
        )

        anchor_id = _require_identity(
            document["anchor_id"],
            "signed anchor identity",
        )

        authority_id = _require_identity(
            document["authority_id"],
            "signed authority identity",
        )

        root_id = _require_identity(
            document["root_id"],
            "signed root identity",
        )

        if (
            anchor_id != self.expected_anchor_id
            or authority_id != self.expected_authority_id
            or root_id != self.expected_root_id
        ):
            raise ValueError(
                "Signed anchor identity binding mismatch."
            )

        authority_key = _require_hex32(
            document["authority_public_key_hex"],
            "signed authority public key",
        )

        root_key = _require_hex32(
            document["root_public_key_hex"],
            "signed root public key",
        )

        if not hmac.compare_digest(
            authority_key,
            self.expected_authority_public_key,
        ):
            raise ValueError(
                "Signed anchor authority key mismatch."
            )

        if not hmac.compare_digest(
            root_key,
            self.expected_root_public_key,
        ):
            raise ValueError(
                "Signed anchor root key mismatch."
            )

        signed_challenge = _require_hex32(
            document["challenge_hex"],
            "signed anchor challenge",
        )

        if not hmac.compare_digest(
            signed_challenge,
            challenge,
        ):
            raise ValueError(
                "Signed anchor challenge mismatch."
            )

        epoch = _require_integer(
            document["enrollment_epoch"],
            "signed anchor enrollment epoch",
        )

        revision = _require_integer(
            document["revision"],
            "signed anchor revision",
        )

        generation = _require_integer(
            document["generation"],
            "signed anchor generation",
        )

        fence = _require_integer(
            document["fence_token"],
            "signed anchor fencing token",
        )

        if epoch != self.expected_enrollment_epoch:
            raise ValueError(
                "Signed anchor enrollment epoch mismatch."
            )

        if (
            revision < self.minimum_revision
            or generation < self.minimum_generation
            or fence < self.minimum_fence_token
        ):
            raise ValueError(
                "Signed anchor state below caller-supplied floors."
            )

        try:
            Ed25519PublicKey.from_public_bytes(
                self.expected_anchor_public_key
            ).verify(
                signature,
                message,
            )

        except Exception as exc:
            raise ValueError(
                "Signed anchor Ed25519 verification failed."
            ) from exc

        return (
            authority_id,
            bytes(authority_key),
            root_id,
            bytes(root_key),
            epoch,
            revision,
            generation,
            fence,
        )

    @contextmanager
    def hold(self):
        caller_completed = False
        provider_released = False

        try:
            self.__post_init__()

            challenge = _fresh_challenge()

            with self.provider.hold(
                challenge=challenge
            ) as response:

                snapshot = self._verify(
                    response=response,
                    challenge=challenge,
                )

                yield snapshot

                caller_completed = True

            provider_released = True

            if not (
                caller_completed
                and provider_released
            ):
                raise ValueError(
                    "Signed anchor held verification incomplete."
                )

        except Exception as exc:
            raise ValueError(
                "Pinned signed anchor held read failed."
            ) from exc
