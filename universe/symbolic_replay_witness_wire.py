"""Strict JSON wire format for signed symbolic replay authority responses.

This is a transport serialization boundary, not runtime mapping state.
"""
import base64
import binascii
import json

from universe.symbolic_replay_receipt_witness import (
    SymbolicReplayReceiptWitness,
)
from universe.symbolic_replay_witness_authority import (
    SymbolicReplayWitnessRevision,
)
from universe.symbolic_replay_authenticated_witness import (
    SignedSymbolicReplayWitnessRevision,
)

_FORMAT = "adamshell.symbolic_replay_signed_witness"
_VERSION = 1


def _require_fields(value, fields, name):
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(f"Invalid {name} fields.")


def witness_to_wire(witness):
    if type(witness) is not SymbolicReplayReceiptWitness:
        raise TypeError("Witness must be canonical.")
    return {
        "universe_id": witness.universe_id,
        "batch_sha256": witness.batch_sha256,
        "receipt_ids": list(witness.receipt_ids),
    }


def witness_from_wire(value):
    _require_fields(
        value,
        {"universe_id", "batch_sha256", "receipt_ids"},
        "witness",
    )
    if type(value["receipt_ids"]) is not list:
        raise TypeError("Witness receipt IDs must be an array.")
    return SymbolicReplayReceiptWitness(
        universe_id=value["universe_id"],
        batch_sha256=value["batch_sha256"],
        receipt_ids=tuple(value["receipt_ids"]),
    )


def signed_to_wire(signed):
    if type(signed) is not SignedSymbolicReplayWitnessRevision:
        raise TypeError("Signed response must be canonical.")
    return {
        "format": _FORMAT,
        "version": _VERSION,
        "key_id": signed.key_id,
        "revision": signed.revision.revision,
        "witness": witness_to_wire(signed.revision.witness),
        "signature": base64.b64encode(
            signed.signature
        ).decode("ascii"),
    }


def signed_from_wire(value):
    _require_fields(
        value,
        {"format", "version", "key_id", "revision", "witness", "signature"},
        "signed witness",
    )
    if value["format"] != _FORMAT or type(value["version"]) is not int or value["version"] != _VERSION:
        raise ValueError("Unsupported signed witness wire version.")
    if type(value["signature"]) is not str:
        raise TypeError("Witness signature must be base64 text.")
    try:
        signature = base64.b64decode(
            value["signature"], validate=True,
        )
    except (binascii.Error, ValueError) as error:
        raise ValueError("Invalid witness signature encoding.") from error
    return SignedSymbolicReplayWitnessRevision(
        revision=SymbolicReplayWitnessRevision(
            revision=value["revision"],
            witness=witness_from_wire(value["witness"]),
        ),
        key_id=value["key_id"],
        signature=signature,
    )


def loads_strict(raw):
    """Reject duplicate JSON keys and nonstandard numeric values."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON field.")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("Nonstandard JSON constant.")

    return json.loads(
        raw, object_pairs_hook=unique, parse_constant=reject_constant,
    )


def dumps_canonical(value):
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False,
        allow_nan=False, separators=(",", ":"),
    ).encode("utf-8")
