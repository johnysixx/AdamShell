"""A44 persistent signed writer policy authority.

The policy store retains the complete authenticated policy lineage
from an externally pinned signed genesis.

Historical retired keys are reconstructed from signed history rather
than trusted as independently mutable auxiliary records.

Policy publication and authorized CAS use the same SQLite BEGIN
IMMEDIATE transaction boundary in a separate policy database.

The policy transaction remains open through the existing floor CAS.
This serializes cooperating instances using the same policy database,
but does not constitute a distributed transaction across databases.

SECURITY LIMITS:
- Trusted external genesis and rollback pins remain necessary.
- Restoring an older valid database may restore an older policy.
- An opened authority pins its observed opening history reference.
- This is not an independently durable monotonic root.
- Legacy gateways and arbitrary backend access are not fenced.
- Independent copies of the policy database are not fenced.
- Database paths, directory access and process code must be trusted.
- No isolated signer custody or authenticated network transport.
- Complete history verification is deliberately performed on every
  policy-sensitive operation. This is a reference implementation.
"""

import hmac
import os
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water
    as high_water,
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
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy
    as versioned,
)


_BUSY_TIMEOUT_SECONDS = 30


@dataclass(frozen=True, slots=True)
class _StorePins:

    path: Path

    backend: object = field(repr=False)

    policy_id: str

    policy_public_key: bytes = field(repr=False)

    genesis_sha256: str


@dataclass(frozen=True, slots=True)
class _LoadedHistory:

    current: versioned._WriterPolicyState

    signed_current: tuple

    retired: frozenset


def _require_distinct_store(path, backend):

    floor_path = Path(
        backend._path,
    ).resolve()

    if path.resolve() == floor_path:

        raise ValueError(
            "Writer policy store cannot alias floor database."
        )

    if path.exists() and floor_path.exists():

        if os.path.samefile(
            path,
            floor_path,
        ):

            raise ValueError(
                "Writer policy store aliases floor database."
            )


def _make_pins(
    *,
    path,
    backend,
    expected_policy_id,
    expected_policy_public_key,
    expected_genesis_sha256,
):

    backend = versioned._require_backend(
        backend,
    )

    if not isinstance(
        path,
        (str, Path),
    ):

        raise ValueError(
            "Invalid writer policy database path."
        )

    if isinstance(path, str) and not path:

        raise ValueError(
            "Empty writer policy database path."
        )

    path = Path(path).resolve()

    _require_distinct_store(
        path,
        backend,
    )

    policy_id = high_water._identity(
        expected_policy_id,
        "persistent writer policy identity",
    )

    root_key = versioned._require_public_key(
        expected_policy_public_key,
        "persistent writer policy root",
    )

    if any(
        hmac.compare_digest(
            root_key,
            reserved,
        )
        for reserved in
        versioned._reserved_backend_keys(backend)
    ):

        raise ValueError(
            "Policy signing root cannot reuse a reserved role."
        )

    genesis_sha256 = versioned._require_digest(
        expected_genesis_sha256,
        "retained writer policy genesis",
    )

    return _StorePins(
        path=path,
        backend=backend,
        policy_id=policy_id,
        policy_public_key=root_key,
        genesis_sha256=genesis_sha256,
    )


def _parse_policy(pins, signed_policy):

    return versioned._parse_signed_policy(
        backend=pins.backend,
        expected_policy_id=pins.policy_id,
        policy_public_key=pins.policy_public_key,
        signed_policy=signed_policy,
    )


def _require_genesis(pins, state):

    if state.epoch != 1:

        raise ValueError(
            "Persistent policy lineage must begin at epoch 1."
        )

    if state.previous_sha256 != "0" * 64:

        raise ValueError(
            "Invalid persistent policy genesis predecessor."
        )

    if not hmac.compare_digest(
        state.sha256,
        pins.genesis_sha256,
    ):

        raise ValueError(
            "Persistent policy genesis digest mismatch."
        )


def _genesis_retired(state):

    return frozenset(
        key
        for writer_id, key in state.writers
        if writer_id in state.revoked
    )


