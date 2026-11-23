"""A44 pinned read-only signed provisioning-generation witness.

Verifies a separately pinned Ed25519-signed witness read and demands exact
agreement with the existing signed provisioning-generation client. This
module provides neither an independent service nor a protected trust root.
The caller must authenticate both pins and arrange witness storage/key
independence; no cross-store atomicity, persistence, remote execution or
rollback resistance is established by the Python checks alone.
"""

import hmac
import json
import os

from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from core.existence.history_receipt_trust_checkpoint_protected_provisioning_floor import (
    PinnedSignedProvisioningGenerationClient,
)
from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water as high_water,
)


_DOMAIN = "AdamShell/A44/provisioning-generation-witness/v1"
_VERSION = 1
_MAX_MESSAGE_BYTES = 4096
_FIELDS = frozenset({
    "domain", "version", "operation", "witness_id", "subject_id",
    "generation", "challenge_hex",
})


def _unique_properties(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("Duplicate signed witness JSON property.")
        result[name] = value
    return result


def _invalid_constant(value):
    raise ValueError("Nonfinite signed witness number.")


def _require_witness(witness):
    if not callable(getattr(witness, "hold", None)):
        raise ValueError("Signed provisioning witness hold unavailable.")
    return witness


def _require_client(client):
    if type(client) is not PinnedSignedProvisioningGenerationClient:
        raise ValueError("Expected pinned signed provisioning generation client.")
    client.__post_init__()
    return client


def _validate_pair(response):
    if type(response) is not tuple or len(response) != 2:
        raise ValueError("Invalid signed witness response pair.")
    message, signature = response
    if (
        type(message) is not bytes or not message
        or len(message) > _MAX_MESSAGE_BYTES
        or type(signature) is not bytes or len(signature) != 64
    ):
        raise ValueError("Invalid signed witness message/signature.")
    return message, signature


def _parse_message(message):
    try:
        document = json.loads(
            message.decode("ascii"),
            object_pairs_hook=_unique_properties,
            parse_constant=_invalid_constant,
        )
        canonical = json.dumps(
            document,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError) as exc:
        raise ValueError("Invalid signed witness JSON document.") from exc
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
        raise ValueError("Invalid witness domain/version/operation or fields.")
    return document


@dataclass(frozen=True, slots=True)
class PinnedSignedProvisioningGenerationWitness:
    """Read-only dual-pin client; caller supplies BOTH trust roots."""

    client: PinnedSignedProvisioningGenerationClient
    witness: object
    expected_witness_id: str
    expected_witness_public_key: bytes
    expected_subject_id: str
    minimum_generation: int

    def __post_init__(self):
        client = _require_client(self.client)
        _require_witness(self.witness)
        high_water._identity(self.expected_witness_id, "provisioning witness ID")
        high_water._identity(self.expected_subject_id, "provisioning witness subject")
        high_water._key(self.expected_witness_public_key, "provisioning witness public key")
        high_water._counter(self.minimum_generation, "provisioning witness generation minimum")
        if client.expected_subject_id != self.expected_subject_id:
            raise ValueError("Witness and authority subject pins differ.")
        if hmac.compare_digest(
            client.expected_authority_public_key,
            self.expected_witness_public_key,
        ):
            raise ValueError("Witness and authority cannot share signing key.")

    @classmethod
    def from_sources(
        cls, *, client, witness, expected_witness_id,
        expected_witness_public_key, expected_subject_id, minimum_generation,
    ):
        try:
            return cls(
                client=client,
                witness=witness,
                expected_witness_id=expected_witness_id,
                expected_witness_public_key=expected_witness_public_key,
                expected_subject_id=expected_subject_id,
                minimum_generation=minimum_generation,
            )
        except Exception as exc:
            raise ValueError("Pinned provisioning witness binding failed.") from exc

    def _witness_generation(self, *, response, challenge):
        message, signature = _validate_pair(response)
        document = _parse_message(message)
        high_water._identity(document["witness_id"], "signed witness ID")
        high_water._identity(document["subject_id"], "signed witness subject")
        generation = high_water._counter(
            document["generation"], "signed witness generation"
        )
        signed_challenge = document["challenge_hex"]
        if (
            document["witness_id"] != self.expected_witness_id
            or document["subject_id"] != self.expected_subject_id
            or type(signed_challenge) is not str
            or len(signed_challenge) != 64
            or not hmac.compare_digest(signed_challenge, challenge.hex())
            or generation < self.minimum_generation
        ):
            raise ValueError("Witness identity, challenge, or minimum mismatch.")
        try:
            Ed25519PublicKey.from_public_bytes(
                self.expected_witness_public_key
            ).verify(signature, message)
        except Exception as exc:
            raise ValueError("Witness signature was not verified.") from exc
        return generation

    def _run_under_witness(self, callback):
        try:
            self.__post_init__()
            challenge = os.urandom(32)
            if type(challenge) is not bytes or len(challenge) != 32:
                raise ValueError("Fresh witness challenge unavailable.")
            with self.witness.hold(challenge=challenge) as response:
                witnessed = self._witness_generation(
                    response=response, challenge=challenge
                )
                return callback(witnessed)
        except Exception as exc:
            raise ValueError("Signed provisioning witness check failed.") from exc

    def read_generation(self):
        def compare(witnessed):
            local = self.client.read_generation()
            if local != witnessed:
                raise ValueError("Provisioning authority and witness disagree.")
            return witnessed
        return self._run_under_witness(compare)

    def bind_provisioning(self, *, source, manifest, signature):
        def bind(witnessed):
            binding = self.client.bind_provisioning(
                source=source, manifest=manifest, signature=signature
            )
            if binding.pins.provisioning_generation != witnessed:
                raise ValueError("Signed witness and enrollment disagree.")
            return binding
        return self._run_under_witness(bind)
