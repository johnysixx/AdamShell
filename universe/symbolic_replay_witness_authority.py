"""Contract for a trusted monotonic receipt witness authority.

This module has NO durable storage or remote implementation.

A real provider must supply:
- a linearizable current-state read;
- durable compare-and-swap publication;
- independence from local checkpoint rollback;
- trustworthy authentication and authorization.

Monotonic local validation is not a distributed transaction.
"""

from dataclasses import dataclass

from universe.symbolic_replay_receipt_witness import (
    SymbolicReplayReceiptWitness,
)


@dataclass(frozen=True, slots=True)
class SymbolicReplayWitnessRevision:
    revision: int
    witness: SymbolicReplayReceiptWitness

    def __post_init__(self):
        if (
            type(self.revision) is not int
            or self.revision < 0
        ):
            raise ValueError(
                "Invalid witness authority revision."
            )

        if (
            type(self.witness)
            is not SymbolicReplayReceiptWitness
        ):
            raise TypeError(
                "Authority revision requires canonical witness."
            )


def enforce_trusted_floor(
    current,
    trusted_floor,
    *,
    universe_id,
    batch_sha256,
):
    """Check independently supplied minimum witness state.

    The floor is caller-supplied evidence. This function
    does NOT authenticate its provenance or freshness.

    A floor obtained from the rolled-back checkpoint
    cannot protect against rollback of that checkpoint.
    """
    if (
        type(current)
        is not SymbolicReplayWitnessRevision
    ):
        raise TypeError(
            "Current witness revision must be canonical."
        )

    if (
        current.witness.universe_id != universe_id
        or current.witness.batch_sha256 != batch_sha256
    ):
        raise ValueError(
            "Current witness authority scope mismatch."
        )

    if trusted_floor is None:
        return current

    if (
        type(trusted_floor)
        is not SymbolicReplayWitnessRevision
    ):
        raise TypeError(
            "Trusted witness floor must be canonical."
        )

    if (
        trusted_floor.witness.universe_id != universe_id
        or trusted_floor.witness.batch_sha256
        != batch_sha256
    ):
        raise ValueError(
            "Trusted witness floor scope mismatch."
        )

    if current.revision < trusted_floor.revision:
        raise ValueError(
            "Witness authority below trusted floor."
        )

    if not frozenset(
        trusted_floor.witness.receipt_ids
    ).issubset(
        current.witness.receipt_ids
    ):
        raise ValueError(
            "Witness authority contradicts trusted floor."
        )

    return current


class SymbolicReplayWitnessAuthority:
    """Interface and pure transition rule.

    Concrete read_current()/publish() implementations
    must be provided by an independent trusted service.
    """

    def read_current(
        self, *, universe_id, batch_sha256,
    ):
        """Return the latest committed witness revision.

        Must fail rather than return a stale cached result
        or silently fall back to local checkpoint data.
        """
        raise NotImplementedError

    def publish(
        self, witness, *, expected_revision,
    ):
        """Durably commit a monotonic CAS update.

        Return a canonical SymbolicReplayWitnessRevision.
        """
        raise NotImplementedError

    @staticmethod
    def transition(
        current,
        proposed,
        *,
        expected_revision,
    ):
        """Pure CAS validation, not persistent publication."""
        if (
            type(current)
            is not SymbolicReplayWitnessRevision
        ):
            raise TypeError(
                "Current authority revision is not canonical."
            )

        if (
            type(proposed)
            is not SymbolicReplayReceiptWitness
        ):
            raise TypeError(
                "Proposed authority witness is not canonical."
            )

        if type(expected_revision) is not int:
            raise TypeError(
                "Expected authority revision must be an integer."
            )

        if expected_revision != current.revision:
            raise RuntimeError(
                "Stale witness authority revision."
            )

        old = current.witness

        if (
            proposed.universe_id != old.universe_id
            or proposed.batch_sha256 != old.batch_sha256
        ):
            raise ValueError(
                "Witness authority scope mismatch."
            )

        old_ids = frozenset(old.receipt_ids)
        new_ids = frozenset(proposed.receipt_ids)

        if not old_ids.issubset(new_ids):
            raise ValueError(
                "Witness authority receipt revocation forbidden."
            )

        if new_ids == old_ids:
            return current

        return SymbolicReplayWitnessRevision(
            revision=current.revision + 1,
            witness=proposed,
        )
