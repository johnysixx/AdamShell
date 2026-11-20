"""A44 checkpoint backend trust-bound held read gate.

Combines two injected held trust sources:

    Enrollment source:
        (backend_id, backend_public_key,
         root_id, root_public_key, enrollment_epoch)

    Revision-floor source:
        (root_id, root_public_key,
         enrollment_epoch, minimum_revision)

The gate verifies both snapshots and uses the existing
signed checkpoint backend source for authenticated-data
checking under a fresh challenge.

Both trust source leases remain active during the signed
backend read AND throughout caller verification.

SECURITY LIMITATIONS:

- Neither source is independently authenticated here.
- Both trust sources may be attacker-controlled.
- Two Python objects do not establish independent trust.
- Held snapshots do not prove durable monotonic storage.
- A valid signature cannot prove honest backend execution.
- No trusted enrollment mechanism is implemented here.
- No genuine restart or rollback resistance is established.
- No backend linearizability or cross-backend atomicity.
- No checkpoint restore or republication authorization.
- Frozen Python objects are not security boundaries.

This module is READ ONLY.
"""

import hmac

from contextlib import contextmanager
from dataclasses import dataclass

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)

from core.existence.history_receipt_trust_checkpoint_signed_backend_source import (
    SignedCheckpointRootFloorSource,
)


def _require_backend(backend):
    hold = getattr(
        backend,
        "hold",
        None,
    )

    advance = getattr(
        backend,
        "advance_if_current",
        None,
    )

    if not callable(hold) or not callable(advance):
        raise ValueError(
            "Checkpoint backend capabilities unavailable."
        )

    return backend


def _require_held_source(source, name):
    hold = getattr(
        source,
        "hold",
        None,
    )

    if not callable(hold):
        raise ValueError(
            f"Invalid {name}: held read unavailable."
        )

    return hold


def _require_public_key(value, name):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(
            f"Invalid {name}: expected 32 immutable bytes."
        )

    return bytes(value)


def _require_nonnegative_integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _require_enrollment(
    snapshot,
    *,
    expected_root_id,
):
    """Strictly validate an injected enrollment snapshot.

    No independent authentication of its origin occurs.
    """

    if type(snapshot) is not tuple or len(snapshot) != 5:
        raise ValueError(
            "Malformed checkpoint backend enrollment snapshot."
        )

    (
        backend_id,
        backend_public_key,
        root_id,
        root_public_key,
        epoch,
    ) = snapshot

    backend_id = _require_identity(
        backend_id,
        "enrolled checkpoint backend identity",
    )

    backend_public_key = _require_public_key(
        backend_public_key,
        "enrolled backend public key",
    )

    root_id = _require_identity(
        root_id,
        "enrolled checkpoint root identity",
    )

    if root_id != expected_root_id:
        raise ValueError(
            "Enrolled checkpoint root identity mismatch."
        )

    root_public_key = _require_public_key(
        root_public_key,
        "enrolled checkpoint root public key",
    )

    epoch = _require_nonnegative_integer(
        epoch,
        "backend enrollment epoch",
    )

    return (
        backend_id,
        backend_public_key,
        root_id,
        root_public_key,
        epoch,
    )


def _require_floor(
    snapshot,
    *,
    expected_root_id,
    expected_root_public_key,
    expected_epoch,
):
    """Validate a held revision-floor snapshot against enrollment."""

    if type(snapshot) is not tuple or len(snapshot) != 4:
        raise ValueError(
            "Malformed checkpoint backend revision-floor snapshot."
        )

    (
        root_id,
        root_public_key,
        epoch,
        minimum_revision,
    ) = snapshot

    root_id = _require_identity(
        root_id,
        "held revision-floor root identity",
    )

    root_public_key = _require_public_key(
        root_public_key,
        "held revision-floor root key",
    )

    epoch = _require_nonnegative_integer(
        epoch,
        "held revision-floor enrollment epoch",
    )

    minimum_revision = _require_nonnegative_integer(
        minimum_revision,
        "held minimum checkpoint revision",
    )

    if root_id != expected_root_id:
        raise ValueError(
            "Checkpoint enrollment/floor root identity mismatch."
        )

    if not hmac.compare_digest(
        root_public_key,
        expected_root_public_key,
    ):
        raise ValueError(
            "Checkpoint enrollment/floor root key mismatch."
        )

    if epoch != expected_epoch:
        raise ValueError(
            "Checkpoint enrollment/floor epoch mismatch."
        )

    return minimum_revision


