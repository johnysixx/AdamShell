"""Experimental split checkpoint trust source binding.

Composes two externally supplied held sources:

    key_source.hold() ->
        (authority_id, raw_ed25519_public_key)

    generation_source.hold() ->
        (authority_id, minimum_generation)

Both leases remain active while the caller uses the
combined snapshot.

The snapshot is compatible with the existing
verify_checkpoint_attestation_with_held_trust API.

SECURITY LIMITATIONS:

- This adapter cannot authenticate the supplied providers.
- It does not independently enroll authority public keys.
- It cannot guarantee persistent monotonic generations.
- Separate provider leases do not prove an atomic or
  linearizable cross-provider publication transaction.
- In-process Python objects do not provide isolation
  against malicious code running in the same process.
- No checkpoint restoration or republication is authorized.
"""

from contextlib import contextmanager
from dataclasses import dataclass

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)


def _require_held_source(source, name):
    """Require an available context-manager factory."""

    hold = getattr(
        source,
        "hold",
        None,
    )

    if not callable(hold):
        raise ValueError(
            f"Invalid {name} held trust provider."
        )

    return hold


def _validated_key_snapshot(
    snapshot,
    *,
    expected_authority_id,
):
    """Validate an externally supplied held key snapshot."""

    if type(snapshot) is not tuple or len(snapshot) != 2:
        raise ValueError(
            "Invalid held checkpoint key snapshot."
        )

    authority_id, public_key = snapshot

    _require_identity(
        authority_id,
        "held checkpoint key authority",
    )

    if authority_id != expected_authority_id:
        raise ValueError(
            "Held checkpoint key authority mismatch."
        )

    if (
        type(public_key) is not bytes
        or len(public_key) != 32
    ):
        raise ValueError(
            "Held checkpoint Ed25519 public key "
            "must be exactly 32 immutable bytes."
        )

    return (
        authority_id,
        bytes(public_key),
    )


def _validated_generation_snapshot(
    snapshot,
    *,
    expected_authority_id,
):
    """Validate an externally supplied generation floor."""

    if type(snapshot) is not tuple or len(snapshot) != 2:
        raise ValueError(
            "Invalid held checkpoint generation snapshot."
        )

    authority_id, generation_floor = snapshot

    _require_identity(
        authority_id,
        "held checkpoint generation authority",
    )

    if authority_id != expected_authority_id:
        raise ValueError(
            "Held checkpoint generation authority mismatch."
        )

    if (
        type(generation_floor) is not int
        or generation_floor < 0
    ):
        raise ValueError(
            "Invalid held checkpoint generation floor."
        )

    return generation_floor


@dataclass(frozen=True, slots=True)
class SplitCheckpointTrustSource:
    """Compose two external leases into one held snapshot.

    Frozen fields protect against ordinary accidental
    assignment only. They do not authenticate either
    provider or establish a secure Python trust boundary.
    """

    key_source: object
    generation_source: object
    expected_authority_id: str

    @classmethod
    def from_sources(
        cls,
        *,
        key_source,
        generation_source,
        expected_authority_id,
    ):
        """Validate provider interfaces, not their provenance."""

        try:
            _require_identity(
                expected_authority_id,
                "expected checkpoint authority",
            )

            _require_held_source(
                key_source,
                "checkpoint key",
            )

            _require_held_source(
                generation_source,
                "checkpoint generation",
            )

            return cls(
                key_source=key_source,
                generation_source=generation_source,
                expected_authority_id=expected_authority_id,
            )

        except Exception as exc:
            raise ValueError(
                "Checkpoint trust source binding failed."
            ) from exc

    @contextmanager
    def hold(self):
        """Hold both providers through the caller's work.

        Acquire key first and generation second. Release
        generation first and key second.

        The two held snapshots are required to identify
        the same expected authority.

        A provider may suppress an error thrown into its
        context manager. A completion sentinel ensures
        that such suppression cannot silently turn an
        interrupted operation into a successful lease.
        """

        # Each required phase has its own completion marker.
        body_completed = False
        generation_released = False
        key_released = False

        try:
            _require_identity(
                self.expected_authority_id,
                "expected checkpoint authority",
            )

            key_hold = _require_held_source(
                self.key_source,
                "checkpoint key",
            )

            generation_hold = _require_held_source(
                self.generation_source,
                "checkpoint generation",
            )

            with key_hold() as key_witness:
                (
                    authority_id,
                    public_key,
                ) = _validated_key_snapshot(
                    key_witness,
                    expected_authority_id=self.expected_authority_id,
                )

                with generation_hold() as generation_witness:
                    minimum_generation = (
                        _validated_generation_snapshot(
                            generation_witness,
                            expected_authority_id=authority_id,
                        )
                    )

                    # Both source leases are active here.
                    #
                    # The checkpoint verifier receives this
                    # exact three-element tuple and performs
                    # Ed25519 verification before exiting.
                    yield (
                        authority_id,
                        public_key,
                        minimum_generation,
                    )

                    # The caller finished its work, but neither
                    # provider has completed teardown yet.
                    body_completed = True

                # Only reached after normal generation teardown.
                generation_released = True

            # Only reached after normal key teardown.
            key_released = True

            # Outside both provider contexts. A key provider
            # cannot suppress this final completion check.
            if not (
                body_completed
                and generation_released
                and key_released
            ):
                raise ValueError(
                    "Held checkpoint trust operation "
                    "did not complete successfully."
                )

        except Exception as exc:
            raise ValueError(
                "Split checkpoint trust lease failed."
            ) from exc
