"""A44 durable writer policy high-water reference authority.

A stable anchor is a historical authenticated policy reference.

A prepared publication is an independently committed record of the
exact signed candidate and its predecessor. It is retained until
that candidate is committed or authenticated in persisted history.

There is no automatic cancellation of prepared publications.

LOCK ORDER

    coordination fence database
        -> persistent policy database
            -> short durable-state transactions
            -> existing floor backend transaction

The coordination fence is a separate SQLite database. Its writer
transaction remains held across independently committed durable
state changes, policy commits, and authorized floor CAS.

Durable-state inspection does not acquire the coordination fence.
It can therefore inspect committed PREPARED state while another
authority holds the policy transaction.

TRUST BOUNDARY

The durable store and its paired coordination database must remain
independently trusted and protected from rollback, replacement,
unauthorized modification and filesystem aliasing.

This local reference implementation cannot prevent simultaneous
rollback of all trusted stores.

Legacy gateways and direct backend access are outside this fence.
"""


import hashlib
import json
import os
import secrets
import sqlite3

from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_sqlite_reference
    as persistent,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy
    as versioned,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_remote_client
    as remote,
)


_BUSY_TIMEOUT_SECONDS = 30.0

_STORE_DOMAIN = "a44-durable-writer-policy-reference-v1"


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class PolicyReference:

    epoch: int

    sha256: str

    def __post_init__(self):

        versioned._require_epoch(
            self.epoch,
            "durable policy epoch",
        )

        versioned._require_digest(
            self.sha256,
            "durable policy reference",
        )

    def pair(self):

        return (
            self.epoch,
            self.sha256,
        )


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class PreparedPolicyPublication:

    predecessor: PolicyReference

    candidate: PolicyReference

    signed_policy: tuple[bytes, bytes] = field(
        repr=False,
    )

    def __post_init__(self):

        if (
            type(self.predecessor) is not PolicyReference
            or type(self.candidate) is not PolicyReference
        ):

            raise ValueError(
                "Expected canonical prepared policy references."
            )

        if (
            self.candidate.epoch
            != self.predecessor.epoch + 1
        ):

            raise ValueError(
                "Prepared policy epoch must be consecutive."
            )

        if (
            type(self.signed_policy) is not tuple
            or len(self.signed_policy) != 2
        ):

            raise ValueError(
                "Expected immutable signed policy pair."
            )

        message, signature = self.signed_policy

        if (
            type(message) is not bytes
            or not message
            or len(message) > versioned._MAX_POLICY_BYTES
            or type(signature) is not bytes
            or len(signature) != 64
        ):

            raise ValueError(
                "Invalid prepared signed policy material."
            )

        if (
            hashlib.sha256(message).hexdigest()
            != self.candidate.sha256
        ):

            raise ValueError(
                "Prepared candidate digest mismatch."
            )


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class DurablePolicyHighWaterState:

    anchor: PolicyReference

    prepared: PreparedPolicyPublication | None = None

    def __post_init__(self):

        if type(self.anchor) is not PolicyReference:

            raise ValueError(
                "Expected canonical durable policy anchor."
            )

        if self.prepared is not None:

            if (
                type(self.prepared)
                is not PreparedPolicyPublication
            ):

                raise ValueError(
                    "Expected canonical prepared publication."
                )

            if self.prepared.predecessor != self.anchor:

                raise ValueError(
                    "Prepared predecessor differs from durable anchor."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class _Configuration:

    policy_pins: object = field(repr=False)

    state_path: Path

    fence_path: Path

    identity: str


def _reference(state):

    return PolicyReference(
        epoch=state.epoch,
        sha256=state.sha256,
    )


def _stable(reference):

    return DurablePolicyHighWaterState(
        anchor=reference,
    )


@contextmanager
def _operation(label):

    try:

        yield

    except Exception as exc:

        raise ValueError(
            "Durable writer policy " + label + " failed."
        ) from exc


def _canonical_path(value):

    if not isinstance(value, (str, Path)):

        raise ValueError(
            "Invalid durable database path."
        )

    if isinstance(value, str) and not value:

        raise ValueError(
            "Empty durable database path."
        )

    return Path(value).resolve()


def _check_paths(config):

    paths = (
        config.policy_pins.path,
        Path(
            config.policy_pins.backend._path
        ).resolve(),
        config.state_path,
        config.fence_path,
    )

    if len(set(paths)) != len(paths):

        raise ValueError(
            "Policy, floor, durable and fence databases "
            "must use distinct paths."
        )

    for index, path in enumerate(paths):

        if path.resolve() != path:

            raise ValueError(
                "Database path identity changed."
            )

        if path.exists():

            if not path.is_file():

                raise ValueError(
                    "Expected regular database file."
                )

            if path.stat().st_nlink != 1:

                raise ValueError(
                    "Hard-linked database aliases are forbidden."
                )

            for other in paths[index + 1:]:

                if (
                    other.exists()
                    and os.path.samefile(path, other)
                ):

                    raise ValueError(
                        "Database filesystem alias forbidden."
                    )


def _make_configuration(
    *,
    path,
    high_water_path,
    backend,
    expected_store_id,
    expected_policy_id,
    expected_policy_public_key,
    expected_genesis_sha256,
):

    pins = persistent._make_pins(
        path=path,
        backend=backend,
        expected_policy_id=expected_policy_id,
        expected_policy_public_key=expected_policy_public_key,
        expected_genesis_sha256=expected_genesis_sha256,
    )

    store_id = persistent.high_water._identity(
        expected_store_id,
        "durable high-water store identity",
    )

    state_path = _canonical_path(
        high_water_path
    )

    fence_path = state_path.with_name(
        state_path.name + ".fence.sqlite3"
    )

    reserved_keys = (
        versioned._reserved_backend_keys(
            backend
        )
    )

    # The policy database path is deliberately not part of
    # this identity. Cooperating copies may share one fence.

    material = (
        _STORE_DOMAIN,
        store_id,
        pins.policy_id,
        pins.policy_public_key.hex(),
        pins.genesis_sha256,
        backend.floor_id,
        backend.subject_id,
        backend.authority_id,
        backend.witness_id,
        *(key.hex() for key in reserved_keys),
    )

    encoded = json.dumps(
        material,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")

    config = _Configuration(
        policy_pins=pins,
        state_path=state_path,
        fence_path=fence_path,
        identity=hashlib.sha256(
            encoded
        ).hexdigest(),
    )

    _check_paths(config)

    return config


@contextmanager
def _database(
    path,
    *,
    write=False,
    allow_empty=False,
):

    if not path.is_file():

        raise ValueError(
            "Required durable database is missing."
        )

    if (
        not allow_empty
        and path.stat().st_size == 0
    ):

        raise ValueError(
            "Required durable database is empty."
        )

    mode = "rw" if write else "ro"

    uri = path.as_uri() + "?mode=" + mode

    with closing(
        sqlite3.connect(
            uri,
            uri=True,
            timeout=_BUSY_TIMEOUT_SECONDS,
            isolation_level=None,
        )
    ) as connection:

        if write:

            connection.execute(
                "PRAGMA synchronous = FULL"
            )

            connection.execute(
                "BEGIN IMMEDIATE"
            )

        else:

            connection.execute(
                "PRAGMA query_only = ON"
            )

            connection.execute(
                "BEGIN"
            )

        try:

            yield connection

            connection.commit()

        except BaseException:

            if connection.in_transaction:

                connection.rollback()

            raise


def _create_exclusive_file(path):

    # Never truncate or replace an existing trusted store.

    with path.open("xb"):
        pass


def _create_metadata(
    connection,
    config,
    nonce,
):

    connection.execute(
        """
        CREATE TABLE durable_policy_metadata (
            singleton INTEGER PRIMARY KEY
                CHECK (singleton = 1),
            identity TEXT NOT NULL,
            nonce BLOB NOT NULL
                CHECK (
                    typeof(nonce) = 'blob'
                    AND length(nonce) = 32
                )
        )
        """
    )

    connection.execute(
        """
        INSERT INTO durable_policy_metadata
        (singleton, identity, nonce)
        VALUES (1, ?, ?)
        """,
        (
            config.identity,
            nonce,
        ),
    )


def _read_metadata(
    connection,
    config,
    *,
    nonce=None,
):

    rows = connection.execute(
        """
        SELECT singleton, identity, nonce
        FROM durable_policy_metadata
        """
    ).fetchall()

    if len(rows) != 1:

        raise ValueError(
            "Expected one durable store identity record."
        )

    singleton, identity, retained_nonce = rows[0]

    if (
        type(singleton) is not int
        or singleton != 1
        or type(identity) is not str
        or identity != config.identity
        or type(retained_nonce) is not bytes
        or len(retained_nonce) != 32
    ):

        raise ValueError(
            "Durable store identity mismatch."
        )

    if (
        nonce is not None
        and retained_nonce != nonce
    ):

        raise ValueError(
            "Durable store and coordination fence pairing mismatch."
        )

    return retained_nonce


def _create_state_schema(connection):

    connection.execute(
        """
        CREATE TABLE durable_policy_state (
            singleton INTEGER PRIMARY KEY
                CHECK (singleton = 1),
            anchor_epoch INTEGER NOT NULL
                CHECK (anchor_epoch >= 1),
            anchor_sha256 TEXT NOT NULL
                CHECK (length(anchor_sha256) = 64),
            prepared_epoch INTEGER,
            prepared_sha256 TEXT,
            prepared_message BLOB,
            prepared_signature BLOB,
            CHECK (
                (
                    prepared_epoch IS NULL
                    AND prepared_sha256 IS NULL
                    AND prepared_message IS NULL
                    AND prepared_signature IS NULL
                )
                OR
                (
                    prepared_epoch IS NOT NULL
                    AND prepared_epoch = anchor_epoch + 1
                    AND prepared_sha256 IS NOT NULL
                    AND length(prepared_sha256) = 64
                    AND prepared_message IS NOT NULL
                    AND typeof(prepared_message) = 'blob'
                    AND prepared_signature IS NOT NULL
                    AND typeof(prepared_signature) = 'blob'
                    AND length(prepared_signature) = 64
                )
            )
        )
        """
    )


def _state_values(state):

    if type(state) is not DurablePolicyHighWaterState:

        raise ValueError(
            "Expected canonical durable policy state."
        )

    anchor = state.anchor

    prepared = state.prepared

    if prepared is None:

        return (
            anchor.epoch,
            anchor.sha256,
            None,
            None,
            None,
            None,
        )

    message, signature = prepared.signed_policy

    return (
        anchor.epoch,
        anchor.sha256,
        prepared.candidate.epoch,
        prepared.candidate.sha256,
        message,
        signature,
    )


def _insert_initial_state(connection, state):

    connection.execute(
        """
        INSERT INTO durable_policy_state (
            singleton,
            anchor_epoch,
            anchor_sha256,
            prepared_epoch,
            prepared_sha256,
            prepared_message,
            prepared_signature
        )
        VALUES (1, ?, ?, ?, ?, ?, ?)
        """,
        _state_values(state),
    )


def _validate_prepared_signature(
    config,
    prepared,
):

    parsed = persistent._parse_policy(
        config.policy_pins,
        prepared.signed_policy,
    )

    if (
        _reference(parsed) != prepared.candidate
        or parsed.previous_sha256
            != prepared.predecessor.sha256
    ):

        raise ValueError(
            "Prepared signed policy and references diverged."
        )

    return parsed


def _read_state_record(
    connection,
    config,
):

    rows = connection.execute(
        """
        SELECT
            singleton,
            anchor_epoch,
            anchor_sha256,
            prepared_epoch,
            prepared_sha256,
            prepared_message,
            prepared_signature
        FROM durable_policy_state
        """
    ).fetchall()

    if len(rows) != 1:

        raise ValueError(
            "Expected exactly one durable policy state."
        )

    (
        singleton,
        anchor_epoch,
        anchor_digest,
        pending_epoch,
        pending_digest,
        pending_message,
        pending_signature,
    ) = rows[0]

    if (
        type(singleton) is not int
        or singleton != 1
    ):

        raise ValueError(
            "Invalid durable state identity."
        )

    anchor = PolicyReference(
        epoch=anchor_epoch,
        sha256=anchor_digest,
    )

    if (
        anchor.epoch == 1
        and anchor.sha256
            != config.policy_pins.genesis_sha256
    ):

        raise ValueError(
            "Durable genesis anchor mismatch."
        )

    pending_fields = (
        pending_epoch,
        pending_digest,
        pending_message,
        pending_signature,
    )

    if all(
        value is None
        for value in pending_fields
    ):

        return _stable(anchor)

    if any(
        value is None
        for value in pending_fields
    ):

        raise ValueError(
            "Incomplete durable prepared publication."
        )

    prepared = PreparedPolicyPublication(
        predecessor=anchor,
        candidate=PolicyReference(
            epoch=pending_epoch,
            sha256=pending_digest,
        ),
        signed_policy=(
            pending_message,
            pending_signature,
        ),
    )

    _validate_prepared_signature(
        config,
        prepared,
    )

    return DurablePolicyHighWaterState(
        anchor=anchor,
        prepared=prepared,
    )


def _validate_state_transition(
    previous,
    replacement,
):

    old = previous.anchor

    new = replacement.anchor

    if new.epoch < old.epoch:

        raise ValueError(
            "Durable anchor cannot decrease."
        )

    if (
        new.epoch == old.epoch
        and new.sha256 != old.sha256
    ):

        raise ValueError(
            "Durable anchor cannot switch branches."
        )

    if previous.prepared is None:

        if replacement.prepared is not None:

            if replacement.anchor != previous.anchor:

                raise ValueError(
                    "Preparation cannot change the anchor."
                )

        return

    # There is intentionally no pending-to-pending replacement
    # and no pending-to-predecessor cancellation transition.

    if replacement.prepared is not None:

        raise ValueError(
            "Prepared publication replacement forbidden."
        )

    candidate = previous.prepared.candidate

    if new.epoch < candidate.epoch:

        raise ValueError(
            "Prepared publication cannot be aborted."
        )

    if (
        new.epoch == candidate.epoch
        and new != candidate
    ):

        raise ValueError(
            "Finalization changed the prepared candidate."
        )


def _append_policy(
    connection,
    pins,
    history,
    candidate,
    signed_policy,
):

    next_retired = persistent._validate_transition(
        current=history.current,
        candidate=candidate,
        retired=history.retired,
    )

    persistent._insert_history(
        connection,
        candidate,
        signed_policy,
    )

    result = connection.execute(
        """
        UPDATE writer_policy_head
        SET policy_epoch = ?, policy_sha256 = ?
        WHERE singleton = 1
        AND policy_epoch = ?
        AND policy_sha256 = ?
        """,
        (
            candidate.epoch,
            candidate.sha256,
            history.current.epoch,
            history.current.sha256,
        ),
    )

    if result.rowcount != 1:

        raise ValueError(
            "Persistent policy head update failed."
        )

    verified = persistent._load_history(
        connection,
        pins,
        anchor=(
            candidate.epoch,
            candidate.sha256,
        ),
    )

    if (
        verified.current != candidate
        or verified.signed_current != signed_policy
        or verified.retired != next_retired
    ):

        raise ValueError(
            "Prepared policy publication verification failed."
        )

    return verified


@dataclass(
    frozen=True,
    slots=True,
    init=False,
    eq=False,
)
class DurableWriterPolicyAuthority:

    _configuration: _Configuration = field(
        repr=False,
    )

    _nonce: bytes = field(
        repr=False,
    )

    def __init__(self):

        raise ValueError(
            "Use explicit durable bootstrap or open."
        )

    @property
    def _pins(self):

        return self._configuration.policy_pins

    @classmethod
    def _construct(
        cls,
        config,
        nonce,
    ):

        if cls is not DurableWriterPolicyAuthority:

            raise ValueError(
                "Expected canonical durable authority type."
            )

        instance = object.__new__(
            cls
        )

        object.__setattr__(
            instance,
            "_configuration",
            config,
        )

        object.__setattr__(
            instance,
            "_nonce",
            nonce,
        )

        return instance

    @classmethod
    def bootstrap(
        cls,
        *,
        path,
        high_water_path,
        backend,
        expected_store_id,
        expected_policy_id,
        expected_policy_public_key,
        expected_genesis_sha256,
        initial_policy_reference,
    ):

        with _operation("bootstrap"):

            if (
                type(initial_policy_reference)
                is not PolicyReference
            ):

                raise ValueError(
                    "Expected explicit trusted policy reference."
                )

            config = _make_configuration(
                path=path,
                high_water_path=high_water_path,
                backend=backend,
                expected_store_id=expected_store_id,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                expected_genesis_sha256=expected_genesis_sha256,
            )

            if (
                config.state_path.exists()
                or config.fence_path.exists()
            ):

                raise ValueError(
                    "Durable provisioning targets already exist."
                )

            pins = config.policy_pins

            nonce = secrets.token_bytes(32)

            with persistent._transaction(
                pins
            ) as connection:

                history = persistent._load_history(
                    connection,
                    pins,
                )

                current = _reference(
                    history.current
                )

                if current != initial_policy_reference:

                    raise ValueError(
                        "Trusted provisioning reference is not "
                        "the exact authenticated policy head."
                    )

                # Validate before creating either provisioning
                # target. Existing targets are never overwritten.

                _check_paths(config)

                _create_exclusive_file(
                    config.fence_path
                )

                with _database(
                    config.fence_path,
                    write=True,
                    allow_empty=True,
                ) as fence:

                    _create_metadata(
                        fence,
                        config,
                        nonce,
                    )

                _create_exclusive_file(
                    config.state_path
                )

                with _database(
                    config.state_path,
                    write=True,
                    allow_empty=True,
                ) as durable:

                    _create_metadata(
                        durable,
                        config,
                        nonce,
                    )

                    _create_state_schema(
                        durable
                    )

                    initial_state = _stable(
                        current
                    )

                    _insert_initial_state(
                        durable,
                        initial_state,
                    )

                    if (
                        _read_state_record(
                            durable,
                            config,
                        ) != initial_state
                    ):

                        raise ValueError(
                            "Durable bootstrap verification failed."
                        )

            # Incomplete provisioning is not automatically
            # deleted or recreated after an ambiguous error.

            return cls._construct(
                config,
                nonce,
            )

    @classmethod
    def open(
        cls,
        *,
        path,
        high_water_path,
        backend,
        expected_store_id,
        expected_policy_id,
        expected_policy_public_key,
        expected_genesis_sha256,
    ):

        with _operation("open"):

            config = _make_configuration(
                path=path,
                high_water_path=high_water_path,
                backend=backend,
                expected_store_id=expected_store_id,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                expected_genesis_sha256=expected_genesis_sha256,
            )

            with _database(
                config.fence_path
            ) as fence:

                nonce = _read_metadata(
                    fence,
                    config,
                )

            instance = cls._construct(
                config,
                nonce,
            )

            with instance._fence():

                state = instance._read_state()

                if state.prepared is not None:

                    # Pending state is available for explicit
                    # recovery. Opening never clears or silently
                    # completes a prepared publication.

                    return instance

                with persistent._transaction(
                    instance._pins
                ) as connection:

                    instance._load_and_observe(
                        connection,
                        state,
                    )

            return instance

    @contextmanager
    def _fence(self):

        config = self._configuration

        _check_paths(config)

        # Holding BEGIN IMMEDIATE in this database does not
        # prevent independent durable-state commits.

        with _database(
            config.fence_path,
            write=True,
        ) as connection:

            _read_metadata(
                connection,
                config,
                nonce=self._nonce,
            )

            yield

    def _read_state(self):

        config = self._configuration

        _check_paths(config)

        with _database(
            config.state_path
        ) as connection:

            _read_metadata(
                connection,
                config,
                nonce=self._nonce,
            )

            return _read_state_record(
                connection,
                config,
            )

    def durable_state(self):

        with _operation("state inspection"):

            # Deliberately does not acquire _fence or open
            # the policy database.

            return self._read_state()

    def _replace_state(
        self,
        expected,
        replacement,
    ):

        # The caller holds the shared coordination fence.

        _validate_state_transition(
            expected,
            replacement,
        )

        config = self._configuration

        _check_paths(config)

        with _database(
            config.state_path,
            write=True,
        ) as connection:

            _read_metadata(
                connection,
                config,
                nonce=self._nonce,
            )

            current = _read_state_record(
                connection,
                config,
            )

            if current != expected:

                raise ValueError(
                    "Unexpected durable policy state transition."
                )

            result = connection.execute(
                """
                UPDATE durable_policy_state
                SET
                    anchor_epoch = ?,
                    anchor_sha256 = ?,
                    prepared_epoch = ?,
                    prepared_sha256 = ?,
                    prepared_message = ?,
                    prepared_signature = ?
                WHERE singleton = 1
                """,
                _state_values(
                    replacement
                ),
            )

            if result.rowcount != 1:

                raise ValueError(
                    "Durable policy state update failed."
                )

            verified = _read_state_record(
                connection,
                config,
            )

            if verified != replacement:

                raise ValueError(
                    "Durable policy state verification failed."
                )

        # The durable database commit has completed before
        # this method returns.

        return replacement

    def _load_and_observe(
        self,
        connection,
        state,
    ):

        if state.prepared is not None:

            raise ValueError(
                "Prepared publication requires explicit recovery."
            )

        history = persistent._load_history(
            connection,
            self._pins,
            anchor=state.anchor.pair(),
        )

        current = _reference(
            history.current
        )

        if current != state.anchor:

            state = self._replace_state(
                state,
                _stable(current),
            )

        return history, state

    def current_policy_reference(self):

        with _operation("reference read"):

            with self._fence():

                state = self._read_state()

                if state.prepared is not None:

                    raise ValueError(
                        "Publication recovery required."
                    )

                with persistent._transaction(
                    self._pins
                ) as connection:

                    history, observed = (
                        self._load_and_observe(
                            connection,
                            state,
                        )
                    )

                    return observed.anchor.pair()

    def retired_writer_keys(self):

        with _operation("retirement read"):

            with self._fence():

                state = self._read_state()

                if state.prepared is not None:

                    raise ValueError(
                        "Publication recovery required."
                    )

                with persistent._transaction(
                    self._pins
                ) as connection:

                    history, _ = self._load_and_observe(
                        connection,
                        state,
                    )

                    return tuple(
                        sorted(
                            history.retired
                        )
                    )

    def publish_policy(
        self,
        *,
        signed_policy,
    ):

        with _operation("publication"):

            with self._fence():

                state = self._read_state()

                if state.prepared is not None:

                    raise ValueError(
                        "Existing prepared publication must "
                        "be recovered explicitly."
                    )

                pins = self._pins

                with persistent._transaction(
                    pins
                ) as connection:

                    history, state = (
                        self._load_and_observe(
                            connection,
                            state,
                        )
                    )

                    candidate = persistent._parse_policy(
                        pins,
                        signed_policy,
                    )

                    # No preparation before all signature
                    # and historical transition checks pass.

                    persistent._validate_transition(
                        current=history.current,
                        candidate=candidate,
                        retired=history.retired,
                    )

                    prepared = PreparedPolicyPublication(
                        predecessor=state.anchor,
                        candidate=_reference(candidate),
                        signed_policy=signed_policy,
                    )

                    pending = DurablePolicyHighWaterState(
                        anchor=state.anchor,
                        prepared=prepared,
                    )

                    # CRITICAL BOUNDARY:
                    #
                    # Persist and commit PREPARED in the
                    # independent durable database before
                    # any policy mutation may commit.

                    self._replace_state(
                        state,
                        pending,
                    )

                    _append_policy(
                        connection,
                        pins,
                        history,
                        candidate,
                        signed_policy,
                    )

                # The policy commit completed successfully.
                #
                # If its acknowledgement was lost, execution
                # never reaches finalization. PREPARED remains.

                finalized = self._replace_state(
                    pending,
                    _stable(
                        prepared.candidate
                    ),
                )

                return finalized.anchor.pair()

    def recover_publication(self):

        with _operation("publication recovery"):

            with self._fence():

                state = self._read_state()

                pins = self._pins

                with persistent._transaction(
                    pins
                ) as connection:

                    if state.prepared is None:

                        # Idempotent stable recovery.

                        _, observed = (
                            self._load_and_observe(
                                connection,
                                state,
                            )
                        )

                        return observed.anchor.pair()

                    prepared = state.prepared

                    history = persistent._load_history(
                        connection,
                        pins,
                        anchor=state.anchor.pair(),
                    )

                    candidate = (
                        _validate_prepared_signature(
                            self._configuration,
                            prepared,
                        )
                    )

                    current = _reference(
                        history.current
                    )

                    if current == prepared.predecessor:

                        # We do not infer that the original
                        # publication never committed.
                        #
                        # Complete the exact prepared candidate,
                        # whether the old head resulted from
                        # precommit failure or later rollback.

                        history = _append_policy(
                            connection,
                            pins,
                            history,
                            candidate,
                            prepared.signed_policy,
                        )

                    else:

                        # The exact candidate must already be
                        # present in fully authenticated history.

                        history = persistent._load_history(
                            connection,
                            pins,
                            anchor=prepared.candidate.pair(),
                        )

                        rows = connection.execute(
                            """
                            SELECT message, signature
                            FROM writer_policy_history
                            WHERE policy_epoch = ?
                            """,
                            (
                                prepared.candidate.epoch,
                            ),
                        ).fetchall()

                        if rows != [
                            prepared.signed_policy
                        ]:

                            raise ValueError(
                                "Prepared signed candidate is "
                                "missing or conflicts with history."
                            )

                    recovered_head = _reference(
                        history.current
                    )

                # Never finalize until the policy transaction
                # has completed. The shared fence remains held.

                finalized = self._replace_state(
                    state,
                    _stable(
                        recovered_head
                    ),
                )

                return finalized.anchor.pair()

    def exchange(self, request):

        with _operation("exchange"):

            document = remote._parse(
                request,
                maximum=versioned._MAX_WIRE_BYTES,
            )

            operation = document.get(
                "operation"
            )

            if operation in ("read", "lookup"):

                # Existing signed public recovery is independent
                # of both policy and durable storage availability.

                return (
                    persistent.SQLitePersistentWriterPolicyAuthority
                    ._public_read_or_lookup(
                        self,
                        document,
                    )
                )

            if set(document) != versioned._CAS_FIELDS:

                raise ValueError(
                    "Expected versioned writer CAS envelope."
                )

            with self._fence():

                state = self._read_state()

                if state.prepared is not None:

                    raise ValueError(
                        "Writer CAS blocked by prepared publication."
                    )

                pins = self._pins

                with persistent._transaction(
                    pins
                ) as connection:

                    history, observed = (
                        self._load_and_observe(
                            connection,
                            state,
                        )
                    )

                    current = history.current

                    if observed.anchor != _reference(
                        current
                    ):

                        raise ValueError(
                            "Durable observation mismatch."
                        )

                    # Durable observation has committed before
                    # any authorization or floor mutation.
                    #
                    # A failed writer check or backend failure
                    # cannot roll it back.

                    verifier = (
                        versioned.VersionedWriterPolicyAuthority
                        .from_signed_policy(
                            backend=pins.backend,
                            expected_policy_id=pins.policy_id,
                            expected_policy_public_key=(
                                pins.policy_public_key
                            ),
                            signed_policy=history.signed_current,
                            minimum_policy_epoch=current.epoch,
                            expected_policy_sha256=current.sha256,
                        )
                    )

                    response = verifier.exchange(
                        request
                    )

                return response


@dataclass(
    frozen=True,
    slots=True,
    eq=False,
)
class DurableWriterPolicyGateway:

    _authority: DurableWriterPolicyAuthority = field(
        repr=False,
    )

    def __post_init__(self):

        if (
            type(self._authority)
            is not DurableWriterPolicyAuthority
            or not hasattr(
                self._authority,
                "_configuration",
            )
            or not hasattr(
                self._authority,
                "_nonce",
            )
        ):

            raise ValueError(
                "Expected initialized canonical durable authority."
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

    def exchange(self, request):

        return self._authority.exchange(
            request
        )
