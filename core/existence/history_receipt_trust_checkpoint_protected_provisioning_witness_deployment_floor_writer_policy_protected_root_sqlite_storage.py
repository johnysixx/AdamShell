"""Internal SQLite storage foundation for protected root state.

Canonical protected root objects remain the runtime representation.
Serialization occurs only at the persistent storage boundary.

State and coordination databases are independently transactional.
Both databases bind the same deployment identity and storage ID.

The storage pair and filesystem are trusted. This reference does
not protect against replacement or rollback of the trusted pair.

An incomplete creation is deliberately not repaired automatically.
"""

import hashlib
import json
import os
import secrets
import sqlite3
import stat

from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root
    as root,
)


durable = root.durable
versioned = root.versioned

_STORAGE_DOMAIN = "a44-sqlite-protected-root-storage-v1"

_TIMEOUT_SECONDS = 30

_MAX_STATE_BYTES = (
    2 * versioned._MAX_POLICY_BYTES + 8192
)

_METADATA_SQL = (
    "CREATE TABLE root_metadata ("
    "singleton INTEGER PRIMARY KEY CHECK(singleton = 1), "
    "metadata BLOB NOT NULL)"
)

_STATE_SQL = (
    "CREATE TABLE root_state ("
    "singleton INTEGER PRIMARY KEY CHECK(singleton = 1), "
    "payload BLOB, "
    "digest TEXT, "
    "CHECK((payload IS NULL AND digest IS NULL) OR "
    "(payload IS NOT NULL AND digest IS NOT NULL)))"
)


# Explicit state schema versions.

_STATE_SCHEMA_V1 = 0
_STATE_SCHEMA_V2 = 2

_SESSION_METADATA_SQL = (
    "CREATE TABLE session_metadata ("
    "singleton INTEGER PRIMARY KEY CHECK(singleton = 1), "
    "enrollment BLOB, "
    "history_digest TEXT NOT NULL)"
)

_CONSUMED_SESSIONS_SQL = (
    "CREATE TABLE consumed_sessions ("
    "session BLOB PRIMARY KEY NOT NULL "
    "CHECK(typeof(session) = 'blob' AND length(session) = 32)) "
    "WITHOUT ROWID"
)

_SESSION_HISTORY_DOMAIN = (
    "AdamShell/A44/protected-root-session-history/v2"
)


def _session_history_digest(connection):

    """Canonical commitment to the complete session set."""

    digest = hashlib.sha256()

    digest.update(
        _SESSION_HISTORY_DOMAIN.encode("ascii")
        + b"\x00"
    )

    count = 0

    for (session,) in connection.execute(
        "SELECT session FROM consumed_sessions "
        "ORDER BY session"
    ):

        if type(session) is not bytes or len(session) != 32:

            raise ValueError(
                "Invalid consumed session record."
            )

        digest.update(session)
        count += 1

    digest.update(
        count.to_bytes(8, "big")
    )

    return digest.hexdigest()


def _state_schema_version(connection):

    row = connection.execute(
        "PRAGMA user_version"
    ).fetchone()

    if row not in (
        (_STATE_SCHEMA_V1,),
        (_STATE_SCHEMA_V2,),
    ):

        raise ValueError(
            "Unsupported protected state schema version."
        )

    return row[0]


def _validate_session_history(connection):

    rows = connection.execute(
        "SELECT singleton, enrollment, history_digest "
        "FROM session_metadata"
    ).fetchall()

    if len(rows) != 1 or rows[0][0] != 1:

        raise ValueError(
            "Invalid session metadata singleton."
        )

    _, enrollment, expected = rows[0]

    if enrollment is not None and (
        type(enrollment) is not bytes
        or not enrollment
        or len(enrollment) > 8192
    ):

        raise ValueError(
            "Invalid stored session enrollment."
        )

    versioned._require_digest(
        expected,
        "stored session history digest",
    )

    if _session_history_digest(connection) != expected:

        raise ValueError(
            "Stored session history digest mismatch."
        )

    if enrollment is None:

        if connection.execute(
            "SELECT 1 FROM consumed_sessions LIMIT 1"
        ).fetchone() is not None:

            raise ValueError(
                "Unbound session registry contains records."
            )


