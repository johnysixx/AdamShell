"""A44 local SQLite reference CAS authority for signed deployment floors.

A state update and its operation receipt commit in one local SQLite transaction.
This is NOT an independently durable, rollback-proof, or remotely deployed
trust root. Private keys are supplied by the caller and not protected here.
A valid old database image can restore an earlier floor and erase receipts.
No cross-store atomicity or automatic retry after ambiguous outcomes exists.
"""

import hmac
import json
import sqlite3
from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water as high_water,
)
from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor
    as deployment_floor,
)

_STATE_SCHEMA = (
    "CREATE TABLE witness_deployment_floor_state ("
    "singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),"
    "floor_id TEXT NOT NULL, subject_id TEXT NOT NULL,"
    "signer_public_key BLOB NOT NULL,"
    "authority_id TEXT NOT NULL, authority_public_key BLOB NOT NULL,"
    "witness_id TEXT NOT NULL, witness_public_key BLOB NOT NULL,"
    "minimum_generation INTEGER NOT NULL, epoch INTEGER NOT NULL)"
)
_OPERATIONS_SCHEMA = (
    "CREATE TABLE witness_deployment_floor_operations ("
    "operation_id TEXT PRIMARY KEY NOT NULL,"
    "expected_epoch INTEGER NOT NULL, next_epoch INTEGER NOT NULL,"
    "expected_minimum_generation INTEGER NOT NULL,"
    "next_minimum_generation INTEGER NOT NULL,"
    "committed_epoch INTEGER NOT NULL,"
    "committed_minimum_generation INTEGER NOT NULL)"
)


def _path(value):
    if type(value) is str and value:
        value = Path(value)
    if not isinstance(value, Path) or not str(value):
        raise ValueError("Invalid deployment floor SQLite path.")
    return value


def _identity(value, label):
    return high_water._identity(value, label)


def _counter(value, label):
    return high_water._counter(value, label)


def _key(value, label):
    return high_water._key(value, label)


def _operation_id(value):
    return high_water._operation_id(value)


def _challenge(value):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError("Expected 32-byte deployment floor challenge.")
    return value


def _public_key(signer):
    if not isinstance(signer, Ed25519PrivateKey):
        raise ValueError("Expected Ed25519 deployment floor signer.")
    return signer.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _pins(signer, authority_public_key, witness_public_key):
    signing_key = _public_key(signer)
    authority_key = _key(authority_public_key, "authority public key")
    witness_key = _key(witness_public_key, "witness public key")
    if (
        hmac.compare_digest(signing_key, authority_key)
        or hmac.compare_digest(signing_key, witness_key)
        or hmac.compare_digest(authority_key, witness_key)
    ):
        raise ValueError("Deployment floor must have three distinct signing keys.")
    return signing_key, authority_key, witness_key


