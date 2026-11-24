"""A44 monotonic observed writer policy authority.

This layer extends persistent signed policy validation with a live,
instance-local high-water reference.

The complete authenticated policy history must contain the exact
previously observed epoch and digest. Valid extensions advance the
reference, while rollback and conflicting histories are rejected.

Observation of an existing committed policy is retained independently
of the result of authorization, publication or backend execution.

A publication candidate advances the reference only after successful
completion of the persistent policy transaction.

Lock order:
    1. Instance operation lock.
    2. Persistent policy SQLite BEGIN IMMEDIATE.
    3. Existing floor backend transaction, when required.

The instance lock remains held through successful publication commit
and subsequent high-water advancement.

Public signed READ and LOOKUP remain independent of policy storage.

SECURITY LIMITS:
- The high-water is instance-local and in-memory.
- A fresh authority requires externally retained trust references.
- Independent policy-store copies are not globally fenced.
- Legacy authorities and direct floor backend access are not fenced.
- This is not independent durable rollback protection.
- The policy and floor databases are not one distributed transaction.
- Trusted process code, filesystem paths and directory access remain
  necessary.
"""

import hmac
import threading

from dataclasses import dataclass, field

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


def _reference(state):

    return (
        state.epoch,
        state.sha256,
    )


@dataclass(
    frozen=True,
    slots=True,
    init=False,
    eq=False,
)
class MonotonicObservedWriterPolicyAuthority:
    """Persistent policy authority retaining its highest observed head."""

    _persistent: (
        persistent.SQLitePersistentWriterPolicyAuthority
    ) = field(repr=False)

    _observed: tuple

    _lock: object = field(repr=False)

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

        if hasattr(self, "_persistent"):

            raise ValueError(
                "An initialized observed authority cannot be reopened in place."
            )

        base = (
            persistent.SQLitePersistentWriterPolicyAuthority.open(
                path=path,
                backend=backend,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                expected_genesis_sha256=expected_genesis_sha256,
                minimum_policy_epoch=minimum_policy_epoch,
                expected_current_policy_sha256=(
                    expected_current_policy_sha256
                ),
            )
        )

        self._initialize_from_opened(
            base
        )

    def _initialize_from_opened(
        self,
        base,
    ):

        if hasattr(self, "_persistent"):

            raise ValueError(
                "Observed authority already initialized."
            )

        if type(base) is not (
            persistent.SQLitePersistentWriterPolicyAuthority
        ):

            raise ValueError(
                "Expected canonical persistent writer policy authority."
            )

        # Reuse the authenticated opening anchor directly.
        #
        # A second unpinned database read here could discard the
        # reference authenticated by the persistent OPEN operation.

        reference = base._opening_anchor

        if (
            type(reference) is not tuple
            or len(reference) != 2
        ):

            raise ValueError(
                "Invalid persistent opening reference."
            )

        epoch = versioned._require_epoch(
            reference[0],
            "observed opening epoch",
        )

        digest = versioned._require_digest(
            reference[1],
            "observed opening digest",
        )

        object.__setattr__(
            self,
            "_lock",
            threading.RLock(),
        )

        object.__setattr__(
            self,
            "_observed",
            (
                epoch,
                digest,
            ),
        )

        object.__setattr__(
            self,
            "_persistent",
            base,
        )

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
        """Explicitly create and authenticate a new policy store."""

        base = (
            persistent.SQLitePersistentWriterPolicyAuthority.create(
                path=path,
                backend=backend,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                signed_genesis_policy=signed_genesis_policy,
                expected_genesis_sha256=expected_genesis_sha256,
            )
        )

        instance = object.__new__(
            cls
        )

        instance._initialize_from_opened(
            base
        )

        return instance

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
        """Authenticate an existing store without initializing it."""

        return cls(
            path=path,
            backend=backend,
            expected_policy_id=expected_policy_id,
            expected_policy_public_key=expected_policy_public_key,
            expected_genesis_sha256=expected_genesis_sha256,
            minimum_policy_epoch=minimum_policy_epoch,
            expected_current_policy_sha256=(
                expected_current_policy_sha256
            ),
        )

    def observed_policy_reference(self):
        """Return the retained reference without reading SQLite."""

        with self._lock:

            return self._observed

    def _advance_observed(
        self,
        state,
    ):
        """Retain a fully authenticated policy reference.

        The caller must hold the instance lock and must have
        established authenticated lineage continuity.

        A publication candidate must already have committed.
        """

        candidate = _reference(
            state
        )

        previous = self._observed

        if candidate[0] < previous[0]:

            raise ValueError(
                "Observed writer policy epoch cannot decrease."
            )

        if candidate[0] == previous[0]:

            if not hmac.compare_digest(
                candidate[1],
                previous[1],
            ):

                raise ValueError(
                    "Observed writer policy digest cannot change "
                    "at the same epoch."
                )

            return previous

        object.__setattr__(
            self,
            "_observed",
            candidate,
        )

        return candidate

    def _load_observed_history(
        self,
        connection,
    ):
        """Authenticate history against the current live anchor.

        Existing committed history advances observation before any
        writer authorization or candidate publication is attempted.

        The complete lineage, signatures, retirement rules and
        persistent head must validate before observation changes.
        """

        history = persistent._load_history(
            connection,
            self._persistent._pins,
            anchor=self._observed,
        )

        self._advance_observed(
            history.current,
        )

        return history

    def current_policy_reference(self):

        try:

            with self._lock:

                with persistent._transaction(
                    self._persistent._pins,
                ) as connection:

                    history = self._load_observed_history(
                        connection
                    )

                    return _reference(
                        history.current
                    )

        except Exception as exc:

            raise ValueError(
                "Observed writer policy reference read failed."
            ) from exc

    def retired_writer_keys(self):

        try:

            with self._lock:

                with persistent._transaction(
                    self._persistent._pins,
                ) as connection:

                    history = self._load_observed_history(
                        connection
                    )

                    return tuple(
                        sorted(
                            history.retired
                        )
                    )

        except Exception as exc:

            raise ValueError(
                "Observed writer policy retirement read failed."
            ) from exc

    def publish_policy(
        self,
        *,
        signed_policy,
    ):
        """Publish a valid extension without observing uncommitted state."""

        try:

            with self._lock:

                pins = self._persistent._pins

                with persistent._transaction(
                    pins,
                ) as connection:

                    # The existing committed head is authenticated
                    # and retained even if the candidate is invalid.

                    history = self._load_observed_history(
                        connection
                    )

                    current = history.current

                    candidate = persistent._parse_policy(
                        pins,
                        signed_policy,
                    )

                    next_retired = persistent._validate_transition(
                        current=current,
                        candidate=candidate,
                        retired=history.retired,
                    )

                    persistent._insert_history(
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
                            "Observed policy head update failed."
                        )

                    # IMPORTANT:
                    #
                    # This is validation of an uncommitted candidate.
                    # Do not call _load_observed_history here.
                    #
                    # Updating the live high-water before COMMIT
                    # could permanently retain an unpublished policy.

                    verified = persistent._load_history(
                        connection,
                        pins,
                        anchor=self._observed,
                    )

                    if (
                        verified.current != candidate
                        or verified.signed_current != signed_policy
                        or verified.retired != next_retired
                    ):

                        raise ValueError(
                            "Observed policy publication verification failed."
                        )

                # The persistent transaction has committed.
                #
                # The instance lock is still held. No other
                # operation of this authority can race between
                # COMMIT and high-water advancement.

                return self._advance_observed(
                    candidate
                )

        except Exception as exc:

            raise ValueError(
                "Observed writer policy publication failed."
            ) from exc

    def exchange(
        self,
        request,
    ):
        """Authorize floor CAS against monotonic authenticated history."""

        try:

            document = remote._parse(
                request,
                maximum=versioned._MAX_WIRE_BYTES,
            )

            operation = document.get(
                "operation"
            )

            # Public signed recovery is deliberately independent
            # of writer-policy availability and rollback detection.
            #
            # It neither mutates nor advances the observed reference.

            if operation in (
                "read",
                "lookup",
            ):

                return self._persistent._public_read_or_lookup(
                    document
                )

            if set(document) != versioned._CAS_FIELDS:

                raise ValueError(
                    "Expected versioned writer CAS envelope."
                )

            with self._lock:

                pins = self._persistent._pins

                with persistent._transaction(
                    pins,
                ) as connection:

                    # Retain the authenticated current policy
                    # BEFORE writer validation and floor mutation.
                    #
                    # A rejected request, backend failure or lost
                    # acknowledgement cannot undo this observation.

                    history = self._load_observed_history(
                        connection
                    )

                    current = history.current

                    verifier = (
                        versioned.VersionedWriterPolicyAuthority
                        .from_signed_policy(
                            backend=pins.backend,
                            expected_policy_id=pins.policy_id,
                            expected_policy_public_key=(
                                pins.policy_public_key
                            ),
                            signed_policy=(
                                history.signed_current
                            ),
                            minimum_policy_epoch=(
                                current.epoch
                            ),
                            expected_policy_sha256=(
                                current.sha256
                            ),
                        )
                    )

                    response = verifier.exchange(
                        request
                    )

                return response

        except Exception as exc:

            # The floor CAS may already have committed.
            # Signed LOOKUP remains available for recovery.
            #
            # The observed high-water is intentionally not rolled
            # back when processing a request fails.

            raise ValueError(
                "Observed writer policy exchange failed."
            ) from exc


@dataclass(
    frozen=True,
    slots=True,
    eq=False,
)
class MonotonicObservedWriterPolicyGateway:
    """Canonical gateway using one observed policy authority."""

    _authority: (
        MonotonicObservedWriterPolicyAuthority
    ) = field(repr=False)

    def __post_init__(self):

        if type(self._authority) is not (
            MonotonicObservedWriterPolicyAuthority
        ):

            raise ValueError(
                "Expected canonical monotonic observed policy authority."
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
            request
        )
