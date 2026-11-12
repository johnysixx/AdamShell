"""Authenticate data-only history effect receipts."""

import hashlib
import hmac
import json
import re

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum


_DOMAIN = b"adam-shell/a44/effect-receipt/v1\x00"


@dataclass(frozen=True, slots=True)
class SignedEffectReceipt:
    cycle_id: str
    branch_id: str
    effect_id: str
    source_id: str
    nonce: str
    receipt_id: str
    mac_sha256: str


def _wire(receipt):
    fields = (
        receipt.cycle_id,
        receipt.branch_id,
        receipt.effect_id,
        receipt.source_id,
        receipt.nonce,
    )

    if any(
        type(item) is not str
        or not item
        or len(item) > 1024
        for item in fields
    ):
        raise ValueError("Invalid signed receipt claims.")

    if len(receipt.nonce) > 256:
        raise ValueError("Receipt nonce is too long.")

    payload = {
        "version": 1,
        "cycle_id": receipt.cycle_id,
        "branch_id": receipt.branch_id,
        "effect_id": receipt.effect_id,
        "source_id": receipt.source_id,
        "nonce": receipt.nonce,
    }

    return _DOMAIN + json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _verify_v1_receipt(
    receipt,
    *,
    cycle_id,
    branch_id,
    effect_id,
    expected_source_id,
    receipt_id,
    trusted_provider_keys,
):
    """Verify a caller-pinned provider HMAC; never mutate state."""

    if type(receipt) is not SignedEffectReceipt:
        return False

    if (
        receipt.cycle_id != cycle_id
        or receipt.branch_id != branch_id
        or receipt.effect_id != effect_id
        or receipt.source_id != expected_source_id
        or receipt.receipt_id != receipt_id
    ):
        return False

    if not isinstance(trusted_provider_keys, Mapping):
        return False

    secret = trusted_provider_keys.get(expected_source_id)

    if type(secret) is not bytes or len(secret) < 32:
        return False

    if (
        type(receipt.receipt_id) is not str
        or type(receipt.mac_sha256) is not str
        or not receipt.receipt_id.isascii()
        or not receipt.mac_sha256.isascii()
        or len(receipt.mac_sha256) != 64
    ):
        return False

    try:
        wire = _wire(receipt)
    except (TypeError, ValueError, OverflowError):
        return False

    expected_id = (
        "r1-" + hashlib.sha256(wire).hexdigest()
    )

    if not hmac.compare_digest(
        receipt.receipt_id, expected_id
    ):
        return False

    expected_mac = hmac.new(
        secret,
        wire,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        receipt.mac_sha256,
        expected_mac,
    )


# Version 2 retains version 1's exact wire format and verification path.
# New receipts bind the key generation to the authenticated payload.
_DOMAIN_V2 = b"adam-shell/a44/effect-receipt/v2\x00"
_KEY_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}")


class ReceiptKeyStatus(str, Enum):
    ACTIVE = "active"
    VERIFY_ONLY = "verify_only"
    REVOKED = "revoked"


@dataclass(frozen=True, slots=True)
class TrustedReceiptKey:
    key_id: str
    secret: bytes
    status: ReceiptKeyStatus


@dataclass(frozen=True, slots=True)
class ProviderReceiptKeyRing:
    """Keys provisioned by a trusted caller, never extracted from receipts.

    legacy_key_id explicitly selects one version-1 verification key.
    No trial verification or silent fallback to another key is allowed.
    """

    keys: tuple[TrustedReceiptKey, ...]
    legacy_key_id: str | None = None


@dataclass(frozen=True, slots=True)
class VersionedSignedEffectReceipt:
    cycle_id: str
    branch_id: str
    effect_id: str
    source_id: str
    nonce: str
    key_id: str
    receipt_id: str
    mac_sha256: str


def _valid_key_id(value):
    return (
        type(value) is str
        and _KEY_ID_PATTERN.fullmatch(value) is not None
    )


