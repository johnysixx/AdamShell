"""A44 data-only signed checkpoint witness rotation coordinator.

The two backends are EXTERNAL contracts. Their trust, identity,
CAS linearizability, durability, and rollback resistance are NOT
established by this Python orchestration layer.

Rotation sequence:
  1. Verify the old and successor signed witnesses under a held root.
  2. Publish the successor witness using its backend's CAS.
  3. Re-read the held state; require the successor is visible.
  4. Advance the root revision using its backend's CAS.
  5. Re-read both sources; require the advanced floor and successor.

Neither a successful readback nor a returned CAS tuple guarantees
independent provenance or durable, cross-backend atomic publication.
Failures after partial publication are ambiguous and must be inspected
explicitly; never infer rollback or retry blindly.

No restoration, execution, or republication authority is granted.
"""

from dataclasses import dataclass, field

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


def _require_source(source, read_name, publish_name):
    read = getattr(source, read_name, None)
    publish = getattr(source, publish_name, None)

    if not callable(read) or not callable(publish):
        raise ValueError(
            "Rotation source lacks required operations."
        )

    return read, publish


def _require_challenge(challenge):
    if type(challenge) is not bytes or len(challenge) != 32:
        raise ValueError(
            "Rotation challenge must be 32 immutable bytes."
        )

    return bytes(challenge)


def _require_revision(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f"Invalid {name}.")

    return value


def _require_witness_pair(value, name):
    if type(value) is not tuple or len(value) != 2:
        raise ValueError(f"Invalid {name} pair.")

    message, signature = value

    if (
        type(message) is not bytes
        or not message
        or len(message) > 4096
    ):
        raise ValueError(f"Invalid {name} message.")

    if type(signature) is not bytes or len(signature) != 64:
        raise ValueError(f"Invalid {name} signature.")

    return bytes(message), bytes(signature)


def _require_root_snapshot(value, expected_root_id):
    if type(value) is not tuple or len(value) != 3:
        raise ValueError(
            "Malformed held rotation root snapshot."
        )

    root_id, public_key, revision = value

    _require_identity(
        root_id,
        "held checkpoint root",
    )

    if root_id != expected_root_id:
        raise ValueError(
            "Rotation root identity mismatch."
        )

    if type(public_key) is not bytes or len(public_key) != 32:
        raise ValueError(
            "Malformed held rotation root key."
        )

    _require_revision(
        revision,
        "held rotation floor",
    )

    return root_id, bytes(public_key), revision


def _require_request(
    expected_revision,
    next_revision,
    expected_witness,
    next_witness,
):
    previous = _require_revision(
        expected_revision,
        "expected rotation floor",
    )

    target = _require_revision(
        next_revision,
        "next rotation floor",
    )

    if target != previous + 1:
        raise ValueError(
            "Rotation floor must advance one revision."
        )

    predecessor = _require_witness_pair(
        expected_witness,
        "predecessor",
    )

    successor = _require_witness_pair(
        next_witness,
        "successor",
    )

    if predecessor == successor:
        raise ValueError(
            "Rotation successor is identical to predecessor."
        )

    return previous, target, predecessor, successor


def _check_verified(
    value,
    *,
    root_id,
    authority_id,
    universe_id,
    challenge,
    minimum_revision,
):
    if (
        type(value) is not VerifiedCheckpointTrustWitness
        or value.root_signature_verified is not True
        or value.is_independently_trusted is not False
        or value.is_authoritative is not False
        or value.is_restorable is not False
        or value.can_republish is not False
        or value.root_id != root_id
        or value.authority_id != authority_id
        or value.universe_id != universe_id
        or value.challenge != challenge
        or type(value.witness_revision) is not int
        or value.witness_revision <= minimum_revision
        or type(value.checkpoint_public_key) is not bytes
        or len(value.checkpoint_public_key) != 32
        or type(value.minimum_generation) is not int
        or value.minimum_generation < 0
    ):
        raise ValueError(
            "Invalid signed rotation witness verification."
        )

    return value


