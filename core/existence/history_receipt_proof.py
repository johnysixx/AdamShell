"""Authenticate data-only history effect receipts."""

import hashlib
import hmac
import json

from collections.abc import Mapping
from dataclasses import dataclass


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
