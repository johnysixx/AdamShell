from dataclasses import dataclass, field

from core.entity.cronenberg_system.quantum_state import (
    CronenbergQuantumState
)


@dataclass(slots=True, frozen=True)
class CronenbergPairSpin:

    participant_id: str
    spin: float

    def __post_init__(self):
        object.__setattr__(
            self,
            "participant_id",
            str(self.participant_id),
        )

        object.__setattr__(
            self,
            "spin",
            float(self.spin),
        )


@dataclass(slots=True, frozen=True)
class CronenbergQuantumPairEncounteredEvent:

    pair_id: str
    location: object
    participants: tuple[str, str]
    spins: tuple[
        CronenbergPairSpin,
        CronenbergPairSpin,
    ]
    universe_tick: int | None = None

    name: str = field(
        default=(
            "cronenberg_quantum_pair_encountered"
        ),
        init=False,
    )

    encountered: bool = field(
        default=True,
        init=False,
    )

    resolution: None = field(
        default=None,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "pair_id",
            str(self.pair_id),
        )

        participants = tuple(
            str(participant)
            for participant
            in self.participants
        )

        if len(participants) != 2:
            raise ValueError(
                "Cronenberg pair encounter requires "
                "exactly two participants."
            )

        object.__setattr__(
            self,
            "participants",
            participants,
        )

        spins = tuple(
            self.spins
        )

        if (
            len(spins) != 2
            or not all(
                isinstance(
                    spin,
                    CronenbergPairSpin,
                )
                for spin in spins
            )
        ):
            raise TypeError(
                "Cronenberg pair encounter spins "
                "require two CronenbergPairSpin "
                "objects."
            )

        object.__setattr__(
            self,
            "spins",
            spins,
        )

        if self.universe_tick is not None:
            object.__setattr__(
                self,
                "universe_tick",
                int(self.universe_tick),
            )

    def to_dict(self):
        return {
            "name": self.name,
            "encountered": self.encountered,
            "pair_id": self.pair_id,
            "location": self.location,
            "participants": list(
                self.participants
            ),
            "spins": {
                spin.participant_id:
                    spin.spin
                for spin
                in self.spins
            },
            "universe_tick": (
                self.universe_tick
            ),
            "resolution": self.resolution,
        }


class CronenbergPairEncounter:

    def __init__(self):
        self.name = "cronenberg_pair_encounter"
        self.history = []

    def detect(
        self,
        first,
        second,
        universe_tick=None
    ):
        if first is second:
            return self._not_encountered(
                reason="same_object"
            )

        if getattr(first, "type", None) != "cronenberg":
            return self._not_encountered(
                reason="first_not_cronenberg"
            )

        if getattr(second, "type", None) != "cronenberg":
            return self._not_encountered(
                reason="second_not_cronenberg"
            )

        if not first.is_alive or not second.is_alive:
            return self._not_encountered(
                reason="dead_member"
            )

        first_state = getattr(
            first,
            "quantum_state",
            None
        )

        second_state = getattr(
            second,
            "quantum_state",
            None
        )

        if not isinstance(
            first_state,
            CronenbergQuantumState
        ):
            return self._not_encountered(
                reason="first_quantum_state_missing"
            )

        if not isinstance(
            second_state,
            CronenbergQuantumState
        ):
            return self._not_encountered(
                reason="second_quantum_state_missing"
            )

        first_pair_id = first_state.pair_id
        second_pair_id = second_state.pair_id

        if (
            first_pair_id is None
            or first_pair_id != second_pair_id
        ):
            return self._not_encountered(
                reason="different_quantum_pair"
            )

        if (
            first_state.counterpart_id
            != second.id
            or second_state.counterpart_id
            != first.id
        ):
            return self._not_encountered(
                reason="counterpart_mismatch"
            )

        if first.location != second.location:
            return self._not_encountered(
                reason="different_location"
            )

        event = (
            CronenbergQuantumPairEncounteredEvent(
                pair_id=first_pair_id,
                location=first.location,
                participants=(
                    first.id,
                    second.id,
                ),
                spins=(
                    CronenbergPairSpin(
                        participant_id=first.id,
                        spin=first_state.spin,
                    ),
                    CronenbergPairSpin(
                        participant_id=second.id,
                        spin=second_state.spin,
                    ),
                ),
                universe_tick=universe_tick,
            )
        )

        self.record_event(
            event
        )

        return event.to_dict()

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            CronenbergQuantumPairEncounteredEvent,
        ):
            raise TypeError(
                "Cronenberg pair encounter history "
                "requires a "
                "CronenbergQuantumPairEncounteredEvent "
                "object."
            )

        self.history.append(
            event
        )

        return event

    def _not_encountered(self, reason):
        return {
            "name": "cronenberg_quantum_pair_not_encountered",
            "encountered": False,
            "reason": reason
        }

    @property
    def public_state(self):
        return {
            "name": self.name,
            "encounter_count": len(
                self.history
            )
        }
