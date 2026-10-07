from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatSiblingPlayEvaluationResult:
    first: str
    second: str
    relation: str | None
    littermates: bool
    old_enough: bool
    same_layer: bool
    allowed: bool

    name: str = field(
        default="cat_sibling_play_evaluation",
        init=False,
    )

    def __post_init__(self):
        for attribute in (
            "littermates",
            "old_enough",
            "same_layer",
            "allowed",
        ):
            object.__setattr__(
                self,
                attribute,
                bool(
                    getattr(
                        self,
                        attribute,
                    )
                ),
            )


@dataclass(slots=True, frozen=True)
class CatSiblingPlayDeniedResult:
    first: str
    second: str
    relation: str | None
    littermates: bool
    old_enough: bool
    same_layer: bool

    name: str = field(
        default="sibling_play_denied",
        init=False,
    )

    allowed: bool = field(
        default=False,
        init=False,
    )

    played: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        for attribute in (
            "littermates",
            "old_enough",
            "same_layer",
        ):
            object.__setattr__(
                self,
                attribute,
                bool(
                    getattr(
                        self,
                        attribute,
                    )
                ),
            )


@dataclass(slots=True, frozen=True)
class CatSiblingPlayEvent:
    first: str
    second: str
    relation: str
    play_type: str
    age_days: int
    day: int | None

    name: str = field(
        default="cat_sibling_play",
        init=False,
    )

    played: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "age_days",
            int(self.age_days),
        )
