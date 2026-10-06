from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupEncounterPeacefulResult:
    first_group: str
    second_group: str

    name: str = field(
        default="cat_group_encounter_peaceful",
        init=False,
    )

    conflict: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupConflictEvent:
    first_group: str
    second_group: str
    resource: object
    shared_territories: tuple[str, ...]
    first_strength: float
    second_strength: float
    winner: str | None
    loser: str | None
    outcome: str

    name: str = field(
        default="cat_inter_group_conflict",
        init=False,
    )

    conflict: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "shared_territories",
            tuple(
                self.shared_territories
            ),
        )

        object.__setattr__(
            self,
            "first_strength",
            float(
                self.first_strength
            ),
        )

        object.__setattr__(
            self,
            "second_strength",
            float(
                self.second_strength
            ),
        )
