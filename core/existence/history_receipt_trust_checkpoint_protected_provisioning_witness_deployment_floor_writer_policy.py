"""A44 versioned signed writer policy and shared authorization gateway.

A separately pinned Ed25519 policy signing authority authenticates writer
enrollment, rotation and revocation. Policies are canonical signed documents
with consecutive epochs and an exact predecessor SHA-256.

The current policy is immutable object state. Publication and authorized CAS
execution share one authority-local lock. Gateways using the same live
authority always consult its current policy.

SECURITY LIMITS:
- This is an in-process reference authority, not durable policy storage.
- Retained bootstrap epoch and digest must come from trusted external state.
- Separate authorities, old v1 gateways and direct backend access are not
  fenced by this module.
- Revocation tombstones are permanent within the live policy lineage.
- Historical writer key reuse across removed or rotated identities is not
  independently tracked beyond the current roster.
- No protected signer custody, trusted network transport, cross-process
  locking, cross-store atomicity or independent rollback protection.
"""

import hashlib
import hmac
import re
import threading

from dataclasses import dataclass, field

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water as high_water,
)
from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_remote_client
    as remote,
)
from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_authority
    as writer_authority,
)
from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_cas_backend_sqlite_reference
    as sqlite_reference,
)


_POLICY_DOMAIN = "AdamShell/A44/writer-floor-policy/v1"
_POLICY_VERSION = 1

_CAS_DOMAIN = "AdamShell/A44/authorized-writer-floor-cas/v2"
_CAS_VERSION = 2

_MAX_POLICY_BYTES = 65536
_MAX_WIRE_BYTES = 16384
_MAX_INNER_BYTES = 4096

_GENESIS_PREVIOUS = "0" * 64

_DIGEST_HEX = re.compile(r"[0-9a-f]{64}\Z")
_SIGNATURE_HEX = re.compile(r"[0-9a-f]{128}\Z")
_REQUEST_HEX = re.compile(r"[0-9a-f]{2,8192}\Z")

_POLICY_FIELDS = frozenset({
    "domain",
    "version",
    "policy_id",
    "floor_id",
    "subject_id",
    "floor_public_key_hex",
    "policy_epoch",
    "previous_policy_sha256",
    "writer_public_keys",
    "revoked_writer_ids",
})

_CAS_CLAIMS = frozenset({
    "domain",
    "version",
    "policy_id",
    "policy_epoch",
    "policy_sha256",
    "writer_id",
    "request_hex",
})

_CAS_FIELDS = _CAS_CLAIMS | frozenset({
    "writer_signature_hex",
})


def _require_digest(value, label):
    if (
        type(value) is not str
        or _DIGEST_HEX.fullmatch(value) is None
    ):
        raise ValueError("Invalid " + label + " SHA-256.")

    return value


def _require_epoch(value, label):
    epoch = high_water._counter(value, label)

    if epoch < 1:
        raise ValueError("Writer policy epoch must be positive.")

    return epoch


def _require_public_key(value, label):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError("Invalid " + label + " public key.")

    return high_water._key(value, label)


def _require_backend(backend):
    if type(backend) is not (
        sqlite_reference.SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority
    ):
        raise ValueError("Expected canonical SQLite floor CAS authority.")

    backend.__post_init__()

    return backend


def _reserved_backend_keys(backend):
    return (
        sqlite_reference._public_key(backend.signer),
        backend.authority_public_key,
        backend.witness_public_key,
    )


def _verify_signature(public_key, message, signature):
    if (
        type(message) is not bytes
        or type(signature) is not bytes
        or len(signature) != 64
    ):
        raise ValueError("Invalid signed writer policy material.")

    try:
        Ed25519PublicKey.from_public_bytes(
            public_key
        ).verify(
            signature,
            message,
        )
    except Exception as exc:
        raise ValueError("Writer policy signature verification failed.") from exc


@dataclass(frozen=True, slots=True)
class _WriterPolicyState:
    """Immutable validated policy snapshot."""

    policy_id: str
    epoch: int
    sha256: str
    previous_sha256: str
    writers: tuple
    revoked: frozenset

    def writer_public_key(self, writer_id):
        if writer_id in self.revoked:
            raise ValueError("Writer identity has been revoked.")

        for pinned_id, pinned_key in self.writers:
            if pinned_id == writer_id:
                return pinned_key

        raise ValueError("Writer identity is not enrolled.")