@dataclass(frozen=True, slots=True)
class _Storage:

    path: Path
    fence_path: Path
    identity: root.ProtectedDeploymentIdentity
    storage_id: str


def _json_bytes(value):

    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _identity_fields(identity):

    if type(identity) is not root.ProtectedDeploymentIdentity:
        raise ValueError("Expected canonical deployment identity.")

    return [
        identity.deployment_id,
        identity.configuration_sha256,
        identity.provisioning_nonce.hex(),
    ]


def _encode_state(state):

    if type(state) is not root.ProtectedDurableRootState:
        raise ValueError("Expected canonical protected root state.")

    durable_state = state.durable_state
    prepared = durable_state.prepared

    pending = None

    if prepared is not None:

        message, signature = prepared.signed_policy

        pending = [
            prepared.predecessor.epoch,
            prepared.predecessor.sha256,
            prepared.candidate.epoch,
            prepared.candidate.sha256,
            message.hex(),
            signature.hex(),
        ]

    payload = _json_bytes([
        root._STATE_DOMAIN,
        *_identity_fields(state.identity),
        state.revision,
        durable_state.anchor.epoch,
        durable_state.anchor.sha256,
        pending,
    ])

    if len(payload) > _MAX_STATE_BYTES:
        raise ValueError("Protected state exceeds serialization limit.")

    digest = hashlib.sha256(payload).hexdigest()

    if digest != state.reference().sha256:
        raise ValueError("Canonical root commitment mismatch.")

    return payload, digest


def _decode_state(payload, digest, identity):

    try:

        if (
            type(payload) is not bytes
            or not payload
            or len(payload) > _MAX_STATE_BYTES
        ):
            raise ValueError("Invalid protected state payload.")

        versioned._require_digest(
            digest,
            "stored protected state digest",
        )

        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError("Stored protected state digest mismatch.")

        fields = json.loads(payload.decode("utf-8"))

        if type(fields) is not list or len(fields) != 8:
            raise ValueError("Invalid protected state record.")

        (
            domain,
            deployment_id,
            configuration,
            nonce,
            revision,
            anchor_epoch,
            anchor_digest,
            pending,
        ) = fields

        if domain != root._STATE_DOMAIN:
            raise ValueError("Invalid protected state domain.")

        stored_identity = root.ProtectedDeploymentIdentity(
            deployment_id=deployment_id,
            configuration_sha256=configuration,
            provisioning_nonce=bytes.fromhex(nonce),
        )

        if stored_identity != identity:
            raise ValueError("Stored deployment identity mismatch.")

        anchor = durable.PolicyReference(
            epoch=anchor_epoch,
            sha256=anchor_digest,
        )

        prepared = None

        if pending is not None:

            if type(pending) is not list or len(pending) != 6:
                raise ValueError("Invalid prepared record.")

            (
                predecessor_epoch,
                predecessor_digest,
                candidate_epoch,
                candidate_digest,
                message,
                signature,
            ) = pending

            prepared = durable.PreparedPolicyPublication(
                predecessor=durable.PolicyReference(
                    epoch=predecessor_epoch,
                    sha256=predecessor_digest,
                ),
                candidate=durable.PolicyReference(
                    epoch=candidate_epoch,
                    sha256=candidate_digest,
                ),
                signed_policy=(
                    bytes.fromhex(message),
                    bytes.fromhex(signature),
                ),
            )

        state = root.ProtectedDurableRootState(
            identity=stored_identity,
            revision=revision,
            durable_state=durable.DurablePolicyHighWaterState(
                anchor=anchor,
                prepared=prepared,
            ),
        )

        if _encode_state(state) != (payload, digest):
            raise ValueError("Noncanonical protected state serialization.")

        return state

    except Exception as exc:

        raise ValueError(
            "Protected root state decoding failed."
        ) from exc


