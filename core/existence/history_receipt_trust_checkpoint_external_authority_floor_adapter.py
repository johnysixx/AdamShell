"""A44 signed external authority held revision-floor adapter.

Projects the canonical signed authority client's six-field
held snapshot into the existing checkpoint trust gate's
four-field revision-floor contract.

Source snapshot:

    (root_id, root_public_key, enrollment_epoch,
     revision, generation, fence_token)

Projected snapshot:

    (root_id, root_public_key, enrollment_epoch,
     minimum_revision)

The signed source context remains active during the entire
caller verification scope. All fields are validated before
projection, including the counters omitted from the output.

SECURITY BOUNDARY:

- This adapter validates an exact canonical source object.
- Key pins and minima remain caller supplied.
- It does not independently enroll an authority.
- It does not create or authenticate an external service.
- Context lifetime does not prove a genuine remote lease.
- There is no persistent independent monotonic state.
- Authority rollback remains possible with stale minima.
- A malicious valid signer can produce false claims.
- Python object checks are not an in-process security boundary.
- No cross-system atomicity is established.
- No checkpoint restoration or republication is authorized.

This adapter is READ ONLY.
"""

import hmac

from contextlib import contextmanager
from dataclasses import dataclass

from core.existence.history_receipt_trust_checkpoint_external_monotonic_authority import (
    SignedCheckpointExternalMonotonicAuthoritySource,
)

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)


def _require_canonical_source(source):
    """Reject unsigned providers and overriding subclasses."""

    if type(source) is not (
        SignedCheckpointExternalMonotonicAuthoritySource
    ):
        raise ValueError(
            "Expected canonical signed external authority source."
        )

    source.__post_init__()

    return source


def _require_counter(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _validated_floor(snapshot, *, source):
    """Validate all six source fields before projection."""

    source = _require_canonical_source(
        source
    )

    if type(snapshot) is not tuple or len(snapshot) != 6:
        raise ValueError(
            "Malformed signed external authority snapshot."
        )

    (
        root_id,
        root_public_key,
        epoch,
        revision,
        generation,
        fence_token,
    ) = snapshot

    root_id = _require_identity(
        root_id,
        "signed authority floor root identity",
    )

    if root_id != source.expected_root_id:
        raise ValueError(
            "Signed authority floor root identity mismatch."
        )

    if (
        type(root_public_key) is not bytes
        or len(root_public_key) != 32
    ):
        raise ValueError(
            "Invalid signed authority floor root key."
        )

    if not hmac.compare_digest(
        root_public_key,
        source.expected_root_public_key,
    ):
        raise ValueError(
            "Signed authority floor root key mismatch."
        )

    epoch = _require_counter(
        epoch,
        "authority floor enrollment epoch",
    )

    revision = _require_counter(
        revision,
        "authority floor revision",
    )

    generation = _require_counter(
        generation,
        "authority floor generation",
    )

    fence_token = _require_counter(
        fence_token,
        "authority floor fencing token",
    )

    if epoch != source.expected_enrollment_epoch:
        raise ValueError(
            "Signed authority floor enrollment epoch mismatch."
        )

    if revision < source.minimum_revision:
        raise ValueError(
            "Signed authority floor revision below minimum."
        )

    if generation < source.minimum_generation:
        raise ValueError(
            "Signed authority floor generation below minimum."
        )

    if fence_token < source.minimum_fence_token:
        raise ValueError(
            "Signed authority floor fencing token below minimum."
        )

    return (
        root_id,
        bytes(root_public_key),
        epoch,
        revision,
    )


@dataclass(frozen=True, slots=True)
class ExternalMonotonicAuthorityFloorAdapter:
    """Read-only held projection of a canonical signed source."""

    source: SignedCheckpointExternalMonotonicAuthoritySource

    def __post_init__(self):
        _require_canonical_source(
            self.source
        )

    @classmethod
    def from_source(cls, *, source):
        """Bind an exact signed external authority source."""

        try:
            return cls(
                source=source
            )

        except Exception as exc:
            raise ValueError(
                "External authority floor adapter binding failed."
            ) from exc

    @contextmanager
    def hold(self):
        """Retain the signed source context through caller use.

        Each operation obtains a fresh signed read. No cached
        snapshot, unsigned fallback or publication is allowed.

        The completion sentinel is evaluated outside the
        enclosing source context to reject error suppression.
        """

        caller_completed = False

        try:
            source = _require_canonical_source(
                self.source
            )

            with source.hold() as snapshot:
                floor = _validated_floor(
                    snapshot,
                    source=source,
                )

                yield floor

                caller_completed = True

            if not caller_completed:
                raise ValueError(
                    "External authority floor hold "
                    "did not complete safely."
                )

        except Exception as exc:
            raise ValueError(
                "Held external authority floor read failed."
            ) from exc