def _parse_signed_policy(
    *,
    backend,
    expected_policy_id,
    policy_public_key,
    signed_policy,
):
    if (
        type(signed_policy) is not tuple
        or len(signed_policy) != 2
    ):
        raise ValueError("Expected signed policy message/signature pair.")

    message, signature = signed_policy

    if (
        type(message) is not bytes
        or not message
        or len(message) > _MAX_POLICY_BYTES
        or type(signature) is not bytes
        or len(signature) != 64
    ):
        raise ValueError("Invalid signed writer policy size or type.")

    _verify_signature(
        policy_public_key,
        message,
        signature,
    )

    document = remote._parse(
        message,
        maximum=_MAX_POLICY_BYTES,
    )

    if set(document) != _POLICY_FIELDS:
        raise ValueError("Invalid signed writer policy schema.")

    if (
        type(document["domain"]) is not str
        or document["domain"] != _POLICY_DOMAIN
        or type(document["version"]) is not int
        or document["version"] != _POLICY_VERSION
    ):
        raise ValueError("Invalid writer policy domain/version.")

    policy_id = high_water._identity(
        document["policy_id"],
        "writer policy identity",
    )

    if policy_id != expected_policy_id:
        raise ValueError("Writer policy identity mismatch.")

    if (
        type(document["floor_id"]) is not str
        or document["floor_id"] != backend.floor_id
        or type(document["subject_id"]) is not str
        or document["subject_id"] != backend.subject_id
    ):
        raise ValueError("Writer policy floor scope mismatch.")

    floor_public_key = remote._hex_key(
        document["floor_public_key_hex"],
        "policy floor public key",
    )

    if not hmac.compare_digest(
        floor_public_key,
        sqlite_reference._public_key(backend.signer),
    ):
        raise ValueError("Writer policy floor signing key mismatch.")

    epoch = _require_epoch(
        document["policy_epoch"],
        "writer policy epoch",
    )

    previous = _require_digest(
        document["previous_policy_sha256"],
        "previous writer policy",
    )

    if epoch == 1 and previous != _GENESIS_PREVIOUS:
        raise ValueError("Invalid genesis writer policy predecessor.")

    if epoch > 1 and previous == _GENESIS_PREVIOUS:
        raise ValueError("Missing predecessor for non-genesis policy.")

    writer_keys = document["writer_public_keys"]

    if type(writer_keys) is not dict or not writer_keys:
        raise ValueError("Expected nonempty writer policy roster.")

    reserved_keys = (
        *_reserved_backend_keys(backend),
        policy_public_key,
    )

    names = set()
    used_keys = set()
    snapshot = []

    for identity, public_key_hex in writer_keys.items():

        writer_id = high_water._identity(
            identity,
            "policy writer identity",
        )

        key = remote._hex_key(
            public_key_hex,
            "policy writer public key",
        )

        key = _require_public_key(
            key,
            "policy writer",
        )

        if (
            writer_id in names
            or key in used_keys
            or any(
                hmac.compare_digest(key, reserved)
                for reserved in reserved_keys
            )
        ):
            raise ValueError("Duplicate or reserved writer public key.")

        names.add(writer_id)
        used_keys.add(key)

        snapshot.append((writer_id, key))

    revoked_document = document["revoked_writer_ids"]

    if type(revoked_document) is not list:
        raise ValueError("Invalid writer policy revocation collection.")

    revoked = set()

    for identity in revoked_document:

        writer_id = high_water._identity(
            identity,
            "revoked writer identity",
        )

        if writer_id not in names:
            raise ValueError("Unknown revoked writer identity.")

        if writer_id in revoked:
            raise ValueError("Duplicate revoked writer identity.")

        revoked.add(writer_id)

    if revoked_document != sorted(revoked):
        raise ValueError("Noncanonical writer revocation order.")

    return _WriterPolicyState(
        policy_id=policy_id,
        epoch=epoch,
        sha256=hashlib.sha256(message).hexdigest(),
        previous_sha256=previous,
        writers=tuple(sorted(snapshot)),
        revoked=frozenset(revoked),
    )