@dataclass(frozen=True, slots=True)
class CheckpointBackendTrustHeldReadGate:
    """Read-only bridge from held trust snapshots to signed backend.

    Trust sources and backend are externally injected.
    Their honesty and durability are not established here.
    """

    backend: object
    enrollment_source: object
    revision_floor_source: object
    expected_root_id: str

    def __post_init__(self):
        _require_backend(
            self.backend
        )

        _require_held_source(
            self.enrollment_source,
            "backend enrollment source",
        )

        _require_held_source(
            self.revision_floor_source,
            "backend revision-floor source",
        )

        _require_identity(
            self.expected_root_id,
            "expected checkpoint root identity",
        )

    @classmethod
    def from_sources(
        cls,
        *,
        backend,
        enrollment_source,
        revision_floor_source,
        expected_root_id,
    ):
        try:
            return cls(
                backend=backend,
                enrollment_source=enrollment_source,
                revision_floor_source=revision_floor_source,
                expected_root_id=expected_root_id,
            )

        except Exception as exc:
            raise ValueError(
                "Checkpoint backend trust gate binding failed."
            ) from exc

    @contextmanager
    def hold(self):
        """Hold enrollment, floor and signed backend read together.

        The completion sentinel rejects providers that suppress
        ValueError raised by the caller or nested verifiers.

        Validation must finish before contacting the backend.
        The signed backend's lease stays active through yield.
        """

        caller_completed = False
        floor_released = False
        enrollment_released = False

        try:
            # Revalidate frozen fields at the use boundary.
            self.__post_init__()

            enrollment_hold = _require_held_source(
                self.enrollment_source,
                "backend enrollment source",
            )

            floor_hold = _require_held_source(
                self.revision_floor_source,
                "backend revision-floor source",
            )

            with enrollment_hold() as enrollment_snapshot:
                (
                    backend_id,
                    backend_public_key,
                    root_id,
                    root_public_key,
                    enrollment_epoch,
                ) = _require_enrollment(
                    enrollment_snapshot,
                    expected_root_id=self.expected_root_id,
                )

                with floor_hold() as floor_snapshot:
                    minimum_revision = _require_floor(
                        floor_snapshot,
                        expected_root_id=root_id,
                        expected_root_public_key=root_public_key,
                        expected_epoch=enrollment_epoch,
                    )

                    signed_source = (
                        SignedCheckpointRootFloorSource.from_backend(
                            backend=self.backend,
                            expected_backend_id=backend_id,
                            expected_backend_public_key=(
                                backend_public_key
                            ),
                            expected_root_id=root_id,
                            expected_root_public_key=(
                                root_public_key
                            ),
                            minimum_revision=minimum_revision,
                        )
                    )

                    with signed_source.hold() as snapshot:
                        if (
                            type(snapshot) is not tuple
                            or len(snapshot) != 3
                        ):
                            raise ValueError(
                                "Invalid signed backend root snapshot."
                            )

                        (
                            signed_root_id,
                            signed_root_key,
                            signed_revision,
                        ) = snapshot

                        if signed_root_id != root_id:
                            raise ValueError(
                                "Signed backend root identity mismatch."
                            )

                        if (
                            type(signed_root_key) is not bytes
                            or not hmac.compare_digest(
                                signed_root_key,
                                root_public_key,
                            )
                        ):
                            raise ValueError(
                                "Signed backend root key mismatch."
                            )

                        if (
                            type(signed_revision) is not int
                            or signed_revision < minimum_revision
                        ):
                            raise ValueError(
                                "Signed backend revision below held floor."
                            )

                        yield (
                            root_id,
                            bytes(root_public_key),
                            signed_revision,
                        )

                        caller_completed = True

                floor_released = True

            enrollment_released = True

            # This check is deliberately OUTSIDE both
            # untrusted source context managers.
            if not (
                caller_completed
                and floor_released
                and enrollment_released
            ):
                raise ValueError(
                    "Checkpoint trust gate did not complete "
                    "all held verification scopes."
                )

        except Exception as exc:
            raise ValueError(
                "Checkpoint trust-bound signed read failed."
            ) from exc
