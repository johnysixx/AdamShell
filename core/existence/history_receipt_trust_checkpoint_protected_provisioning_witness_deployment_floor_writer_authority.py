"""A44 pinned writer-authorized deployment floor transport adapter.

Verifies Ed25519 writer authorization over canonical CAS requests before any
SQLite state transition. READ and LOOKUP remain public, signed and compatible
with the existing remote client protocol. Writer keys and revocations are
snapshotted at construction.

This is an IN-PROCESS reference adapter, not a remotely deployed service.
It supplies no TLS, trusted writer enrollment, key rotation, protected signer
custody, independently durable revocation, or rollback-proof monotonic root.
A valid replay of the same authorized CAS retains backend idempotency.
"""

import hmac
import re
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water as high_water,
)
from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_remote_client
    as remote,
)
from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_cas_backend_sqlite_reference
    as sqlite_reference,
)

_AUTH_DOMAIN = "AdamShell/A44/authorized-writer-floor-cas/v1"
_AUTH_VERSION = 1
_MAX_WIRE_BYTES = 16384
_MAX_INNER_BYTES = 4096
_AUTH_CLAIMS = frozenset({
    "domain", "version", "writer_id", "request_hex",
})
_AUTH_FIELDS = _AUTH_CLAIMS | frozenset({"writer_signature_hex"})
_SIGNATURE_HEX = re.compile(r"[0-9a-f]{128}\Z")
_REQUEST_HEX = re.compile(r"[0-9a-f]{2,8192}\Z")


def _decode_challenge(value):
    result = remote._hex_key(value, "wire challenge")
    return remote._challenge(result)


def _signed_envelope(pair):
    if type(pair) is not tuple or len(pair) != 2:
        raise ValueError("Invalid authority signed response pair.")
    message, signature = pair
    if (
        type(message) is not bytes
        or not message
        or len(message) > 4096
        or type(signature) is not bytes
        or len(signature) != 64
    ):
        raise ValueError("Invalid authority signed response.")
    return remote._canonical({
        "message_hex": message.hex(),
        "signature_hex": signature.hex(),
    })


def _validate_identity(document, backend):
    if (
        type(document.get("domain")) is not str
        or document["domain"] != remote._WIRE_DOMAIN
        or type(document.get("version")) is not int
        or document["version"] != remote._WIRE_VERSION
        or type(document.get("floor_id")) is not str
        or document["floor_id"] != backend.floor_id
        or type(document.get("subject_id")) is not str
        or document["subject_id"] != backend.subject_id
    ):
        raise ValueError("Writer authority request identity mismatch.")
    return _decode_challenge(document["challenge_hex"])


def _validate_cas(document, backend):
    if set(document) != remote._CAS:
        raise ValueError("Invalid signed writer CAS request schema.")
    if document.get("operation") != "cas":
        raise ValueError("Signed writer request must be CAS.")
    challenge = _validate_identity(document, backend)
    operation_id = high_water._operation_id(document["operation_id"])
    expected_epoch = high_water._counter(
        document["expected_epoch"], "authorized expected epoch"
    )
    next_epoch = high_water._counter(
        document["next_epoch"], "authorized next epoch"
    )
    expected_minimum = high_water._counter(
        document["expected_minimum_generation"],
        "authorized expected minimum generation",
    )
    next_minimum = high_water._counter(
        document["next_minimum_generation"],
        "authorized next minimum generation",
    )
    if (
        expected_epoch < 1
        or next_epoch != expected_epoch + 1
        or next_minimum < expected_minimum
    ):
        raise ValueError("Invalid signed writer monotonic CAS.")
    return {
        "operation_id": operation_id,
        "expected_epoch": expected_epoch,
        "next_epoch": next_epoch,
        "expected_minimum_generation": expected_minimum,
        "next_minimum_generation": next_minimum,
        "challenge": challenge,
    }