@dataclass(frozen=True, slots=True)
class CheckpointWitnessRotationObservation:
    """Observed state only; no external security guarantees."""

    state: str
    floor_revision: int
    witness_revision: int

    signature_verified: bool = field(
        default=True,
        init=False,
    )
    is_independently_trusted: bool = field(
        default=False,
        init=False,
    )
    is_authoritative: bool = field(
        default=False,
        init=False,
    )
    is_durable: bool = field(
        default=False,
        init=False,
    )
    is_restorable: bool = field(
        default=False,
        init=False,
    )
    can_republish: bool = field(
        default=False,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class CheckpointWitnessRotationCoordinator:
    """Data-only coordinator over externally supplied sources."""

    root_floor_source: object
    signed_witness_source: object
    expected_root_id: str
    expected_authority_id: str
    expected_universe_id: str
    expected_challenge: bytes

    @classmethod
    def from_sources(
        cls,
        *,
        root_floor_source,
        signed_witness_source,
        expected_root_id,
        expected_authority_id,
        expected_universe_id,
        expected_challenge,
    ):
        try:
            _require_identity(
                expected_root_id,
                "expected rotation root",
            )

            _require_identity(
                expected_authority_id,
                "expected rotation authority",
            )

            _require_universe_id(
                expected_universe_id
            )

            challenge = _require_challenge(
                expected_challenge
            )

            _require_source(
                root_floor_source,
                "hold",
                "advance",
            )

            _require_source(
                signed_witness_source,
                "hold",
                "publish_if_current",
            )

            return cls(
                root_floor_source=root_floor_source,
                signed_witness_source=signed_witness_source,
                expected_root_id=expected_root_id,
                expected_authority_id=expected_authority_id,
                expected_universe_id=expected_universe_id,
                expected_challenge=challenge,
            )

        except Exception as exc:
            raise ValueError(
                "Invalid checkpoint rotation sources."
            ) from exc

    def inspect(
        self,
        *,
        expected_revision,
        next_revision,
        expected_witness,
        next_witness,
    ):
        """Verify signed witnesses under both held source leases.

        This inspection reports observed state only.
        Completion markers reject masked provider failures.
        """

        body_completed = False
        witness_released = False
        root_released = False

        try:
            (
                previous,
                target,
                old_pair,
                new_pair,
            ) = _require_request(
                expected_revision,
                next_revision,
                expected_witness,
                next_witness,
            )

            _require_identity(
                self.expected_root_id,
                "expected rotation root",
            )

            _require_identity(
                self.expected_authority_id,
                "expected rotation authority",
            )

            _require_universe_id(
                self.expected_universe_id
            )

            challenge = _require_challenge(
                self.expected_challenge
            )

            root_hold, _ = _require_source(
                self.root_floor_source,
                "hold",
                "advance",
            )

            witness_hold, _ = _require_source(
                self.signed_witness_source,
                "hold",
                "publish_if_current",
            )

            with root_hold() as root_snapshot:
                (
                    root_id,
                    root_key,
                    actual_floor,
                ) = _require_root_snapshot(
                    root_snapshot,
                    self.expected_root_id,
                )

                with witness_hold() as held_pair:
                    observed_pair = _require_witness_pair(
                        held_pair,
                        "held",
                    )

                    old_report = _check_verified(
                        verify_signed_checkpoint_trust_witness(
                            message=old_pair[0],
                            signature=old_pair[1],
                            trusted_root_id=root_id,
                            trusted_root_public_key=root_key,
                            expected_authority_id=(
                                self.expected_authority_id
                            ),
                            expected_universe_id=(
                                self.expected_universe_id
                            ),
                            expected_challenge=challenge,
                            minimum_witness_revision=previous,
                        ),
                        root_id=root_id,
                        authority_id=self.expected_authority_id,
                        universe_id=self.expected_universe_id,
                        challenge=challenge,
                        minimum_revision=previous,
                    )

                    new_report = _check_verified(
                        verify_signed_checkpoint_trust_witness(
                            message=new_pair[0],
                            signature=new_pair[1],
                            trusted_root_id=root_id,
                            trusted_root_public_key=root_key,
                            expected_authority_id=(
                                self.expected_authority_id
                            ),
                            expected_universe_id=(
                                self.expected_universe_id
                            ),
                            expected_challenge=challenge,
                            minimum_witness_revision=target,
                        ),
                        root_id=root_id,
                        authority_id=self.expected_authority_id,
                        universe_id=self.expected_universe_id,
                        challenge=challenge,
                        minimum_revision=target,
                    )

                    if (
                        old_report.witness_revision != target
                        or new_report.witness_revision
                        <= old_report.witness_revision
                    ):
                        raise ValueError(
                            "Invalid signed witness revision transition."
                        )

                    if (
                        actual_floor == previous
                        and observed_pair == old_pair
                    ):
                        state = "ready"
                        observed_revision = (
                            old_report.witness_revision
                        )

                    elif (
                        actual_floor == previous
                        and observed_pair == new_pair
                    ):
                        state = "witness_published"
                        observed_revision = (
                            new_report.witness_revision
                        )

                    elif (
                        actual_floor == target
                        and observed_pair == new_pair
                    ):
                        state = "observed_advanced"
                        observed_revision = (
                            new_report.witness_revision
                        )

                    else:
                        raise ValueError(
                            "Inconsistent rotation source snapshots."
                        )

                    observation = (
                        CheckpointWitnessRotationObservation(
                            state=state,
                            floor_revision=actual_floor,
                            witness_revision=observed_revision,
                        )
                    )

                    body_completed = True

                witness_released = True

            root_released = True

            if not (
                body_completed
                and witness_released
                and root_released
            ):
                raise ValueError(
                    "Rotation source lease was not completed."
                )

            return observation

        except Exception as exc:
            raise ValueError(
                "Checkpoint rotation inspection failed."
            ) from exc

    def rotate(
        self,
        *,
        expected_revision,
        next_revision,
        expected_witness,
        next_witness,
    ):
        """Publish successor, then floor; read back after each.

        Fail closed on any error. Never retry or rollback
        automatically. A backend may commit before failing.
        """

        try:
            (
                previous,
                target,
                old_pair,
                new_pair,
            ) = _require_request(
                expected_revision,
                next_revision,
                expected_witness,
                next_witness,
            )

            arguments = dict(
                expected_revision=previous,
                next_revision=target,
                expected_witness=old_pair,
                next_witness=new_pair,
            )

            initial = self.inspect(**arguments)

            if initial.state != "ready":
                raise ValueError(
                    "Rotation is not at its expected initial state."
                )

            _, publish = _require_source(
                self.signed_witness_source,
                "hold",
                "publish_if_current",
            )

            published_reply = publish(
                expected_witness=old_pair,
                next_witness=new_pair,
            )

            reply = _require_witness_pair(
                published_reply,
                "published",
            )

            if reply != new_pair:
                raise ValueError(
                    "Witness publication returned unexpected reply."
                )

            intermediate = self.inspect(**arguments)

            if intermediate.state != "witness_published":
                raise ValueError(
                    "Successor witness not observed after publication."
                )

            _, advance = _require_source(
                self.root_floor_source,
                "hold",
                "advance",
            )

            published_root = _require_root_snapshot(
                advance(
                    expected_revision=previous,
                    next_revision=target,
                ),
                self.expected_root_id,
            )

            if published_root[2] != target:
                raise ValueError(
                    "Unexpected root floor CAS reply."
                )

            final = self.inspect(**arguments)

            if final.state != "observed_advanced":
                raise ValueError(
                    "Advanced rotation state not observed."
                )

            return final

        except Exception as exc:
            # Partial commit is possible.
            # Never infer rollback from an exception.
            raise ValueError(
                "Checkpoint witness rotation failed; "
                "inspect state before retry."
            ) from exc