def _validate_transition(
    *,
    current,
    candidate,
    retired,
):
    """Validate a complete transition and derive historical retirement."""

    if candidate.epoch != current.epoch + 1:

        raise ValueError(
            "Persistent policy epoch is not consecutive."
        )

    if not hmac.compare_digest(
        candidate.previous_sha256,
        current.sha256,
    ):

        raise ValueError(
            "Persistent policy predecessor digest mismatch."
        )

    if not current.revoked.issubset(
        candidate.revoked,
    ):

        raise ValueError(
            "Historical revocation tombstone removal forbidden."
        )

    old_keys = dict(
        current.writers,
    )

    new_keys = dict(
        candidate.writers,
    )

    old_owners = {
        key: writer_id
        for writer_id, key in current.writers
    }

    # Existing identities cannot rotate their keys in the same
    # transition in which they are newly revoked. Previously
    # revoked identities must retain their exact tombstone key.

    for writer_id in candidate.revoked:

        if writer_id in old_keys:

            if new_keys.get(
                writer_id,
            ) != old_keys[writer_id]:

                raise ValueError(
                    "Revoked identity must retain its existing key."
                )

    # Reject transfers, including swaps or remove-and-reenroll
    # operations attempted within a single signed transition.

    for writer_id, key in candidate.writers:

        old_owner = old_owners.get(key)

        if (
            old_owner is not None
            and old_owner != writer_id
        ):

            raise ValueError(
                "Writer key transfer between identities forbidden."
            )

        if key in retired:

            original_tombstone = (
                writer_id in current.revoked
                and writer_id in candidate.revoked
                and old_keys.get(writer_id) == key
            )

            if not original_tombstone:

                raise ValueError(
                    "Historical retired writer key cannot be reenrolled."
                )

    next_retired = set(retired)

    # A replaced or removed key is permanently retired.

    for writer_id, key in current.writers:

        if new_keys.get(
            writer_id,
        ) != key:

            next_retired.add(key)

    # Revoked identities retain their keys as inert tombstones.

    for writer_id in candidate.revoked:

        next_retired.add(
            new_keys[writer_id],
        )

    # Check the entire candidate against the resulting retirement
    # state before publishing anything.

    for writer_id, key in candidate.writers:

        if (
            writer_id not in candidate.revoked
            and key in next_retired
        ):

            raise ValueError(
                "Candidate activates a retired writer key."
            )

    return frozenset(
        next_retired,
    )


@contextmanager
def _transaction(
    pins,
    *,
    allow_empty=False,
):
    """Acquire the shared policy-store writer transaction."""

    path = pins.path

    _require_distinct_store(
        path,
        pins.backend,
    )

    if not path.is_file():

        raise ValueError(
            "Persistent writer policy database missing."
        )

    if (
        not allow_empty
        and path.stat().st_size == 0
    ):

        raise ValueError(
            "Persistent writer policy database is empty."
        )

    # mode=rw never initializes a missing database.

    uri = path.as_uri() + "?mode=rw"

    with closing(
        sqlite3.connect(
            uri,
            uri=True,
            timeout=_BUSY_TIMEOUT_SECONDS,
            isolation_level=None,
        )
    ) as connection:

        connection.execute(
            "PRAGMA synchronous = FULL"
        )

        connection.execute(
            "BEGIN IMMEDIATE"
        )

        try:

            yield connection

            connection.commit()

        except BaseException:

            if connection.in_transaction:

                connection.rollback()

            raise


