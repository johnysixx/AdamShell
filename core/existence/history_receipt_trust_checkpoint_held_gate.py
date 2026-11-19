"""A44 held checkpoint trust verification boundary.

A caller-supplied source exposes hold(), a context manager
yielding (authority_id, raw_public_key, minimum_generation).

The public key and generation floor must be obtained from
the SAME held snapshot. Signature verification must finish
before that trust lease is released.

This adapter cannot independently authenticate the source,
guarantee durable monotonic generations, or establish a
trust root. It does not authorize Universe restoration,
entity creation or republication.
"""

from core.existence.history_receipt_trust_checkpoint_attestation import (
    PinnedCronenbergCheckpointAttestationVerifier,
    VerifiedCronenbergCheckpointAttestation,
)

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)

from core.existence.history_receipt_trust_incident_outbox import (
    _require_incident_id,
)

from core.existence.history_receipt_trust_publication_witness import (
    _require_universe_id,
)


def _validated_held_snapshot(
    snapshot,
    *,
    expected_authority_id,
):
    """Validate one held snapshot, not its external provenance."""

    if type(snapshot) is not tuple or len(snapshot) != 3:
        raise ValueError(
            "Invalid held checkpoint trust snapshot."
        )

    authority_id, public_key, generation_floor = snapshot

    _require_identity(
        authority_id,
        "held checkpoint authority",
    )

    if authority_id != expected_authority_id:
        raise ValueError(
            "Held checkpoint authority identity mismatch."
        )

    if type(public_key) is not bytes or len(public_key) != 32:
        raise ValueError(
            "Held checkpoint public key must be 32 immutable bytes."
        )

    if (
        type(generation_floor) is not int
        or generation_floor < 0
    ):
        raise ValueError(
            "Invalid held checkpoint generation floor."
        )

    return (
        authority_id,
        bytes(public_key),
        generation_floor,
    )


def verify_checkpoint_attestation_with_held_trust(
    *,
    evidence,
    checkpoint,
    message,
    signature,
    trusted_source,
    expected_authority_id,
    expected_universe_id,
    expected_incident_id,
):
    """Verify signed checkpoint bytes under one held trust snapshot.

    The result only confirms consistency of the supplied signed
    bytes and checkpoint under the selected public-key pin.
    """

    try:
        _require_identity(
            expected_authority_id,
            "expected checkpoint authority",
        )

        _require_universe_id(
            expected_universe_id
        )

        _require_incident_id(
            expected_incident_id
        )

        hold = getattr(
            trusted_source,
            "hold",
            None,
        )

        if not callable(hold):
            raise ValueError(
                "Held checkpoint trust source unavailable."
            )

        # A suppressed exception must never produce implicit success.
        verified_result = None

        with hold() as witness:
            (
                authority_id,
                public_key,
                minimum_generation,
            ) = _validated_held_snapshot(
                witness,
                expected_authority_id=expected_authority_id,
            )

            verifier = (
                PinnedCronenbergCheckpointAttestationVerifier
                .from_pinned_keys({
                    authority_id: public_key,
                })
            )

            result = verifier.verify(
                evidence=evidence,
                checkpoint=checkpoint,
                message=message,
                signature=signature,
                expected_authority_id=expected_authority_id,
                expected_universe_id=expected_universe_id,
                expected_incident_id=expected_incident_id,
                minimum_generation=minimum_generation,
            )

            if (
                type(result)
                is not VerifiedCronenbergCheckpointAttestation
                or result.signature_verified is not True
                or result.is_authoritative is not False
                or result.is_restorable is not False
                or result.can_republish is not False
            ):
                raise ValueError(
                    "Invalid non-authoritative checkpoint result."
                )

            # Only a fully validated result may survive the lease.
            verified_result = result

        # A provider can suppress an exception raised inside the
        # context body. Without this check, the function could
        # implicitly return None after the suppressed failure.
        if (
            type(verified_result)
            is not VerifiedCronenbergCheckpointAttestation
            or verified_result.signature_verified is not True
            or verified_result.is_authoritative is not False
            or verified_result.is_restorable is not False
            or verified_result.can_republish is not False
        ):
            raise ValueError(
                "Incomplete held checkpoint trust verification."
            )

        # The held context and its __exit__ have completed.
        return verified_result

    except Exception as exc:
        raise ValueError(
            "Held checkpoint trust verification failed."
        ) from exc
