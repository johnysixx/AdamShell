from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupRitualPerformanceDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_ritual_denied",
        init=False,
    )

    performed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupRitualPerformedEvent:
    group_id: str
    ritual: str
    participants: tuple[str, ...]
    strength: float

    name: str = field(
        default="cat_group_ritual_performed",
        init=False,
    )

    performed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "participants",
            tuple(
                self.participants
            ),
        )

        object.__setattr__(
            self,
            "strength",
            float(
                self.strength
            ),
        )
