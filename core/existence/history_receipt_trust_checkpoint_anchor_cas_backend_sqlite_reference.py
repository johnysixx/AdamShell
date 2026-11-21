"""A44 SQLite reference checkpoint anchor CAS authority.

Reference implementation only: state and operation receipt are updated in
one local SQLite transaction. This is NOT an independent remote anchor,
rollback-resistant store, hardware-protected identity or power-loss proof.
A valid old database image can replace a newer image. The signing key is
provided externally and is not stored in the database.
"""

import hmac
import json
import os
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)
from core.existence import history_receipt_trust_checkpoint_pinned_anchor_client as signed_read
from core.existence import history_receipt_trust_checkpoint_anchor_cas_client as cas_client

_MAX = (1 << 63) - 1

_SCHEMA = (
    "CREATE TABLE checkpoint_anchor_cas_state ("
    "singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),"
    "anchor_id TEXT NOT NULL, anchor_public_key BLOB NOT NULL,"
    "authority_id TEXT NOT NULL, authority_public_key BLOB NOT NULL,"
    "root_id TEXT NOT NULL, root_public_key BLOB NOT NULL,"
    "enrollment_epoch INTEGER NOT NULL,"
    "revision INTEGER NOT NULL, generation INTEGER NOT NULL,"
    "fence_token INTEGER NOT NULL)"
)

_OPERATIONS_SCHEMA = (
    "CREATE TABLE checkpoint_anchor_cas_operations ("
    "operation_id TEXT PRIMARY KEY NOT NULL,"
    "expected_revision INTEGER NOT NULL,"
    "next_revision INTEGER NOT NULL,"
    "expected_generation INTEGER NOT NULL,"
    "expected_fence_token INTEGER NOT NULL,"
    "committed_revision INTEGER NOT NULL,"
    "committed_generation INTEGER NOT NULL,"
    "committed_fence_token INTEGER NOT NULL)"
)


def _path(value):
    if type(value) is str and value:
        value = Path(value)

    if not isinstance(value, Path) or not str(value):
        raise ValueError("Invalid reference anchor SQLite path.")

    return value


def _key(value, label):
    return signed_read._require_key(value, label)


def _integer(value, label):
    return signed_read._require_integer(value, label)


def _challenge(value):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError("Invalid anchor challenge.")

    return bytes(value)


def _signer_key(signer):
    if not isinstance(signer, Ed25519PrivateKey):
        raise ValueError("Expected Ed25519 anchor signer.")

    try:
        raw = signer.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    except Exception as exc:
        raise ValueError("Cannot derive anchor signing key.") from exc

    return _key(raw, "anchor signer public key")


def _identity_values(
    anchor_id, authority_id, authority_key, root_id, root_key, epoch
):
    return (
        _require_identity(anchor_id, "anchor identity"),
        _require_identity(authority_id, "authority identity"),
        _key(authority_key, "authority public key"),
        _require_identity(root_id, "root identity"),
        _key(root_key, "root public key"),
        _integer(epoch, "enrollment epoch"),
    )


