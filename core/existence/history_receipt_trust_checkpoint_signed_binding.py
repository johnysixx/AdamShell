"""A44 single signed-witness held checkpoint binding.

Combines two externally held sources:

    root_source.hold() ->
        (root_id, raw_root_public_key, minimum_witness_revision)

    signed_witness_source.hold() ->
        (canonical_witness_message, witness_signature)

ONE verified, root-signed document supplies both:
    (checkpoint_authority_id,
     checkpoint_public_key,
     minimum_checkpoint_generation)

Both source leases remain held while the caller performs
checkpoint signature verification.

SECURITY LIMITATIONS:

- The supplied root source is not independently authenticated.
- A caller-controlled root key can verify attacker-signed data.
- The root revision floor is not durably monotonic here.
- Reusing an identical challenge is not prevented.
- This does not guarantee atomic publication by a remote backend.
- In-process malicious Python code is outside this trust model.
- No restoration or republication is authorized.
"""

from contextlib import contextmanager
from dataclasses import dataclass

from core.existence.history_receipt_trust_checkpoint_signed_witness import (
    VerifiedCheckpointTrustWitness,
    verify_signed_checkpoint_trust_witness,
)

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)

from core.existence.history_receipt_trust_publication_witness import (
    _require_universe_id,
)


def _require_source(source, name):
    hold = getattr(source, "hold", None)

    if not callable(hold):
        raise ValueError(
            f"Invalid {name} held source."
        )

    return hold


def _validate_challenge(challenge):
    if type(challenge) is not bytes or len(challenge) != 32:
        raise ValueError(
            "Expected signed witness challenge must be 32 bytes."
        )

    return bytes(challenge)


def _validate_root_snapshot(snapshot, *, expected_root_id):
    if type(snapshot) is not tuple or len(snapshot) != 3:
        raise ValueError(
            "Invalid signed binding root snapshot."
        )

    root_id, root_public_key, revision_floor = snapshot

    _require_identity(
        root_id,
        "signed binding root identity",
    )

    if root_id != expected_root_id:
        raise ValueError(
            "Signed binding root identity mismatch."
        )

    if (
        type(root_public_key) is not bytes
        or len(root_public_key) != 32
    ):
        raise ValueError(
            "Signed binding root key must be 32 immutable bytes."
        )

    if (
        type(revision_floor) is not int
        or revision_floor < 0
    ):
        raise ValueError(
            "Invalid signed binding witness revision floor."
        )

    return (
        root_id,
        bytes(root_public_key),
        revision_floor,
    )


def _validate_signed_snapshot(snapshot):
    if type(snapshot) is not tuple or len(snapshot) != 2:
        raise ValueError(
            "Invalid held signed-witness snapshot."
        )

    message, signature = snapshot

    if (
        type(message) is not bytes
        or not message
        or len(message) > 4096
    ):
        raise ValueError(
            "Invalid held signed-witness message."
        )

    if type(signature) is not bytes or len(signature) != 64:
        raise ValueError(
            "Invalid held signed-witness signature."
        )

    return (
        bytes(message),
        bytes(signature),
    )