@dataclass(frozen=True, slots=True)
class PinnedWriterAuthorizedWitnessDeploymentFloorTransport:
    """Pinned in-process writer authorization gateway for signed floor CAS."""

    backend: sqlite_reference.SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority
    _writers: tuple
    _revoked: frozenset

    def __post_init__(self):
        if type(self.backend) is not (
            sqlite_reference.SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority
        ):
            raise ValueError("Expected canonical SQLite floor authority backend.")
        self.backend.__post_init__()
        if (
            type(self._writers) is not tuple
            or not self._writers
            or type(self._revoked) is not frozenset
        ):
            raise ValueError("Invalid pinned writer authority configuration.")

    @classmethod
    def from_sources(
        cls, *, backend, writer_public_keys, revoked_writer_ids=(),
    ):
        try:
            if type(backend) is not (
                sqlite_reference.SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority
            ):
                raise ValueError("Expected canonical floor CAS authority.")
            backend.__post_init__()

            if type(writer_public_keys) is not dict or not writer_public_keys:
                raise ValueError("Expected nonempty pinned writer key dictionary.")

            reserved = (
                sqlite_reference._public_key(backend.signer),
                backend.authority_public_key,
                backend.witness_public_key,
            )

            names = set()
            public_keys = set()
            snapshot = []

            for writer_id, public_key in writer_public_keys.items():
                high_water._identity(writer_id, "authorized writer identity")

                if (
                    type(public_key) is not bytes
                    or len(public_key) != 32
                ):
                    raise ValueError("Invalid authorized writer public key.")

                high_water._key(public_key, "authorized writer public key")

                if (
                    writer_id in names
                    or public_key in public_keys
                    or any(
                        hmac.compare_digest(public_key, reserved_key)
                        for reserved_key in reserved
                    )
                ):
                    raise ValueError("Duplicate or reused writer public key.")

                names.add(writer_id)
                public_keys.add(public_key)
                snapshot.append((writer_id, public_key))

            if type(revoked_writer_ids) not in (
                tuple, list, frozenset,
            ):
                raise ValueError("Invalid writer revocation collection.")

            revoked_list = list(revoked_writer_ids)
            revoked = set()

            for writer_id in revoked_list:
                high_water._identity(writer_id, "revoked writer identity")

                if writer_id not in names or writer_id in revoked:
                    raise ValueError("Invalid or duplicate revoked writer.")

                revoked.add(writer_id)

            return cls(
                backend=backend,
                _writers=tuple(sorted(snapshot)),
                _revoked=frozenset(revoked),
            )
        except Exception as exc:
            raise ValueError("Pinned writer authority construction failed.") from exc

    def _public_read_or_lookup(self, document):
        operation = document.get("operation")

        expected = {
            "read": remote._BASE,
            "lookup": remote._LOOKUP,
        }.get(operation)

        if expected is None or set(document) != expected:
            raise ValueError("Invalid public floor wire operation.")

        challenge = _validate_identity(document, self.backend)

        if operation == "read":
            with self.backend.hold(challenge=challenge) as response:
                return _signed_envelope(response)

        operation_id = high_water._operation_id(document["operation_id"])
        return _signed_envelope(
            self.backend.lookup_operation(
                operation_id=operation_id,
                challenge=challenge,
            )
        )

    def _authorized_cas(self, document):
        if set(document) != _AUTH_FIELDS:
            raise ValueError("Invalid writer authorization envelope fields.")

        if (
            type(document.get("domain")) is not str
            or document["domain"] != _AUTH_DOMAIN
            or type(document.get("version")) is not int
            or document["version"] != _AUTH_VERSION
        ):
            raise ValueError("Invalid writer authorization domain/version.")

        writer_id = high_water._identity(
            document["writer_id"], "signed writer identity"
        )

        if writer_id in self._revoked:
            raise ValueError("Revoked writer cannot publish a floor.")

        public_key = None

        for pinned_id, pinned_key in self._writers:
            if pinned_id == writer_id:
                public_key = pinned_key
                break

        if public_key is None:
            raise ValueError("Unknown writer cannot publish a floor.")

        request_hex = document["request_hex"]
        signature_hex = document["writer_signature_hex"]

        if (
            type(request_hex) is not str
            or _REQUEST_HEX.fullmatch(request_hex) is None
            or len(request_hex) % 2 != 0
            or type(signature_hex) is not str
            or _SIGNATURE_HEX.fullmatch(signature_hex) is None
        ):
            raise ValueError("Malformed signed writer CAS envelope.")

        claims = {
            "domain": document["domain"],
            "version": document["version"],
            "writer_id": writer_id,
            "request_hex": request_hex,
        }

        try:
            Ed25519PublicKey.from_public_bytes(public_key).verify(
                bytes.fromhex(signature_hex),
                remote._canonical(claims),
            )
        except Exception as exc:
            raise ValueError("Invalid writer authorization signature.") from exc

        request = remote._parse(
            bytes.fromhex(request_hex),
            maximum=_MAX_INNER_BYTES,
        )

        arguments = _validate_cas(request, self.backend)

        # No call to the underlying SQLite CAS occurs until every
        # writer key, signature, identity and CAS parameter is verified.
        response = self.backend.advance_if_current(**arguments)

        return _signed_envelope(response)

    def exchange(self, request):
        try:
            document = remote._parse(
                request,
                maximum=_MAX_WIRE_BYTES,
            )

            operation = document.get("operation")

            if operation in ("read", "lookup"):
                return self._public_read_or_lookup(document)

            # A bare legacy CAS is deliberately not a supported operation.
            # Only a valid signed writer envelope may reach SQLite CAS.
            return self._authorized_cas(document)

        except Exception as exc:
            # A CAS failure may be ambiguous after the SQLite commit.
            # Recover by LOOKUP of the original operation ID; do not
            # blindly create a replacement operation.
            raise ValueError("Writer-authorized floor exchange failed.") from exc
