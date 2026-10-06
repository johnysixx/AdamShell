from copy import deepcopy
from dataclasses import dataclass, field

from cats.cat_group_memory_state import (
    CatGroupMemoryState,
)


@dataclass(slots=True, frozen=True)
class CatGroupMemorySnapshot:
    encounters: int
    peaceful_encounters: int
    conflicts: int
    victories: int
    defeats: int
    standoffs: int
    cooperations: int
    betrayals: int
    last_outcome: str | None
    recent_events: tuple[object, ...]

    @classmethod
    def from_state(
        cls,
        state,
    ):
        if not isinstance(
            state,
            CatGroupMemoryState,
        ):
            raise TypeError(
                "Cat group memory snapshot "
                "requires CatGroupMemoryState."
            )

        return cls(
            encounters=int(state.encounters),
            peaceful_encounters=int(
                state.peaceful_encounters
            ),
            conflicts=int(state.conflicts),
            victories=int(state.victories),
            defeats=int(state.defeats),
            standoffs=int(state.standoffs),
            cooperations=int(state.cooperations),
            betrayals=int(state.betrayals),
            last_outcome=state.last_outcome,
            recent_events=tuple(
                deepcopy(
                    state.recent_events
                )
            ),
        )


@dataclass(slots=True, frozen=True)
class CatGroupDiplomacyDecaySkippedResult:
    reason: str

    name: str = field(
        default="cat_group_diplomacy_decay_skipped",
        init=False,
    )

    advanced: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupDiplomacyMemoryAgedEvent:
    group_id: str
    other_group_id: str
    before: CatGroupMemorySnapshot
    after: CatGroupMemorySnapshot

    name: str = field(
        default="cat_group_diplomacy_memory_aged",
        init=False,
    )

    advanced: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupBetrayalRecoveryDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_betrayal_recovery_denied",
        init=False,
    )

    recovered: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupBetrayalRecoverySkippedResult:
    reason: str

    name: str = field(
        default="cat_group_betrayal_recovery_skipped",
        init=False,
    )

    recovered: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupBetrayalRecoveredResult:
    group_id: str
    other_group_id: str
    remaining_betrayals: int

    name: str = field(
        default="cat_group_betrayal_recovered",
        init=False,
    )

    recovered: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "remaining_betrayals",
            int(self.remaining_betrayals),
        )
