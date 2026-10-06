from dataclasses import dataclass, field
from enum import Enum


class CatGroupLifecycleState(Enum):
    FORMING = "forming"
    GROWING = "growing"
    STABLE = "stable"
    STRAINED = "strained"
    DISSOLVED = "dissolved"


@dataclass(slots=True, frozen=True)
class CatGroupLifecycleSkippedResult:
    group_id: str
    state: CatGroupLifecycleState

    name: str = field(
        default="cat_group_lifecycle_skipped",
        init=False,
    )

    advanced: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            CatGroupLifecycleState,
        ):
            raise TypeError(
                "Cat group lifecycle state "
                "must be CatGroupLifecycleState."
            )


@dataclass(slots=True, frozen=True)
class CatGroupLifecycleAdvancedEvent:
    group_id: str
    previous_state: CatGroupLifecycleState
    state: CatGroupLifecycleState
    age_ticks: int
    member_count: int
    cohesion: float

    name: str = field(
        default="cat_group_lifecycle_advanced",
        init=False,
    )

    advanced: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        for state in (
            self.previous_state,
            self.state,
        ):
            if not isinstance(
                state,
                CatGroupLifecycleState,
            ):
                raise TypeError(
                    "Cat group lifecycle event "
                    "states must be "
                    "CatGroupLifecycleState."
                )

        object.__setattr__(
            self,
            "age_ticks",
            int(self.age_ticks),
        )

        object.__setattr__(
            self,
            "member_count",
            int(self.member_count),
        )

        object.__setattr__(
            self,
            "cohesion",
            float(self.cohesion),
        )


@dataclass(slots=True, frozen=True)
class CatGroupDissolvedEvent:
    group_id: str
    reason: str
    former_members: tuple[str, ...]

    name: str = field(
        default="cat_group_dissolved",
        init=False,
    )

    dissolved: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "former_members",
            tuple(
                self.former_members
            ),
        )
