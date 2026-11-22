"""A44 signed provisioning-generation floor protocol client.

Verifies fresh canonical Ed25519-signed responses from a caller-
provided authority. Binds an existing verified provisioning
snapshot only when its generation equals a signed authority read.

SECURITY LIMITS:
- The caller must independently authenticate the authority key.
- This module does not deploy or protect authority storage or keys.
- A signed response alone cannot prove durability, honest CAS,
  linearizability, exclusive access or operation retention.
- The provider hold must enforce its own consistency semantics.
- A previously constructed client does not automatically raise
  its minimum after CAS; the caller must retain updated pins.
- A signed CAS plus separate enrollment is not cross-store atomic.
"""

import hmac
import json
import os

from contextlib import contextmanager
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water as high_water,
)

from core.existence.history_receipt_trust_checkpoint_protected_provisioning import (
    PinnedHighWaterProvisioning,
)


_DOMAIN = "AdamShell/A44/provisioning-generation-floor/v1"
_VERSION = 1

_COMMON_FIELDS = frozenset({
    "domain",
    "version",
    "operation",
    "authority_id",
    "subject_id",
    "generation",
    "challenge_hex",
})

_CAS_FIELDS = _COMMON_FIELDS | frozenset({
    "operation_id",
    "expected_generation",
    "next_generation",
    "status",
})

_LOOKUP_FIELDS = _COMMON_FIELDS | frozenset({
    "operation_id",
    "status",
})


def _require_provider(authority):
    for name in (
        "hold",
        "advance_if_current",
        "lookup_operation",
    ):
        if not callable(getattr(authority, name, None)):
            raise ValueError(
                "Signed provisioning generation authority capability missing."
            )
    return authority


def _fresh_challenge():
    challenge = os.urandom(32)
    if type(challenge) is not bytes or len(challenge) != 32:
        raise ValueError("Provisioning generation challenge unavailable.")
    return challenge


def _parse_document(message, operation):
    fields = {
        "read": _COMMON_FIELDS,
        "cas": _CAS_FIELDS,
        "lookup": _LOOKUP_FIELDS,
    }.get(operation)
    if fields is None:
        raise ValueError("Unsupported provisioning generation operation.")

    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=(
                high_water.signed_read._reject_duplicate_properties
            ),
            parse_constant=(
                high_water.signed_read._reject_json_constant
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
            "Invalid provisioning generation signed JSON."
        ) from exc

    if (
        type(document) is not dict
        or set(document) != fields
        or canonical != message
    ):
        raise ValueError(
            "Noncanonical provisioning generation signed response."
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
            "Provisioning generation domain/version/operation mismatch."
        )

    return document


