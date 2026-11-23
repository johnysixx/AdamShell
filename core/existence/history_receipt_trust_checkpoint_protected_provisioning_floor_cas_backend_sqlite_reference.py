"""A44 SQLite reference signed provisioning-generation CAS authority.

LOCAL REFERENCE ONLY. State and operation receipts are committed in one
SQLite transaction. This does not establish an independently trusted or
rollback-resistant authority, secure signing-key storage, physical power-
loss durability, remote linearizability, or cross-store atomicity.
A valid old database image can restore counters and erase receipts.
An ambiguous CAS result requires lookup using the original operation ID.
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
    history_receipt_trust_checkpoint_protected_provisioning_floor as floor,
)


_STATE_SCHEMA = (
    "CREATE TABLE provisioning_generation_state ("
    "singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),"
    "authority_id TEXT NOT NULL,"
    "subject_id TEXT NOT NULL,"
    "signer_public_key BLOB NOT NULL,"
    "generation INTEGER NOT NULL)"
)

_OPERATIONS_SCHEMA = (
    "CREATE TABLE provisioning_generation_operations ("
    "operation_id TEXT PRIMARY KEY NOT NULL,"
    "expected_generation INTEGER NOT NULL,"
    "next_generation INTEGER NOT NULL,"
    "committed_generation INTEGER NOT NULL)"
)


def _path(value):
    if type(value) is str and value:
        value = Path(value)
    if not isinstance(value, Path) or not str(value):
        raise ValueError("Invalid provisioning generation SQLite path.")
    return value


def _identity(value, label):
    return high_water._identity(value, label)


def _generation(value, label):
    return high_water._counter(value, label)


def _operation_id(value):
    return high_water._operation_id(value)


def _challenge(value):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError("Invalid provisioning generation challenge.")
    return value


def _public_key(signer):
    if not isinstance(signer, Ed25519PrivateKey):
        raise ValueError("Expected Ed25519 provisioning authority signer.")
    return signer.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


@dataclass(frozen=True, slots=True)
class SQLiteReferenceSignedProvisioningGenerationCASAuthority:
    """Signed local SQLite provider, not a protected trust root."""

    _path: Path
    signer: Ed25519PrivateKey
    authority_id: str
    subject_id: str

    def __post_init__(self):
        _path(self._path)
        _public_key(self.signer)
        _identity(self.authority_id, "provisioning authority")
        _identity(self.subject_id, "provisioning subject")

    @classmethod
    def bootstrap(
        cls, *, path, signer, authority_id, subject_id, initial_generation
    ):
        path = _path(path)
        _public_key(signer)
        _identity(authority_id, "provisioning authority")
        _identity(subject_id, "provisioning subject")
        initial = _generation(initial_generation, "initial provisioning generation")

        try:
            # Exclusive creation prevents accidental rebootstrap of any
            # existing state, including a corrupt or empty SQLite file.
            with path.open("xb"):
                pass
        except (OSError, ValueError) as exc:
            raise ValueError(
                "Provisioning generation database already exists or is unavailable."
            ) from exc

        backend = cls(path, signer, authority_id, subject_id)
        try:
            with closing(backend._connect(readonly=False)) as connection:
                connection.execute("PRAGMA journal_mode=DELETE")
                connection.execute("PRAGMA synchronous=FULL")
                connection.execute("BEGIN IMMEDIATE")
                try:
                    connection.execute(_STATE_SCHEMA)
                    connection.execute(_OPERATIONS_SCHEMA)
                    connection.execute(
                        "INSERT INTO provisioning_generation_state "
                        "(singleton_id, authority_id, subject_id, "
                        "signer_public_key, generation) VALUES (1, ?, ?, ?, ?)",
                        (authority_id, subject_id, _public_key(signer), initial),
                    )
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
            return backend
        except Exception as exc:
            raise ValueError(
                "Reference provisioning generation bootstrap failed."
            ) from exc

    @classmethod
    def open(
        cls, *, path, signer, expected_authority_id, expected_subject_id
    ):
        backend = cls(
            _path(path), signer, expected_authority_id, expected_subject_id
        )
        try:
            with closing(backend._connect(readonly=True)) as connection:
                backend._snapshot(connection)
            return backend
        except Exception as exc:
            raise ValueError(
                "Reference provisioning generation database open failed."
            ) from exc

    def _connect(self, *, readonly):
        connection = None
        try:
            location = self._path.resolve(strict=True).as_uri()
            mode = "ro" if readonly else "rw"
            connection = sqlite3.connect(
                f"{location}?mode={mode}",
                uri=True,
                timeout=5.0,
                isolation_level=None,
            )
            connection.execute("PRAGMA busy_timeout=5000")
            if not readonly:
                connection.execute("PRAGMA synchronous=FULL")
            return connection
        except Exception as exc:
            if connection is not None:
                connection.close()
            raise ValueError("Provisioning SQLite database unavailable.") from exc

    def _snapshot(self, connection):
        journal = connection.execute("PRAGMA journal_mode").fetchone()
        if (
            type(journal) is not tuple
            or len(journal) != 1
            or type(journal[0]) is not str
            or journal[0].lower() != "delete"
        ):
            raise ValueError("Unsupported provisioning SQLite journal mode.")

        rows = connection.execute(
            "SELECT singleton_id, authority_id, subject_id, "
            "signer_public_key, generation FROM provisioning_generation_state"
        ).fetchall()
        if len(rows) != 1:
            raise ValueError("Missing or ambiguous provisioning state.")
        singleton, authority, subject, key, generation = rows[0]
        if type(singleton) is not int or singleton != 1:
            raise ValueError("Invalid provisioning state singleton.")
        _identity(authority, "stored provisioning authority")
        _identity(subject, "stored provisioning subject")
        high_water._key(key, "stored provisioning signer key")
        generation = _generation(generation, "stored provisioning generation")

        if (
            authority != self.authority_id
            or subject != self.subject_id
            or not hmac.compare_digest(key, _public_key(self.signer))
        ):
            raise ValueError("Stored provisioning identity or signer mismatch.")
        return generation

    @staticmethod
    def _receipt(connection, operation_id, generation):
        rows = connection.execute(
            "SELECT expected_generation, next_generation, "
            "committed_generation FROM provisioning_generation_operations "
            "WHERE operation_id = ?",
            (operation_id,),
        ).fetchall()
        if len(rows) > 1:
            raise ValueError("Ambiguous provisioning operation receipt.")
        if not rows:
            return None
        expected, proposed, committed = (
            _generation(value, "stored provisioning operation counter")
            for value in rows[0]
        )
        if (
            proposed != expected + 1
            or committed != proposed
            or committed > generation
        ):
            raise ValueError("Invalid provisioning operation receipt.")
        return expected, proposed, committed

    def _signed(self, *, operation, challenge, generation, extra=None):
        doc = {
            "domain": floor._DOMAIN,
            "version": floor._VERSION,
            "operation": operation,
            "authority_id": self.authority_id,
            "subject_id": self.subject_id,
            "generation": generation,
            "challenge_hex": challenge.hex(),
        }
        if extra:
            doc.update(extra)
        message = json.dumps(
            doc, sort_keys=True, ensure_ascii=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("ascii")
        return message, self.signer.sign(message)

    @contextmanager
    def hold(self, *, challenge):
        _challenge(challenge)
        try:
            with closing(self._connect(readonly=True)) as connection:
                connection.execute("BEGIN")
                try:
                    generation = self._snapshot(connection)
                    result = self._signed(
                        operation="read", challenge=challenge,
                        generation=generation,
                    )
                    yield result
                finally:
                    connection.rollback()
        except Exception as exc:
            raise ValueError("Reference provisioning signed read failed.") from exc

    def advance_if_current(
        self, *, operation_id, expected_generation, next_generation, challenge
    ):
        operation_id = _operation_id(operation_id)
        expected = _generation(expected_generation, "expected provisioning generation")
        proposed = _generation(next_generation, "proposed provisioning generation")
        _challenge(challenge)
        if proposed != expected + 1:
            raise ValueError("Provisioning CAS must advance by one generation.")

        try:
            with closing(self._connect(readonly=False)) as connection:
                connection.execute("BEGIN IMMEDIATE")
                try:
                    generation = self._snapshot(connection)
                    prior = self._receipt(connection, operation_id, generation)
                    if prior is not None:
                        if prior[:2] != (expected, proposed):
                            raise ValueError("Provisioning operation ID rebound.")
                        status = "committed"
                    elif expected != generation:
                        status = "rejected"
                    else:
                        connection.execute(
                            "UPDATE provisioning_generation_state "
                            "SET generation = ? WHERE singleton_id = 1",
                            (proposed,),
                        )
                        connection.execute(
                            "INSERT INTO provisioning_generation_operations "
                            "(operation_id, expected_generation, next_generation, "
                            "committed_generation) VALUES (?, ?, ?, ?)",
                            (operation_id, expected, proposed, proposed),
                        )
                        generation = proposed
                        status = "committed"
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
            return self._signed(
                operation="cas", challenge=challenge, generation=generation,
                extra={
                    "operation_id": operation_id,
                    "expected_generation": expected,
                    "next_generation": proposed,
                    "status": status,
                },
            )
        except Exception as exc:
            raise ValueError("Reference provisioning generation CAS failed.") from exc

    def lookup_operation(self, *, operation_id, challenge):
        operation_id = _operation_id(operation_id)
        _challenge(challenge)
        try:
            with closing(self._connect(readonly=True)) as connection:
                connection.execute("BEGIN")
                try:
                    generation = self._snapshot(connection)
                    prior = self._receipt(connection, operation_id, generation)
                    status = "committed" if prior is not None else "unknown"
                    result = self._signed(
                        operation="lookup", challenge=challenge,
                        generation=generation,
                        extra={"operation_id": operation_id, "status": status},
                    )
                finally:
                    connection.rollback()
            return result
        except Exception as exc:
            raise ValueError(
                "Reference provisioning operation lookup failed."
            ) from exc