def _load_history(
    connection,
    pins,
    *,
    anchor=None,
):
    """Authenticate the full history and reconstruct retired keys."""

    head_rows = connection.execute(
        "SELECT singleton, policy_epoch, policy_sha256 "
        "FROM writer_policy_head"
    ).fetchall()

    if len(head_rows) != 1:

        raise ValueError(
            "Expected exactly one persistent policy head."
        )

    singleton, head_epoch, head_digest = head_rows[0]

    if type(singleton) is not int or singleton != 1:

        raise ValueError(
            "Invalid persistent policy head identity."
        )

    head_epoch = versioned._require_epoch(
        head_epoch,
        "persistent policy head epoch",
    )

    head_digest = versioned._require_digest(
        head_digest,
        "persistent policy head",
    )

    cursor = connection.execute(
        "SELECT policy_epoch, message, signature "
        "FROM writer_policy_history "
        "ORDER BY policy_epoch"
    )

    current = None
    signed_current = None
    retired = frozenset()

    expected_epoch = 1

    anchor_seen = anchor is None

    for row_epoch, message, signature in cursor:

        if (
            type(row_epoch) is not int
            or row_epoch != expected_epoch
        ):

            raise ValueError(
                "Persistent policy history has a gap."
            )

        signed_policy = (
            message,
            signature,
        )

        candidate = _parse_policy(
            pins,
            signed_policy,
        )

        if candidate.epoch != row_epoch:

            raise ValueError(
                "Policy history row and signed epoch mismatch."
            )

        if current is None:

            _require_genesis(
                pins,
                candidate,
            )

            retired = _genesis_retired(
                candidate,
            )

        else:

            retired = _validate_transition(
                current=current,
                candidate=candidate,
                retired=retired,
            )

        if (
            anchor is not None
            and candidate.epoch == anchor[0]
        ):

            if not hmac.compare_digest(
                candidate.sha256,
                anchor[1],
            ):

                raise ValueError(
                    "Opening policy history anchor mismatch."
                )

            anchor_seen = True

        current = candidate

        signed_current = signed_policy

        expected_epoch += 1

    if current is None:

        raise ValueError(
            "Persistent writer policy history is empty."
        )

    if not anchor_seen:

        raise ValueError(
            "Previously retained opening policy is missing."
        )

    if (
        current.epoch != head_epoch
        or not hmac.compare_digest(
            current.sha256,
            head_digest,
        )
    ):

        raise ValueError(
            "Persistent policy history and head diverged."
        )

    return _LoadedHistory(
        current=current,
        signed_current=signed_current,
        retired=retired,
    )


def _create_schema(connection):

    connection.execute(
        """
        CREATE TABLE writer_policy_history (
            policy_epoch INTEGER PRIMARY KEY
                CHECK (policy_epoch >= 1),
            message BLOB NOT NULL
                CHECK (typeof(message) = 'blob'),
            signature BLOB NOT NULL
                CHECK (
                    typeof(signature) = 'blob'
                    AND length(signature) = 64
                )
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE writer_policy_head (
            singleton INTEGER PRIMARY KEY
                CHECK (singleton = 1),
            policy_epoch INTEGER NOT NULL
                CHECK (policy_epoch >= 1),
            policy_sha256 TEXT NOT NULL
                CHECK (length(policy_sha256) = 64)
        )
        """
    )


def _insert_history(
    connection,
    state,
    signed_policy,
):

    message, signature = signed_policy

    result = connection.execute(
        "INSERT INTO writer_policy_history "
        "(policy_epoch, message, signature) "
        "VALUES (?, ?, ?)",
        (
            state.epoch,
            message,
            signature,
        ),
    )

    if result.rowcount != 1:

        raise ValueError(
            "Persistent policy history insertion failed."
        )


