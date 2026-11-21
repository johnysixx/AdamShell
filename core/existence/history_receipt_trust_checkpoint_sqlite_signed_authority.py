"""A44 SQLite-backed signed checkpoint monotonic authority (local reference).

The single SQLite rollback-journal database persists revision, generation
and fencing token, and its held read transaction excludes a conflicting local
CAS commit. The signing key is injected, never stored in the database.

SECURITY LIMITS: Caller-supplied trust pins, no independent key enrollment,
no rollback-resistant anchor, no remote service/lease, no power-loss proof,
no cross-system atomicity and no checkpoint restore/republish authority.
Replacing the entire database with an older valid copy can roll back state.
A stolen signing key or dishonest signer can make false signed assertions.
"""

import hmac
import json
import os
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)


_DOMAIN = "AdamShell/A44/checkpoint-monotonic-authority/v1"
_MAX_INTEGER = (1 << 63) - 1
_LOCK_TIMEOUT = 0.15

_SCHEMA = """
CREATE TABLE checkpoint_signed_authority_state (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    authority_id TEXT NOT NULL,
    authority_public_key BLOB NOT NULL,
    root_id TEXT NOT NULL,
    root_public_key BLOB NOT NULL,
    enrollment_epoch INTEGER NOT NULL CHECK (enrollment_epoch >= 0),
    revision INTEGER NOT NULL CHECK (revision >= 0),
    generation INTEGER NOT NULL CHECK (generation >= 0),
    fence_token INTEGER NOT NULL CHECK (fence_token >= 0)
)
"""


def _require_path(value):
    if type(value) is str and value:
        value = Path(value)
    if not isinstance(value, Path) or not str(value):
        raise ValueError("Invalid SQLite signed authority database path.")
    return value


def _require_public_key(value, name):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(f"Invalid {name}: expected 32 immutable bytes.")
    return bytes(value)


def _require_integer(value, name):
    if type(value) is not int or not (0 <= value <= _MAX_INTEGER):
        raise ValueError(f"Invalid {name}.")
    return value


def _require_challenge(challenge):
    if type(challenge) is not bytes or len(challenge) != 32:
        raise ValueError("Invalid signed authority challenge.")
    return bytes(challenge)


def _require_signer(signer):
    if not isinstance(signer, Ed25519PrivateKey):
        raise ValueError("Expected Ed25519 authority signer.")
    try:
        raw = signer.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    except Exception as exc:
        raise ValueError("Authority signer public key unavailable.") from exc
    return _require_public_key(raw, "authority signing public key")


def _validate_identity(authority_id, root_id, root_public_key, epoch):
    authority_id = _require_identity(authority_id, "authority identity")
    root_id = _require_identity(root_id, "checkpoint root identity")
    root_public_key = _require_public_key(root_public_key, "root public key")
    epoch = _require_integer(epoch, "enrollment epoch")
    return authority_id, root_id, root_public_key, epoch


