from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupCulturalPracticeEvent:
    group_id: str
    practice: str
    category: str
    participants: tuple[str, ...]
    strength: float

    name: str = field(
        default="cat_group_cultural_practice",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "participants",
            tuple(self.participants),
        )

        object.__setattr__(
            self,
            "strength",
            float(self.strength),
        )


@dataclass(slots=True, frozen=True)
class CatGroupPreferenceExpressedResult:
    group_id: str
    preference: str
    value: object
    strength: float

    name: str = field(
        default="cat_group_preference_expressed",
        init=False,
    )

    expressed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "strength",
            float(self.strength),
        )
