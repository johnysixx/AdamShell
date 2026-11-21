"""A44 signed checkpoint anchor enrollment validation.

Verifies a canonical Ed25519-signed enrollment manifest against
caller-supplied, externally trusted provisioning identity and key.

This does NOT establish or securely provision that trust root.
The caller must obtain trusted_signer_public_key independently
of the manifest and of the untrusted anchor database.

High-water floors are immutable in-memory values, NOT durable.
Python objects are NOT in-process security boundaries.
No remote service, key isolation, rollback-resistant persistence,
checkpoint restoration or cross-store atomicity is provided.
"""

import hmac
import json

from dataclasses import InitVar, dataclass, replace

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

from core.existence.history_receipt_trust_checkpoint_anchor_cas_client import (
    PinnedSignedCheckpointAnchorCASClient,
)


_DOMAIN = "AdamShell/A44/anchor-enrollment/v1"
_VERSION = 1
_FACTORY_TOKEN = object()

_FIELDS = frozenset({
    "domain",
    "version",
    "operation",
    "signer_id",
    "anchor_id",
    "anchor_public_key_hex",
    "authority_id",
    "authority_public_key_hex",
    "root_id",
    "root_public_key_hex",
    "enrollment_epoch",
    "minimum_revision",
    "minimum_generation",
    "minimum_fence_token",
})


def _key(value, label):
    return signed_read._require_key(value, label)


def _integer(value, label):
    return signed_read._require_integer(value, label)


def _identity(value, label):
    return _require_identity(value, label)


def _signed_manifest_document(manifest):
    if (
        type(manifest) is not bytes
        or not manifest
        or len(manifest) > signed_read._MAX_MESSAGE_BYTES
    ):
        raise ValueError(
            "Invalid enrollment manifest encoding or size."
        )

    try:
        document = json.loads(
            manifest.decode("ascii"),
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
            "Invalid canonical enrollment manifest."
        ) from exc

    if (
        type(document) is not dict
        or set(document) != _FIELDS
        or manifest != canonical
    ):
        raise ValueError(
            "Enrollment manifest is noncanonical or has wrong fields."
        )

    if (
        type(document["domain"]) is not str
        or document["domain"] != _DOMAIN
        or type(document["version"]) is not int
        or document["version"] != _VERSION
        or type(document["operation"]) is not str
        or document["operation"] != "enroll"
    ):
        raise ValueError(
            "Enrollment domain, version or operation mismatch."
        )

    return document


def _manifest_fields(document):
    return {
        "signer_id": _identity(
            document["signer_id"],
            "manifest signer identity",
        ),
        "anchor_id": _identity(
            document["anchor_id"],
            "manifest anchor identity",
        ),
        "anchor_key": signed_read._require_hex32(
            document["anchor_public_key_hex"],
            "manifest anchor public key",
        ),
        "authority_id": _identity(
            document["authority_id"],
            "manifest authority identity",
        ),
        "authority_key": signed_read._require_hex32(
            document["authority_public_key_hex"],
            "manifest authority public key",
        ),
        "root_id": _identity(
            document["root_id"],
            "manifest root identity",
        ),
        "root_key": signed_read._require_hex32(
            document["root_public_key_hex"],
            "manifest root public key",
        ),
        "epoch": _integer(
            document["enrollment_epoch"],
            "manifest enrollment epoch",
        ),
        "revision": _integer(
            document["minimum_revision"],
            "manifest minimum revision",
        ),
        "generation": _integer(
            document["minimum_generation"],
            "manifest minimum generation",
        ),
        "fence": _integer(
            document["minimum_fence_token"],
            "manifest minimum fencing token",
        ),
    }


