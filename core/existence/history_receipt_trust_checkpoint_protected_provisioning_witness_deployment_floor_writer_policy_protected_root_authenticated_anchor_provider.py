"""Authenticated local protected root anchor provider.

The provider holds the canonical SQLite backend fence throughout
a protocol session. Root mutations commit independently of that
fence and are never reverted merely because signing or session
completion fails.

Runtime root state remains represented by canonical immutable
objects. Serialization is restricted to the signature boundary.

This reference assumes trusted Python code, trusted local storage
and an authorized caller. It does not provide remote client
authentication, hardware signing-key isolation, distributed
consensus or resistance to complete trusted storage rollback.
"""

import json
import os
import threading

from contextlib import contextmanager
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidSignature

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root import (
    ProtectedDeploymentIdentity,
    ProtectedDurableRootState,
    ProtectedRootReference,
)

from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_anchor_enrollment import (
    PinnedProtectedRootAnchorEnrollment,
)

from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_sqlite_reference import (
    SQLiteProtectedRootBackend,
)


from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_anchor_session_registry import (
    reserve_session,
)


_OPERATION_DOMAIN = (
    "AdamShell/A44/protected-root-anchor-operation/v1"
)

# Bound the memory required by a single reference session.
# Exhaustion fails closed instead of forgetting old challenges.

_MAX_SESSION_CHALLENGES = 65536


def _require_nonce(value, label):

    if type(value) is not bytes or len(value) != 32:

        raise ValueError(
            label + " must be immutable 32-byte data."
        )

    return value


def _require_reference(value):

    if type(value) is not ProtectedRootReference:

        raise ValueError(
            "Expected canonical protected root reference."
        )

    return value


def _reference_fields(value):

    if value is None:

        return None

    reference = _require_reference(value)

    return [
        reference.revision,
        reference.sha256,
    ]


def _canonical_json(value):

    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


@dataclass(slots=True)
class _ProviderSession:

    phase: str = "idle"

    session: bytes | None = field(
        default=None,
        repr=False,
    )

    owner: object = field(
        default=None,
        repr=False,
    )

    reference: ProtectedRootReference | None = None

    challenges: set[bytes] = field(
        default_factory=set,
        repr=False,
    )

    poisoned: bool = False

    def reset(self):

        self.phase = "idle"
        self.session = None
        self.owner = None
        self.reference = None
        self.challenges.clear()
        self.poisoned = False


# The SQLite fence serializes independent threads and processes.
# Its intentional same-thread reentrancy must not authorize a
# second provider session over the same canonical storage path.

_PROVIDER_OWNERSHIP_LOCAL = threading.local()


def _active_provider_owners():

    process_id = os.getpid()

    owners = getattr(
        _PROVIDER_OWNERSHIP_LOCAL,
        "owners",
        None,
    )

    previous_process = getattr(
        _PROVIDER_OWNERSHIP_LOCAL,
        "process_id",
        None,
    )

    if owners is None:

        owners = {}

        _PROVIDER_OWNERSHIP_LOCAL.owners = owners
        _PROVIDER_OWNERSHIP_LOCAL.process_id = process_id

    elif previous_process != process_id:

        if owners:

            raise ValueError(
                "Inherited active provider ownership forbidden."
            )

        _PROVIDER_OWNERSHIP_LOCAL.process_id = process_id

    return owners


@contextmanager
def _exclusive_provider_fence(provider):

    """Hold one provider ownership claim through fence cleanup.

    Different threads use independent ownership maps and must
    still acquire the original SQLite fence.

    The claim precedes fence acquisition to reject same-thread
    callbacks during both acquisition and release.
    """

    from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_sqlite_reference import (
        _active_leases,
        _require_current_lease,
    )

    provider._require_process()

    descriptor = provider._backend._storage

    key = descriptor.fence_path

    owners = _active_provider_owners()

    if key in owners:

        raise ValueError(
            "Protected storage already has an active provider owner."
        )

    token = object()

    owners[key] = token

    try:

        with provider._backend.exclusive():

            lease = _active_leases().get(key)

            if lease is None:

                raise ValueError(
                    "Provider ownership requires an active backend fence."
                )

            _require_current_lease(
                lease,
                descriptor,
            )

            if owners.get(key) is not token:

                raise ValueError(
                    "Provider ownership claim changed."
                )

            yield

    finally:

        if owners.get(key) is token:

            del owners[key]


