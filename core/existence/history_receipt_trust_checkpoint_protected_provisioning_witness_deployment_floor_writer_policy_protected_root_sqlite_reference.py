"""SQLite reference protected root backend.

The state database commits independently from the shared SQLite
coordination fence.

Cooperating backend instances use the same storage pair.

The fence is reentrant for the current thread and storage pair.
Independent threads and processes acquire the SQLite writer
transaction before entering the protected operation.

Runtime policy state remains represented by canonical immutable
protected root objects.

The database pair and filesystem are trusted. This reference
does not provide hardware rollback resistance, distributed
consensus, or protection against trusted storage replacement.
"""

import os
import threading

from contextlib import contextmanager
from dataclasses import dataclass, field

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_sqlite_storage
    as storage,
)


root = storage.root
durable = storage.durable


@dataclass(frozen=True, slots=True)
class _FenceLease:

    descriptor: storage._Storage
    connection: object = field(repr=False)
    process_id: int
    thread_id: int


# Synchronization bookkeeping only.
# No canonical policy or protected root state is cached here.

_LOCAL = threading.local()


def _active_leases():

    pid = os.getpid()

    previous_pid = getattr(_LOCAL, "pid", None)
    leases = getattr(_LOCAL, "leases", None)

    if previous_pid != pid:

        if leases:
            raise ValueError(
                "Inherited active protected fence is forbidden."
            )

        _LOCAL.pid = pid
        _LOCAL.leases = {}

    elif leases is None:

        _LOCAL.leases = {}

    return _LOCAL.leases


def _require_current_lease(lease, descriptor):

    if lease.descriptor != descriptor:

        raise ValueError(
            "Nested protected storage identity mismatch."
        )

    if (
        lease.process_id != os.getpid()
        or lease.thread_id != threading.get_ident()
    ):

        raise ValueError(
            "Protected fence holder identity mismatch."
        )

    if not lease.connection.in_transaction:

        raise ValueError(
            "Protected fence transaction is not active."
        )

    storage._check_pair(descriptor)

    storage._validate_metadata(
        lease.connection,
        descriptor,
        "fence",
    )