@dataclass(frozen=True, slots=True, init=False, eq=False)
class VersionedWriterPolicyAuthority:
    """Shared live authority for one signed writer policy lineage."""

    _backend: object = field(repr=False)

    _policy_id: str

    _policy_public_key: bytes = field(repr=False)

    _policy: _WriterPolicyState = field(repr=False)

    _lock: object = field(repr=False)

    def __init__(
        self,
        *,
        backend,
        expected_policy_id,
        expected_policy_public_key,
        signed_policy,
        minimum_policy_epoch,
        expected_policy_sha256,
    ):
        backend = _require_backend(backend)

        policy_id = high_water._identity(
            expected_policy_id,
            "expected writer policy identity",
        )

        root_key = _require_public_key(
            expected_policy_public_key,
            "writer policy root",
        )

        if any(
            hmac.compare_digest(root_key, reserved)
            for reserved in _reserved_backend_keys(backend)
        ):
            raise ValueError("Policy signing key must be independently scoped.")

        minimum_epoch = _require_epoch(
            minimum_policy_epoch,
            "minimum retained writer policy epoch",
        )

        expected_digest = _require_digest(
            expected_policy_sha256,
            "retained writer policy",
        )

        initial = _parse_signed_policy(
            backend=backend,
            expected_policy_id=policy_id,
            policy_public_key=root_key,
            signed_policy=signed_policy,
        )

        if initial.epoch < minimum_epoch:
            raise ValueError("Writer policy rollback below retained epoch.")

        if not hmac.compare_digest(
            initial.sha256,
            expected_digest,
        ):
            raise ValueError("Writer policy retained digest mismatch.")

        object.__setattr__(
            self,
            "_backend",
            backend,
        )

        object.__setattr__(
            self,
            "_policy_id",
            policy_id,
        )

        object.__setattr__(
            self,
            "_policy_public_key",
            root_key,
        )

        object.__setattr__(
            self,
            "_policy",
            initial,
        )

        object.__setattr__(
            self,
            "_lock",
            threading.Lock(),
        )

    @classmethod
    def from_signed_policy(
        cls,
        *,
        backend,
        expected_policy_id,
        expected_policy_public_key,
        signed_policy,
        minimum_policy_epoch,
        expected_policy_sha256,
    ):
        return cls(
            backend=backend,
            expected_policy_id=expected_policy_id,
            expected_policy_public_key=expected_policy_public_key,
            signed_policy=signed_policy,
            minimum_policy_epoch=minimum_policy_epoch,
            expected_policy_sha256=expected_policy_sha256,
        )

    def current_policy_reference(self):
        """Return an immutable epoch/digest snapshot."""

        with self._lock:
            return (
                self._policy.epoch,
                self._policy.sha256,
            )

    def publish_policy(self, *, signed_policy):
        """Atomically validate and publish the next in-memory policy."""

        candidate = _parse_signed_policy(
            backend=self._backend,
            expected_policy_id=self._policy_id,
            policy_public_key=self._policy_public_key,
            signed_policy=signed_policy,
        )

        with self._lock:

            current = self._policy

            if candidate.epoch != current.epoch + 1:
                raise ValueError("Writer policy epoch is not consecutive.")

            if not hmac.compare_digest(
                candidate.previous_sha256,
                current.sha256,
            ):
                raise ValueError("Writer policy predecessor mismatch.")

            if not current.revoked.issubset(
                candidate.revoked
            ):
                raise ValueError("Writer revocation tombstone removal forbidden.")

            # A revoked identity must keep its tombstone and key.
            # This prevents reassignment of its current revoked key
            # within subsequent policies in the same lineage.
            candidate_keys = dict(candidate.writers)

            for writer_id, public_key in current.writers:
                if writer_id in current.revoked:
                    retained_key = candidate_keys.get(writer_id)

                    if (
                        retained_key is None
                        or not hmac.compare_digest(
                            retained_key,
                            public_key,
                        )
                    ):
                        raise ValueError("Revoked writer tombstone key changed.")

            object.__setattr__(
                self,
                "_policy",
                candidate,
            )

            return (
                candidate.epoch,
                candidate.sha256,
            )

    def _public_read_or_lookup(self, document):

        operation = document.get("operation")

        if operation == "read":
            expected_fields = remote._BASE
        elif operation == "lookup":
            expected_fields = remote._LOOKUP
        else:
            raise ValueError("Unsupported public floor operation.")

        if set(document) != expected_fields:
            raise ValueError("Invalid public floor request schema.")

        challenge = writer_authority._validate_identity(
            document,
            self._backend,
        )

        if operation == "read":
            with self._backend.hold(
                challenge=challenge,
            ) as pair:

                return writer_authority._signed_envelope(pair)

        operation_id = high_water._operation_id(
            document["operation_id"]
        )

        pair = self._backend.lookup_operation(
            operation_id=operation_id,
            challenge=challenge,
        )

        return writer_authority._signed_envelope(pair)

    def _authorized_cas(self, document):

        if set(document) != _CAS_FIELDS:
            raise ValueError("Invalid versioned writer CAS envelope.")

        if (
            type(document["domain"]) is not str
            or document["domain"] != _CAS_DOMAIN
            or type(document["version"]) is not int
            or document["version"] != _CAS_VERSION
        ):
            raise ValueError("Invalid versioned writer CAS domain/version.")

        policy_id = high_water._identity(
            document["policy_id"],
            "CAS writer policy identity",
        )

        policy_epoch = _require_epoch(
            document["policy_epoch"],
            "CAS writer policy epoch",
        )

        policy_digest = _require_digest(
            document["policy_sha256"],
            "CAS writer policy",
        )

        writer_id = high_water._identity(
            document["writer_id"],
            "CAS writer identity",
        )

        request_hex = document["request_hex"]
        signature_hex = document["writer_signature_hex"]

        if (
            type(request_hex) is not str
            or _REQUEST_HEX.fullmatch(request_hex) is None
            or len(request_hex) % 2 != 0
            or type(signature_hex) is not str
            or _SIGNATURE_HEX.fullmatch(signature_hex) is None
        ):
            raise ValueError("Malformed versioned writer CAS material.")

        claims = {
            name: document[name]
            for name in _CAS_CLAIMS
        }

        message = remote._canonical(claims)
        signature = bytes.fromhex(signature_hex)

        # The lock spans policy selection, writer authentication,
        # inner request validation and backend CAS execution.
        #
        # A policy publication cannot interleave between writer
        # authentication and the underlying SQLite commit.

        with self._lock:

            current = self._policy

            if (
                policy_id != current.policy_id
                or policy_epoch != current.epoch
                or not hmac.compare_digest(
                    policy_digest,
                    current.sha256,
                )
            ):
                raise ValueError("CAS writer policy is not current.")

            writer_key = current.writer_public_key(
                writer_id
            )

            _verify_signature(
                writer_key,
                message,
                signature,
            )

            inner = remote._parse(
                bytes.fromhex(request_hex),
                maximum=_MAX_INNER_BYTES,
            )

            arguments = writer_authority._validate_cas(
                inner,
                self._backend,
            )

            pair = self._backend.advance_if_current(
                **arguments
            )

            return writer_authority._signed_envelope(pair)

    def exchange(self, request):
        """Dispatch public signed reads and versioned authorized CAS."""

        try:
            document = remote._parse(
                request,
                maximum=_MAX_WIRE_BYTES,
            )

            operation = document.get("operation")

            if operation in ("read", "lookup"):
                return self._public_read_or_lookup(
                    document
                )

            # Legacy unsigned CAS and v1 authorization envelopes
            # cannot satisfy the v2 schema and policy binding.

            return self._authorized_cas(
                document
            )

        except Exception as exc:
            # Backend commit acknowledgement can be ambiguous.
            # Recover with LOOKUP using the original operation ID.

            raise ValueError(
                "Versioned writer policy exchange failed."
            ) from exc


@dataclass(frozen=True, slots=True, eq=False)
class VersionedWriterPolicyGateway:
    """Gateway retaining a live policy authority, never a roster snapshot."""

    _authority: VersionedWriterPolicyAuthority = field(
        repr=False
    )

    def __post_init__(self):
        if type(self._authority) is not VersionedWriterPolicyAuthority:
            raise ValueError("Expected canonical live writer policy authority.")

    @classmethod
    def from_authority(cls, *, authority):
        return cls(
            _authority=authority,
        )

    def exchange(self, request):
        return self._authority.exchange(request)