@dataclass(frozen=True, slots=True)
class SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority:
    """Local reference provider for signed read, CAS and operation lookup."""

    _path: Path
    signer: Ed25519PrivateKey
    floor_id: str
    subject_id: str
    authority_id: str
    authority_public_key: bytes
    witness_id: str
    witness_public_key: bytes

    def __post_init__(self):
        _path(self._path)
        _identity(self.floor_id, "deployment floor identity")
        _identity(self.subject_id, "deployment floor subject")
        _identity(self.authority_id, "deployment authority identity")
        _identity(self.witness_id, "deployment witness identity")
        _pins(self.signer, self.authority_public_key, self.witness_public_key)

    @classmethod
    def bootstrap(
        cls, *, path, signer, floor_id, subject_id, authority_id,
        authority_public_key, witness_id, witness_public_key,
        initial_minimum_generation, initial_epoch,
    ):
        path = _path(path)
        minimum = _counter(initial_minimum_generation, "initial deployment minimum")
        epoch = _counter(initial_epoch, "initial deployment epoch")
        if epoch < 1:
            raise ValueError("Initial deployment floor epoch must be positive.")
        backend = cls(
            path, signer, floor_id, subject_id, authority_id,
            authority_public_key, witness_id, witness_public_key,
        )
        # Refuse all existing paths, even empty or corrupt SQLite files.
        try:
            with path.open("xb"):
                pass
        except (OSError, ValueError) as exc:
            raise ValueError("Deployment floor database exists or is unavailable.") from exc
        try:
            with closing(backend._connect(readonly=False)) as connection:
                connection.execute("PRAGMA journal_mode=DELETE")
                connection.execute("PRAGMA synchronous=FULL")
                connection.execute("BEGIN IMMEDIATE")
                try:
                    connection.execute(_STATE_SCHEMA)
                    connection.execute(_OPERATIONS_SCHEMA)
                    connection.execute(
                        "INSERT INTO witness_deployment_floor_state ("
                        "singleton_id, floor_id, subject_id, signer_public_key, "
                        "authority_id, authority_public_key, witness_id, "
                        "witness_public_key, minimum_generation, epoch) "
                        "VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            floor_id, subject_id, _public_key(signer),
                            authority_id, authority_public_key, witness_id,
                            witness_public_key, minimum, epoch,
                        ),
                    )
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
            return backend
        except Exception as exc:
            raise ValueError("Deployment floor SQLite bootstrap failed.") from exc

    @classmethod
    def open(
        cls, *, path, signer, expected_floor_id, expected_subject_id,
        expected_authority_id, expected_authority_public_key,
        expected_witness_id, expected_witness_public_key,
    ):
        backend = cls(
            _path(path), signer, expected_floor_id, expected_subject_id,
            expected_authority_id, expected_authority_public_key,
            expected_witness_id, expected_witness_public_key,
        )
        try:
            with closing(backend._connect(readonly=True)) as connection:
                backend._snapshot(connection)
            return backend
        except Exception as exc:
            raise ValueError("Deployment floor SQLite open failed.") from exc

    def _connect(self, *, readonly):
        connection = None
        try:
            location = self._path.resolve(strict=True).as_uri()
            mode = "ro" if readonly else "rw"
            connection = sqlite3.connect(
                f"{location}?mode={mode}", uri=True,
                timeout=5.0, isolation_level=None,
            )
            connection.execute("PRAGMA busy_timeout=5000")
            if not readonly:
                connection.execute("PRAGMA synchronous=FULL")
            return connection
        except Exception as exc:
            if connection is not None:
                connection.close()
            raise ValueError("Deployment floor SQLite database unavailable.") from exc

    def _snapshot(self, connection):
        journal = connection.execute("PRAGMA journal_mode").fetchone()
        if (
            type(journal) is not tuple or len(journal) != 1
            or type(journal[0]) is not str or journal[0].lower() != "delete"
        ):
            raise ValueError("Unsupported deployment floor journal mode.")
        rows = connection.execute(
            "SELECT singleton_id, floor_id, subject_id, signer_public_key, "
            "authority_id, authority_public_key, witness_id, "
            "witness_public_key, minimum_generation, epoch "
            "FROM witness_deployment_floor_state"
        ).fetchall()
        if len(rows) != 1:
            raise ValueError("Missing or ambiguous deployment floor singleton.")
        (singleton, floor_id, subject_id, signer_key, authority_id,
         authority_key, witness_id, witness_key, minimum, epoch) = rows[0]
        if type(singleton) is not int or singleton != 1:
            raise ValueError("Invalid deployment floor singleton ID.")
        _identity(floor_id, "stored floor identity")
        _identity(subject_id, "stored subject identity")
        _identity(authority_id, "stored authority identity")
        _identity(witness_id, "stored witness identity")
        _key(signer_key, "stored floor signing key")
        _key(authority_key, "stored authority signing key")
        _key(witness_key, "stored witness signing key")
        minimum = _counter(minimum, "stored minimum generation")
        epoch = _counter(epoch, "stored deployment epoch")
        if epoch < 1 or (
            floor_id != self.floor_id
            or subject_id != self.subject_id
            or authority_id != self.authority_id
            or witness_id != self.witness_id
            or not hmac.compare_digest(signer_key, _public_key(self.signer))
            or not hmac.compare_digest(authority_key, self.authority_public_key)
            or not hmac.compare_digest(witness_key, self.witness_public_key)
        ):
            raise ValueError("Deployment floor state does not match trusted pins.")
        return minimum, epoch

    @staticmethod
    def _receipt(connection, operation_id, minimum, epoch):
        rows = connection.execute(
            "SELECT expected_epoch, next_epoch, expected_minimum_generation, "
            "next_minimum_generation, committed_epoch, "
            "committed_minimum_generation "
            "FROM witness_deployment_floor_operations WHERE operation_id = ?",
            (operation_id,),
        ).fetchall()
        if len(rows) > 1:
            raise ValueError("Ambiguous deployment floor operation receipt.")
        if not rows:
            return None
        (expected_epoch, next_epoch, expected_minimum, next_minimum,
         committed_epoch, committed_minimum) = (
            _counter(value, "stored deployment operation counter")
            for value in rows[0]
        )
        if (
            next_epoch != expected_epoch + 1
            or expected_epoch < 1
            or next_minimum < expected_minimum
            or committed_epoch != next_epoch
            or committed_minimum != next_minimum
            or committed_epoch > epoch
            or committed_minimum > minimum
        ):
            raise ValueError("Invalid deployment floor committed receipt.")
        return expected_epoch, next_epoch, expected_minimum, next_minimum

    def _signed(self, *, operation, challenge, minimum, epoch, extra=None):
        document = {
            "domain": deployment_floor._DOMAIN,
            "version": deployment_floor._VERSION,
            "operation": operation,
            "floor_id": self.floor_id,
            "subject_id": self.subject_id,
            "authority_id": self.authority_id,
            "authority_public_key_hex": self.authority_public_key.hex(),
            "witness_id": self.witness_id,
            "witness_public_key_hex": self.witness_public_key.hex(),
            "minimum_generation": minimum,
            "epoch": epoch,
            "challenge_hex": challenge.hex(),
        }
        if extra is not None:
            document.update(extra)
        message = json.dumps(
            document, sort_keys=True, ensure_ascii=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("ascii")
        return message, self.signer.sign(message)

    @contextmanager
    def hold(self, *, challenge):
        challenge = _challenge(challenge)
        try:
            with closing(self._connect(readonly=True)) as connection:
                connection.execute("BEGIN")
                try:
                    minimum, epoch = self._snapshot(connection)
                    signed = self._signed(
                        operation="read", challenge=challenge,
                        minimum=minimum, epoch=epoch,
                    )
                    yield signed
                finally:
                    connection.rollback()
        except Exception as exc:
            raise ValueError("Deployment floor signed hold failed.") from exc

    def advance_if_current(
        self, *, operation_id, expected_epoch, next_epoch,
        expected_minimum_generation, next_minimum_generation, challenge,
    ):
        operation_id = _operation_id(operation_id)
        expected_epoch = _counter(expected_epoch, "expected deployment epoch")
        next_epoch = _counter(next_epoch, "next deployment epoch")
        expected_minimum = _counter(
            expected_minimum_generation, "expected deployment minimum"
        )
        next_minimum = _counter(next_minimum_generation, "next deployment minimum")
        challenge = _challenge(challenge)
        if (
            expected_epoch < 1
            or next_epoch != expected_epoch + 1
            or next_minimum < expected_minimum
        ):
            raise ValueError("Deployment floor CAS must be monotonic.")
        try:
            with closing(self._connect(readonly=False)) as connection:
                connection.execute("BEGIN IMMEDIATE")
                try:
                    minimum, epoch = self._snapshot(connection)
                    prior = self._receipt(connection, operation_id, minimum, epoch)
                    if prior is not None:
                        if prior != (
                            expected_epoch, next_epoch, expected_minimum,
                            next_minimum,
                        ):
                            raise ValueError("Deployment floor operation ID rebound.")
                        status = "committed"
                    elif (epoch, minimum) != (expected_epoch, expected_minimum):
                        status = "rejected"
                    else:
                        connection.execute(
                            "UPDATE witness_deployment_floor_state "
                            "SET minimum_generation = ?, epoch = ? "
                            "WHERE singleton_id = 1",
                            (next_minimum, next_epoch),
                        )
                        connection.execute(
                            "INSERT INTO witness_deployment_floor_operations ("
                            "operation_id, expected_epoch, next_epoch, "
                            "expected_minimum_generation, next_minimum_generation, "
                            "committed_epoch, committed_minimum_generation) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (
                                operation_id, expected_epoch, next_epoch,
                                expected_minimum, next_minimum,
                                next_epoch, next_minimum,
                            ),
                        )
                        minimum, epoch = next_minimum, next_epoch
                        status = "committed"
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
            return self._signed(
                operation="cas", challenge=challenge, minimum=minimum,
                epoch=epoch,
                extra={
                    "operation_id": operation_id,
                    "expected_epoch": expected_epoch,
                    "next_epoch": next_epoch,
                    "expected_minimum_generation": expected_minimum,
                    "next_minimum_generation": next_minimum,
                    "status": status,
                },
            )
        except Exception as exc:
            raise ValueError("Deployment floor CAS failed or ambiguous.") from exc

    def lookup_operation(self, *, operation_id, challenge):
        operation_id = _operation_id(operation_id)
        challenge = _challenge(challenge)
        try:
            with closing(self._connect(readonly=True)) as connection:
                connection.execute("BEGIN")
                try:
                    minimum, epoch = self._snapshot(connection)
                    prior = self._receipt(connection, operation_id, minimum, epoch)
                    status = "committed" if prior is not None else "unknown"
                    signed = self._signed(
                        operation="lookup", challenge=challenge,
                        minimum=minimum, epoch=epoch,
                        extra={"operation_id": operation_id, "status": status},
                    )
                finally:
                    connection.rollback()
            return signed
        except Exception as exc:
            raise ValueError("Deployment floor operation lookup failed.") from exc
