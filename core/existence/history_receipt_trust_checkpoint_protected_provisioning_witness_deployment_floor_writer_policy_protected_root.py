"""Protected writer policy root objects and backend abstraction.

The in-memory backend is a reference trust model only.

It is not process-durable, hardware-backed, remotely authenticated,
or resistant to arbitrary modification by trusted Python code.

All cooperating authorities must use the same protected backend.

The authority authenticates signed policy history and validates
writer authorization. The root backend enforces canonical state,
monotonic revisions, exact expected references, structural
transitions and a shared exclusive authorization fence.
"""

import hashlib
import json
import threading

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_durable_high_water
    as durable,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy
    as versioned,
)


_STATE_DOMAIN = "a44-protected-durable-root-state-v1"


@dataclass(frozen=True, slots=True, kw_only=True)
class ProtectedDeploymentIdentity:

    deployment_id: str
    configuration_sha256: str
    provisioning_nonce: bytes

    def __post_init__(self):

        durable.persistent.high_water._identity(
            self.deployment_id,
            "protected deployment identity",
        )

        versioned._require_digest(
            self.configuration_sha256,
            "protected deployment configuration",
        )

        if (
            type(self.provisioning_nonce) is not bytes
            or len(self.provisioning_nonce) != 32
        ):
            raise ValueError(
                "Expected immutable 32-byte provisioning nonce."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class ProtectedRootReference:

    revision: int
    sha256: str

    def __post_init__(self):

        versioned._require_epoch(
            self.revision,
            "protected root revision",
        )

        versioned._require_digest(
            self.sha256,
            "protected root digest",
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ProtectedDurableRootState:

    identity: ProtectedDeploymentIdentity
    revision: int
    durable_state: durable.DurablePolicyHighWaterState

    def __post_init__(self):

        if type(self.identity) is not ProtectedDeploymentIdentity:
            raise ValueError(
                "Expected canonical deployment identity."
            )

        versioned._require_epoch(
            self.revision,
            "protected root revision",
        )

        if (
            type(self.durable_state)
            is not durable.DurablePolicyHighWaterState
        ):
            raise ValueError(
                "Expected canonical durable policy state."
            )

    def reference(self):

        identity = self.identity
        state = self.durable_state
        prepared = state.prepared

        if prepared is None:
            pending = None
        else:
            message, signature = prepared.signed_policy

            pending = [
                prepared.predecessor.epoch,
                prepared.predecessor.sha256,
                prepared.candidate.epoch,
                prepared.candidate.sha256,
                message.hex(),
                signature.hex(),
            ]

        # Serialization is restricted to the commitment boundary.

        payload = [
            _STATE_DOMAIN,
            identity.deployment_id,
            identity.configuration_sha256,
            identity.provisioning_nonce.hex(),
            self.revision,
            state.anchor.epoch,
            state.anchor.sha256,
            pending,
        ]

        encoded = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return ProtectedRootReference(
            revision=self.revision,
            sha256=hashlib.sha256(encoded).hexdigest(),
        )


class ProtectedRootBackend(ABC):

    """Trusted root interface.

    Implementations must serialize provision and compare-and-set
    operations through the same exclusive fence.

    The fence must support nested backend operations performed
    by its current holder.

    Committed transitions must not be reverted merely because
    an enclosing authority operation raises an exception.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def identity(self):
        """Externally provisioned deployment identity."""
        raise NotImplementedError

    @abstractmethod
    def provision(self, *, state):
        """Initialize an explicitly unprovisioned root once."""
        raise NotImplementedError

    @abstractmethod
    def read(self):
        """Return the current canonical protected state."""
        raise NotImplementedError

    @abstractmethod
    def compare_and_set(self, *, expected, replacement):
        """Atomically commit the next canonical root revision."""
        raise NotImplementedError

    @abstractmethod
    def exclusive(self):
        """Hold the shared authorization fence."""
        raise NotImplementedError


def _validate_transition(previous, replacement):

    if type(replacement) is not ProtectedDurableRootState:
        raise ValueError(
            "Expected canonical replacement root state."
        )

    if replacement.identity != previous.identity:
        raise ValueError(
            "Protected deployment identity cannot change."
        )

    if replacement.revision != previous.revision + 1:
        raise ValueError(
            "Protected revision must advance exactly once."
        )

    old = previous.durable_state
    new = replacement.durable_state

    if old == new:
        raise ValueError(
            "No-op protected state transition."
        )

    if old.prepared is not None:

        if new.prepared is not None:
            raise ValueError(
                "Prepared publication replacement forbidden."
            )

        if new.anchor != old.prepared.candidate:
            raise ValueError(
                "Finalize the exact prepared candidate."
            )

        return

    if new.prepared is not None:

        if new.anchor != old.anchor:
            raise ValueError(
                "Preparation cannot advance the stable anchor."
            )

        return

    # Stable-to-stable observation.
    # Authenticated lineage verification belongs to the authority.

    if new.anchor.epoch <= old.anchor.epoch:
        raise ValueError(
            "Protected anchor rollback or same-epoch fork."
        )


@dataclass(
    frozen=True,
    slots=True,
    init=False,
    eq=False,
)
class InMemoryProtectedRootBackend(ProtectedRootBackend):

    """Single-process reference protected root."""

    _identity: ProtectedDeploymentIdentity
    _lock: object = field(repr=False)
    _state: ProtectedDurableRootState | None = field(repr=False)

    def __init__(self, *, identity):

        if hasattr(self, "_identity"):
            raise ValueError(
                "Protected backend cannot be reinitialized."
            )

        if type(identity) is not ProtectedDeploymentIdentity:
            raise ValueError(
                "Expected canonical protected identity."
            )

        object.__setattr__(self, "_lock", threading.RLock())
        object.__setattr__(self, "_state", None)
        object.__setattr__(self, "_identity", identity)

    @property
    def identity(self):
        return self._identity

    @contextmanager
    def exclusive(self):

        with self._lock:
            yield

    def provision(self, *, state):

        with self.exclusive():

            if self._state is not None:
                raise ValueError(
                    "Protected root already provisioned."
                )

            if type(state) is not ProtectedDurableRootState:
                raise ValueError(
                    "Expected canonical provisioning state."
                )

            if state.identity != self._identity:
                raise ValueError(
                    "Protected provisioning identity mismatch."
                )

            if (
                state.revision != 1
                or state.durable_state.prepared is not None
            ):
                raise ValueError(
                    "Provisioning requires initial stable state."
                )

            reference = state.reference()

            object.__setattr__(
                self,
                "_state",
                state,
            )

            return reference

    def read(self):

        with self.exclusive():

            if self._state is None:
                raise ValueError(
                    "Protected root is not provisioned."
                )

            return self._state

    def compare_and_set(self, *, expected, replacement):

        with self.exclusive():

            previous = self.read()

            if type(expected) is not ProtectedRootReference:
                raise ValueError(
                    "Expected canonical protected root reference."
                )

            if expected != previous.reference():
                raise ValueError(
                    "Stale or conflicting protected root reference."
                )

            _validate_transition(
                previous,
                replacement,
            )

            reference = replacement.reference()

            object.__setattr__(
                self,
                "_state",
                replacement,
            )

            return reference

    def __copy__(self):
        raise TypeError("Protected backend cannot be copied.")

    def __deepcopy__(self, memo):
        raise TypeError("Protected backend cannot be deep-copied.")

    def __reduce_ex__(self, protocol):
        raise TypeError("Protected backend cannot be serialized.")
