"""Authenticated protected root anchor client.

The enrollment is independently trusted configuration.

All provider statements are authenticated against the pinned
Ed25519 public key and exact operation transcript.

Authentication does not prove physical fencing, remote
linearizability, durability or honest provider execution.

An uncertain CAS is never automatically retried or rolled back.
"""

import json
import secrets

from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import RLock

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root import (
    ProtectedDeploymentIdentity,
    ProtectedDurableRootState,
    ProtectedRootBackend,
    ProtectedRootReference,
)

from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_anchor_enrollment import (
    PinnedProtectedRootAnchorEnrollment,
)


DOMAIN = "AdamShell/A44/protected-root-anchor-operation/v1"


def _canonical_json(value):
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def _reference_fields(reference):
    if reference is None:
        return None

    if type(reference) is not ProtectedRootReference:
        raise ValueError("Canonical root reference required.")

    return [
        reference.revision,
        reference.sha256,
    ]


@dataclass(slots=True)
class _HeldSession:
    session: bytes | None = None
    reference: ProtectedRootReference | None = None
    poisoned: bool = False
    phase: str = "idle"


@dataclass(frozen=True, slots=True)
class AuthenticatedProtectedRootAnchorClient(ProtectedRootBackend):
    """Pinned authenticated adapter for protected root operations."""

    enrollment: PinnedProtectedRootAnchorEnrollment

    _provider: object = field(
        repr=False,
        compare=False,
    )

    _lock: object = field(
        default_factory=RLock,
        init=False,
        repr=False,
        compare=False,
    )

    _held: _HeldSession = field(
        default_factory=_HeldSession,
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self):
        if (
            type(self.enrollment)
            is not PinnedProtectedRootAnchorEnrollment
        ):
            raise ValueError(
                "Canonical pinned enrollment required."
            )

        for name in (
            "hold",
            "read",
            "compare_and_set",
            "finish",
        ):
            if not callable(
                getattr(self._provider, name, None)
            ):
                raise ValueError(
                    "Missing provider operation: " + name
                )

    @classmethod
    def from_provider(cls, *, provider, enrollment):
        return cls(
            enrollment=enrollment,
            _provider=provider,
        )

    @property
    def identity(self) -> ProtectedDeploymentIdentity:
        return self.enrollment.identity

    def _validate_state(self, state):
        if type(state) is not ProtectedDurableRootState:
            raise ValueError(
                "Canonical protected durable root state required."
            )

        if state.identity != self.identity:
            raise ValueError(
                "Protected root deployment identity mismatch."
            )

        reference = state.reference()

        if type(reference) is not ProtectedRootReference:
            raise ValueError(
                "Canonical protected root reference required."
            )

        return reference

    def _verify_response(
        self,
        response,
        *,
        operation,
        session,
        challenge,
        expected=None,
        replacement=None,
    ):
        if type(response) is not tuple or len(response) != 2:
            raise ValueError(
                "Invalid authenticated provider response."
            )

        state, signature = response

        if type(signature) is not bytes or len(signature) != 64:
            raise ValueError(
                "Canonical Ed25519 signature required."
            )

        reference = self._validate_state(state)

        message = _canonical_json(
            [
                DOMAIN,
                self.enrollment.fingerprint(),
                operation,
                session.hex(),
                challenge.hex(),
                _reference_fields(expected),
                _reference_fields(replacement),
                _reference_fields(reference),
            ]
        )

        public_key = Ed25519PublicKey.from_public_bytes(
            self.enrollment.anchor_public_key
        )

        try:
            public_key.verify(signature, message)
        except InvalidSignature as exc:
            raise ValueError(
                "Invalid protected root operation signature."
            ) from exc

        return state, reference

    def _reject_transport_reentrancy(self):
        if self._held.phase not in ("idle", "held"):
            self._held.poisoned = True
            raise ValueError(
                "Protected root transport reentrancy rejected."
            )

    def _require_held(self):
        if self._held.session is None:
            raise ValueError(
                "No authenticated held session."
            )

        if self._held.poisoned:
            raise ValueError(
                "Authenticated held session is poisoned."
            )

        return self._held.session

    def _reset_session(self):
        self._held.session = None
        self._held.reference = None
        self._held.poisoned = False
        self._held.phase = "idle"

    def _operation(
        self,
        operation,
        *,
        expected=None,
        replacement=None,
    ):
        self._reject_transport_reentrancy()
        self._require_held()

        if self._held.phase != "held":
            raise ValueError(
                "Authenticated root session is not held."
            )

        self._held.phase = "in_flight"

        try:
            result = self._dispatch_operation(
                operation,
                expected=expected,
                replacement=replacement,
            )

            # A provider may catch a rejected callback.
            # It must not restore trust in this session.
            self._require_held()

            return result

        except BaseException:
            self._held.poisoned = True
            raise

        finally:
            self._held.phase = "held"

    def _dispatch_operation(
        self,
        operation,
        *,
        expected=None,
        replacement=None,
    ):
        session = self._require_held()
        challenge = secrets.token_bytes(32)

        try:
            if operation == "read":
                response = self._provider.read(
                    session=session,
                    challenge=challenge,
                )

                state, reference = self._verify_response(
                    response,
                    operation=operation,
                    session=session,
                    challenge=challenge,
                )

                if reference != self._held.reference:
                    raise ValueError(
                        "Unexpected root change during held read."
                    )

                return state

            if operation == "cas":
                if expected != self._held.reference:
                    raise ValueError(
                        "CAS expected reference mismatch."
                    )

                replacement_reference = self._validate_state(
                    replacement
                )

                response = self._provider.compare_and_set(
                    session=session,
                    challenge=challenge,
                    expected=expected,
                    replacement=replacement,
                )

                state, reference = self._verify_response(
                    response,
                    operation=operation,
                    session=session,
                    challenge=challenge,
                    expected=expected,
                    replacement=replacement_reference,
                )

                if (
                    reference != replacement_reference
                    or state != replacement
                ):
                    raise ValueError(
                        "Authenticated CAS result mismatch."
                    )

                self._held.reference = reference

                return reference

            if operation == "finish":
                reference = self._held.reference

                response = self._provider.finish(
                    session=session,
                    challenge=challenge,
                    expected=reference,
                )

                _, observed = self._verify_response(
                    response,
                    operation=operation,
                    session=session,
                    challenge=challenge,
                    expected=reference,
                )

                if observed != reference:
                    raise ValueError(
                        "Authenticated final reference mismatch."
                    )

                return None

            raise ValueError(
                "Unsupported authenticated root operation."
            )

        except BaseException:
            self._held.poisoned = True
            raise

    @contextmanager
    def exclusive(self):
        """Hold an authenticated, transport-isolated session."""

        with self._lock:
            self._reject_transport_reentrancy()

            if self._held.session is not None:
                self._require_held()

                try:
                    yield
                except BaseException:
                    self._held.poisoned = True
                    raise

                self._require_held()
                return

            if self._held.phase != "idle":
                raise ValueError(
                    "Protected root session is not idle."
                )

            session = secrets.token_bytes(32)

            failure = None
            failure_traceback = None
            completed = False

            self._held.phase = "opening"

            try:
                try:
                    with self._provider.hold(
                        session=session
                    ) as response:

                        try:
                            _, reference = self._verify_response(
                                response,
                                operation="hold",
                                session=session,
                                challenge=session,
                            )

                            # Reject callbacks attempted during
                            # provider creation or HOLD entry.
                            if self._held.poisoned:
                                raise ValueError(
                                    "Authenticated HOLD was compromised."
                                )

                            self._held.session = session
                            self._held.reference = reference
                            self._held.phase = "held"

                            yield

                            self._require_held()

                            self._operation("finish")

                            completed = True

                        except BaseException as exc:
                            self._held.poisoned = True
                            failure = exc
                            failure_traceback = exc.__traceback__
                            raise

                        finally:
                            # The provider's __exit__ is also
                            # an untrusted transport callback.
                            self._held.phase = "closing"

                except BaseException as cleanup_error:
                    if (
                        failure is None
                        or cleanup_error is failure
                    ):
                        raise

                    # Preserve the primary exception without
                    # creating a circular exception chain.
                    failure.add_note(
                        "Secondary protected root transport "
                        "cleanup failure: "
                        + type(cleanup_error).__name__
                    )

                # A suppressing provider must not turn a
                # primary failure into successful completion.
                if failure is not None:
                    raise failure.with_traceback(
                        failure_traceback
                    )

                if not completed:
                    raise ValueError(
                        "Authenticated root session incomplete."
                    )

                # A cleanup callback may have attempted
                # reentrancy and caught its own rejection.
                self._require_held()

            finally:
                self._reset_session()

    def read(self) -> ProtectedDurableRootState:
        with self.exclusive():
            return self._operation("read")

    def compare_and_set(
        self,
        *,
        expected,
        replacement,
    ) -> ProtectedRootReference:

        with self._lock:
            self._reject_transport_reentrancy()

            if self._held.session is not None:
                self._require_held()

            if type(expected) is not ProtectedRootReference:
                raise ValueError(
                    "Canonical CAS expected reference required."
                )

            self._validate_state(replacement)

            with self.exclusive():
                return self._operation(
                    "cas",
                    expected=expected,
                    replacement=replacement,
                )

    def provision(self, *, state):
        with self._lock:
            self._reject_transport_reentrancy()

            raise ValueError(
                "Authenticated anchor client cannot provision roots."
            )
