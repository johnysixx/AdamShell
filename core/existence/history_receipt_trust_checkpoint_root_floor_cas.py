"""A44 external checkpoint root-floor CAS adapter.

Backend contract:

    backend.hold() ->
        (root_id, raw_root_public_key, minimum_witness_revision)

    backend.advance_if_current(
        expected_revision=int,
        next_revision=int,
    ) -> resulting root snapshot

The adapter validates a caller-supplied root identity
and immutable Ed25519 public key, then delegates
revision publication to the backend.

SECURITY LIMITATIONS:

- A caller-supplied root pin is not independently enrolled.
- Backend hold() must provide a consistent read lease.
- Backend advance_if_current() must perform genuine
  atomic compare-and-swap publication.
- The adapter cannot prove backend linearizability.
- It cannot prove persistent rollback resistance.
- A successful backend reply is not proof of durability.
- A backend can commit and then fail to reply; the caller
  must reconcile uncertain publication outcomes.
- Malicious Python code in the same process is not isolated.
- No checkpoint restoration or republication is authorized.
"""

import hmac

from contextlib import contextmanager
from dataclasses import dataclass

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)


def _require_backend(backend):
    """Validate backend interfaces, not their provenance."""

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
            "External root-floor CAS backend unavailable."
        )

    return hold, advance


def _require_pinned_root(root_id, public_key):
    _require_identity(
        root_id,
        "expected checkpoint root identity",
    )

    if (
        type(public_key) is not bytes
        or len(public_key) != 32
    ):
        raise ValueError(
            "Expected root Ed25519 public key must be "
            "exactly 32 immutable bytes."
        )

    return root_id, bytes(public_key)


def _require_revision(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _validated_snapshot(
    snapshot,
    *,
    expected_root_id,
    expected_root_public_key,
):
    """Validate exact root pin and exclusive revision floor.

    The caller-selected pin does not establish an
    independent trust root.
    """

    if type(snapshot) is not tuple or len(snapshot) != 3:
        raise ValueError(
            "Invalid external root-floor snapshot."
        )

    root_id, public_key, revision = snapshot

    _require_identity(
        root_id,
        "held checkpoint root identity",
    )

    if root_id != expected_root_id:
        raise ValueError(
            "External checkpoint root identity mismatch."
        )

    if (
        type(public_key) is not bytes
        or len(public_key) != 32
    ):
        raise ValueError(
            "Malformed external root public key."
        )

    if not hmac.compare_digest(
        public_key,
        expected_root_public_key,
    ):
        raise ValueError(
            "External root public key differs from supplied pin."
        )

    _require_revision(
        revision,
        "held checkpoint witness revision",
    )

    return (
        root_id,
        bytes(public_key),
        revision,
    )


@dataclass(frozen=True, slots=True)
class ExternalCheckpointRootFloorAdapter:
    """Validate externally held root and monotonic-floor data.

    This object is an adapter, not an authenticated store.
    Frozen Python fields provide no security isolation.
    """

    backend: object
    expected_root_id: str
    expected_root_public_key: bytes

    @classmethod
    def from_backend(
        cls,
        *,
        backend,
        expected_root_id,
        expected_root_public_key,
    ):
        try:
            root_id, public_key = _require_pinned_root(
                expected_root_id,
                expected_root_public_key,
            )

            _require_backend(backend)

            return cls(
                backend=backend,
                expected_root_id=root_id,
                expected_root_public_key=public_key,
            )

        except Exception as exc:
            raise ValueError(
                "External checkpoint root-floor binding failed."
            ) from exc

    @contextmanager
    def hold(self):
        """Hold a root snapshot through caller verification.

        A completion sentinel protects against providers
        that suppress a ValueError thrown into their context.

        The final check executes outside the provider lease.
        """

        body_completed = False
        backend_released = False

        try:
            root_id, public_key = _require_pinned_root(
                self.expected_root_id,
                self.expected_root_public_key,
            )

            backend_hold, _ = _require_backend(
                self.backend
            )

            with backend_hold() as snapshot:
                validated = _validated_snapshot(
                    snapshot,
                    expected_root_id=root_id,
                    expected_root_public_key=public_key,
                )

                # The external root lease remains active
                # while the caller verifies the witness
                # and the checkpoint attestation.
                yield validated

                body_completed = True

            # Reached only after normal lease teardown.
            backend_released = True

            # A provider cannot suppress this check.
            if not (
                body_completed
                and backend_released
            ):
                raise ValueError(
                    "External root-floor hold did not complete."
                )

        except Exception as exc:
            raise ValueError(
                "External checkpoint root-floor lease failed."
            ) from exc

    def advance(
        self,
        *,
        expected_revision,
        next_revision,
    ):
        """Request a backend CAS revision advancement.

        expected_revision must equal the backend state.
        next_revision must be strictly greater.

        Actual atomicity and durability belong to the
        external backend, not this Python adapter.

        Do not retry blindly after an uncertain backend
        failure; re-read trusted backend state first.
        """

        try:
            root_id, public_key = _require_pinned_root(
                self.expected_root_id,
                self.expected_root_public_key,
            )

            previous = _require_revision(
                expected_revision,
                "expected checkpoint witness revision",
            )

            target = _require_revision(
                next_revision,
                "next checkpoint witness revision",
            )

            if target <= previous:
                raise ValueError(
                    "Checkpoint witness revision must increase."
                )

            _, backend_advance = _require_backend(
                self.backend
            )

            # A real backend must implement this as
            # one linearizable compare-and-swap operation.
            published_snapshot = backend_advance(
                expected_revision=previous,
                next_revision=target,
            )

            validated = _validated_snapshot(
                published_snapshot,
                expected_root_id=root_id,
                expected_root_public_key=public_key,
            )

            if validated[2] != target:
                raise ValueError(
                    "External CAS returned unexpected revision."
                )

            return validated

        except Exception as exc:
            # A failure may occur after the backend has
            # committed. Report failure; never infer rollback.
            raise ValueError(
                "External checkpoint root-floor CAS failed."
            ) from exc