@dataclass(frozen=True, slots=True)
class SQLiteReferenceSignedCheckpointAnchorCASAuthority:
    """Local transactional CAS reference, not a trusted external authority."""

    _path: Path
    signer: Ed25519PrivateKey
    anchor_id: str
    authority_id: str
    authority_public_key: bytes
    root_id: str
    root_public_key: bytes
    enrollment_epoch: int

    def __post_init__(self):
        _path(self._path)
        _signer_key(self.signer)

        _identity_values(
            self.anchor_id,
            self.authority_id,
            self.authority_public_key,
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
                timeout=3.0,
            )

            connection.execute("PRAGMA busy_timeout=3000")

            if not readonly:
                connection.execute("PRAGMA synchronous=FULL")

            return connection

        except (OSError, sqlite3.Error, ValueError) as exc:
            if connection is not None:
                connection.close()

            raise ValueError(
                "Reference anchor database unavailable."
            ) from exc

    def _snapshot(self, connection):
        mode = connection.execute("PRAGMA journal_mode").fetchone()

        if (
            type(mode) is not tuple
            or len(mode) != 1
            or type(mode[0]) is not str
            or mode[0].lower() != "delete"
        ):
            raise ValueError(
                "Unsupported reference anchor SQLite journal mode."
            )

        rows = connection.execute(
            "SELECT singleton_id, anchor_id, anchor_public_key, "
            "authority_id, authority_public_key, root_id, root_public_key, "
            "enrollment_epoch, revision, generation, fence_token "
            "FROM checkpoint_anchor_cas_state"
        ).fetchall()

        if len(rows) != 1:
            raise ValueError(
                "Missing or ambiguous reference anchor state."
            )

        (
            singleton,
            anchor_id,
            anchor_key,
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
            raise ValueError("Invalid anchor singleton.")

        _identity_values(
            anchor_id,
            authority_id,
            authority_key,
            root_id,
            root_key,
            epoch,
        )

        _key(anchor_key, "stored anchor key")
        revision = _integer(revision, "stored revision")
        generation = _integer(generation, "stored generation")
        fence = _integer(fence, "stored fence token")

        if (
            anchor_id != self.anchor_id
            or authority_id != self.authority_id
            or root_id != self.root_id
            or epoch != self.enrollment_epoch
            or not hmac.compare_digest(
                anchor_key, _signer_key(self.signer)
            )
            or not hmac.compare_digest(
                authority_key, self.authority_public_key
            )
            or not hmac.compare_digest(
                root_key, self.root_public_key
            )
        ):
            raise ValueError(
                "Stored anchor identity or key pin mismatch."
            )

        return (
            authority_id,
            bytes(authority_key),
            root_id,
            bytes(root_key),
            epoch,
            revision,
            generation,
            fence,
        )

    @staticmethod
    def _operation(connection, operation_id):
        rows = connection.execute(
            "SELECT expected_revision, next_revision, expected_generation, "
            "expected_fence_token, committed_revision, "
            "committed_generation, committed_fence_token "
            "FROM checkpoint_anchor_cas_operations WHERE operation_id = ?",
            (operation_id,),
        ).fetchall()

        if len(rows) > 1:
            raise ValueError(
                "Ambiguous persisted operation record."
            )

        if not rows:
            return None

        values = tuple(
            _integer(value, "stored operation field")
            for value in rows[0]
        )

        if (
            values[1] <= values[0]
            or values[4] != values[1]
            or values[5] != values[2] + 1
            or values[6] != values[3] + 1
        ):
            raise ValueError(
                "Corrupt committed operation record."
            )

        return values

    def _signed(self, operation, snapshot, challenge, extra=None):
        challenge = _challenge(challenge)

        (
            authority_id,
            authority_key,
            root_id,
            root_key,
            epoch,
            revision,
            generation,
            fence,
        ) = snapshot

        document = {
            "domain": signed_read._DOMAIN,
            "version": 1,
            "operation": operation,
            "anchor_id": self.anchor_id,
            "authority_id": authority_id,
            "authority_public_key_hex": authority_key.hex(),
            "root_id": root_id,
            "root_public_key_hex": root_key.hex(),
            "enrollment_epoch": epoch,
            "revision": revision,
            "generation": generation,
            "fence_token": fence,
            "challenge_hex": challenge.hex(),
        }

        if extra:
            document.update(extra)

        payload = json.dumps(
            document,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")

        return payload, self.signer.sign(payload)

    @classmethod
    def bootstrap(
        cls,
        *,
        path,
        signer,
        anchor_id,
        authority_id,
        authority_public_key,
        root_id,
        root_public_key,
        enrollment_epoch,
        initial_revision,
        initial_generation,
        initial_fence_token,
    ):
        obj = cls(
            _path=_path(path),
            signer=signer,
            anchor_id=anchor_id,
            authority_id=authority_id,
            authority_public_key=authority_public_key,
            root_id=root_id,
            root_public_key=root_public_key,
            enrollment_epoch=enrollment_epoch,
        )

        revision = _integer(initial_revision, "initial revision")
        generation = _integer(initial_generation, "initial generation")
        fence = _integer(initial_fence_token, "initial fence token")

        try:
            fd = os.open(
                obj._path,
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
            )
            os.close(fd)

        except OSError as exc:
            raise ValueError(
                "Reference anchor store exists or cannot be created."
            ) from exc

        try:
            with closing(obj._connect(readonly=False)) as connection:
                try:
                    journal = connection.execute(
                        "PRAGMA journal_mode=DELETE"
                    ).fetchone()

                    if (
                        journal is None
                        or str(journal[0]).lower() != "delete"
                    ):
                        raise ValueError(
                            "DELETE journal mode unavailable."
                        )

                    connection.execute("BEGIN IMMEDIATE")
                    connection.execute(_SCHEMA)
                    connection.execute(_OPERATIONS_SCHEMA)

                    connection.execute(
                        "INSERT INTO checkpoint_anchor_cas_state VALUES "
                        "(1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            obj.anchor_id,
                            _signer_key(obj.signer),
                            obj.authority_id,
                            obj.authority_public_key,
                            obj.root_id,
                            obj.root_public_key,
                            obj.enrollment_epoch,
                            revision,
                            generation,
                            fence,
                        ),
                    )

                    connection.commit()

                finally:
                    if connection.in_transaction:
                        connection.rollback()

            with obj.hold(challenge=b"\x00" * 32):
                pass

            return obj

        except Exception as exc:
            # Never delete or auto-recreate an uncertain store.
            raise ValueError(
                "Reference anchor bootstrap failed; inspect store before retry."
            ) from exc

    @classmethod
    def open(
        cls,
        *,
        path,
        signer,
        expected_anchor_id,
        expected_authority_id,
        expected_authority_public_key,
        expected_root_id,
        expected_root_public_key,
        expected_enrollment_epoch,
    ):
        try:
            obj = cls(
                _path=_path(path),
                signer=signer,
                anchor_id=expected_anchor_id,
                authority_id=expected_authority_id,
                authority_public_key=expected_authority_public_key,
                root_id=expected_root_id,
                root_public_key=expected_root_public_key,
                enrollment_epoch=expected_enrollment_epoch,
            )

            with obj.hold(challenge=b"\x00" * 32):
                pass

            return obj

        except Exception as exc:
            raise ValueError(
                "Reference anchor open failed."
            ) from exc

    @contextmanager
    def hold(self, *, challenge):
        try:
            self.__post_init__()
            challenge = _challenge(challenge)

            with closing(self._connect(readonly=True)) as connection:
                try:
                    connection.execute("BEGIN")
                    snapshot = self._snapshot(connection)

                    response = self._signed(
                        "read",
                        snapshot,
                        challenge,
                    )

                    yield response

                finally:
                    if connection.in_transaction:
                        connection.rollback()

        except Exception as exc:
            raise ValueError(
                "Reference anchor held read failed."
            ) from exc

    def advance_if_current(
        self,
        *,
        operation_id,
        expected_revision,
        next_revision,
        expected_generation,
        expected_fence_token,
        challenge,
    ):
        try:
            self.__post_init__()

            operation_id = cas_client._require_operation_id(
                operation_id
            )

            old = _integer(
                expected_revision,
                "expected revision",
            )

            new = _integer(
                next_revision,
                "next revision",
            )

            generation = _integer(
                expected_generation,
                "expected generation",
            )

            fence = _integer(
                expected_fence_token,
                "expected fencing token",
            )

            challenge = _challenge(challenge)

            if (
                new <= old
                or generation >= _MAX
                or fence >= _MAX
            ):
                raise ValueError(
                    "Invalid CAS monotonic transition."
                )

            requested = (
                old,
                new,
                generation,
                fence,
            )

            with closing(self._connect(readonly=False)) as connection:
                try:
                    connection.execute("BEGIN IMMEDIATE")

                    current = self._snapshot(connection)

                    recorded = self._operation(
                        connection,
                        operation_id,
                    )

                    if recorded is not None:
                        if recorded[:4] != requested:
                            raise ValueError(
                                "Operation ID already bound to another request."
                            )

                        snapshot = current[:5] + recorded[4:]
                        status = "committed"

                    elif current[5:] != (
                        old,
                        generation,
                        fence,
                    ):
                        snapshot = current
                        status = "rejected"

                    else:
                        updated = connection.execute(
                            "UPDATE checkpoint_anchor_cas_state "
                            "SET revision = ?, generation = ?, fence_token = ? "
                            "WHERE singleton_id = 1 AND revision = ? "
                            "AND generation = ? AND fence_token = ?",
                            (
                                new,
                                generation + 1,
                                fence + 1,
                                old,
                                generation,
                                fence,
                            ),
                        )

                        if updated.rowcount != 1:
                            raise ValueError(
                                "CAS state update changed no row."
                            )

                        connection.execute(
                            "INSERT INTO checkpoint_anchor_cas_operations "
                            "(operation_id, expected_revision, next_revision, "
                            "expected_generation, expected_fence_token, "
                            "committed_revision, committed_generation, "
                            "committed_fence_token) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                operation_id,
                                old,
                                new,
                                generation,
                                fence,
                                new,
                                generation + 1,
                                fence + 1,
                            ),
                        )

                        # State and operation log commit together.
                        connection.commit()

                        snapshot = current[:5] + (
                            new,
                            generation + 1,
                            fence + 1,
                        )

                        status = "committed"

                finally:
                    if connection.in_transaction:
                        connection.rollback()

            return self._signed(
                "cas",
                snapshot,
                challenge,
                {
                    "operation_id": operation_id,
                    "expected_revision": old,
                    "next_revision": new,
                    "expected_generation": generation,
                    "expected_fence_token": fence,
                    "status": status,
                },
            )

        except Exception as exc:
            # A failure can occur after COMMIT.
            # Never automatically retry an ambiguous CAS.
            raise ValueError(
                "Reference anchor CAS failed or outcome is ambiguous."
            ) from exc

    def lookup_operation(self, *, operation_id, challenge):
        try:
            self.__post_init__()

            operation_id = cas_client._require_operation_id(
                operation_id
            )

            challenge = _challenge(challenge)

            with closing(self._connect(readonly=True)) as connection:
                try:
                    connection.execute("BEGIN")

                    current = self._snapshot(connection)
                    record = self._operation(
                        connection,
                        operation_id,
                    )

                    status = (
                        "committed"
                        if record is not None
                        else "unknown"
                    )

                    response = self._signed(
                        "lookup",
                        current,
                        challenge,
                        {
                            "operation_id": operation_id,
                            "status": status,
                        },
                    )

                finally:
                    if connection.in_transaction:
                        connection.rollback()

            return response

        except Exception as exc:
            raise ValueError(
                "Reference anchor lookup failed."
            ) from exc
