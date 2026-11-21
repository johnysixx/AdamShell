"""A44 signed checkpoint anchor CAS and operation lookup client.

Verifies caller-pinned signed CAS and lookup responses.

SECURITY LIMITATIONS:
- Caller-provided trust pins are not independent enrollment.
- A valid signature cannot prove honest CAS or durable publication.
- The backend must independently provide linearizable CAS,
  operation ID retention, crash durability and rollback resistance.
- An ambiguous CAS failure is not proof of rollback.
- Lookup "unknown" does not authorize automatic retry.
- Operation IDs must survive caller restarts outside this client.
- No cross-store atomicity, checkpoint restore or republication.
- Python objects are not in-process security boundaries.
"""

import hmac
import json
import re

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


_OPERATION_ID = re.compile(r"[0-9a-f]{32}\Z")

_COMMON_FIELDS = signed_read._FIELDS

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


def _require_operation_id(value):
    if (
        type(value) is not str
        or _OPERATION_ID.fullmatch(value) is None
    ):
        raise ValueError(
            "Operation ID must contain exactly 32 lowercase hex characters."
        )

    return value


def _require_capabilities(provider):
    signed_read._require_provider(provider)

    if not callable(
        getattr(provider, "advance_if_current", None)
    ):
        raise ValueError(
            "Anchor CAS operation unavailable."
        )

    if not callable(
        getattr(provider, "lookup_operation", None)
    ):
        raise ValueError(
            "Anchor operation lookup unavailable."
        )

    return provider


def _parse_operation_document(message, operation):
    expected_fields = (
        _CAS_FIELDS
        if operation == "cas"
        else _LOOKUP_FIELDS
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
            "Invalid signed anchor operation JSON."
        ) from exc

    if (
        type(document) is not dict
        or set(document) != expected_fields
        or canonical != message
    ):
        raise ValueError(
            "Noncanonical or unexpected anchor operation document."
        )

    if (
        type(document["domain"]) is not str
        or document["domain"] != signed_read._DOMAIN
        or type(document["version"]) is not int
        or document["version"] != signed_read._VERSION
        or type(document["operation"]) is not str
        or document["operation"] != operation
    ):
        raise ValueError(
            "Signed anchor operation domain/version mismatch."
        )

    return document


