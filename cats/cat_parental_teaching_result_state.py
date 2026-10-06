from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatParentalTeachingDeniedResult:
    parent: str
    kitten: str
    reason: str
    skill: str | None = None

    name: str = field(
        default="parental_teaching_denied",
        init=False,
    )

    taught: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatParentTaughtKittenEvent:
    parent: str
    parent_role: str
    kitten: str
    skill: str
    progress_before: float
    progress_after: float
    learned: bool
    learned_now: bool
    day: int | None

    name: str = field(
        default="cat_parent_taught_kitten",
        init=False,
    )

    taught: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "progress_before",
            float(self.progress_before),
        )

        object.__setattr__(
            self,
            "progress_after",
            float(self.progress_after),
        )

        object.__setattr__(
            self,
            "learned",
            bool(self.learned),
        )

        object.__setattr__(
            self,
            "learned_now",
            bool(self.learned_now),
        )
