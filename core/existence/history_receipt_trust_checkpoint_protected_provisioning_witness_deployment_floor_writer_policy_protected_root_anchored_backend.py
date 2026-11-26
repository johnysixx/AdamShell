"""Independent-anchor protected root backend.

The anchor is authoritative. Local state is a checked replica.

Both backends must be explicitly provisioned and implement
reentrant exclusive fencing with committed CAS semantics.

The anchor fence is acquired before the local fence and held
throughout the caller's protected operation.

A successful anchor transition precedes the local transition.
Failures never trigger automatic rollback of the anchor.

Explicit recovery permits only equal-state reconciliation or
one valid forward transition into the local backend.

This adapter cannot establish independence, authenticity,
durability or rollback resistance of the supplied anchor.
Those are requirements on the deployment trust boundary.

Direct access to unguarded authority backends remains outside
the guarantees provided by this adapter.
"""

from contextlib import contextmanager
from dataclasses import dataclass, field

from . import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root
    as root,
)

from . import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_sqlite_reference
    as sqlite_root,
)


durable = root.durable

ProtectedDeploymentIdentity = root.ProtectedDeploymentIdentity

ProtectedRootReference = root.ProtectedRootReference

ProtectedDurableRootState = root.ProtectedDurableRootState

ProtectedRootBackend = root.ProtectedRootBackend


def _require_identity(value, expected):

    if (
        type(value) is not ProtectedDeploymentIdentity
        or value != expected
    ):

        raise ValueError(
            "Protected root identity mismatch."
        )


def _require_reference(value):

    if type(value) is not ProtectedRootReference:

        raise ValueError(
            "Expected canonical protected root reference."
        )

    # Revalidate the canonical reference fields.

    return ProtectedRootReference(
        revision=value.revision,
        sha256=value.sha256,
    )


def _require_state(value, identity):

    if type(value) is not ProtectedDurableRootState:

        raise ValueError(
            "Expected canonical protected root state."
        )

    _require_identity(
        value.identity,
        identity,
    )

    canonical = ProtectedDurableRootState(
        identity=value.identity,
        revision=value.revision,
        durable_state=value.durable_state,
    )

    _require_reference(
        canonical.reference()
    )

    return canonical


def _require_receipt(receipt, expected):

    actual = _require_reference(receipt)

    if actual != expected:

        raise ValueError(
            "Protected root CAS receipt mismatch."
        )


def _require_distinct_backends(local, anchor):

    if not isinstance(local, ProtectedRootBackend):

        raise ValueError(
            "Expected protected local backend."
        )

    if not isinstance(anchor, ProtectedRootBackend):

        raise ValueError(
            "Expected protected anchor backend."
        )

    if local is anchor:

        raise ValueError(
            "Local and anchor backends must be distinct."
        )

    if (
        isinstance(local, AnchoredProtectedRootBackend)
        or isinstance(anchor, AnchoredProtectedRootBackend)
    ):

        raise ValueError(
            "Nested anchored backend composition is forbidden."
        )

    # Reject known SQLite aliases even when represented by
    # independently constructed Python objects.
    #
    # This does not prove independent storage trust domains.

    if (
        isinstance(local, sqlite_root.SQLiteProtectedRootBackend)
        and isinstance(anchor, sqlite_root.SQLiteProtectedRootBackend)
    ):

        first = local._storage
        second = anchor._storage

        first_paths = (
            first.path,
            first.fence_path,
        )

        second_paths = (
            second.path,
            second.fence_path,
        )

        if (
            first.storage_id == second.storage_id
            or any(
                left == right
                for left in first_paths
                for right in second_paths
            )
        ):

            raise ValueError(
                "Local and anchor SQLite stores overlap."
            )


