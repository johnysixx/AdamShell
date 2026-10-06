from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupBondEvaluation:
    group_id: str
    cohesion: float
    bonded_group: bool
    member_count: int
    trust: float = 0.0
    affiliation: float = 0.0
    tension: float = 0.0
    shared_scent: float = 0.0

    def __post_init__(self):
        object.__setattr__(
            self,
            "cohesion",
            float(self.cohesion),
        )

        object.__setattr__(
            self,
            "bonded_group",
            bool(self.bonded_group),
        )

        object.__setattr__(
            self,
            "member_count",
            int(self.member_count),
        )

        for name in (
            "trust",
            "affiliation",
            "tension",
            "shared_scent",
        ):
            object.__setattr__(
                self,
                name,
                float(
                    getattr(
                        self,
                        name,
                    )
                ),
            )


@dataclass(slots=True, frozen=True)
class CatGroupBondReinforcedEvent:
    group_id: str
    members: tuple[str, ...]
    amount: float

    name: str = field(
        default="cat_group_bond_reinforced",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "members",
            tuple(self.members),
        )

        object.__setattr__(
            self,
            "amount",
            float(self.amount),
        )


@dataclass(slots=True, frozen=True)
class CatGroupBondReinforcedResult:
    group_id: str
    members: tuple[str, ...]
    amount: float
    cohesion: float
    bonded_group: bool

    name: str = field(
        default="cat_group_bond_reinforced",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "members",
            tuple(self.members),
        )

        object.__setattr__(
            self,
            "amount",
            float(self.amount),
        )

        object.__setattr__(
            self,
            "cohesion",
            float(self.cohesion),
        )

        object.__setattr__(
            self,
            "bonded_group",
            bool(self.bonded_group),
        )
