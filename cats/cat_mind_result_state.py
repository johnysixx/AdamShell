from dataclasses import dataclass, field

from cats.cat_intention_state import (
    CatIntentionCandidate,
)


@dataclass(slots=True, frozen=True)
class CatIntentionNotSelectedResult:

    cat: str
    reason: str

    name: str = field(
        default="cat_intention_not_selected",
        init=False,
    )

    selected: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatIntentionSelectedEvent:

    cat: str
    intention: str
    target: object
    score: float
    reasons: tuple[str, ...]
    quantum_roll: int | None
    intellect_score: int
    intellect_category: str
    finalists: tuple[CatIntentionCandidate, ...]
    previous_intention: CatIntentionCandidate | None

    name: str = field(
        default="cat_intention_selected",
        init=False,
    )

    selected: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not all(
            isinstance(
                finalist,
                CatIntentionCandidate,
            )
            for finalist
            in self.finalists
        ):
            raise TypeError(
                "Cat decision finalists must "
                "be CatIntentionCandidate objects."
            )

        if (
            self.previous_intention is not None
            and not isinstance(
                self.previous_intention,
                CatIntentionCandidate,
            )
        ):
            raise TypeError(
                "Previous cat intention must "
                "be CatIntentionCandidate or None."
            )

        object.__setattr__(
            self,
            "score",
            float(self.score),
        )

        object.__setattr__(
            self,
            "reasons",
            tuple(
                self.reasons
            ),
        )

        object.__setattr__(
            self,
            "finalists",
            tuple(
                self.finalists
            ),
        )

    @property
    def finalist_count(self):
        return len(
            self.finalists
        )