@dataclass(
    frozen=True,
    slots=True,
    init=False,
    eq=False,
)
class AnchoredProtectedRootBackend(ProtectedRootBackend):

    """Fail-closed local replica guarded by a trusted anchor."""

    _local: ProtectedRootBackend = field(repr=False)

    _anchor: ProtectedRootBackend = field(repr=False)

    _identity: ProtectedDeploymentIdentity

    def __init__(self, *args, **kwargs):

        raise ValueError(
            "Use explicit anchored backend open."
        )

    @classmethod
    def _construct(
        cls,
        *,
        local_backend,
        anchor_backend,
        expected_identity,
    ):

        if cls is not AnchoredProtectedRootBackend:

            raise ValueError(
                "Expected canonical anchored backend class."
            )

        if type(expected_identity) is not ProtectedDeploymentIdentity:

            raise ValueError(
                "Expected canonical protected deployment identity."
            )

        _require_distinct_backends(
            local_backend,
            anchor_backend,
        )

        instance = object.__new__(cls)

        object.__setattr__(
            instance, "_local", local_backend
        )

        object.__setattr__(
            instance, "_anchor", anchor_backend
        )

        object.__setattr__(
            instance, "_identity", expected_identity
        )

        return instance

    @classmethod
    def open(
        cls,
        *,
        local_backend,
        anchor_backend,
        expected_identity,
    ):

        with durable._operation("Open anchored protected root"):

            instance = cls._construct(
                local_backend=local_backend,
                anchor_backend=anchor_backend,
                expected_identity=expected_identity,
            )

            with instance.exclusive():

                instance._equal_state()

            return instance

    @property
    def identity(self):

        return self._identity

    def _check_bindings(self):

        _require_distinct_backends(
            self._local,
            self._anchor,
        )

        _require_identity(
            self._anchor.identity,
            self._identity,
        )

        _require_identity(
            self._local.identity,
            self._identity,
        )

    @contextmanager
    def _held_backends(self):

        body_error = None
        entered = False

        try:

            # The authoritative lock is always outermost.

            with self._anchor.exclusive():

                with self._local.exclusive():

                    self._check_bindings()

                    entered = True

                    try:

                        yield

                    except BaseException as exc:

                        body_error = exc
                        raise

        except Exception as exc:

            # Preserve exceptions originating in the protected
            # caller operation rather than misclassifying them
            # as fence acquisition failures.

            if exc is body_error:

                raise

            raise ValueError(
                "Protected root fencing failed."
            ) from exc

        if not entered:

            raise ValueError(
                "Protected backend fence was not entered."
            )

        if body_error is not None:

            raise body_error

    def _read_anchor(self):

        _require_identity(
            self._anchor.identity,
            self._identity,
        )

        return _require_state(
            self._anchor.read(),
            self._identity,
        )

    def _read_local(self):

        _require_identity(
            self._local.identity,
            self._identity,
        )

        return _require_state(
            self._local.read(),
            self._identity,
        )

    def _states(self):

        self._check_bindings()

        anchor = self._read_anchor()
        local = self._read_local()

        return local, anchor

    def _equal_state(self):

        local, anchor = self._states()

        if (
            local != anchor
            or local.reference() != anchor.reference()
        ):

            raise ValueError(
                "Local protected root differs from authoritative anchor."
            )

        return anchor

    @contextmanager
    def exclusive(self):

        with self._held_backends():

            with durable._operation(
                "Validate anchored protected root"
            ):

                self._equal_state()

            yield

            with durable._operation(
                "Revalidate anchored protected root"
            ):

                self._equal_state()

    def read(self):

        with durable._operation("Read anchored protected root"):

            with self.exclusive():

                return self._equal_state()

    def provision(self, *, state):

        raise ValueError(
            "Anchored backend requires separately provisioned roots."
        )

    def compare_and_set(
        self,
        *,
        expected,
        replacement,
    ):

        with durable._operation("Anchored protected root CAS"):

            expected = _require_reference(expected)

            replacement = _require_state(
                replacement,
                self._identity,
            )

            with self.exclusive():

                previous = self._equal_state()

                if previous.reference() != expected:

                    raise ValueError(
                        "Stale or conflicting anchored root reference."
                    )

                root._validate_transition(
                    previous,
                    replacement,
                )

                target = replacement.reference()

                # Commit authoritative state first.

                anchor_receipt = self._anchor.compare_and_set(
                    expected=expected,
                    replacement=replacement,
                )

                _require_receipt(
                    anchor_receipt,
                    target,
                )

                if self._read_anchor() != replacement:

                    raise ValueError(
                        "Anchor CAS readback mismatch."
                    )

                if self._read_local() != previous:

                    raise ValueError(
                        "Local root changed during anchor CAS."
                    )

                # Only the confirmed authoritative state may
                # now be committed into the local replica.

                local_receipt = self._local.compare_and_set(
                    expected=expected,
                    replacement=replacement,
                )

                _require_receipt(
                    local_receipt,
                    target,
                )

                if self._equal_state() != replacement:

                    raise ValueError(
                        "Anchored CAS final readback mismatch."
                    )

                return target

    @classmethod
    def recover_local(
        cls,
        *,
        local_backend,
        anchor_backend,
        expected_identity,
        expected_local,
        expected_anchor,
    ):

        """Explicitly reconcile a local replica to its anchor."""

        with durable._operation("Recover anchored protected root"):

            expected_local = _require_reference(
                expected_local
            )

            expected_anchor = _require_reference(
                expected_anchor
            )

            instance = cls._construct(
                local_backend=local_backend,
                anchor_backend=anchor_backend,
                expected_identity=expected_identity,
            )

            # Recovery needs both fences but must not require
            # initial equality, since divergence is its purpose.

            with instance._held_backends():

                local, anchor = instance._states()

                if (
                    local.reference() != expected_local
                    or anchor.reference() != expected_anchor
                ):

                    raise ValueError(
                        "Stale explicit recovery reference."
                    )

                if local == anchor:

                    if expected_local != expected_anchor:

                        raise ValueError(
                            "Conflicting equal-state recovery references."
                        )

                    return anchor.reference()

                if anchor.revision != local.revision + 1:

                    raise ValueError(
                        "Recovery requires exactly one forward revision."
                    )

                root._validate_transition(
                    local,
                    anchor,
                )

                # Recovery must never update the anchor.

                receipt = instance._local.compare_and_set(
                    expected=expected_local,
                    replacement=anchor,
                )

                _require_receipt(
                    receipt,
                    expected_anchor,
                )

                if instance._equal_state() != anchor:

                    raise ValueError(
                        "Recovery readback mismatch."
                    )

                return expected_anchor

    def __copy__(self):

        raise TypeError(
            "Anchored protected backend cannot be copied."
        )

    def __deepcopy__(self, memo):

        raise TypeError(
            "Anchored protected backend cannot be deep-copied."
        )

    def __reduce_ex__(self, protocol):

        raise TypeError(
            "Anchored protected backend cannot be serialized."
        )
