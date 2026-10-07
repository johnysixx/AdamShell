from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class AdultVocalizationLearnedEvent:

    teacher: str
    student: str
    vocalization: str
    day: int
    learned_count: int
    total_count: int
    adult_meowing_complete: bool

    name: str = field(
        default="adult_vocalization_learned",
        init=False,
    )

    taught: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class AdultVocalizationLessonDeniedEvent:

    teacher: str | None
    student: str | None
    vocalization: str
    day: int
    reason: str

    name: str = field(
        default="adult_vocalization_lesson_denied",
        init=False,
    )

    taught: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class AdultVocalizationRepertoireTaughtEvent:

    teacher: str
    student: str
    day: int
    results: tuple[object, ...]
    complete: bool

    name: str = field(
        default="adult_vocalization_repertoire_taught",
        init=False,
    )

    def __post_init__(self):
        results = tuple(
            self.results
        )

        allowed_types = (
            AdultVocalizationLearnedEvent,
            AdultVocalizationLessonDeniedEvent,
        )

        if not all(
            isinstance(
                result,
                allowed_types,
            )
            for result
            in results
        ):
            raise TypeError(
                "Adult vocalization repertoire "
                "requires vocalization result objects."
            )

        object.__setattr__(
            self,
            "results",
            results,
        )

        object.__setattr__(
            self,
            "complete",
            bool(self.complete),
        )
