from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatCulturalPreferenceConflict:
    preference: str
    first_value: object
    second_value: object

    kind: str = field(
        default="preference",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupCulturalComparisonResult:
    first_group: str
    second_group: str
    status: str
    conflict_score: float
    preference_conflicts: tuple[
        CatCulturalPreferenceConflict,
        ...,
    ]
    agreements: tuple[str, ...]
    trait_distance: float

    name: str = field(
        default="cat_group_cultural_comparison",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "conflict_score",
            float(self.conflict_score),
        )

        object.__setattr__(
            self,
            "preference_conflicts",
            tuple(self.preference_conflicts),
        )

        object.__setattr__(
            self,
            "agreements",
            tuple(self.agreements),
        )

        object.__setattr__(
            self,
            "trait_distance",
            float(self.trait_distance),
        )


@dataclass(slots=True, frozen=True)
class CatGroupCulturalInteractionEvent:
    first_group: str
    second_group: str
    status: str
    conflict_score: float
    preference_conflicts: tuple[
        CatCulturalPreferenceConflict,
        ...,
    ]
    agreements: tuple[str, ...]
    trait_distance: float
    diplomacy_delta: float

    name: str = field(
        default="cat_group_cultural_interaction",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "conflict_score",
            float(self.conflict_score),
        )

        object.__setattr__(
            self,
            "preference_conflicts",
            tuple(self.preference_conflicts),
        )

        object.__setattr__(
            self,
            "agreements",
            tuple(self.agreements),
        )

        object.__setattr__(
            self,
            "trait_distance",
            float(self.trait_distance),
        )

        object.__setattr__(
            self,
            "diplomacy_delta",
            float(self.diplomacy_delta),
        )
