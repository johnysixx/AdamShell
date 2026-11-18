"""Experimental authority trust-root bootstrap adapter.

A trusted_source must expose hold(), a context manager
that yields one stable tuple:

    (trusted_root_id, trusted_root_public_key, minimum_epoch)

The context must remain held throughout signed-manifest
verification. Its implementation must independently
provide the necessary trust guarantees.

IMPORTANT SECURITY LIMITATIONS:

- This adapter cannot authenticate a caller-supplied source.
- A lock does not prove independent trust or durability.
- A local snapshot is not automatically rollback-resistant.
- A malicious in-process caller can construct Python objects.
- This module does not authorize receipt publication.
- This module does not provision private signing keys.

Production deployment requires a genuinely independent
authenticated root and protected monotonic epoch source.
"""

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)

from core.existence.history_receipt_trust_key_provisioning import (
    VerifiedAuthorityKeyCatalog,
)


def _validated_root_snapshot(witness):
    """Validate one exact externally supplied trust snapshot.

    Validation protects the API against malformed inputs.
    It does not establish the independent trustworthiness
    or freshness of the provider itself.
    """

    if (
        type(witness) is not tuple
        or len(witness) != 3
    ):
        raise ValueError(
            "Invalid trusted root snapshot."
        )

    root_id, raw_public_key, minimum_epoch = witness

    _require_identity(
        root_id,
        "trusted root identity",
    )

    if (
        type(raw_public_key) is not bytes
        or len(raw_public_key) != 32
    ):
        raise ValueError(
            "Trusted root public key must be "
            "exactly 32 immutable bytes."
        )

    if (
        type(minimum_epoch) is not int
        or minimum_epoch < 0
    ):
        raise ValueError(
            "Invalid trusted minimum epoch."
        )

    return (
        root_id,
        raw_public_key,
        minimum_epoch,
    )


def bootstrap_signed_authority_key_catalog(
    message,
    signature,
    *,
    trusted_source,
):
    """Verify a signed key manifest under a held trust lease.

    1. Require a callable trusted_source.hold().
    2. Enter the trust source's context.
    3. Validate the root identity, key and epoch snapshot.
    4. Verify the signed manifest while the lease is held.
    5. Release the context before returning the catalog.

    Any ordinary backend, validation or signature error
    fails closed with ValueError.

    A caller-controlled source can still impersonate a
    trusted source. This function must not be treated
    as proof of independent root enrollment or protected
    monotonic state.
    """

    try:
        hold = getattr(
            trusted_source,
            "hold",
            None,
        )

        if not callable(hold):
            raise ValueError(
                "Trusted root source is unavailable."
            )

        with hold() as witness:
            (
                root_id,
                root_public_key,
                minimum_epoch,
            ) = _validated_root_snapshot(witness)

            # The trust-source context is intentionally
            # still held throughout signature verification.
            #
            # The verified catalog does not itself carry
            # protected provenance from the trust source.
            catalog = (
                VerifiedAuthorityKeyCatalog
                .from_signed_manifest(
                    message,
                    signature,
                    trusted_root_id=root_id,
                    trusted_root_public_key=root_public_key,
                    minimum_epoch=minimum_epoch,
                )
            )

            return catalog

    except Exception as exc:
        # Fail closed on unavailable context managers,
        # malformed snapshots, backend exceptions,
        # invalid signatures and stale epochs.
        #
        # Do not mistake this generic exception mapping
        # for sufficient operational observability.
        raise ValueError(
            "Trusted root bootstrap verification failed."
        ) from exc
