"""Experimental signed authority-key manifest verification.

An Ed25519 root public key and a minimum accepted manifest
epoch must originate from independently trusted sources.

This module authenticates a manifest against the SUPPLIED root.
It does not authenticate how the root or epoch was provisioned.

No automatic network enrollment, key generation, persistent
trust root, rollback protection, revocation service, or
publication authorization is implemented here.

Python objects are not an isolation boundary against
malicious code executing in the same process.
"""

import json
import re

from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from core.existence.history_receipt_trust_ed25519_verifier import (
    PinnedEd25519AuthorityVerifier,
)

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)


KEY_MANIFEST_DOMAIN = (
    "adam-shell.receipt-trust.authority-key-manifest"
)

KEY_MANIFEST_VERSION = 1

_MAX_MANIFEST_BYTES = 1_048_576
_MAX_AUTHORITY_KEYS = 4096

_HEX_PUBLIC_KEY = re.compile(r"[0-9a-f]{64}\Z")


def _reject_duplicate_properties(pairs):
    """Reject duplicate JSON properties at every nesting level."""

    result = {}

    for name, value in pairs:
        if name in result:
            raise ValueError(
                "Duplicate authority manifest JSON property."
            )

        result[name] = value

    return result


def _reject_nonfinite_constant(value):
    raise ValueError(
        "Non-finite JSON values are not permitted."
    )


def _canonical_manifest_document(message):
    """Parse only exact, unambiguous canonical ASCII JSON."""

    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=_reject_duplicate_properties,
            parse_constant=_reject_nonfinite_constant,
        )

        canonical = json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")

    except (ValueError, UnicodeError, TypeError) as exc:
        raise ValueError(
            "Invalid authority key manifest JSON."
        ) from exc

    if canonical != message:
        raise ValueError(
            "Authority key manifest is not canonical JSON."
        )

    if (
        type(document) is not dict
        or set(document) != {
            "domain",
            "version",
            "root_id",
            "epoch",
            "keys",
        }
    ):
        raise ValueError(
            "Unexpected authority key manifest schema."
        )

    if document["domain"] != KEY_MANIFEST_DOMAIN:
        raise ValueError(
            "Wrong authority key manifest domain."
        )

    if (
        type(document["version"]) is not int
        or document["version"] != KEY_MANIFEST_VERSION
    ):
        raise ValueError(
            "Unsupported authority key manifest version."
        )

    return document


def _validated_authority_keys(entries):
    """Require an explicit, sorted, unique key catalog."""

    if (
        type(entries) is not list
        or not entries
        or len(entries) > _MAX_AUTHORITY_KEYS
    ):
        raise ValueError(
            "Invalid authority key manifest catalog."
        )

    validated = []
    previous_identity = None

    for item in entries:
        if (
            type(item) is not dict
            or set(item) != {
                "authority_id",
                "public_key_hex",
            }
        ):
            raise ValueError(
                "Invalid authority key manifest entry."
            )

        authority_id = _require_identity(
            item["authority_id"],
            "authority identity",
        )

        # Strict ascending order rejects both unsorted
        # manifests and duplicate authority identities.
        if (
            previous_identity is not None
            and authority_id <= previous_identity
        ):
            raise ValueError(
                "Authority keys must be strictly sorted "
                "and unique."
            )

        encoded_key = item["public_key_hex"]

        if (
            type(encoded_key) is not str
            or _HEX_PUBLIC_KEY.fullmatch(encoded_key) is None
        ):
            raise ValueError(
                "Invalid Ed25519 public key hex encoding."
            )

        public_key_bytes = bytes.fromhex(encoded_key)

        try:
            Ed25519PublicKey.from_public_bytes(
                public_key_bytes
            )

        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Invalid authority Ed25519 public key."
            ) from exc

        validated.append(
            (authority_id, public_key_bytes)
        )

        previous_identity = authority_id

    return tuple(validated)


@dataclass(frozen=True, slots=True)
class VerifiedAuthorityKeyCatalog:
    """Structurally immutable verified manifest result.

    The factory verifies the signed manifest before creating
    an instance. However, public Python object construction
    is NOT proof of cryptographic provenance.

    Security-sensitive callers must control the creation
    boundary and independently authenticate root keys
    and minimum accepted epochs.
    """

    root_id: str
    epoch: int
    pinned_keys: tuple[tuple[str, bytes], ...]

    @classmethod
    def from_signed_manifest(
        cls,
        message,
        signature,
        *,
        trusted_root_id,
        trusted_root_public_key,
        minimum_epoch,
    ):
        """Verify signature, canonical schema and epoch floor.

        The minimum epoch is exclusive.

        The root key and floor are externally supplied trust
        inputs. This method cannot make them trustworthy.
        """

        _require_identity(
            trusted_root_id,
            "trusted root identity",
        )

        if (
            type(trusted_root_public_key) is not bytes
            or len(trusted_root_public_key) != 32
        ):
            raise ValueError(
                "Trusted Ed25519 root key must be "
                "exactly 32 immutable bytes."
            )

        if (
            type(minimum_epoch) is not int
            or minimum_epoch < 0
        ):
            raise ValueError(
                "Invalid minimum trusted manifest epoch."
            )

        if (
            type(message) is not bytes
            or not message
            or len(message) > _MAX_MANIFEST_BYTES
        ):
            raise ValueError(
                "Missing, oversized or invalid manifest bytes."
            )

        if (
            type(signature) is not bytes
            or len(signature) != 64
        ):
            raise ValueError(
                "Invalid manifest Ed25519 signature."
            )

        # Authenticate the raw bytes before parsing JSON.
        # A signature alone is insufficient when the root
        # public key came from an untrusted source.
        try:
            root_public = (
                Ed25519PublicKey.from_public_bytes(
                    trusted_root_public_key
                )
            )

            root_public.verify(
                signature,
                message,
            )

        except Exception as exc:
            raise ValueError(
                "Authority key manifest signature "
                "could not be verified."
            ) from exc

        document = _canonical_manifest_document(
            message
        )

        root_id = _require_identity(
            document["root_id"],
            "manifest root identity",
        )

        if root_id != trusted_root_id:
            raise ValueError(
                "Authority manifest root identity mismatch."
            )

        epoch = document["epoch"]

        if (
            type(epoch) is not int
            or epoch < 1
            or epoch <= minimum_epoch
        ):
            raise ValueError(
                "Stale or invalid authority manifest epoch."
            )

        pinned_keys = _validated_authority_keys(
            document["keys"]
        )

        return cls(
            root_id=root_id,
            epoch=epoch,
            pinned_keys=pinned_keys,
        )

    def make_verifier(self):
        """Build a detached verifier from the catalog keys.

        Do not treat direct construction of this catalog
        as trusted provenance.
        """

        return (
            PinnedEd25519AuthorityVerifier.from_pinned_keys(
                dict(self.pinned_keys)
            )
        )
