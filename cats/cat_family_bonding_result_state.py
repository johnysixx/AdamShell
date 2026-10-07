from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatFamilyBondEvaluationResult:
    related: bool
    eligible: bool
    relation: str | None
    tension: float = 0.0
    care_events: int = 0
    play_events: int = 0
    reason: str | None = None

    name: str = field(
        default="cat_family_bond_evaluation",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "related",
            bool(self.related),
        )

        object.__setattr__(
            self,
            "eligible",
            bool(self.eligible),
        )

        object.__setattr__(
            self,
            "tension",
            float(self.tension),
        )

        object.__setattr__(
            self,
            "care_events",
            int(self.care_events),
        )

        object.__setattr__(
            self,
            "play_events",
            int(self.play_events),
        )


@dataclass(slots=True, frozen=True)
class CatFamilyBondNotFormedResult:
    first: str
    second: str
    reason: str

    name: str = field(
        default="cat_family_bond_not_formed",
        init=False,
    )

    formed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatFamilyBondFormedEvent:
    first: str
    second: str
    relation: str
    strength: float

    name: str = field(
        default="cat_family_bond_formed",
        init=False,
    )

    formed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "strength",
            float(self.strength),
        )