@contextmanager
def _exclusive(descriptor):

    # Exceptions raised by the caller's protected operation must
    # not be confused with errors acquiring or releasing a fence.

    body_error = None

    try:

        storage._check_pair(descriptor)

        leases = _active_leases()

        key = descriptor.fence_path

        existing = leases.get(key)

        if existing is not None:

            _require_current_lease(
                existing,
                descriptor,
            )

            try:

                yield

            except BaseException as exc:

                body_error = exc
                raise

            return

        # This transaction remains active for the complete outer
        # authorization operation. It never writes root state.

        with storage._transaction(
            descriptor.fence_path,
            write=True,
        ) as connection:

            lease = _FenceLease(
                descriptor=descriptor,
                connection=connection,
                process_id=os.getpid(),
                thread_id=threading.get_ident(),
            )

            _require_current_lease(
                lease,
                descriptor,
            )

            # Validate the independently stored root after
            # acquiring the shared coordination fence.

            with storage._transaction(
                descriptor.path,
            ) as state_connection:

                storage._read_state(
                    state_connection,
                    descriptor,
                )

            leases[key] = lease

            try:

                yield

            except BaseException as exc:

                body_error = exc
                raise

            finally:

                del leases[key]

    except Exception as exc:

        if exc is body_error:
            raise

        raise ValueError(
            "Protected SQLite fence operation failed."
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
    init=False,
    eq=False,
)
class SQLiteProtectedRootBackend(root.ProtectedRootBackend):

    """Persistent reference implementation of ProtectedRootBackend."""

    _storage: storage._Storage = field(repr=False)

    def __init__(self, *args, **kwargs):

        raise ValueError(
            "Use explicit protected root create() or open()."
        )

    @classmethod
    def _construct(cls, descriptor):

        if cls is not SQLiteProtectedRootBackend:

            raise ValueError(
                "Expected canonical SQLite protected backend class."
            )

        if type(descriptor) is not storage._Storage:

            raise ValueError(
                "Expected canonical protected storage descriptor."
            )

        instance = object.__new__(cls)

        object.__setattr__(
            instance,
            "_storage",
            descriptor,
        )

        return instance

    @classmethod
    def create(cls, *, path, expected_identity):

        with durable._operation(
            "SQLite protected root creation"
        ):

            if cls is not SQLiteProtectedRootBackend:

                raise ValueError(
                    "Unsupported protected backend subclass."
                )

            descriptor = storage._create(
                path,
                expected_identity,
            )

            return cls._construct(descriptor)

    @classmethod
    def open(cls, *, path, expected_identity):

        with durable._operation(
            "SQLite protected root opening"
        ):

            if cls is not SQLiteProtectedRootBackend:

                raise ValueError(
                    "Unsupported protected backend subclass."
                )

            descriptor = storage._open(
                path,
                expected_identity,
            )

            return cls._construct(descriptor)

    @property
    def identity(self):

        return self._storage.identity

    @contextmanager
    def exclusive(self):

        with _exclusive(self._storage):

            yield

    def _require_initialized(self, connection):

        state = storage._read_state(
            connection,
            self._storage,
        )

        if state is None:

            raise ValueError(
                "Protected root has not been provisioned."
            )

        return state

    def read(self):

        with durable._operation(
            "SQLite protected root read"
        ):

            with self.exclusive():

                with storage._transaction(
                    self._storage.path,
                ) as connection:

                    state = self._require_initialized(
                        connection
                    )

                return state

    def provision(self, *, state):

        with durable._operation(
            "SQLite protected root provisioning"
        ):

            if type(state) is not root.ProtectedDurableRootState:

                raise ValueError(
                    "Expected canonical initial root state."
                )

            if state.identity != self.identity:

                raise ValueError(
                    "Initial protected deployment identity mismatch."
                )

            if (
                state.revision != 1
                or state.durable_state.prepared is not None
            ):

                raise ValueError(
                    "Provisioning requires stable root revision one."
                )

            with self.exclusive():

                with storage._transaction(
                    self._storage.path,
                    write=True,
                ) as connection:

                    existing = storage._read_state(
                        connection,
                        self._storage,
                    )

                    if existing is not None:

                        raise ValueError(
                            "Protected root already provisioned."
                        )

                    reference = storage._write_state(
                        connection,
                        self._storage,
                        state,
                    )

                    if reference != state.reference():

                        raise ValueError(
                            "Provisioning commitment mismatch."
                        )

                # The state database COMMIT has completed.
                # The independent fence remains held.

                return reference

    def compare_and_set(self, *, expected, replacement):

        with durable._operation(
            "SQLite protected root compare-and-set"
        ):

            if type(expected) is not root.ProtectedRootReference:

                raise ValueError(
                    "Expected canonical protected root reference."
                )

            if (
                type(replacement)
                is not root.ProtectedDurableRootState
            ):

                raise ValueError(
                    "Expected canonical replacement root state."
                )

            with self.exclusive():

                with storage._transaction(
                    self._storage.path,
                    write=True,
                ) as connection:

                    previous = self._require_initialized(
                        connection
                    )

                    if expected != previous.reference():

                        raise ValueError(
                            "Protected root reference is stale."
                        )

                    root._validate_transition(
                        previous,
                        replacement,
                    )

                    reference = storage._write_state(
                        connection,
                        self._storage,
                        replacement,
                    )

                    if reference != replacement.reference():

                        raise ValueError(
                            "Replacement commitment mismatch."
                        )

                # Return only after the independent root state
                # transaction has committed successfully.

                return reference

    def __copy__(self):

        raise TypeError(
            "Protected backend copying is forbidden."
        )

    def __deepcopy__(self, memo):

        raise TypeError(
            "Protected backend deep copying is forbidden."
        )

    def __reduce_ex__(self, protocol):

        raise TypeError(
            "Protected backend serialization is forbidden."
        )