def _lookup_trusted_key(ring, key_id):
    """Fail closed for any malformed or ambiguous trusted key registry."""
    if (
        type(ring) is not ProviderReceiptKeyRing
        or type(ring.keys) is not tuple
        or not ring.keys
        or not _valid_key_id(key_id)
    ):
        return None

    if (
        ring.legacy_key_id is not None
        and not _valid_key_id(ring.legacy_key_id)
    ):
        return None

    seen = set()
    selected = None

    for record in ring.keys:
        if (
            type(record) is not TrustedReceiptKey
            or not _valid_key_id(record.key_id)
            or record.key_id in seen
            or type(record.secret) is not bytes
            or len(record.secret) < 32
            or type(record.status) is not ReceiptKeyStatus
        ):
            return None

        seen.add(record.key_id)

        if record.key_id == key_id:
            selected = record

    if (
        selected is None
        or selected.status is ReceiptKeyStatus.REVOKED
    ):
        return None

    # ACTIVE and VERIFY_ONLY may verify signatures.
    # This module never issues new signatures.
    return selected.secret


def _wire_v2(receipt):
    claims = (
        receipt.cycle_id,
        receipt.branch_id,
        receipt.effect_id,
        receipt.source_id,
        receipt.nonce,
    )

    if any(
        type(item) is not str
        or not item
        or len(item) > 1024
        for item in claims
    ):
        raise ValueError("Invalid version-2 receipt claims.")

    if len(receipt.nonce) > 256 or not _valid_key_id(receipt.key_id):
        raise ValueError("Invalid nonce or key identifier.")

    payload = {
        "version": 2,
        "cycle_id": receipt.cycle_id,
        "branch_id": receipt.branch_id,
        "effect_id": receipt.effect_id,
        "source_id": receipt.source_id,
        "nonce": receipt.nonce,
        "key_id": receipt.key_id,
    }

    return _DOMAIN_V2 + json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _verify_v2_receipt(
    receipt,
    *,
    cycle_id,
    branch_id,
    effect_id,
    expected_source_id,
    receipt_id,
    trusted_provider_keys,
):
    if (
        receipt.cycle_id != cycle_id
        or receipt.branch_id != branch_id
        or receipt.effect_id != effect_id
        or receipt.source_id != expected_source_id
        or receipt.receipt_id != receipt_id
        or not isinstance(trusted_provider_keys, Mapping)
    ):
        return False

    ring = trusted_provider_keys.get(expected_source_id)
    secret = _lookup_trusted_key(ring, receipt.key_id)

    if secret is None:
        return False

    if (
        type(receipt.receipt_id) is not str
        or type(receipt.mac_sha256) is not str
        or not receipt.receipt_id.isascii()
        or not receipt.mac_sha256.isascii()
        or len(receipt.mac_sha256) != 64
    ):
        return False

    try:
        wire = _wire_v2(receipt)
    except (TypeError, ValueError, OverflowError):
        return False

    digest = "r2-" + hashlib.sha256(wire).hexdigest()

    if not hmac.compare_digest(receipt.receipt_id, digest):
        return False

    expected_mac = hmac.new(
        secret,
        wire,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(receipt.mac_sha256, expected_mac)


def verify_signed_receipt(
    receipt,
    *,
    cycle_id,
    branch_id,
    effect_id,
    expected_source_id,
    receipt_id,
    trusted_provider_keys,
):
    """Fail-closed v1/v2 verification with caller-pinned trust anchors.

    v1: legacy bytes remain compatible. A key ring requires one explicit
    legacy_key_id; other versions are NEVER tried.
    v2: key_id is signed and selects exactly one trusted provider key.
    Revoked keys never verify. This grants no execution/retry authority.
    """
    if type(receipt) is VersionedSignedEffectReceipt:
        return _verify_v2_receipt(
            receipt,
            cycle_id=cycle_id,
            branch_id=branch_id,
            effect_id=effect_id,
            expected_source_id=expected_source_id,
            receipt_id=receipt_id,
            trusted_provider_keys=trusted_provider_keys,
        )

    if type(receipt) is not SignedEffectReceipt:
        return False

    if not isinstance(trusted_provider_keys, Mapping):
        return False

    provider_key = trusted_provider_keys.get(expected_source_id)

    if type(provider_key) is ProviderReceiptKeyRing:
        if provider_key.legacy_key_id is None:
            return False

        secret = _lookup_trusted_key(
            provider_key,
            provider_key.legacy_key_id,
        )

        if secret is None:
            return False

        trusted_provider_keys = {expected_source_id: secret}

    # Original version-1 verifier and wire encoding are unchanged.
    return _verify_v1_receipt(
        receipt,
        cycle_id=cycle_id,
        branch_id=branch_id,
        effect_id=effect_id,
        expected_source_id=expected_source_id,
        receipt_id=receipt_id,
        trusted_provider_keys=trusted_provider_keys,
    )