@dataclass(
    frozen=True,
    slots=True,
    eq=False,
)
class AuthenticatedProtectedRootAnchorProvider:

    """Signed reference provider over a canonical SQLite root."""

    enrollment: PinnedProtectedRootAnchorEnrollment

    _backend: SQLiteProtectedRootBackend = field(
        repr=False,
    )

    _signer: Ed25519PrivateKey = field(
        repr=False,
    )

    _lock: object = field(
        default_factory=threading.RLock,
        init=False,
        repr=False,
    )

    _held: _ProviderSession = field(
        default_factory=_ProviderSession,
        init=False,
        repr=False,
    )

    _process_id: int = field(
        default_factory=os.getpid,
        init=False,
        repr=False,
    )

    def __post_init__(self):

        if (
            type(self.enrollment)
            is not PinnedProtectedRootAnchorEnrollment
        ):

            raise ValueError(
                "Expected canonical pinned anchor enrollment."
            )

        if (
            type(self._backend)
            is not SQLiteProtectedRootBackend
        ):

            raise ValueError(
                "Expected canonical persistent SQLite root backend."
            )

        if self._backend.identity != self.enrollment.identity:

            raise ValueError(
                "Provider deployment identity mismatch."
            )

        if not isinstance(
            self._signer,
            Ed25519PrivateKey,
        ):

            raise ValueError(
                "Expected Ed25519 private signing key."
            )

        try:

            public_key = (
                self._signer.public_key().public_bytes(
                    Encoding.Raw,
                    PublicFormat.Raw,
                )
            )

        except Exception as exc:

            raise ValueError(
                "Provider signing key validation failed."
            ) from exc

        if public_key != self.enrollment.anchor_public_key:

            raise ValueError(
                "Provider signing key does not match enrollment."
            )

    @classmethod
    def from_backend(
        cls,
        *,
        backend,
        enrollment,
        signer,
    ):

        if cls is not AuthenticatedProtectedRootAnchorProvider:

            raise ValueError(
                "Unsupported authenticated provider subclass."
            )

        return cls(
            enrollment=enrollment,
            _backend=backend,
            _signer=signer,
        )

    @property
    def identity(self) -> ProtectedDeploymentIdentity:

        return self.enrollment.identity

    def _require_process(self):

        if os.getpid() != self._process_id:

            raise ValueError(
                "Inherited provider instance is forbidden."
            )

    def _require_owner(self):

        self._require_process()

        if (
            self._held.owner
            is not threading.current_thread()
        ):

            raise ValueError(
                "Protected provider session owner mismatch."
            )

    def _state_reference(self, state):

        if type(state) is not ProtectedDurableRootState:

            raise ValueError(
                "Expected canonical protected root state."
            )

        if state.identity != self.identity:

            raise ValueError(
                "Protected root deployment identity mismatch."
            )

        return _require_reference(
            state.reference()
        )

    def _read_current(self):

        state = self._backend.read()

        reference = self._state_reference(state)

        return state, reference

    def _read_held_state(self):

        state, reference = self._read_current()

        if reference != self._held.reference:

            raise ValueError(
                "Protected root changed outside provider operation."
            )

        return state, reference

    def _signed(
        self,
        *,
        operation,
        session,
        challenge,
        state,
        expected=None,
        replacement=None,
    ):

        reference = self._state_reference(state)

        message = _canonical_json([
            _OPERATION_DOMAIN,
            self.enrollment.fingerprint(),
            operation,
            session.hex(),
            challenge.hex(),
            _reference_fields(expected),
            _reference_fields(replacement),
            _reference_fields(reference),
        ])

        signature = self._signer.sign(message)

        if type(signature) is not bytes or len(signature) != 64:

            raise ValueError(
                "Noncanonical provider signature."
            )

        public_key = Ed25519PublicKey.from_public_bytes(
            self.enrollment.anchor_public_key
        )

        try:

            public_key.verify(
                signature,
                message,
            )

        except InvalidSignature as exc:

            raise ValueError(
                "Provider generated an invalid signature."
            ) from exc

        return state, signature

    def _require_healthy(self):

        self._require_owner()

        if self._held.poisoned:

            raise ValueError(
                "Protected provider session is poisoned."
            )

    def _reserve_operation(
        self,
        *,
        session,
        challenge,
    ):

        self._require_healthy()

        if self._held.phase != "held":

            raise ValueError(
                "Protected provider session is not held."
            )

        _require_nonce(
            session,
            "Session",
        )

        _require_nonce(
            challenge,
            "Challenge",
        )

        if session != self._held.session:

            raise ValueError(
                "Protected provider session mismatch."
            )

        if challenge in self._held.challenges:

            raise ValueError(
                "Protected provider challenge replay."
            )

        if (
            len(self._held.challenges)
            >= _MAX_SESSION_CHALLENGES
        ):

            raise ValueError(
                "Protected provider challenge limit exceeded."
            )

        self._held.challenges.add(
            challenge
        )

        self._held.phase = "in_flight"

    @contextmanager
    def hold(self, *, session):

        self._require_process()

        with self._lock:

            if self._held.phase != "idle":

                if (
                    self._held.owner
                    is threading.current_thread()
                ):

                    self._held.poisoned = True

                raise ValueError(
                    "Provider already has an active session."
                )

            _require_nonce(
                session,
                "Session",
            )

            self._held.phase = "acquiring"
            self._held.session = session
            self._held.owner = threading.current_thread()

            # HOLD uses the session nonce as its challenge.
            # The nonce cannot be reused for another operation.

            self._held.challenges.add(session)

        primary = None
        traceback = None
        completed = False

        try:

            try:

                with _exclusive_provider_fence(self):

                    try:

                        with self._lock:

                            self._require_healthy()

                            state, reference = self._read_current()

                            self._held.reference = reference

                            reserve_session(
                                backend=self._backend,
                                enrollment=self.enrollment,
                                session=session,
                            )

                            self._require_healthy()
                            self._read_held_state()

                            response = self._signed(
                                operation="hold",
                                session=session,
                                challenge=session,
                                state=state,
                            )

                            self._require_healthy()

                            self._held.phase = "held"

                        yield response

                        with self._lock:

                            self._require_healthy()

                            if self._held.phase != "finished":

                                raise ValueError(
                                    "Provider HOLD requires successful FINISH."
                                )

                            # Ensure that the state acknowledged by
                            # FINISH has not changed before release.

                            self._read_held_state()

                            completed = True

                    except BaseException as exc:

                        primary = exc
                        traceback = exc.__traceback__

                        with self._lock:

                            self._held.poisoned = True

                        raise

                    finally:

                        with self._lock:

                            self._held.phase = "releasing"

            except BaseException as cleanup_error:

                if primary is None or cleanup_error is primary:

                    raise

                # A cleanup exception must not replace the
                # original protocol or caller exception.

                try:

                    BaseException.add_note(
                        primary,
                        "Secondary provider fence cleanup failure: "
                        + type(cleanup_error).__name__,
                    )

                except BaseException:

                    pass

            if primary is not None:

                raise BaseException.with_traceback(
                    primary,
                    traceback,
                )

            if not completed:

                raise ValueError(
                    "Protected provider HOLD incomplete."
                )

            with self._lock:

                self._require_healthy()

        finally:

            with self._lock:

                self._held.reset()

    def _execute(
        self,
        *,
        operation,
        session,
        challenge,
        expected=None,
        replacement=None,
    ):

        self._require_process()

        with self._lock:

            # Foreign callers must not take ownership of or
            # reset an existing provider session.

            self._require_owner()

            try:

                self._reserve_operation(
                    session=session,
                    challenge=challenge,
                )

                if operation == "read":

                    state, reference = self._read_held_state()

                    response = self._signed(
                        operation="read",
                        session=session,
                        challenge=challenge,
                        state=state,
                    )

                    next_phase = "held"

                elif operation == "cas":

                    _require_reference(expected)

                    replacement_reference = (
                        self._state_reference(
                            replacement
                        )
                    )

                    if expected != self._held.reference:

                        raise ValueError(
                            "Stale protected provider CAS reference."
                        )

                    if replacement.revision != expected.revision + 1:

                        raise ValueError(
                            "Protected CAS must advance one revision."
                        )

                    self._read_held_state()

                    committed = self._backend.compare_and_set(
                        expected=expected,
                        replacement=replacement,
                    )

                    # CAS has its own durable state transaction.
                    # Never retry or roll back after this boundary.

                    if (
                        _require_reference(committed)
                        != replacement_reference
                    ):

                        raise ValueError(
                            "Protected backend CAS commitment mismatch."
                        )

                    state, observed = self._read_current()

                    if (
                        observed != replacement_reference
                        or state != replacement
                    ):

                        raise ValueError(
                            "Committed protected state mismatch."
                        )

                    self._held.reference = observed

                    response = self._signed(
                        operation="cas",
                        session=session,
                        challenge=challenge,
                        state=state,
                        expected=expected,
                        replacement=replacement_reference,
                    )

                    next_phase = "held"

                elif operation == "finish":

                    _require_reference(expected)

                    if expected != self._held.reference:

                        raise ValueError(
                            "Protected FINISH reference mismatch."
                        )

                    state, reference = self._read_held_state()

                    response = self._signed(
                        operation="finish",
                        session=session,
                        challenge=challenge,
                        state=state,
                        expected=expected,
                    )

                    next_phase = "finished"

                else:

                    raise ValueError(
                        "Unsupported protected provider operation."
                    )

                self._require_healthy()

                self._held.phase = next_phase

                return response

            except BaseException:

                self._held.poisoned = True

                raise

    def read(
        self,
        *,
        session,
        challenge,
    ):

        return self._execute(
            operation="read",
            session=session,
            challenge=challenge,
        )

    def compare_and_set(
        self,
        *,
        session,
        challenge,
        expected,
        replacement,
    ):

        return self._execute(
            operation="cas",
            session=session,
            challenge=challenge,
            expected=expected,
            replacement=replacement,
        )

    def finish(
        self,
        *,
        session,
        challenge,
        expected,
    ):

        return self._execute(
            operation="finish",
            session=session,
            challenge=challenge,
            expected=expected,
        )

    def __copy__(self):

        raise TypeError(
            "Protected provider copying is forbidden."
        )

    def __deepcopy__(self, memo):

        raise TypeError(
            "Protected provider deep copying is forbidden."
        )

    def __reduce_ex__(self, protocol):

        raise TypeError(
            "Protected provider serialization is forbidden."
        )
