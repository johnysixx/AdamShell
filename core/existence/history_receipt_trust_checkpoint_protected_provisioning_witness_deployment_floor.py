"""A44 signed deployment floor gate for an already pinned provisioning witness.

The external deployment floor is a caller-provided, read-only protocol source.
Signature verification cannot establish independent deployment, protected
storage, honest monotonicity, trustworthy enrollment, or cross-store atomicity.
There is no autonomous CAS or reconciliation path in this module.
"""

import hmac
import json
import os
import re
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water as high_water,
)
from core.existence.history_receipt_trust_checkpoint_protected_provisioning_floor_pinned_witness import (
    PinnedSignedProvisioningGenerationWitness,
)

_DOMAIN = "AdamShell/A44/witness-deployment-floor/v1"
_VERSION = 1
_MAX_MESSAGE_BYTES = 4096
_HEX_KEY = re.compile(r"[0-9a-f]{64}\Z")
_FIELDS = frozenset({
    "domain", "version", "operation", "floor_id", "subject_id",
    "authority_id", "authority_public_key_hex", "witness_id",
    "witness_public_key_hex", "minimum_generation", "epoch",
    "challenge_hex",
})


def _no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate deployment floor JSON property.")
        result[key] = value
    return result


def _no_json_constant(value):
    raise ValueError("Nonfinite deployment floor JSON constant.")


def _signed_pair(value):
    if type(value) is not tuple or len(value) != 2:
        raise ValueError("Malformed deployment floor signed response pair.")
    message, signature = value
    if (
        type(message) is not bytes
        or not message
        or len(message) > _MAX_MESSAGE_BYTES
        or type(signature) is not bytes
        or len(signature) != 64
    ):
        raise ValueError("Malformed deployment floor signed message.")
    return message, signature


def _parse_document(message):
    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=_no_duplicates,
            parse_constant=_no_json_constant,
        )
        canonical = json.dumps(
            document, sort_keys=True, ensure_ascii=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("ascii")
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError) as exc:
        raise ValueError("Invalid deployment floor JSON.") from exc
    if (
        type(document) is not dict
        or set(document) != _FIELDS
        or canonical != message
        or type(document["domain"]) is not str
        or document["domain"] != _DOMAIN
        or type(document["version"]) is not int
        or document["version"] != _VERSION
        or type(document["operation"]) is not str
        or document["operation"] != "read"
    ):
        raise ValueError("Invalid deployment floor signed document.")
    return document


def _key_hex(value, label):
    if type(value) is not str or _HEX_KEY.fullmatch(value) is None:
        raise ValueError("Invalid signed " + label + ".")
    return bytes.fromhex(value)


@dataclass(frozen=True, slots=True)
class PinnedSignedWitnessDeploymentFloor:
    """Compare two signed generation reads with a third signed minimum."""

    guard: PinnedSignedProvisioningGenerationWitness
    floor_source: object
    expected_floor_id: str
    expected_floor_public_key: bytes
    expected_subject_id: str
    minimum_epoch: int

    def __post_init__(self):
        if type(self.guard) is not PinnedSignedProvisioningGenerationWitness:
            raise ValueError("Expected pinned signed provisioning witness guard.")
        self.guard.__post_init__()
        if not callable(getattr(self.floor_source, "hold", None)):
            raise ValueError("Signed deployment floor hold unavailable.")
        high_water._identity(self.expected_floor_id, "deployment floor identity")
        high_water._identity(self.expected_subject_id, "deployment floor subject")
        high_water._key(self.expected_floor_public_key, "deployment floor public key")
        high_water._counter(self.minimum_epoch, "minimum deployment floor epoch")
        if self.minimum_epoch < 1:
            raise ValueError("Deployment floor epoch must be positive.")
        if self.guard.expected_subject_id != self.expected_subject_id:
            raise ValueError("Deployment floor and guard subject pins differ.")
        if (
            hmac.compare_digest(
                self.expected_floor_public_key,
                self.guard.expected_witness_public_key,
            )
            or hmac.compare_digest(
                self.expected_floor_public_key,
                self.guard.client.expected_authority_public_key,
            )
        ):
            raise ValueError("Deployment floor signer must use a distinct key.")

    @classmethod
    def from_sources(
        cls, *, guard, floor_source, expected_floor_id,
        expected_floor_public_key, expected_subject_id, minimum_epoch,
    ):
        try:
            return cls(
                guard=guard,
                floor_source=floor_source,
                expected_floor_id=expected_floor_id,
                expected_floor_public_key=expected_floor_public_key,
                expected_subject_id=expected_subject_id,
                minimum_epoch=minimum_epoch,
            )
        except Exception as exc:
            raise ValueError("Pinned deployment floor binding failed.") from exc

    def _verify_floor(self, *, response, challenge):
        message, signature = _signed_pair(response)
        try:
            Ed25519PublicKey.from_public_bytes(
                self.expected_floor_public_key
            ).verify(signature, message)
        except Exception as exc:
            raise ValueError("Deployment floor signature verification failed.") from exc
        document = _parse_document(message)
        floor_id = high_water._identity(document["floor_id"], "signed deployment floor")
        subject = high_water._identity(document["subject_id"], "signed deployment subject")
        authority_id = high_water._identity(
            document["authority_id"], "signed provisioning authority"
        )
        witness_id = high_water._identity(document["witness_id"], "signed witness")
        generation = high_water._counter(
            document["minimum_generation"], "signed deployment minimum generation"
        )
        epoch = high_water._counter(document["epoch"], "signed deployment epoch")
        authority_key = _key_hex(
            document["authority_public_key_hex"], "authority public key"
        )
        witness_key = _key_hex(
            document["witness_public_key_hex"], "witness public key"
        )
        signed_challenge = _key_hex(document["challenge_hex"], "challenge")
        if (
            floor_id != self.expected_floor_id
            or subject != self.expected_subject_id
            or authority_id != self.guard.client.expected_authority_id
            or witness_id != self.guard.expected_witness_id
            or not hmac.compare_digest(
                authority_key, self.guard.client.expected_authority_public_key
            )
            or not hmac.compare_digest(
                witness_key, self.guard.expected_witness_public_key
            )
            or not hmac.compare_digest(signed_challenge, challenge)
            or epoch < self.minimum_epoch
        ):
            raise ValueError("Deployment floor pin, freshness, or epoch mismatch.")
        return generation

    def _run_under_floor(self, callback):
        try:
            self.__post_init__()
            challenge = os.urandom(32)
            if type(challenge) is not bytes or len(challenge) != 32:
                raise ValueError("Fresh deployment floor challenge unavailable.")
            with self.floor_source.hold(challenge=challenge) as response:
                minimum = self._verify_floor(
                    response=response, challenge=challenge
                )
                return callback(minimum)
        except Exception as exc:
            raise ValueError("Signed witness deployment floor check failed.") from exc

    def read_generation(self):
        def read(minimum):
            generation = self.guard.read_generation()
            if generation < minimum:
                raise ValueError("Witness generation below signed deployment floor.")
            return generation
        return self._run_under_floor(read)

    def bind_provisioning(self, *, source, manifest, signature):
        def bind(minimum):
            binding = self.guard.bind_provisioning(
                source=source, manifest=manifest, signature=signature
            )
            if binding.pins.provisioning_generation < minimum:
                raise ValueError("Enrollment below signed deployment minimum.")
            return binding
        return self._run_under_floor(bind)
