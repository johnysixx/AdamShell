from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatHumanInteractionRememberedEvent:
    cat: str
    human: str
    positive: bool
    right_human_score: float

    name: str = field(
        default="cat_human_interaction_remembered",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "positive",
            bool(self.positive),
        )

        object.__setattr__(
            self,
            "right_human_score",
            float(self.right_human_score),
        )


@dataclass(slots=True, frozen=True)
class CatHumanBondEvaluationResult:
    cat: str
    human: str | None
    score: float
    right_human: bool
    trust: float | None = None
    affection: float | None = None
    familiarity: float | None = None
    reason: str | None = None

    name: str = field(
        default="cat_human_bond_evaluation",
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
            "right_human",
            bool(self.right_human),
        )

        for attribute in (
            "trust",
            "affection",
            "familiarity",
        ):
            value = getattr(
                self,
                attribute,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    attribute,
                    float(value),
                )