@dataclass(frozen=True, slots=True)
class PinnedSignedProvisioningGenerationClient:
    """Signed remote-floor *client*, not a protected authority."""

    authority: object
    expected_authority_id: str
    expected_authority_public_key: bytes
    expected_subject_id: str
    minimum_generation: int

    def __post_init__(self):
        _require_provider(self.authority)
        high_water._identity(
            self.expected_authority_id,
            "provisioning generation authority identity",
        )
        high_water._key(
            self.expected_authority_public_key,
            "provisioning generation authority public key",
        )
        high_water._identity(
            self.expected_subject_id,
            "provisioning generation subject identity",
        )
        high_water._counter(
            self.minimum_generation,
            "provisioning generation minimum",
        )

    @classmethod
    def from_authority(
        cls,
        *,
        authority,
        expected_authority_id,
        expected_authority_public_key,
        expected_subject_id,
        minimum_generation,
    ):
        try:
            return cls(
                authority=authority,
                expected_authority_id=expected_authority_id,
                expected_authority_public_key=(
                    expected_authority_public_key
                ),
                expected_subject_id=expected_subject_id,
                minimum_generation=minimum_generation,
            )
        except Exception as exc:
            raise ValueError(
                "Signed provisioning generation authority binding failed."
            ) from exc

    def _verify(self, *, response, challenge, operation):
        self.__post_init__()
        if type(challenge) is not bytes or len(challenge) != 32:
            raise ValueError("Invalid provisioning generation challenge.")

        message, signature = high_water._signed_pair(response)

        try:
            Ed25519PublicKey.from_public_bytes(
                self.expected_authority_public_key
            ).verify(signature, message)
        except Exception as exc:
            raise ValueError(
                "Untrusted provisioning generation response signature."
            ) from exc

        document = _parse_document(message, operation)

        signed_authority = high_water._identity(
            document["authority_id"],
            "signed provisioning generation authority",
        )
        signed_subject = high_water._identity(
            document["subject_id"],
            "signed provisioning generation subject",
        )
        if (
            signed_authority != self.expected_authority_id
            or signed_subject != self.expected_subject_id
        ):
            raise ValueError(
                "Signed provisioning generation identity mismatch."
            )

        signed_challenge = high_water.signed_read._require_hex32(
            document["challenge_hex"],
            "signed provisioning generation challenge",
        )
        if not hmac.compare_digest(signed_challenge, challenge):
            raise ValueError(
                "Signed provisioning generation challenge mismatch."
            )

        generation = high_water._counter(
            document["generation"],
            "signed provisioning generation",
        )
        if generation < self.minimum_generation:
            raise ValueError(
                "Signed provisioning generation below trusted minimum."
            )

        return generation, document

    @contextmanager
    def _hold_generation(self):
        self.__post_init__()
        challenge = _fresh_challenge()
        try:
            with self.authority.hold(challenge=challenge) as response:
                generation, _ = self._verify(
                    response=response,
                    challenge=challenge,
                    operation="read",
                )
                yield generation
        except Exception as exc:
            raise ValueError(
                "Protected provisioning generation read failed."
            ) from exc

    def read_generation(self):
        with self._hold_generation() as generation:
            return generation

    def bind_provisioning(self, *, source, manifest, signature):
        """Fail closed unless signed generation equals source pins.

        Keep the provider hold while the signed enrollment is checked.
        Actual atomicity requires an honest authority hold protocol.
        """
        try:
            with self._hold_generation() as generation:
                binding = PinnedHighWaterProvisioning.from_trusted_source(
                    source=source,
                    manifest=manifest,
                    signature=signature,
                )
                if binding.pins.provisioning_generation != generation:
                    raise ValueError(
                        "Provisioning generation differs from authority floor."
                    )
                return binding
        except Exception as exc:
            raise ValueError(
                "Provisioning bootstrap rejected by signed floor."
            ) from exc

    def advance_if_current(
        self,
        *,
        operation_id,
        expected_generation,
        next_generation,
    ):
        try:
            self.__post_init__()
            operation_id = high_water._operation_id(operation_id)
            expected = high_water._counter(
                expected_generation,
                "expected provisioning generation",
            )
            proposed = high_water._counter(
                next_generation,
                "next provisioning generation",
            )
            if (
                expected < self.minimum_generation
                or proposed != expected + 1
            ):
                raise ValueError(
                    "Provisioning generation CAS is not monotonic."
                )

            challenge = _fresh_challenge()
            response = self.authority.advance_if_current(
                operation_id=operation_id,
                expected_generation=expected,
                next_generation=proposed,
                challenge=challenge,
            )
            generation, doc = self._verify(
                response=response,
                challenge=challenge,
                operation="cas",
            )

            signed_op = high_water._operation_id(doc["operation_id"])
            signed_expected = high_water._counter(
                doc["expected_generation"],
                "signed CAS expected generation",
            )
            signed_next = high_water._counter(
                doc["next_generation"],
                "signed CAS next generation",
            )
            status = doc["status"]

            if (
                signed_op != operation_id
                or signed_expected != expected
                or signed_next != proposed
                or type(status) is not str
                or status not in ("committed", "rejected")
            ):
                raise ValueError(
                    "Signed provisioning generation CAS response mismatch."
                )
            if status != "committed":
                raise ValueError(
                    "Provisioning generation CAS was rejected."
                )
            if generation < proposed:
                raise ValueError(
                    "Signed CAS committed below requested generation."
                )
            return generation
        except Exception as exc:
            raise ValueError(
                "Signed provisioning generation CAS failed or ambiguous."
            ) from exc

    def lookup_operation(self, *, operation_id):
        try:
            self.__post_init__()
            operation_id = high_water._operation_id(operation_id)
            challenge = _fresh_challenge()
            response = self.authority.lookup_operation(
                operation_id=operation_id,
                challenge=challenge,
            )
            generation, doc = self._verify(
                response=response,
                challenge=challenge,
                operation="lookup",
            )
            signed_op = high_water._operation_id(doc["operation_id"])
            status = doc["status"]
            if (
                signed_op != operation_id
                or type(status) is not str
                or status not in ("committed", "unknown")
            ):
                raise ValueError(
                    "Signed provisioning generation lookup mismatch."
                )
            return status, generation
        except Exception as exc:
            raise ValueError(
                "Signed provisioning generation lookup failed."
            ) from exc
