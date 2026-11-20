"""A44 signed checkpoint root-floor backend source.

Bridges the checkpoint rotation coordinator to externally
supplied signed backend read and CAS responses.

Public operations:

    hold() -> signed, validated root snapshot under lease

    advance(expected_revision, next_revision) ->
        signed CAS evidence verification followed by a
        separately challenged signed readback

Security boundary:

- Ed25519 verification is relative to caller-supplied pins.
- A cryptographically signed backend assertion does not
  establish that the backend genuinely executed its claim.
- The backend itself is not independently authenticated here.
- Signed readback is not durable storage evidence.
- No persistent, independent monotonic revision is stored.
- No rollback-resistant storage is established.
- No cross-backend atomicity is established.
- The source does not authorize restoration or republication.
- Python objects are not an in-process security boundary.

A failure may occur AFTER the backend has committed.
Never infer rollback or automatically retry a failed CAS.
"""

import os

from contextlib import contextmanager
from dataclasses import dataclass

from core.existence.history_receipt_trust_checkpoint_backend_evidence import (
    CheckpointRootBackendEvidenceVerifier,
    VerifiedCheckpointRootBackendEvidence,
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
            "Signed checkpoint backend operations unavailable."
        )

    return hold, advance


def _require_revision(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(
            f"Invalid {name}."
        )

    return value


def _require_signed_pair(value):
    if type(value) is not tuple or len(value) != 2:
        raise ValueError(
            "Malformed signed checkpoint backend response."
        )

    message, signature = value

    if (
        type(message) is not bytes
        or not message
        or len(message) > 4096
        or type(signature) is not bytes
        or len(signature) != 64
    ):
        raise ValueError(
            "Invalid signed checkpoint backend response."
        )

    return bytes(message), bytes(signature)


def _new_challenge(*, different_from=None):
    """Request a fresh cryptographic challenge.

    A CAS readback must have a challenge different from
    the CAS acknowledgement. An unusable randomness source
    fails closed rather than accepting a repeated challenge.
    """

    for _ in range(8):
        candidate = os.urandom(32)

        if (
            type(candidate) is bytes
            and len(candidate) == 32
            and candidate != different_from
        ):
            return candidate

    raise ValueError(
        "Fresh checkpoint backend challenge unavailable."
    )


def _require_verified(
    report,
    *,
    verifier,
    operation,
    challenge,
    revision,
):
    """Check verifier result shape and intended signed binding.

    Report objects are data containers, not authority tokens.
    Cryptographic verification is performed by the verifier.
    """

    if (
        type(report) is not VerifiedCheckpointRootBackendEvidence
        or report.signature_verified is not True
        or report.is_independently_trusted is not False
        or report.is_authoritative is not False
        or report.is_durable is not False
        or report.is_restorable is not False
        or report.can_republish is not False
        or report.operation != operation
        or report.backend_id
        != verifier.expected_backend_id
        or report.backend_public_key
        != verifier.expected_backend_public_key
        or report.root_id != verifier.expected_root_id
        or report.root_public_key
        != verifier.expected_root_public_key
        or report.challenge != challenge
        or type(report.revision) is not int
        or report.revision != revision
    ):
        raise ValueError(
            "Invalid signed checkpoint backend verification result."
        )

    return report


@dataclass(frozen=True, slots=True)
class SignedCheckpointRootFloorSource:
    """Signed source compatible with checkpoint rotation.

    All storage and signing operations belong to an
    injected external backend. This class only validates
    their responses and controls the operation sequence.
    """

    backend: object
    verifier: CheckpointRootBackendEvidenceVerifier
    minimum_revision: int

    def __post_init__(self):
        _require_backend(self.backend)

        if (
            type(self.verifier)
            is not CheckpointRootBackendEvidenceVerifier
        ):
            raise ValueError(
                "Invalid checkpoint backend evidence verifier."
            )

        self.verifier.__post_init__()

        _require_revision(
            self.minimum_revision,
            "minimum signed checkpoint revision",
        )

    @classmethod
    def from_backend(
        cls,
        *,
        backend,
        expected_backend_id,
        expected_backend_public_key,
        expected_root_id,
        expected_root_public_key,
        minimum_revision,
    ):
        try:
            _require_backend(backend)

            minimum = _require_revision(
                minimum_revision,
                "minimum checkpoint revision",
            )

            verifier = (
                CheckpointRootBackendEvidenceVerifier.from_pinned_key(
                    expected_backend_id=expected_backend_id,
                    expected_backend_public_key=(
                        expected_backend_public_key
                    ),
                    expected_root_id=expected_root_id,
                    expected_root_public_key=(
                        expected_root_public_key
                    ),
                )
            )

            return cls(
                backend=backend,
                verifier=verifier,
                minimum_revision=minimum,
            )

        except Exception as exc:
            raise ValueError(
                "Signed checkpoint backend source binding failed."
            ) from exc

    @contextmanager
    def _signed_hold(self, *, different_from=None):
        """Keep the backend read lease through caller verification.

        Completion markers detect providers that suppress
        ValueError raised inside their context manager.
        """

        body_completed = False
        backend_released = False

        try:
            self.__post_init__()

            challenge = _new_challenge(
                different_from=different_from,
            )

            backend_hold, _ = _require_backend(
                self.backend
            )

            with backend_hold(challenge=challenge) as response:
                message, signature = _require_signed_pair(
                    response
                )

                report = self.verifier.verify_read(
                    message=message,
                    signature=signature,
                    expected_challenge=challenge,
                    minimum_revision=self.minimum_revision,
                )

                if (
                    type(report.revision) is not int
                    or report.revision < self.minimum_revision
                ):
                    raise ValueError(
                        "Signed read is below the required floor."
                    )

                _require_verified(
                    report,
                    verifier=self.verifier,
                    operation="read",
                    challenge=challenge,
                    revision=report.revision,
                )

                if (
                    report.expected_revision is not None
                    or report.next_revision is not None
                ):
                    raise ValueError(
                        "Signed read contains CAS-only fields."
                    )

                snapshot = (
                    self.verifier.expected_root_id,
                    self.verifier.expected_root_public_key,
                    report.revision,
                )

                yield snapshot

                body_completed = True

            backend_released = True

            if not (
                body_completed
                and backend_released
            ):
                raise ValueError(
                    "Signed checkpoint backend lease "
                    "did not complete."
                )

        except Exception as exc:
            raise ValueError(
                "Signed checkpoint backend held read failed."
            ) from exc

    @contextmanager
    def hold(self):
        """Provide a verified root snapshot under a read lease."""

        with self._signed_hold() as snapshot:
            yield snapshot

    def advance(
        self,
        *,
        expected_revision,
        next_revision,
    ):
        """Verify a signed CAS response and fresh signed readback.

        A signed acknowledgement is never accepted alone.
        A backend may have committed before any later failure.
        """

        try:
            self.__post_init__()

            previous = _require_revision(
                expected_revision,
                "expected CAS predecessor",
            )

            target = _require_revision(
                next_revision,
                "next CAS revision",
            )

            if previous < self.minimum_revision:
                raise ValueError(
                    "CAS predecessor is below the minimum floor."
                )

            if target <= previous:
                raise ValueError(
                    "CAS target must advance the revision."
                )

            _, backend_advance = _require_backend(
                self.backend
            )

            cas_challenge = _new_challenge()

            response = backend_advance(
                expected_revision=previous,
                next_revision=target,
                challenge=cas_challenge,
            )

            message, signature = _require_signed_pair(
                response
            )

            report = self.verifier.verify_cas(
                message=message,
                signature=signature,
                expected_challenge=cas_challenge,
                expected_revision=previous,
                next_revision=target,
            )

            _require_verified(
                report,
                verifier=self.verifier,
                operation="cas",
                challenge=cas_challenge,
                revision=target,
            )

            if (
                type(report.expected_revision) is not int
                or report.expected_revision != previous
                or type(report.next_revision) is not int
                or report.next_revision != target
            ):
                raise ValueError(
                    "Signed CAS verification result mismatch."
                )

            # Never return based solely on a signed CAS reply.
            # Obtain a DIFFERENT challenge and verify a new
            # signed read from the externally supplied backend.
            with self._signed_hold(
                different_from=cas_challenge,
            ) as snapshot:

                if snapshot[2] != target:
                    raise ValueError(
                        "Post-CAS signed readback revision mismatch."
                    )

            return snapshot

        except Exception as exc:
            # The backend might already have committed.
            # No automatic retry or rollback is safe here.
            raise ValueError(
                "Signed checkpoint backend CAS failed; "
                "inspect state before retry."
            ) from exc
