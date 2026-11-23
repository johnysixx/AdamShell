"""A44 pinned signed deployment-floor wire client, byte-only transport.

The client retains only public trust pins, never the floor signing key or the
SQLite state. The exchange implementation is supplied by its caller; no
network transport, TLS, writer authorization, independent storage, secure pin
distribution, or cross-store transaction is provided by this client.
The remote signed read is a snapshot, not a distributed locking hold.
"""

import hmac
import json
import re
from contextlib import contextmanager
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water as high_water,
)
from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor
    as floor,
)

_WIRE_DOMAIN = "AdamShell/A44/remote-floor-transport/v1"
_WIRE_VERSION = 1
_MAX_WIRE_BYTES = 16384
_MAX_SIGNED_BYTES = 4096
_KEY_HEX = re.compile(r"[0-9a-f]{64}\Z")
_SIGNATURE_HEX = re.compile(r"[0-9a-f]{128}\Z")
_MESSAGE_HEX = re.compile(r"[0-9a-f]{2,8192}\Z")
_BASE = frozenset({
    "domain", "version", "operation", "floor_id", "subject_id", "challenge_hex",
})
_CAS = _BASE | frozenset({
    "operation_id", "expected_epoch", "next_epoch",
    "expected_minimum_generation", "next_minimum_generation",
})
_LOOKUP = _BASE | frozenset({"operation_id"})
_READ_REPLY = floor._FIELDS
_CAS_REPLY = _READ_REPLY | frozenset({
    "operation_id", "expected_epoch", "next_epoch",
    "expected_minimum_generation", "next_minimum_generation", "status",
})
_LOOKUP_REPLY = _READ_REPLY | frozenset({"operation_id", "status"})


