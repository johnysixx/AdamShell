"""A44 SQLite reference signed protected high-water CAS authority.

LOCAL REFERENCE IMPLEMENTATION ONLY.

The floor and operation receipt are committed in one local SQLite
transaction. The database uses DELETE journal mode and FULL
synchronous settings for ordinary SQLite recovery testing.

This does NOT prove physical power-loss durability, remote
linearizability, independent trust, hardware-protected signing
keys, rollback resistance or cross-store atomicity.

Replacing the SQLite file with an older valid image restores
old counters and may erase committed operation records.

A failed CAS call may have committed already. The caller must
preserve operation IDs and resolve uncertainty using lookup.
No automatic retry, bootstrap overwrite, checkpoint restoration
or republication is authorized.
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

from core.existence.history_receipt_trust_checkpoint_anchor_trusted_enrollment import (
    TrustedSignedCheckpointAnchorEnrollment,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water
    as high_water
)


_MAX = (1 << 63) - 1

_STATE_SCHEMA = (
    "CREATE TABLE protected_high_water_state ("
    "singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),"
    "store_id TEXT NOT NULL,"
    "store_public_key BLOB NOT NULL,"
    "anchor_id TEXT NOT NULL,"
    "anchor_public_key BLOB NOT NULL,"
    "authority_id TEXT NOT NULL,"
    "authority_public_key BLOB NOT NULL,"
    "root_id TEXT NOT NULL,"
    "root_public_key BLOB NOT NULL,"
    "enrollment_epoch INTEGER NOT NULL,"
    "revision INTEGER NOT NULL,"
    "generation INTEGER NOT NULL,"
    "fence_token INTEGER NOT NULL)"
)

_OPERATIONS_SCHEMA = (
    "CREATE TABLE protected_high_water_operations ("
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
        raise ValueError(
            "Invalid reference high-water database path."
        )

    return value


def _counter(value, label):
    return high_water._counter(value, label)


def _identity(value, label):
    return high_water._identity(value, label)


def _key(value, label):
    return high_water._key(value, label)


def _operation_id(value):
    return high_water._operation_id(value)


def _challenge(value):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(
            "Invalid reference high-water challenge."
        )

    return bytes(value)


def _signer_public_key(signer):
    if not isinstance(signer, Ed25519PrivateKey):
        raise ValueError(
            "Expected Ed25519 high-water signing key."
        )

    try:
        public_key = signer.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    except Exception as exc:
        raise ValueError(
            "Cannot derive high-water public key."
        ) from exc

    return _key(
        public_key,
        "high-water signing public key",
    )


def _enrollment_pins(value):
    if type(value) is not TrustedSignedCheckpointAnchorEnrollment:
        raise ValueError(
            "Expected canonical signed anchor enrollment."
        )

    return value._client_pins()


@dataclass(frozen=True, slots=True)
class SQLiteReferenceSignedProtectedHighWaterCASAuthority:
    """Local signed SQLite CAS reference backend, not a trust root."""

    _path: Path
    signer: Ed25519PrivateKey
    store_id: str
    enrollment: TrustedSignedCheckpointAnchorEnrollment

    def __post_init__(self):
        _path(self._path)
        _signer_public_key(self.signer)
        _identity(
            self.store_id,
            "reference high-water store identity",
        )
        _enrollment_pins(self.enrollment)

    def _connect(self, *, readonly):
        connection = None

        try:
            target = (
                self._path.resolve(strict=True).as_uri()
            )

            mode = "ro" if readonly else "rw"

            connection = sqlite3.connect(
                f"{target}?mode={mode}",
                uri=True,
                isolation_level=None,
                timeout=5.0,
            )

            connection.execute(
                "PRAGMA busy_timeout=5000"
            )

            if not readonly:
                connection.execute(
                    "PRAGMA synchronous=FULL"
                )

            return connection

        except (OSError, sqlite3.Error, ValueError) as exc:
            if connection is not None:
                connection.close()

            raise ValueError(
                "Reference high-water database unavailable."
            ) from exc

    def _snapshot(self, connection):
        journal = connection.execute(
            "PRAGMA journal_mode"
        ).fetchone()

        if (
            type(journal) is not tuple
            or len(journal) != 1
            or type(journal[0]) is not str
            or journal[0].lower() != "delete"
        ):
            raise ValueError(
                "Unsupported high-water SQLite journal mode."
            )

        rows = connection.execute(
            "SELECT singleton_id, store_id, store_public_key, "
            "anchor_id, anchor_public_key, "
            "authority_id, authority_public_key, "
            "root_id, root_public_key, enrollment_epoch, "
            "revision, generation, fence_token "
            "FROM protected_high_water_state"
        ).fetchall()

        if len(rows) != 1:
            raise ValueError(
                "Missing or ambiguous high-water state."
            )

        (
            singleton,
            store_id,
            store_key,
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
            raise ValueError(
                "Invalid reference high-water singleton."
            )

        store_id = _identity(
            store_id,
            "stored high-water identity",
        )

        anchor_id = _identity(
            anchor_id,
            "stored anchor identity",
        )

        authority_id = _identity(
            authority_id,
            "stored authority identity",
        )

        root_id = _identity(
            root_id,
            "stored root identity",
        )

        store_key = _key(
            store_key,
            "stored high-water signing key",
        )

        anchor_key = _key(
            anchor_key,
            "stored anchor key",
        )

        authority_key = _key(
            authority_key,
            "stored authority key",
        )

        root_key = _key(
            root_key,
            "stored root key",
        )

        epoch = _counter(
            epoch,
            "stored enrollment epoch",
        )

        revision = _counter(
            revision,
            "stored high-water revision",
        )

        generation = _counter(
            generation,
            "stored high-water generation",
        )

        fence = _counter(
            fence,
            "stored high-water fencing token",
        )

        pins = _enrollment_pins(
            self.enrollment
        )

        if (
            store_id != self.store_id
            or anchor_id != pins["expected_anchor_id"]
            or authority_id != pins["expected_authority_id"]
            or root_id != pins["expected_root_id"]
            or epoch != pins["expected_enrollment_epoch"]
            or not hmac.compare_digest(
                store_key,
                _signer_public_key(self.signer),
            )
            or not hmac.compare_digest(
                anchor_key,
                pins["expected_anchor_public_key"],
            )
            or not hmac.compare_digest(
                authority_key,
                pins["expected_authority_public_key"],
            )
            or not hmac.compare_digest(
                root_key,
                pins["expected_root_public_key"],
            )
        ):
            raise ValueError(
                "Persisted high-water identity or key mismatch."
            )

        if (
            revision < pins["minimum_revision"]
            or generation < pins["minimum_generation"]
            or fence < pins["minimum_fence_token"]
        ):
            raise ValueError(
                "Persisted floor below enrolled high-water minima."
            )

        return (
            revision,
            generation,
            fence,
        )

    @staticmethod
    def _operation(connection, operation_id):
        rows = connection.execute(
            "SELECT expected_revision, next_revision, "
            "expected_generation, expected_fence_token, "
            "committed_revision, committed_generation, "
            "committed_fence_token "
            "FROM protected_high_water_operations "
            "WHERE operation_id = ?",
            (operation_id,),
        ).fetchall()

        if len(rows) > 1:
            raise ValueError(
                "Ambiguous persisted high-water operation."
            )

        if not rows:
            return None

        values = tuple(
            _counter(
                value,
                "persisted high-water operation field",
            )
            for value in rows[0]
        )

        if (
            values[1] <= values[0]
            or values[4] != values[1]
            or values[5] != values[2] + 1
            or values[6] != values[3] + 1
        ):
            raise ValueError(
                "Corrupt high-water operation receipt."
            )

        return values

    def _signed(
        self,
        operation,
        floor,
        challenge,
        extra=None,
    ):
        challenge = _challenge(
            challenge
        )

        pins = _enrollment_pins(
            self.enrollment
        )

        document = {
            "domain": high_water._DOMAIN,
            "version": high_water._VERSION,
            "operation": operation,
            "store_id": self.store_id,
            "anchor_id": pins["expected_anchor_id"],
            "anchor_public_key_hex": (
                pins["expected_anchor_public_key"].hex()
            ),
            "authority_id": pins["expected_authority_id"],
            "authority_public_key_hex": (
                pins["expected_authority_public_key"].hex()
            ),
            "root_id": pins["expected_root_id"],
            "root_public_key_hex": (
                pins["expected_root_public_key"].hex()
            ),
            "enrollment_epoch": pins["expected_enrollment_epoch"],
            "revision": floor[0],
            "generation": floor[1],
            "fence_token": floor[2],
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

        return (
            payload,
            self.signer.sign(payload),
        )

    @classmethod
    def bootstrap(
        cls,
        *,
        path,
        signer,
        store_id,
        enrollment,
        initial_revision,
        initial_generation,
        initial_fence_token,
    ):
        obj = cls(
            _path=_path(path),
            signer=signer,
            store_id=store_id,
            enrollment=enrollment,
        )

        revision = _counter(
            initial_revision,
            "initial high-water revision",
        )

        generation = _counter(
            initial_generation,
            "initial high-water generation",
        )

        fence = _counter(
            initial_fence_token,
            "initial high-water fencing token",
        )

        pins = _enrollment_pins(enrollment)

        if (
            revision < pins["minimum_revision"]
            or generation < pins["minimum_generation"]
            or fence < pins["minimum_fence_token"]
        ):
            raise ValueError(
                "Initial high-water state below enrollment minima."
            )

        try:
            fd = os.open(
                obj._path,
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
            )

            os.close(fd)

        except OSError as exc:
            raise ValueError(
                "High-water store exists or cannot be created."
            ) from exc

        try:
            with closing(
                obj._connect(readonly=False)
            ) as connection:
                try:
                    journal = connection.execute(
                        "PRAGMA journal_mode=DELETE"
                    ).fetchone()

                    if (
                        journal is None
                        or str(journal[0]).lower() != "delete"
                    ):
                        raise ValueError(
                            "SQLite DELETE journal mode unavailable."
                        )

                    connection.execute(
                        "BEGIN IMMEDIATE"
                    )

                    connection.execute(
                        _STATE_SCHEMA
                    )

                    connection.execute(
                        _OPERATIONS_SCHEMA
                    )

                    connection.execute(
                        "INSERT INTO protected_high_water_state "
                        "VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            obj.store_id,
                            _signer_public_key(obj.signer),
                            pins["expected_anchor_id"],
                            pins["expected_anchor_public_key"],
                            pins["expected_authority_id"],
                            pins["expected_authority_public_key"],
                            pins["expected_root_id"],
                            pins["expected_root_public_key"],
                            pins["expected_enrollment_epoch"],
                            revision,
                            generation,
                            fence,
                        ),
                    )

                    connection.commit()

                finally:
                    if connection.in_transaction:
                        connection.rollback()

            with obj.hold(
                challenge=b"\x00" * 32
            ):
                pass

            return obj

        except Exception as exc:
            # The created store may be partially initialized.
            # Never delete it or retry bootstrap automatically.
            raise ValueError(
                "High-water bootstrap failed; inspect store before retry."
            ) from exc

    @classmethod
    def open(
        cls,
        *,
        path,
        signer,
        expected_store_id,
        enrollment,
    ):
        try:
            obj = cls(
                _path=_path(path),
                signer=signer,
                store_id=expected_store_id,
                enrollment=enrollment,
            )

            with obj.hold(
                challenge=b"\x00" * 32
            ):
                pass

            return obj

        except Exception as exc:
            raise ValueError(
                "Reference high-water store open failed."
            ) from exc

    @contextmanager
    def hold(self, *, challenge):
        try:
            self.__post_init__()

            challenge = _challenge(
                challenge
            )

            with closing(
                self._connect(readonly=True)
            ) as connection:
                try:
                    connection.execute(
                        "BEGIN"
                    )

                    floor = self._snapshot(
                        connection
                    )

                    response = self._signed(
                        "read",
                        floor,
                        challenge,
                    )

                    yield response

                finally:
                    if connection.in_transaction:
                        connection.rollback()

        except Exception as exc:
            raise ValueError(
                "Reference high-water held read failed."
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

            operation_id = _operation_id(
                operation_id
            )

            old = _counter(
                expected_revision,
                "expected high-water revision",
            )

            new = _counter(
                next_revision,
                "next high-water revision",
            )

            generation = _counter(
                expected_generation,
                "expected high-water generation",
            )

            fence = _counter(
                expected_fence_token,
                "expected high-water fencing token",
            )

            challenge = _challenge(
                challenge
            )

            if (
                new <= old
                or generation >= _MAX
                or fence >= _MAX
            ):
                raise ValueError(
                    "Invalid reference high-water CAS transition."
                )

            request = (
                old,
                new,
                generation,
                fence,
            )

            with closing(
                self._connect(readonly=False)
            ) as connection:
                try:
                    connection.execute(
                        "BEGIN IMMEDIATE"
                    )

                    current = self._snapshot(
                        connection
                    )

                    recorded = self._operation(
                        connection,
                        operation_id,
                    )

                    if recorded is not None:
                        if recorded[:4] != request:
                            raise ValueError(
                                "Operation ID already bound to another request."
                            )

                        if any(
                            recorded[4 + index] > current[index]
                            for index in range(3)
                        ):
                            raise ValueError(
                                "Operation record exceeds current high-water state."
                            )

                        response_floor = recorded[4:]
                        status = "committed"

                    elif current != (
                        old,
                        generation,
                        fence,
                    ):
                        response_floor = current
                        status = "rejected"

                    else:
                        updated = connection.execute(
                            "UPDATE protected_high_water_state "
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
                                "High-water CAS update changed no row."
                            )

                        connection.execute(
                            "INSERT INTO protected_high_water_operations "
                            "(operation_id, expected_revision, "
                            "next_revision, expected_generation, "
                            "expected_fence_token, committed_revision, "
                            "committed_generation, committed_fence_token) "
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

                        # Both state and receipt commit atomically.
                        connection.commit()

                        response_floor = (
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
                response_floor,
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
            # Failure can occur after the transaction COMMIT.
            # Do not automatically repeat the CAS operation.
            raise ValueError(
                "Reference high-water CAS failed or outcome ambiguous."
            ) from exc

    def lookup_operation(
        self,
        *,
        operation_id,
        challenge,
    ):
        try:
            self.__post_init__()

            operation_id = _operation_id(
                operation_id
            )

            challenge = _challenge(
                challenge
            )

            with closing(
                self._connect(readonly=True)
            ) as connection:
                try:
                    connection.execute(
                        "BEGIN"
                    )

                    current = self._snapshot(
                        connection
                    )

                    record = self._operation(
                        connection,
                        operation_id,
                    )

                    if (
                        record is not None
                        and any(
                            record[4 + index] > current[index]
                            for index in range(3)
                        )
                    ):
                        raise ValueError(
                            "Operation record exceeds persisted high-water state."
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
                "Reference high-water operation lookup failed."
            ) from exc