def _paths(value):

    if not isinstance(value, (str, Path)) or not str(value):
        raise ValueError("Invalid protected storage path.")

    candidate = Path(value)

    if candidate.is_symlink():
        raise ValueError("Symbolic-link storage paths forbidden.")

    path = candidate.resolve()

    fence_path = path.with_name(
        path.name + ".fence.sqlite3"
    )

    return path, fence_path


def _present(path):

    return path.exists() or path.is_symlink()


def _require_file(path, *, allow_empty=False):

    if path.resolve() != path or path.is_symlink():
        raise ValueError("Protected storage path identity changed.")

    try:
        info = path.stat()
    except OSError as exc:
        raise ValueError("Required protected storage is missing.") from exc

    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Expected regular protected database file.")

    if info.st_nlink != 1:
        raise ValueError("Hard-linked protected storage forbidden.")

    if not allow_empty and info.st_size == 0:
        raise ValueError("Protected database is empty.")


def _check_pair(storage):

    _require_file(storage.path)
    _require_file(storage.fence_path)

    if os.path.samefile(storage.path, storage.fence_path):
        raise ValueError("Protected database alias forbidden.")


def _reserve(path):

    descriptor = os.open(
        path,
        os.O_CREAT | os.O_EXCL | os.O_WRONLY,
        0o600,
    )

    os.close(descriptor)


@contextmanager
def _transaction(path, *, write=False, allow_empty=False):

    _require_file(path, allow_empty=allow_empty)

    uri = path.as_uri() + "?mode=rw"

    with closing(
        sqlite3.connect(
            uri,
            uri=True,
            timeout=_TIMEOUT_SECONDS,
            isolation_level=None,
        )
    ) as connection:

        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA trusted_schema=OFF")

        mode = connection.execute(
            "PRAGMA journal_mode"
        ).fetchone()

        if mode != ("delete",):
            raise ValueError("Unexpected protected SQLite journal mode.")

        connection.execute(
            "BEGIN IMMEDIATE" if write else "BEGIN"
        )

        try:

            yield connection

            connection.execute("COMMIT")

        except BaseException:

            if connection.in_transaction:
                connection.execute("ROLLBACK")

            raise


def _metadata(storage, role):

    if role not in ("state", "fence"):
        raise ValueError("Invalid protected database role.")

    return _json_bytes([
        _STORAGE_DOMAIN,
        role,
        storage.storage_id,
        *_identity_fields(storage.identity),
    ])


def _validate_schema(connection, role):

    expected = {
        ("table", "root_metadata", _METADATA_SQL),
    }

    schema_version = None

    if role == "state":

        expected.add(
            ("table", "root_state", _STATE_SQL)
        )

        schema_version = (
            _state_schema_version(connection)
        )

        if schema_version == _STATE_SCHEMA_V2:

            expected.update({
                (
                    "table",
                    "session_metadata",
                    _SESSION_METADATA_SQL,
                ),
                (
                    "table",
                    "consumed_sessions",
                    _CONSUMED_SESSIONS_SQL,
                ),
            })

    elif role != "fence":

        raise ValueError(
            "Invalid protected schema role."
        )

    actual = connection.execute(
        "SELECT type, name, sql FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%'"
    ).fetchall()

    if len(actual) != len(expected) or set(actual) != expected:

        raise ValueError(
            "Unexpected protected database schema."
        )

    if schema_version == _STATE_SCHEMA_V2:

        _validate_session_history(connection)


def _metadata_record(connection, role):

    _validate_schema(connection, role)

    rows = connection.execute(
        "SELECT singleton, metadata FROM root_metadata"
    ).fetchall()

    if (
        len(rows) != 1
        or rows[0][0] != 1
        or type(rows[0][1]) is not bytes
        or len(rows[0][1]) > 8192
    ):
        raise ValueError("Invalid protected storage metadata.")

    return rows[0][1]


def _validate_metadata(connection, storage, role):

    if _metadata_record(connection, role) != _metadata(storage, role):
        raise ValueError("Protected storage identity or role mismatch.")


