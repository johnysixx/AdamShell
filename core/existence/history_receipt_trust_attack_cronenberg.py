"""Experimental A44 security-attack Cronenberg boundary.

A recognized security rejection produces a Cronenberg in
the existing Universe after the rejected operation fails.

Only explicit SecurityAttackDetected exceptions, and
validation failures at the guarded manifest-bootstrap
entrypoint, are classified as suspicious security attempts.

Infrastructure failures are not intentionally classified
as attacks. Classification alone does not establish intent.

Existing unguarded APIs remain callable. This experimental
adapter is not a complete authorization boundary.
"""

from core.existence.history_receipt_trust_root_bootstrap import (
    bootstrap_signed_authority_key_catalog,
)


class SecurityAttackDetected(ValueError):
    """Explicit security violation marker for protected operations."""


_ALLOWED_OPERATIONS = frozenset({
    "signed_manifest_bootstrap",
    "authority_reply",
    "publication_fence",
    "receipt_signature",
    "security_validation",
})


def _has_backend_failure(error):
    """Distinguish recognizable backend failures from rejections."""

    seen = set()
    current = error

    for _ in range(16):
        if current is None or id(current) in seen:
            return False

        seen.add(id(current))

        if isinstance(
            current,
            (OSError, RuntimeError, TypeError, AttributeError),
        ):
            return True

        current = current.__cause__

    return False


class SecurityAttackCronenbergBoundary:
    """Report detected attacks through the existing Universe.

    The caller must provide a trusted Universe instance.
    Arbitrary caller-supplied objects are not an independent
    security boundary.

    Failure to publish a Cronenberg never makes a rejected
    security operation successful.
    """

    def __init__(self, universe):
        create = getattr(
            universe,
            "create_cronenberg_from_quantum_error",
            None,
        )

        if not callable(create):
            raise ValueError(
                "A Cronenberg-capable Universe is required."
            )

        self._universe = universe

    def _reject(self, error, source_operation):
        """Manifest one Cronenberg and preserve denial."""

        try:
            cronenberg = (
                self._universe
                .create_cronenberg_from_quantum_error(
                    error=RuntimeError(
                        "A44 blocked security attack."
                    ),
                    source_component=(
                        "history_receipt_trust_attack"
                    ),
                    source_operation=source_operation,
                )
            )

            if not getattr(cronenberg, "id", None):
                raise RuntimeError(
                    "Cronenberg manifestation incomplete."
                )

        except Exception as publication_error:
            raise ValueError(
                "Security operation rejected; "
                "Cronenberg publication failed."
            ) from publication_error

        raise SecurityAttackDetected(
            "Security attack rejected; "
            "Cronenberg manifested."
        ) from error

    def execute(self, operation, *, source_operation):
        """Run any explicitly instrumented security operation.

        An operation must raise SecurityAttackDetected to
        identify an attack. Ordinary operational failures
        are not converted into attack events.
        """

        if not callable(operation):
            raise ValueError(
                "A callable security operation is required."
            )

        if (
            type(source_operation) is not str
            or source_operation not in _ALLOWED_OPERATIONS
        ):
            raise ValueError(
                "Unsupported security operation identity."
            )

        try:
            return operation()

        except SecurityAttackDetected as attack:
            self._reject(
                attack,
                source_operation,
            )

    def bootstrap_manifest(
        self,
        message,
        signature,
        *,
        trusted_source,
    ):
        """Guard the existing signed-manifest bootstrap.

        Structural and cryptographic validation rejections
        are treated as suspicious attempts.

        This is a conservative classification, not proof
        of malicious intent. Backend errors with recognizable
        failure causes are propagated without manifestation.
        """

        try:
            return bootstrap_signed_authority_key_catalog(
                message,
                signature,
                trusted_source=trusted_source,
            )

        except ValueError as rejection:
            if _has_backend_failure(rejection):
                raise

            self._reject(
                rejection,
                "signed_manifest_bootstrap",
            )