def _reject_duplicates(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("Duplicate remote floor JSON property.")
        result[name] = value
    return result


def _reject_constant(_value):
    raise ValueError("Nonfinite remote floor JSON constant.")


def _canonical(document):
    return json.dumps(
        document, sort_keys=True, ensure_ascii=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("ascii")


def _parse(payload, *, maximum):
    if type(payload) is not bytes or not payload or len(payload) > maximum:
        raise ValueError("Invalid remote floor wire payload size or type.")
    try:
        document = json.loads(
            payload.decode("ascii"), object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_constant,
        )
        canonical = _canonical(document)
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError) as exc:
        raise ValueError("Invalid remote floor canonical JSON.") from exc
    if type(document) is not dict or payload != canonical:
        raise ValueError("Noncanonical remote floor JSON.")
    return document


def _challenge(value):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError("Invalid remote floor 32-byte challenge.")
    return value


def _hex_key(value, label):
    if type(value) is not str or _KEY_HEX.fullmatch(value) is None:
        raise ValueError("Invalid remote floor signed " + label + ".")
    return bytes.fromhex(value)


def _counter(value, label):
    return high_water._counter(value, label)


@dataclass(frozen=True, slots=True)
class PinnedRemoteSignedWitnessDeploymentFloor:
    """Unprivileged signed wire client with caller-supplied trust pins."""

    transport: object
    expected_floor_id: str
    expected_floor_public_key: bytes
    expected_subject_id: str
    expected_authority_id: str
    expected_authority_public_key: bytes
    expected_witness_id: str
    expected_witness_public_key: bytes
    minimum_epoch: int

    def __post_init__(self):
        if not callable(getattr(self.transport, "exchange", None)):
            raise ValueError("Remote floor byte transport unavailable.")
        high_water._identity(self.expected_floor_id, "remote floor identity")
        high_water._identity(self.expected_subject_id, "remote floor subject")
        high_water._identity(self.expected_authority_id, "remote floor authority")
        high_water._identity(self.expected_witness_id, "remote floor witness")
        keys = (
            high_water._key(self.expected_floor_public_key, "remote floor public key"),
            high_water._key(self.expected_authority_public_key, "remote authority key"),
            high_water._key(self.expected_witness_public_key, "remote witness key"),
        )
        if len(set(keys)) != 3:
            raise ValueError("Remote floor requires three distinct public keys.")
        _counter(self.minimum_epoch, "minimum remote floor epoch")
        if self.minimum_epoch < 1:
            raise ValueError("Remote floor minimum epoch must be positive.")

    @classmethod
    def from_transport(
        cls, *, transport, expected_floor_id, expected_floor_public_key,
        expected_subject_id, expected_authority_id,
        expected_authority_public_key, expected_witness_id,
        expected_witness_public_key, minimum_epoch,
    ):
        try:
            return cls(
                transport=transport, expected_floor_id=expected_floor_id,
                expected_floor_public_key=expected_floor_public_key,
                expected_subject_id=expected_subject_id,
                expected_authority_id=expected_authority_id,
                expected_authority_public_key=expected_authority_public_key,
                expected_witness_id=expected_witness_id,
                expected_witness_public_key=expected_witness_public_key,
                minimum_epoch=minimum_epoch,
            )
        except Exception as exc:
            raise ValueError("Invalid pinned remote floor client binding.") from exc

    def _verify_reply(self, *, envelope, operation, challenge, request):
        message_hex = envelope.get("message_hex")
        signature_hex = envelope.get("signature_hex")
        if (
            set(envelope) != {"message_hex", "signature_hex"}
            or type(message_hex) is not str
            or _MESSAGE_HEX.fullmatch(message_hex) is None
            or type(signature_hex) is not str
            or _SIGNATURE_HEX.fullmatch(signature_hex) is None
        ):
            raise ValueError("Invalid remote signed response envelope.")
        message = bytes.fromhex(message_hex)
        signature = bytes.fromhex(signature_hex)
        if len(message) > _MAX_SIGNED_BYTES:
            raise ValueError("Oversized remote signed document.")
        try:
            Ed25519PublicKey.from_public_bytes(
                self.expected_floor_public_key
            ).verify(signature, message)
        except Exception as exc:
            raise ValueError("Invalid remote deployment floor signature.") from exc
        document = _parse(message, maximum=_MAX_SIGNED_BYTES)
        expected_fields = {
            "read": _READ_REPLY, "cas": _CAS_REPLY, "lookup": _LOOKUP_REPLY,
        }[operation]
        if (
            set(document) != expected_fields
            or type(document["domain"]) is not str
            or document["domain"] != floor._DOMAIN
            or type(document["version"]) is not int
            or document["version"] != floor._VERSION
            or type(document["operation"]) is not str
            or document["operation"] != operation
        ):
            raise ValueError("Wrong remote floor signed document schema.")
        for name, expected in (
            ("floor_id", self.expected_floor_id),
            ("subject_id", self.expected_subject_id),
            ("authority_id", self.expected_authority_id),
            ("witness_id", self.expected_witness_id),
        ):
            value = high_water._identity(document[name], "signed remote floor " + name)
            if value != expected:
                raise ValueError("Remote floor signed identity mismatch.")
        for name, expected in (
            ("authority_public_key_hex", self.expected_authority_public_key),
            ("witness_public_key_hex", self.expected_witness_public_key),
        ):
            value = _hex_key(document[name], name)
            if not hmac.compare_digest(value, expected):
                raise ValueError("Remote floor signed public key mismatch.")
        reply_challenge = _hex_key(document["challenge_hex"], "challenge")
        if not hmac.compare_digest(reply_challenge, challenge):
            raise ValueError("Remote floor signed challenge mismatch.")
        minimum = _counter(document["minimum_generation"], "signed floor generation")
        epoch = _counter(document["epoch"], "signed floor epoch")
        if epoch < self.minimum_epoch:
            raise ValueError("Remote floor signed epoch below retained minimum.")
        if operation in ("cas", "lookup"):
            op = high_water._operation_id(document["operation_id"])
            if op != request["operation_id"]:
                raise ValueError("Remote floor operation ID substitution.")
            status = document["status"]
            allowed = ("committed", "rejected") if operation == "cas" else ("committed", "unknown")
            if type(status) is not str or status not in allowed:
                raise ValueError("Invalid remote floor signed operation status.")
        if operation == "cas":
            for name in (
                "expected_epoch", "next_epoch", "expected_minimum_generation",
                "next_minimum_generation",
            ):
                actual = _counter(document[name], "signed floor " + name)
                if actual != request[name]:
                    raise ValueError("Remote floor signed CAS argument mismatch.")
            if document["status"] == "committed" and (
                epoch < request["next_epoch"]
                or minimum < request["next_minimum_generation"]
            ):
                raise ValueError("Remote floor committed CAS state inconsistent.")
        return message, signature

    def _exchange(self, *, operation, challenge, extras=None):
        self.__post_init__()
        challenge = _challenge(challenge)
        request = {
            "domain": _WIRE_DOMAIN,
            "version": _WIRE_VERSION,
            "operation": operation,
            "floor_id": self.expected_floor_id,
            "subject_id": self.expected_subject_id,
            "challenge_hex": challenge.hex(),
        }
        if extras:
            request.update(extras)
        if set(request) != {"read": _BASE, "cas": _CAS, "lookup": _LOOKUP}[operation]:
            raise ValueError("Invalid remote floor request schema.")
        try:
            signed = self.transport.exchange(_canonical(request))
            envelope = _parse(signed, maximum=_MAX_WIRE_BYTES)
            return self._verify_reply(
                envelope=envelope, operation=operation, challenge=challenge,
                request=request,
            )
        except Exception as exc:
            # A failed CAS may nevertheless have committed at the service.
            # The caller must inspect the original operation ID via LOOKUP.
            raise ValueError("Remote floor exchange or verification failed.") from exc

    @contextmanager
    def hold(self, *, challenge):
        # A remote READ is a signed snapshot; it cannot lock the server during
        # the caller's with-block and is not cross-store atomic.
        pair = self._exchange(operation="read", challenge=challenge)
        yield pair

    def advance_if_current(
        self, *, operation_id, expected_epoch, next_epoch,
        expected_minimum_generation, next_minimum_generation, challenge,
    ):
        operation_id = high_water._operation_id(operation_id)
        expected_epoch = _counter(expected_epoch, "expected remote epoch")
        next_epoch = _counter(next_epoch, "next remote epoch")
        expected_minimum = _counter(
            expected_minimum_generation, "expected remote minimum"
        )
        next_minimum = _counter(
            next_minimum_generation, "next remote minimum"
        )
        _challenge(challenge)
        if (
            expected_epoch < 1 or next_epoch != expected_epoch + 1
            or next_minimum < expected_minimum
        ):
            raise ValueError("Invalid remote floor monotonic CAS parameters.")
        return self._exchange(
            operation="cas", challenge=challenge,
            extras={
                "operation_id": operation_id,
                "expected_epoch": expected_epoch,
                "next_epoch": next_epoch,
                "expected_minimum_generation": expected_minimum,
                "next_minimum_generation": next_minimum,
            },
        )

    def lookup_operation(self, *, operation_id, challenge):
        operation_id = high_water._operation_id(operation_id)
        _challenge(challenge)
        return self._exchange(
            operation="lookup", challenge=challenge,
            extras={"operation_id": operation_id},
        )