def _read_state(connection, storage):

    _validate_metadata(connection, storage, "state")

    rows = connection.execute(
        "SELECT singleton, payload, digest FROM root_state"
    ).fetchall()

    if len(rows) != 1 or rows[0][0] != 1:
        raise ValueError("Expected exactly one protected state record.")

    _, payload, digest = rows[0]

    if payload is None and digest is None:

        # Explicitly unprovisioned storage.

        return None

    if payload is None or digest is None:
        raise ValueError("Incomplete protected state record.")

    return _decode_state(
        payload,
        digest,
        storage.identity,
    )


def _write_state(connection, storage, state):

    """Internal serialization primitive.

    The public backend must validate provisioning or CAS transitions
    under the shared fence before calling this function.
    """

    if not connection.in_transaction:
        raise ValueError("Protected write requires explicit transaction.")

    _validate_metadata(connection, storage, "state")

    if type(state) is not root.ProtectedDurableRootState:
        raise ValueError("Expected canonical protected state.")

    if state.identity != storage.identity:
        raise ValueError("Protected state identity mismatch.")

    payload, digest = _encode_state(state)

    result = connection.execute(
        "UPDATE root_state SET payload = ?, digest = ? "
        "WHERE singleton = 1",
        (payload, digest),
    )

    if result.rowcount != 1:
        raise ValueError("Protected state update failed.")

    if _read_state(connection, storage) != state:
        raise ValueError("Protected state write verification failed.")

    return state.reference()


def _initialize(connection, storage, role):

    connection.execute(_METADATA_SQL)

    connection.execute(
        "INSERT INTO root_metadata VALUES (1, ?)",
        (_metadata(storage, role),),
    )

    if role == "state":

        connection.execute(_STATE_SQL)

        connection.execute(
            "INSERT INTO root_state VALUES (1, NULL, NULL)"
        )

        connection.execute(_SESSION_METADATA_SQL)

        connection.execute(_CONSUMED_SESSIONS_SQL)

        connection.execute(
            "INSERT INTO session_metadata VALUES (1, NULL, ?)",
            (_session_history_digest(connection),),
        )

        connection.execute(
            "PRAGMA user_version = "
            + str(_STATE_SCHEMA_V2)
        )

    _validate_metadata(connection, storage, role)


def _create(path, expected_identity):

    with durable._operation("protected storage creation"):

        _identity_fields(expected_identity)

        path, fence_path = _paths(path)

        if _present(path) or _present(fence_path):
            raise ValueError("Protected storage already or partially exists.")

        storage = _Storage(
            path=path,
            fence_path=fence_path,
            identity=expected_identity,
            storage_id=secrets.token_hex(32),
        )

        # Exclusive filesystem creation. Never truncate an existing
        # database and never delete an incomplete pair automatically.

        _reserve(path)
        _reserve(fence_path)

        with _transaction(
            fence_path,
            write=True,
            allow_empty=True,
        ) as connection:

            _initialize(connection, storage, "fence")

        with _transaction(
            path,
            write=True,
            allow_empty=True,
        ) as connection:

            _initialize(connection, storage, "state")

        opened = _open(path, expected_identity)

        if opened != storage:
            raise ValueError("Created storage identity mismatch.")

        return opened


def _open(path, expected_identity):

    with durable._operation("protected storage opening"):

        _identity_fields(expected_identity)

        path, fence_path = _paths(path)

        _require_file(path)
        _require_file(fence_path)

        if os.path.samefile(path, fence_path):
            raise ValueError("Protected database alias forbidden.")

        with _transaction(path) as connection:

            record = _metadata_record(connection, "state")

            fields = json.loads(record.decode("utf-8"))

            if type(fields) is not list or len(fields) != 6:
                raise ValueError("Invalid protected metadata structure.")

            storage_id = versioned._require_digest(
                fields[2],
                "protected storage ID",
            )

            storage = _Storage(
                path=path,
                fence_path=fence_path,
                identity=expected_identity,
                storage_id=storage_id,
            )

            _validate_metadata(connection, storage, "state")
            _read_state(connection, storage)

        # Opening validates immutable metadata without obtaining a
        # long-lived writer fence or mutating the root state.

        with _transaction(fence_path) as connection:

            _validate_metadata(connection, storage, "fence")

        _check_pair(storage)

        return storage