@dataclass(frozen=True, slots=True)
class SignedCheckpointWitnessHeldSource:
    """Adapter to the existing held checkpoint verification gate.

    The fields are ordinary Python object references.
    Frozen dataclass fields do not establish secure provenance.
    """

    root_source: object
    signed_witness_source: object
    expected_root_id: str
    expected_authority_id: str
    expected_universe_id: str
    expected_challenge: bytes

    @classmethod
    def from_sources(
        cls,
        *,
        root_source,
        signed_witness_source,
        expected_root_id,
        expected_authority_id,
        expected_universe_id,
        expected_challenge,
    ):
        try:
            _require_identity(
                expected_root_id,
                "expected signed binding root",
            )

            _require_identity(
                expected_authority_id,
                "expected signed binding authority",
            )

            _require_universe_id(
                expected_universe_id
            )

            challenge = _validate_challenge(
                expected_challenge
            )

            _require_source(
                root_source,
                "root",
            )

            _require_source(
                signed_witness_source,
                "signed witness",
            )

            return cls(
                root_source=root_source,
                signed_witness_source=signed_witness_source,
                expected_root_id=expected_root_id,
                expected_authority_id=expected_authority_id,
                expected_universe_id=expected_universe_id,
                expected_challenge=challenge,
            )

        except Exception as exc:
            raise ValueError(
                "Signed checkpoint witness binding failed."
            ) from exc

    @contextmanager
    def hold(self):
        """Expose one verified checkpoint trust tuple.

        Acquisition:
            root -> signed witness

        Release:
            signed witness -> root

        Every completion phase is independently marked.
        The final check runs outside both provider contexts,
        so a root provider cannot mask a nested exit failure.
        """

        body_completed = False
        witness_released = False
        root_released = False

        try:
            # Validate again because direct dataclass
            # construction bypasses from_sources().
            _require_identity(
                self.expected_root_id,
                "expected signed binding root",
            )

            _require_identity(
                self.expected_authority_id,
                "expected signed binding authority",
            )

            _require_universe_id(
                self.expected_universe_id
            )

            challenge = _validate_challenge(
                self.expected_challenge
            )

            root_hold = _require_source(
                self.root_source,
                "root",
            )

            signed_hold = _require_source(
                self.signed_witness_source,
                "signed witness",
            )

            with root_hold() as root_snapshot:
                (
                    root_id,
                    root_public_key,
                    minimum_witness_revision,
                ) = _validate_root_snapshot(
                    root_snapshot,
                    expected_root_id=self.expected_root_id,
                )

                with signed_hold() as signed_snapshot:
                    (
                        witness_message,
                        witness_signature,
                    ) = _validate_signed_snapshot(
                        signed_snapshot
                    )

                    # Root and signed-witness leases are
                    # BOTH active throughout this call.
                    verified = verify_signed_checkpoint_trust_witness(
                        message=witness_message,
                        signature=witness_signature,
                        trusted_root_id=root_id,
                        trusted_root_public_key=root_public_key,
                        expected_authority_id=self.expected_authority_id,
                        expected_universe_id=self.expected_universe_id,
                        expected_challenge=challenge,
                        minimum_witness_revision=minimum_witness_revision,
                    )

                    if (
                        type(verified)
                        is not VerifiedCheckpointTrustWitness
                        or verified.root_signature_verified is not True
                        or verified.is_independently_trusted is not False
                        or verified.is_authoritative is not False
                        or verified.is_restorable is not False
                        or verified.can_republish is not False
                        or verified.root_id != root_id
                        or verified.authority_id != self.expected_authority_id
                        or verified.universe_id != self.expected_universe_id
                        or verified.challenge != challenge
                        or type(verified.checkpoint_public_key) is not bytes
                        or len(verified.checkpoint_public_key) != 32
                        or type(verified.minimum_generation) is not int
                        or verified.minimum_generation < 0
                        or type(verified.witness_revision) is not int
                        or verified.witness_revision <= minimum_witness_revision
                    ):
                        raise ValueError(
                            "Invalid signed checkpoint witness verification."
                        )

                    # Key and generation originate from
                    # the SAME validated signed document.
                    # Both leases remain active while
                    # the caller verifies the checkpoint.
                    yield (
                        verified.authority_id,
                        bytes(verified.checkpoint_public_key),
                        verified.minimum_generation,
                    )

                    # Caller completed checkpoint validation.
                    # Providers have not exited yet.
                    body_completed = True

                # Reached only after normal signed-witness exit.
                witness_released = True

            # Reached only after normal root exit.
            root_released = True

            # No provider can suppress this final check.
            if not (
                body_completed
                and witness_released
                and root_released
            ):
                raise ValueError(
                    "Signed checkpoint binding lease incomplete."
                )

        except Exception as exc:
            raise ValueError(
                "Signed checkpoint binding lease failed."
            ) from exc
