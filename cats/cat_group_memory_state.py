from dataclasses import dataclass, field
from enum import Enum


class CatGroupMemoryEventKind(Enum):
    PEACEFUL = "peaceful"
    CONFLICT = "conflict"
    COOPERATION = "cooperation"
    BETRAYAL = "betrayal"


@dataclass(slots=True, frozen=True)
class CatGroupMemorySignal:
    kind: CatGroupMemoryEventKind
    winner: str | None = None
    loser: str | None = None

    def __post_init__(self):
        if not isinstance(
            self.kind,
            CatGroupMemoryEventKind,
        ):
            raise TypeError(
                "Cat group memory signal kind "
                "must be CatGroupMemoryEventKind."
            )


@dataclass(slots=True, frozen=True)
class CatGroupEncounterRememberedResult:
    first_group: str
    second_group: str

    name: str = field(
        default="cat_group_encounter_remembered",
        init=False,
    )

    remembered: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupCooperationEvent:
    first_group: str
    second_group: str
    cooperation_type: str

    name: str = field(
        default="cat_group_cooperation",
        init=False,
    )

    cooperation: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupBetrayalEvent:
    betrayer: str
    victim: str
    reason: str

    name: str = field(
        default="cat_group_betrayal",
        init=False,
    )

    betrayal: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True)
class CatGroupMemoryState:
    encounters: int = 0
    peaceful_encounters: int = 0
    conflicts: int = 0
    victories: int = 0
    defeats: int = 0
    standoffs: int = 0
    cooperations: int = 0
    betrayals: int = 0
    last_outcome: str | None = None
    recent_events: list = field(
        default_factory=list
    )