@dataclass(frozen=True, slots=True)
class SQLiteSignedCheckpointMonotonicAuthority:
    """Local transactional signer, not an independently trusted authority."""

    _path: Path
    authority_id: str
    signer: Ed25519PrivateKey
    root_id: str
    root_public_key: bytes
    enrollment_epoch: int

    def __post_init__(self):
        _require_path(self._path)
        _require_signer(self.signer)
        _validate_identity(
            self.authority_id,
            self.root_id,
            self.root_public_key,
            self.enrollment_epoch,
        )

    def _connect(self, *, readonly):
        connection = None
        try:
            target = self._path.resolve(strict=True).as_uri()
            mode = "ro" if readonly else "rw"
            connection = sqlite3.connect(
                f"{target}?mode={mode}",
                uri=True,
                isolation_level=None,
                timeout=_LOCK_TIMEOUT,
            )
            connection.execute("PRAGMA busy_timeout=150")
            if not readonly:
                connection.execute("PRAGMA synchronous=FULL")
            return connection
        except (OSError, sqlite3.Error, ValueError) as exc:
            if connection is not None:
                connection.close()
            raise ValueError("Signed authority database unavailable.") from exc

    def _validated_snapshot(self, connection):
        rows = connection.execute(
            "SELECT singleton_id, authority_id, authority_public_key, "
            "root_id, root_public_key, enrollment_epoch, "
            "revision, generation, fence_token "
            "FROM checkpoint_signed_authority_state"
        ).fetchall()

        journal = connection.execute("PRAGMA journal_mode").fetchone()
        if (
            type(journal) is not tuple
            or len(journal) != 1
            or type(journal[0]) is not str
            or journal[0].lower() != "delete"
        ):
            raise ValueError("Unsupported signed authority SQLite journal mode.")

        if len(rows) != 1:
            raise ValueError("Missing or ambiguous signed authority state.")

        (
            singleton,
            authority_id,
            authority_key,
            root_id,
            root_key,
            epoch,
            revision,
            generation,
            fence,
        ) = rows[0]

        if type(singleton) is not int or singleton != 1:
            raise ValueError("Invalid signed authority singleton.")

        authority_id, root_id, root_key, epoch = _validate_identity(
            authority_id, root_id, root_key, epoch
        )
        authority_key = _require_public_key(
            authority_key, "stored authority signing key"
        )
        revision = _require_integer(revision, "stored authority revision")
        generation = _require_integer(generation, "stored authority generation")
        fence = _require_integer(fence, "stored authority fencing token")

        if authority_id != self.authority_id or root_id != self.root_id:
            raise ValueError("Signed authority identity mismatch.")
        if epoch != self.enrollment_epoch:
            raise ValueError("Signed authority enrollment epoch mismatch.")
        if not hmac.compare_digest(root_key, self.root_public_key):
            raise ValueError("Signed authority root key mismatch.")
        if not hmac.compare_digest(authority_key, _require_signer(self.signer)):
            raise ValueError("Signed authority signer pin mismatch.")

        return (
            authority_id,
            root_id,
            bytes(root_key),
            epoch,
            revision,
            generation,
            fence,
        )

    def _signed(self, *, operation, snapshot, challenge, transition=None):
        (
            authority_id,
            root_id,
            root_key,
            epoch,
            revision,
            generation,
            fence,
        ) = snapshot
        document = {
            "domain": _DOMAIN,
            "version": 1,
            "operation": operation,
            "authority_id": authority_id,
            "root_id": root_id,
            "root_public_key_hex": root_key.hex(),
            "enrollment_epoch": epoch,
            "revision": revision,
            "generation": generation,
            "fence_token": fence,
            "challenge_hex": challenge.hex(),
        }
        if operation == "cas":
            if type(transition) is not tuple or len(transition) != 4:
                raise ValueError("Invalid signed CAS transition metadata.")
            old, new, old_generation, old_fence = transition
            document.update({
                "expected_revision": old,
                "next_revision": new,
                "expected_generation": old_generation,
                "expected_fence_token": old_fence,
            })
        elif operation != "read" or transition is not None:
            raise ValueError("Invalid signed authority operation.")

        message = json.dumps(
            document,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")
        return message, self.signer.sign(message)

    @classmethod
    def bootstrap(
        cls, *, path, authority_id, signer, root_id,
        root_public_key, enrollment_epoch, initial_revision,
        initial_generation, initial_fence_token,
    ):
        target = _require_path(path)
        authority_id, root_id, root_key, epoch = _validate_identity(
            authority_id, root_id, root_public_key, enrollment_epoch
        )
        signing_key = _require_signer(signer)
        revision = _require_integer(initial_revision, "initial revision")
        generation = _require_integer(initial_generation, "initial generation")
        fence = _require_integer(initial_fence_token, "initial fencing token")

        store = cls(
            _path=target,
            authority_id=authority_id,
            signer=signer,
            root_id=root_id,
            root_public_key=root_key,
            enrollment_epoch=epoch,
        )

        try:
            fd = os.open(target, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
        except OSError as exc:
            raise ValueError("Signed authority database already exists or cannot be created.") from exc

        try:
            with closing(store._connect(readonly=False)) as connection:
                try:
                    mode = connection.execute("PRAGMA journal_mode=DELETE").fetchone()
                    if (
                        type(mode) is not tuple
                        or len(mode) != 1
                        or str(mode[0]).lower() != "delete"
                    ):
                        raise ValueError("SQLite rollback journal mode unavailable.")
                    connection.execute("BEGIN IMMEDIATE")
                    connection.execute(_SCHEMA)
                    connection.execute(
                        "INSERT INTO checkpoint_signed_authority_state "
                        "(singleton_id, authority_id, authority_public_key, "
                        "root_id, root_public_key, enrollment_epoch, "
                        "revision, generation, fence_token) "
                        "VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            authority_id, signing_key, root_id, root_key,
                            epoch, revision, generation, fence,
                        ),
                    )
                    connection.commit()
                finally:
                    if connection.in_transaction:
                        connection.rollback()

            with store.hold(challenge=b"\x00" * 32):
                pass
            return store
        except Exception as exc:
            # Do not automatically remove or reinitialize a potentially
            # committed database: inspect its state before retrying.
            raise ValueError(
                "Signed authority bootstrap failed; inspect database before retry."
            ) from exc

    @classmethod
    def open(
        cls, *, path, expected_authority_id, signer,
        expected_root_id, expected_root_public_key,
        expected_enrollment_epoch,
    ):
        try:
            target = _require_path(path)
            authority_id, root_id, root_key, epoch = _validate_identity(
                expected_authority_id, expected_root_id,
                expected_root_public_key, expected_enrollment_epoch,
            )
            _require_signer(signer)
            store = cls(
                _path=target,
                authority_id=authority_id,
                signer=signer,
                root_id=root_id,
                root_public_key=root_key,
                enrollment_epoch=epoch,
            )
            with store.hold(challenge=b"\x00" * 32):
                pass
            return store
        except Exception as exc:
            raise ValueError("Signed authority open failed.") from exc

    @contextmanager
    def hold(self, *, challenge):
        try:
            self.__post_init__()
            challenge = _require_challenge(challenge)
            with closing(self._connect(readonly=True)) as connection:
                try:
                    connection.execute("BEGIN")
                    snapshot = self._validated_snapshot(connection)
                    response = self._signed(
                        operation="read",
                        snapshot=snapshot,
                        challenge=challenge,
                    )
                    yield response
                finally:
                    if connection.in_transaction:
                        connection.rollback()
        except Exception as exc:
            raise ValueError("Signed authority held read failed.") from exc

    def advance_if_current(
        self, *, expected_revision, next_revision,
        expected_generation, expected_fence_token, challenge,
    ):
        try:
            self.__post_init__()
            challenge = _require_challenge(challenge)
            old = _require_integer(expected_revision, "expected revision")
            new = _require_integer(next_revision, "next revision")
            old_generation = _require_integer(
                expected_generation, "expected generation"
            )
            old_fence = _require_integer(
                expected_fence_token, "expected fencing token"
            )
            if (
                new <= old
                or old_generation >= _MAX_INTEGER
                or old_fence >= _MAX_INTEGER
            ):
                raise ValueError("Invalid signed authority CAS transition.")

            with closing(self._connect(readonly=False)) as connection:
                try:
                    connection.execute("BEGIN IMMEDIATE")
                    current = self._validated_snapshot(connection)
                    if current[4:] != (old, old_generation, old_fence):
                        raise ValueError("Stale signed authority CAS preconditions.")
                    updated = connection.execute(
                        "UPDATE checkpoint_signed_authority_state "
                        "SET revision = ?, generation = ?, fence_token = ? "
                        "WHERE singleton_id = 1 "
                        "AND revision = ? AND generation = ? AND fence_token = ?",
                        (
                            new, old_generation + 1, old_fence + 1,
                            old, old_generation, old_fence,
                        ),
                    )
                    if updated.rowcount != 1:
                        raise ValueError("Signed authority CAS changed no row.")
                    connection.commit()
                    published = (
                        current[0], current[1], current[2], current[3],
                        new, old_generation + 1, old_fence + 1,
                    )
                finally:
                    if connection.in_transaction:
                        connection.rollback()

            return self._signed(
                operation="cas",
                snapshot=published,
                challenge=challenge,
                transition=(old, new, old_generation, old_fence),
            )
        except Exception as exc:
            # An exception after dispatch can leave commit outcome uncertain.
            # Never automatically retry a failed or uncertain publication.
            raise ValueError(
                "Signed authority CAS failed or outcome uncertain; inspect state before retry."
            ) from exc