class PinnedSignedCheckpointAnchorCASClient(
    signed_read.PinnedSignedCheckpointAnchorSource
):
    """Signed CAS client; no backend durability guarantee."""

    def __post_init__(self):
        signed_read.PinnedSignedCheckpointAnchorSource.__post_init__(
            self
        )

        _require_capabilities(
            self.provider
        )

    def _verify_operation(
        self,
        *,
        response,
        challenge,
        operation,
        operation_id,
    ):
        self.__post_init__()

        if (
            type(challenge) is not bytes
            or len(challenge) != 32
        ):
            raise ValueError(
                "Invalid signed operation challenge."
            )

        message, signature = (
            signed_read._require_signed_pair(response)
        )

        document = _parse_operation_document(
            message,
            operation,
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

        authority_key = signed_read._require_hex32(
            document["authority_public_key_hex"],
            "signed authority public key",
        )

        root_key = signed_read._require_hex32(
            document["root_public_key_hex"],
            "signed root public key",
        )

        if not hmac.compare_digest(
            authority_key,
            self.expected_authority_public_key,
        ):
            raise ValueError(
                "Signed authority public key mismatch."
            )

        if not hmac.compare_digest(
            root_key,
            self.expected_root_public_key,
        ):
            raise ValueError(
                "Signed root public key mismatch."
            )

        signed_challenge = signed_read._require_hex32(
            document["challenge_hex"],
            "signed operation challenge",
        )

        if not hmac.compare_digest(
            signed_challenge,
            challenge,
        ):
            raise ValueError(
                "Signed operation challenge mismatch."
            )

        signed_id = _require_operation_id(
            document["operation_id"]
        )

        if signed_id != operation_id:
            raise ValueError(
                "Signed operation ID mismatch."
            )

        epoch = signed_read._require_integer(
            document["enrollment_epoch"],
            "signed enrollment epoch",
        )

        revision = signed_read._require_integer(
            document["revision"],
            "signed revision",
        )

        generation = signed_read._require_integer(
            document["generation"],
            "signed generation",
        )

        fence = signed_read._require_integer(
            document["fence_token"],
            "signed fencing token",
        )

        if epoch != self.expected_enrollment_epoch:
            raise ValueError(
                "Signed enrollment epoch mismatch."
            )

        if (
            revision < self.minimum_revision
            or generation < self.minimum_generation
            or fence < self.minimum_fence_token
        ):
            raise ValueError(
                "Signed operation state below pinned floors."
            )

        status = document["status"]

        if type(status) is not str:
            raise ValueError(
                "Invalid signed operation status type."
            )

        if operation == "cas":
            if status not in (
                "committed",
                "rejected",
            ):
                raise ValueError(
                    "Invalid signed CAS status."
                )

        elif operation == "lookup":
            if status not in (
                "committed",
                "unknown",
            ):
                raise ValueError(
                    "Invalid signed lookup status."
                )

        else:
            raise ValueError(
                "Unsupported signed operation."
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
                "Signed anchor operation Ed25519 verification failed."
            ) from exc

        snapshot = (
            authority_id,
            bytes(authority_key),
            root_id,
            bytes(root_key),
            epoch,
            revision,
            generation,
            fence,
        )

        return document, status, snapshot

    def advance_if_current(
        self,
        *,
        operation_id,
        expected_revision,
        next_revision,
        expected_generation,
        expected_fence_token,
    ):
        """One signed CAS attempt; NEVER retries automatically."""

        try:
            self.__post_init__()

            operation_id = _require_operation_id(
                operation_id
            )

            expected_revision = signed_read._require_integer(
                expected_revision,
                "expected CAS revision",
            )

            next_revision = signed_read._require_integer(
                next_revision,
                "next CAS revision",
            )

            expected_generation = signed_read._require_integer(
                expected_generation,
                "expected CAS generation",
            )

            expected_fence_token = signed_read._require_integer(
                expected_fence_token,
                "expected CAS fencing token",
            )

            if next_revision <= expected_revision:
                raise ValueError(
                    "CAS revision must increase."
                )

            if (
                expected_revision < self.minimum_revision
                or expected_generation < self.minimum_generation
                or expected_fence_token < self.minimum_fence_token
            ):
                raise ValueError(
                    "CAS request below caller-supplied floors."
                )

            challenge = signed_read._fresh_challenge()

            # Exactly one provider invocation.
            # A backend failure may happen AFTER commit.
            # Never infer rollback and never retry here.
            response = self.provider.advance_if_current(
                operation_id=operation_id,
                expected_revision=expected_revision,
                next_revision=next_revision,
                expected_generation=expected_generation,
                expected_fence_token=expected_fence_token,
                challenge=challenge,
            )

            document, status, snapshot = (
                self._verify_operation(
                    response=response,
                    challenge=challenge,
                    operation="cas",
                    operation_id=operation_id,
                )
            )

            signed_request = (
                signed_read._require_integer(
                    document["expected_revision"],
                    "signed expected CAS revision",
                ),
                signed_read._require_integer(
                    document["next_revision"],
                    "signed next CAS revision",
                ),
                signed_read._require_integer(
                    document["expected_generation"],
                    "signed expected CAS generation",
                ),
                signed_read._require_integer(
                    document["expected_fence_token"],
                    "signed expected CAS fencing token",
                ),
            )

            requested = (
                expected_revision,
                next_revision,
                expected_generation,
                expected_fence_token,
            )

            if signed_request != requested:
                raise ValueError(
                    "Signed CAS request binding mismatch."
                )

            if status != "committed":
                raise ValueError(
                    "Signed CAS did not report a commit."
                )

            if (
                snapshot[5] != next_revision
                or snapshot[6] <= expected_generation
                or snapshot[7] <= expected_fence_token
            ):
                raise ValueError(
                    "Signed CAS committed state inconsistent."
                )

            return snapshot

        except Exception as exc:
            # All failures remain fail-closed.
            # Even invalid acknowledgements may follow a real commit.
            raise ValueError(
                "Pinned signed anchor CAS failed or is ambiguous."
            ) from exc

    def lookup_operation(
        self,
        *,
        operation_id,
    ):
        """Signed lookup; unknown is never a retry permit."""

        try:
            self.__post_init__()

            operation_id = _require_operation_id(
                operation_id
            )

            challenge = signed_read._fresh_challenge()

            response = self.provider.lookup_operation(
                operation_id=operation_id,
                challenge=challenge,
            )

            _, status, snapshot = self._verify_operation(
                response=response,
                challenge=challenge,
                operation="lookup",
                operation_id=operation_id,
            )

            # Committed is a signed provider assertion.
            # Unknown does NOT prove the operation was not committed.
            return status, snapshot

        except Exception as exc:
            raise ValueError(
                "Pinned signed anchor operation lookup failed."
            ) from exc
