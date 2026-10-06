from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatCulturalTraditionEvaluationResult:
    tradition: str
    known: bool
    category: str | None = None
    score: float = 0.0
    adopt: bool = False

    name: str = field(
        default="cat_cultural_tradition_evaluation",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "known",
            bool(self.known),
        )

        object.__setattr__(
            self,
            "score",
            float(self.score),
        )

        object.__setattr__(
            self,
            "adopt",
            bool(self.adopt),
        )


@dataclass(slots=True, frozen=True)
class CatCulturalExposureDeniedResult:
    reason: str

    name: str = field(
        default="cat_cultural_exposure_denied",
        init=False,
    )

    adopted: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatCulturalTraditionEvaluatedEvent:
    cat: str
    group_id: str
    tradition: str
    score: float
    outcome: str
    adopted: bool

    name: str = field(
        default="cat_cultural_tradition_evaluated",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "score",
            float(self.score),
        )

        object.__setattr__(
            self,
            "adopted",
            bool(self.adopted),
        )


@dataclass(slots=True, frozen=True)
class CatCulturalPreferenceAdoptionDeniedResult:
    reason: str

    name: str = field(
        default="cat_cultural_preference_denied",
        init=False,
    )

    adopted: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatCulturalPreferenceAdoptedResult:
    cat: str
    preference: str
    value: object

    name: str = field(
        default="cat_cultural_preference_adopted",
        init=False,
    )

    adopted: bool = field(
        default=True,
        init=False,
    )