@dataclass(frozen=True, slots=True)
class TrustedSignedCheckpointAnchorEnrollment:
    """Immutable verified enrollment and client pin binding.

    Public construction without the factory token is rejected.
    This is a programming invariant, not an in-process trust boundary.
    """

    trusted_signer_id: str
    trusted_signer_public_key: bytes

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

    _factory_token: InitVar[object] = None

    def __post_init__(self, _factory_token):
        if _factory_token is not _FACTORY_TOKEN:
            raise ValueError(
                "Enrollment must originate from verified manifest."
            )

        for label, value in (
            ("trusted signer", self.trusted_signer_id),
            ("anchor", self.expected_anchor_id),
            ("authority", self.expected_authority_id),
            ("root", self.expected_root_id),
        ):
            _identity(value, label)

        for label, value in (
            (
                "trusted signer public key",
                self.trusted_signer_public_key,
            ),
            (
                "anchor public key",
                self.expected_anchor_public_key,
            ),
            (
                "authority public key",
                self.expected_authority_public_key,
            ),
            (
                "root public key",
                self.expected_root_public_key,
            ),
        ):
            _key(value, label)

        for label, value in (
            (
                "expected enrollment epoch",
                self.expected_enrollment_epoch,
            ),
            ("minimum revision", self.minimum_revision),
            ("minimum generation", self.minimum_generation),
            ("minimum fencing token", self.minimum_fence_token),
        ):
            _integer(value, label)

    @classmethod
    def from_signed_manifest(
        cls,
        *,
        manifest,
        signature,
        trusted_signer_id,
        trusted_signer_public_key,
        expected_anchor_id,
        expected_authority_id,
        expected_root_id,
        minimum_enrollment_epoch,
        minimum_revision,
        minimum_generation,
        minimum_fence_token,
    ):
        try:
            signer_id = _identity(
                trusted_signer_id,
                "trusted provisioning signer identity",
            )

            signer_key = _key(
                trusted_signer_public_key,
                "trusted provisioning signer public key",
            )

            anchor_id = _identity(
                expected_anchor_id,
                "expected anchor identity",
            )

            authority_id = _identity(
                expected_authority_id,
                "expected authority identity",
            )

            root_id = _identity(
                expected_root_id,
                "expected root identity",
            )

            external_epoch = _integer(
                minimum_enrollment_epoch,
                "trusted minimum enrollment epoch",
            )

            external_revision = _integer(
                minimum_revision,
                "trusted minimum revision",
            )

            external_generation = _integer(
                minimum_generation,
                "trusted minimum generation",
            )

            external_fence = _integer(
                minimum_fence_token,
                "trusted minimum fencing token",
            )

            if (
                type(signature) is not bytes
                or len(signature) != 64
            ):
                raise ValueError(
                    "Invalid enrollment Ed25519 signature."
                )

            document = _signed_manifest_document(manifest)
            fields = _manifest_fields(document)

            if (
                fields["signer_id"] != signer_id
                or fields["anchor_id"] != anchor_id
                or fields["authority_id"] != authority_id
                or fields["root_id"] != root_id
            ):
                raise ValueError(
                    "Enrollment identity binding mismatch."
                )

            if (
                fields["epoch"] < external_epoch
                or fields["revision"] < external_revision
                or fields["generation"] < external_generation
                or fields["fence"] < external_fence
            ):
                raise ValueError(
                    "Enrollment below externally trusted minima."
                )

            # The verifier key MUST come from the caller's
            # independently trusted provisioning input.
            # Never take it from the signed manifest.
            Ed25519PublicKey.from_public_bytes(
                signer_key
            ).verify(
                signature,
                manifest,
            )

            return cls(
                trusted_signer_id=signer_id,
                trusted_signer_public_key=signer_key,
                expected_anchor_id=anchor_id,
                expected_anchor_public_key=fields["anchor_key"],
                expected_authority_id=authority_id,
                expected_authority_public_key=fields["authority_key"],
                expected_root_id=root_id,
                expected_root_public_key=fields["root_key"],
                expected_enrollment_epoch=fields["epoch"],
                minimum_revision=fields["revision"],
                minimum_generation=fields["generation"],
                minimum_fence_token=fields["fence"],
                _factory_token=_FACTORY_TOKEN,
            )

        except Exception as exc:
            raise ValueError(
                "Trusted signed checkpoint anchor enrollment failed."
            ) from exc

    def _client_pins(self):
        self.__post_init__(_FACTORY_TOKEN)

        return {
            "expected_anchor_id": self.expected_anchor_id,
            "expected_anchor_public_key": (
                self.expected_anchor_public_key
            ),
            "expected_authority_id": self.expected_authority_id,
            "expected_authority_public_key": (
                self.expected_authority_public_key
            ),
            "expected_root_id": self.expected_root_id,
            "expected_root_public_key": self.expected_root_public_key,
            "expected_enrollment_epoch": (
                self.expected_enrollment_epoch
            ),
            "minimum_revision": self.minimum_revision,
            "minimum_generation": self.minimum_generation,
            "minimum_fence_token": self.minimum_fence_token,
        }

    def read_source(self, provider):
        return (
            signed_read.PinnedSignedCheckpointAnchorSource.from_provider(
                provider=provider,
                **self._client_pins(),
            )
        )

    def cas_client(self, provider):
        return PinnedSignedCheckpointAnchorCASClient.from_provider(
            provider=provider,
            **self._client_pins(),
        )

    def raise_floor(
        self,
        *,
        minimum_revision,
        minimum_generation,
        minimum_fence_token,
    ):
        try:
            self.__post_init__(_FACTORY_TOKEN)

            revision = _integer(
                minimum_revision,
                "new minimum revision",
            )

            generation = _integer(
                minimum_generation,
                "new minimum generation",
            )

            fence = _integer(
                minimum_fence_token,
                "new minimum fencing token",
            )

            if (
                revision < self.minimum_revision
                or generation < self.minimum_generation
                or fence < self.minimum_fence_token
            ):
                raise ValueError(
                    "Trusted enrollment floor cannot decrease."
                )

            # Immutable copy. No external persistence is claimed.
            return replace(
                self,
                minimum_revision=revision,
                minimum_generation=generation,
                minimum_fence_token=fence,
                _factory_token=_FACTORY_TOKEN,
            )

        except Exception as exc:
            raise ValueError(
                "Trusted enrollment floor advancement failed."
            ) from exc
