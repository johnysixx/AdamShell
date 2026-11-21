"""A44 signed protected high-water protocol client.

Verifies canonical Ed25519-signed read, CAS and operation lookup
responses from a caller-provided high-water authority.

The provider and the store signing public key are externally
supplied. This module does NOT prove honest CAS, linearizability,
independent deployment, operation retention or physical durability.

SECURITY LIMITS:
- Trusted enrollment and store key pins must come from a
  genuinely trusted provisioning boundary.
- A valid signed response does not prove durable publication.
- Rollback protection requires independently preserved floors.
- CAS timeout or verification failure is ambiguous: no auto-retry.
- Lookup "unknown" does not authorize automatic CAS retry.
- Operation IDs must be preserved across caller restarts.
- Python objects are not in-process security boundaries.
- No cross-store atomicity, restoration or republication.
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

from core.existence import (
    history_receipt_trust_checkpoint_pinned_anchor_client
    as signed_read
)

from core.existence import (
    history_receipt_trust_checkpoint_anchor_cas_client
    as anchor_cas
)

from core.existence.history_receipt_trust_checkpoint_anchor_trusted_enrollment import (
    TrustedSignedCheckpointAnchorEnrollment,
)


_DOMAIN = "AdamShell/A44/protected-high-water/v1"
_VERSION = 1
_MAX = (1 << 63) - 1
_MAX_MESSAGE_BYTES = 4096

_COMMON_FIELDS = frozenset({
    "domain",
    "version",
    "operation",
    "store_id",
    "anchor_id",
    "anchor_public_key_hex",
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

_CAS_FIELDS = _COMMON_FIELDS | frozenset({
    "operation_id",
    "expected_revision",
    "next_revision",
    "expected_generation",
    "expected_fence_token",
    "status",
})

_LOOKUP_FIELDS = _COMMON_FIELDS | frozenset({
    "operation_id",
    "status",
})


def _identity(value, label):
    return _require_identity(value, label)


def _key(value, label):
    return signed_read._require_key(value, label)


def _counter(value, label):
    return signed_read._require_integer(value, label)


def _operation_id(value):
    return anchor_cas._require_operation_id(value)


def _fresh_challenge():
    challenge = os.urandom(32)

    if type(challenge) is not bytes or len(challenge) != 32:
        raise ValueError(
            "Fresh high-water challenge unavailable."
        )

    return challenge


def _provider(value):
    if not callable(getattr(value, "hold", None)):
        raise ValueError(
            "Protected high-water signed read unavailable."
        )

    if not callable(
        getattr(value, "advance_if_current", None)
    ):
        raise ValueError(
            "Protected high-water CAS unavailable."
        )

    if not callable(
        getattr(value, "lookup_operation", None)
    ):
        raise ValueError(
            "Protected high-water operation lookup unavailable."
        )

    return value


def _signed_pair(response):
    if type(response) is not tuple or len(response) != 2:
        raise ValueError(
            "Invalid high-water signed response pair."
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
            "Invalid high-water signed response encoding."
        )

    return message, signature


def _parse_document(message, operation):
    expected_fields = {
        "read": _COMMON_FIELDS,
        "cas": _CAS_FIELDS,
        "lookup": _LOOKUP_FIELDS,
    }.get(operation)

    if expected_fields is None:
        raise ValueError(
            "Unsupported high-water response operation."
        )

    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=(
                signed_read._reject_duplicate_properties
            ),
            parse_constant=(
                signed_read._reject_json_constant
            ),
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
            "Invalid high-water canonical JSON."
        ) from exc

    if (
        type(document) is not dict
        or set(document) != expected_fields
        or message != canonical
    ):
        raise ValueError(
            "Noncanonical or unexpected high-water document."
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
            "High-water domain/version/operation mismatch."
        )

    return document


@dataclass(frozen=True, slots=True)
class PinnedSignedProtectedHighWaterClient:
    """Signed high-water client, not an authority implementation."""

    provider: object
    enrollment: TrustedSignedCheckpointAnchorEnrollment

    expected_store_id: str
    expected_store_public_key: bytes

    minimum_revision: int
    minimum_generation: int
    minimum_fence_token: int

    def __post_init__(self):
        _provider(self.provider)

        if type(self.enrollment) is not (
            TrustedSignedCheckpointAnchorEnrollment
        ):
            raise ValueError(
                "Expected canonical verified enrollment."
            )

        pins = self.enrollment._client_pins()

        _identity(
            self.expected_store_id,
            "protected high-water store identity",
        )

        _key(
            self.expected_store_public_key,
            "protected high-water store signing key",
        )

        revision = _counter(
            self.minimum_revision,
            "protected minimum revision",
        )

        generation = _counter(
            self.minimum_generation,
            "protected minimum generation",
        )

        fence = _counter(
            self.minimum_fence_token,
            "protected minimum fencing token",
        )

        if (
            revision < pins["minimum_revision"]
            or generation < pins["minimum_generation"]
            or fence < pins["minimum_fence_token"]
        ):
            raise ValueError(
                "High-water minima below verified enrollment."
            )

    @classmethod
    def from_provider(
        cls,
        *,
        provider,
        enrollment,
        expected_store_id,
        expected_store_public_key,
        minimum_revision,
        minimum_generation,
        minimum_fence_token,
    ):
        try:
            return cls(
                provider=provider,
                enrollment=enrollment,
                expected_store_id=expected_store_id,
                expected_store_public_key=(
                    expected_store_public_key
                ),
                minimum_revision=minimum_revision,
                minimum_generation=minimum_generation,
                minimum_fence_token=minimum_fence_token,
            )

        except Exception as exc:
            raise ValueError(
                "Protected high-water client binding failed."
            ) from exc

    def _verify(
        self,
        *,
        response,
        challenge,
        operation,
    ):
        self.__post_init__()

        if type(challenge) is not bytes or len(challenge) != 32:
            raise ValueError(
                "Invalid high-water response challenge."
            )

        message, signature = _signed_pair(response)

        try:
            Ed25519PublicKey.from_public_bytes(
                self.expected_store_public_key
            ).verify(
                signature,
                message,
            )

        except Exception as exc:
            raise ValueError(
                "Untrusted high-water response signature."
            ) from exc

        document = _parse_document(
            message,
            operation,
        )

        pins = self.enrollment._client_pins()

        signed_store_id = _identity(
            document["store_id"],
            "signed high-water store identity",
        )

        signed_anchor_id = _identity(
            document["anchor_id"],
            "signed anchor identity",
        )

        signed_authority_id = _identity(
            document["authority_id"],
            "signed authority identity",
        )

        signed_root_id = _identity(
            document["root_id"],
            "signed root identity",
        )

        if (
            signed_store_id != self.expected_store_id
            or signed_anchor_id != pins["expected_anchor_id"]
            or signed_authority_id != pins["expected_authority_id"]
            or signed_root_id != pins["expected_root_id"]
        ):
            raise ValueError(
                "Signed high-water identity mismatch."
            )

        key_bindings = (
            (
                "anchor_public_key_hex",
                "expected_anchor_public_key",
            ),
            (
                "authority_public_key_hex",
                "expected_authority_public_key",
            ),
            (
                "root_public_key_hex",
                "expected_root_public_key",
            ),
        )

        for document_field, pin_field in key_bindings:
            signed_key = signed_read._require_hex32(
                document[document_field],
                document_field,
            )

            if not hmac.compare_digest(
                signed_key,
                pins[pin_field],
            ):
                raise ValueError(
                    "Signed high-water identity key mismatch."
                )

        epoch = _counter(
            document["enrollment_epoch"],
            "signed enrollment epoch",
        )

        if epoch != pins["expected_enrollment_epoch"]:
            raise ValueError(
                "Signed high-water enrollment epoch mismatch."
            )

        signed_challenge = signed_read._require_hex32(
            document["challenge_hex"],
            "signed high-water challenge",
        )

        if not hmac.compare_digest(
            signed_challenge,
            challenge,
        ):
            raise ValueError(
                "Signed high-water challenge mismatch."
            )

        floor = (
            _counter(
                document["revision"],
                "signed high-water revision",
            ),
            _counter(
                document["generation"],
                "signed high-water generation",
            ),
            _counter(
                document["fence_token"],
                "signed high-water fencing token",
            ),
        )

        if (
            floor[0] < self.minimum_revision
            or floor[1] < self.minimum_generation
            or floor[2] < self.minimum_fence_token
        ):
            raise ValueError(
                "Signed high-water floor below trusted minimum."
            )

        return floor, document

    @contextmanager
    def hold_floor(self):
        self.__post_init__()
        challenge = _fresh_challenge()

        # Keep the provider's hold context alive while
        # the caller consumes the verified floor.
        with self.provider.hold(
            challenge=challenge
        ) as response:
            floor, _ = self._verify(
                response=response,
                challenge=challenge,
                operation="read",
            )

            yield floor

    def advance_if_current(
        self,
        *,
        operation_id,
        expected_revision,
        next_revision,
        expected_generation,
        expected_fence_token,
    ):
        self.__post_init__()

        operation_id = _operation_id(operation_id)

        old = _counter(
            expected_revision,
            "expected high-water revision",
        )

        new = _counter(
            next_revision,
            "next high-water revision",
        )

        generation = _counter(
            expected_generation,
            "expected high-water generation",
        )

        fence = _counter(
            expected_fence_token,
            "expected high-water fencing token",
        )

        if (
            new <= old
            or generation >= _MAX
            or fence >= _MAX
            or old < self.minimum_revision
            or generation < self.minimum_generation
            or fence < self.minimum_fence_token
        ):
            raise ValueError(
                "Invalid high-water CAS preconditions."
            )

        challenge = _fresh_challenge()

        # No retry: a failure may occur AFTER a durable
        # publication in the external provider.
        try:
            response = self.provider.advance_if_current(
                operation_id=operation_id,
                expected_revision=old,
                next_revision=new,
                expected_generation=generation,
                expected_fence_token=fence,
                challenge=challenge,
            )

            floor, document = self._verify(
                response=response,
                challenge=challenge,
                operation="cas",
            )

            signed_id = _operation_id(
                document["operation_id"]
            )

            signed_request = (
                _counter(
                    document["expected_revision"],
                    "signed expected revision",
                ),
                _counter(
                    document["next_revision"],
                    "signed next revision",
                ),
                _counter(
                    document["expected_generation"],
                    "signed expected generation",
                ),
                _counter(
                    document["expected_fence_token"],
                    "signed expected fence",
                ),
            )

            if (
                signed_id != operation_id
                or signed_request != (
                    old,
                    new,
                    generation,
                    fence,
                )
            ):
                raise ValueError(
                    "Signed high-water CAS request mismatch."
                )

            status = document["status"]

            if type(status) is not str:
                raise ValueError(
                    "Invalid signed high-water CAS status."
                )

            if status == "rejected":
                raise ValueError(
                    "High-water CAS rejected by provider."
                )

            if status != "committed":
                raise ValueError(
                    "Unexpected high-water CAS status."
                )

            if floor != (
                new,
                generation + 1,
                fence + 1,
            ):
                raise ValueError(
                    "Signed committed high-water state mismatch."
                )

            # A historical idempotent operation may return
            # its original committed state. It must not
            # overwrite any separately held current floor.
            return floor

        except Exception as exc:
            raise ValueError(
                "Protected high-water CAS failed or is ambiguous."
            ) from exc

    def lookup_operation(self, *, operation_id):
        self.__post_init__()

        operation_id = _operation_id(operation_id)
        challenge = _fresh_challenge()

        try:
            response = self.provider.lookup_operation(
                operation_id=operation_id,
                challenge=challenge,
            )

            floor, document = self._verify(
                response=response,
                challenge=challenge,
                operation="lookup",
            )

            signed_id = _operation_id(
                document["operation_id"]
            )

            if signed_id != operation_id:
                raise ValueError(
                    "Signed operation lookup identity mismatch."
                )

            status = document["status"]

            if (
                type(status) is not str
                or status not in ("committed", "unknown")
            ):
                raise ValueError(
                    "Invalid signed operation lookup status."
                )

            # "Unknown" is not proof that a prior write
            # did not commit; no automatic retry is allowed.
            return status, floor

        except Exception as exc:
            raise ValueError(
                "Protected high-water operation lookup failed."
            ) from exc