@dataclass(
    frozen=True,
    slots=True,
    init=False,
    eq=False,
)
class SQLitePersistentWriterPolicyAuthority:
    """Persistent shared signed writer policy reference authority."""

    _pins: _StorePins = field(repr=False)

    _opening_anchor: tuple

    def __init__(
        self,
        *,
        path,
        backend,
        expected_policy_id,
        expected_policy_public_key,
        expected_genesis_sha256,
        minimum_policy_epoch=1,
        expected_current_policy_sha256=None,
    ):

        try:

            pins = _make_pins(
                path=path,
                backend=backend,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                expected_genesis_sha256=expected_genesis_sha256,
            )

            minimum = versioned._require_epoch(
                minimum_policy_epoch,
                "retained persistent policy epoch",
            )

            if expected_current_policy_sha256 is not None:

                expected_current_policy_sha256 = (
                    versioned._require_digest(
                        expected_current_policy_sha256,
                        "retained current writer policy",
                    )
                )

            with _transaction(
                pins,
            ) as connection:

                history = _load_history(
                    connection,
                    pins,
                )

                current = history.current

                if current.epoch < minimum:

                    raise ValueError(
                        "Persistent policy rollback below retained epoch."
                    )

                if expected_current_policy_sha256 is not None:

                    if not hmac.compare_digest(
                        current.sha256,
                        expected_current_policy_sha256,
                    ):

                        raise ValueError(
                            "Retained current policy digest mismatch."
                        )

                anchor = (
                    current.epoch,
                    current.sha256,
                )

            object.__setattr__(
                self,
                "_pins",
                pins,
            )

            object.__setattr__(
                self,
                "_opening_anchor",
                anchor,
            )

        except Exception as exc:

            raise ValueError(
                "Persistent writer policy open failed."
            ) from exc

    @classmethod
    def create(
        cls,
        *,
        path,
        backend,
        expected_policy_id,
        expected_policy_public_key,
        signed_genesis_policy,
        expected_genesis_sha256,
    ):
        """Explicitly create a new policy store without overwrite."""

        try:

            pins = _make_pins(
                path=path,
                backend=backend,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                expected_genesis_sha256=expected_genesis_sha256,
            )

            # Authenticate the genesis before creating any file.

            genesis = _parse_policy(
                pins,
                signed_genesis_policy,
            )

            _require_genesis(
                pins,
                genesis,
            )

            # Exclusive creation prevents overwriting a policy store.

            descriptor = os.open(
                str(pins.path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )

            os.close(descriptor)

            try:

                with _transaction(
                    pins,
                    allow_empty=True,
                ) as connection:

                    _create_schema(
                        connection,
                    )

                    _insert_history(
                        connection,
                        genesis,
                        signed_genesis_policy,
                    )

                    connection.execute(
                        "INSERT INTO writer_policy_head "
                        "(singleton, policy_epoch, policy_sha256) "
                        "VALUES (1, ?, ?)",
                        (
                            genesis.epoch,
                            genesis.sha256,
                        ),
                    )

                    loaded = _load_history(
                        connection,
                        pins,
                    )

                    if (
                        loaded.current != genesis
                        or loaded.signed_current
                        != signed_genesis_policy
                    ):

                        raise ValueError(
                            "Persistent genesis verification failed."
                        )

            except Exception:

                # Only remove the newly and exclusively created
                # file when its initialization has failed.
                # All SQLite connections have already been closed.

                pins.path.unlink(
                    missing_ok=True,
                )

                raise

            # Initialization has committed. A later OPEN failure
            # must not delete the committed policy database.

            return cls.open(
                path=pins.path,
                backend=backend,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                expected_genesis_sha256=expected_genesis_sha256,
            )

        except Exception as exc:

            raise ValueError(
                "Persistent writer policy create failed."
            ) from exc

    @classmethod
    def open(
        cls,
        *,
        path,
        backend,
        expected_policy_id,
        expected_policy_public_key,
        expected_genesis_sha256,
        minimum_policy_epoch=1,
        expected_current_policy_sha256=None,
    ):
        """Open an existing authenticated policy history."""

        return cls(
            path=path,
            backend=backend,
            expected_policy_id=expected_policy_id,
            expected_policy_public_key=expected_policy_public_key,
            expected_genesis_sha256=expected_genesis_sha256,
            minimum_policy_epoch=minimum_policy_epoch,
            expected_current_policy_sha256=expected_current_policy_sha256,
        )

    def _load(self, connection):

        return _load_history(
            connection,
            self._pins,
            anchor=self._opening_anchor,
        )

    def current_policy_reference(self):

        try:

            with _transaction(
                self._pins,
            ) as connection:

                current = self._load(
                    connection,
                ).current

                return (
                    current.epoch,
                    current.sha256,
                )

        except Exception as exc:

            raise ValueError(
                "Persistent policy reference read failed."
            ) from exc

    def retired_writer_keys(self):
        """Return detached immutable authenticated retirement state."""

        try:

            with _transaction(
                self._pins,
            ) as connection:

                history = self._load(
                    connection,
                )

                return tuple(
                    sorted(
                        history.retired,
                    )
                )

        except Exception as exc:

            raise ValueError(
                "Persistent retired writer key read failed."
            ) from exc

    def publish_policy(
        self,
        *,
        signed_policy,
    ):
        """Atomically append a signed policy and advance the head."""

        try:

            candidate = _parse_policy(
                self._pins,
                signed_policy,
            )

            with _transaction(
                self._pins,
            ) as connection:

                history = self._load(
                    connection,
                )

                current = history.current

                next_retired = _validate_transition(
                    current=current,
                    candidate=candidate,
                    retired=history.retired,
                )

                _insert_history(
                    connection,
                    candidate,
                    signed_policy,
                )

                result = connection.execute(
                    "UPDATE writer_policy_head "
                    "SET policy_epoch = ?, policy_sha256 = ? "
                    "WHERE singleton = 1 "
                    "AND policy_epoch = ? "
                    "AND policy_sha256 = ?",
                    (
                        candidate.epoch,
                        candidate.sha256,
                        current.epoch,
                        current.sha256,
                    ),
                )

                if result.rowcount != 1:

                    raise ValueError(
                        "Persistent policy head update failed."
                    )

                # Verify the complete resulting state before COMMIT.
                # Any exception rolls back both INSERT and UPDATE.

                verified = self._load(
                    connection,
                )

                if (
                    verified.current != candidate
                    or verified.signed_current != signed_policy
                    or verified.retired != next_retired
                ):

                    raise ValueError(
                        "Persistent policy publication verification failed."
                    )

                reference = (
                    candidate.epoch,
                    candidate.sha256,
                )

            return reference

        except Exception as exc:

            raise ValueError(
                "Persistent writer policy publication failed."
            ) from exc

    def _public_read_or_lookup(
        self,
        document,
    ):
        """Preserve public signed recovery independently of writer access."""

        operation = document.get(
            "operation",
        )

        if operation == "read":

            fields = remote._BASE

        elif operation == "lookup":

            fields = remote._LOOKUP

        else:

            raise ValueError(
                "Unsupported public floor operation."
            )

        if set(document) != fields:

            raise ValueError(
                "Invalid public floor wire schema."
            )

        backend = self._pins.backend

        challenge = writer_authority._validate_identity(
            document,
            backend,
        )

        if operation == "read":

            with backend.hold(
                challenge=challenge,
            ) as response:

                return writer_authority._signed_envelope(
                    response,
                )

        operation_id = high_water._operation_id(
            document["operation_id"],
        )

        response = backend.lookup_operation(
            operation_id=operation_id,
            challenge=challenge,
        )

        return writer_authority._signed_envelope(
            response,
        )

    def exchange(
        self,
        request,
    ):
        """Authorize CAS using the current persisted policy."""

        try:

            document = remote._parse(
                request,
                maximum=versioned._MAX_WIRE_BYTES,
            )

            operation = document.get(
                "operation",
            )

            # READ and LOOKUP do not require writer authorization.
            # They do not mutate the writer policy or floor state.

            if operation in (
                "read",
                "lookup",
            ):

                return self._public_read_or_lookup(
                    document,
                )

            if set(document) != versioned._CAS_FIELDS:

                raise ValueError(
                    "Expected versioned writer CAS envelope."
                )

            # Critical transaction boundary:
            #
            # The policy database writer lock is acquired before
            # reading or authenticating the current policy.
            #
            # Every cooperating policy publication must acquire
            # this same lock before modifying persistent history.
            #
            # The lock remains held throughout the existing floor
            # backend CAS and until the signed result is prepared.

            with _transaction(
                self._pins,
            ) as connection:

                history = self._load(
                    connection,
                )

                current = history.current

                # Reuse the existing fully validated v2 wire
                # implementation. The temporary authority is
                # never retained by this persistent gateway.

                verifier = (
                    versioned.VersionedWriterPolicyAuthority
                    .from_signed_policy(
                        backend=self._pins.backend,
                        expected_policy_id=self._pins.policy_id,
                        expected_policy_public_key=(
                            self._pins.policy_public_key
                        ),
                        signed_policy=history.signed_current,
                        minimum_policy_epoch=current.epoch,
                        expected_policy_sha256=current.sha256,
                    )
                )

                response = verifier.exchange(
                    request,
                )

            return response

        except Exception as exc:

            # A floor commit may have succeeded even if returning
            # its acknowledgement failed. Recover using signed
            # LOOKUP with the original operation identifier.
            #
            # This is not cross-database atomic commit.

            raise ValueError(
                "Persistent writer policy exchange failed."
            ) from exc


@dataclass(
    frozen=True,
    slots=True,
    eq=False,
)
class PersistentWriterPolicyGateway:
    """Gateway consulting one persistent authority on every CAS."""

    _authority: SQLitePersistentWriterPolicyAuthority = field(
        repr=False,
    )

    def __post_init__(self):

        if type(self._authority) is not (
            SQLitePersistentWriterPolicyAuthority
        ):

            raise ValueError(
                "Expected canonical persistent writer policy authority."
            )

    @classmethod
    def from_authority(
        cls,
        *,
        authority,
    ):

        return cls(
            _authority=authority,
        )

    def exchange(
        self,
        request,
    ):

        return self._authority.exchange(
            request,
        )
