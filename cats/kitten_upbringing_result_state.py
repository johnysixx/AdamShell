from dataclasses import dataclass, field

from cats.cat_personality_state import (
    CatPersonalityExperienceAppliedResult,
)
from cats.kitten_growth_state import (
    KittenGrowthAlreadyProcessedEvent,
    KittenGrowthAppliedEvent,
)
from cats.kitten_upbringing_phase import (
    KittenUpbringingPhase,
)


GROWTH_EVENT_TYPES = (
    KittenGrowthAppliedEvent,
    KittenGrowthAlreadyProcessedEvent,
)

DAILY_CARE_EVENT_NAMES = {
    "fed_by_mother",
    "cleaned_by_mother",
    "warmed_by_mother",
    "protected_by_mother",
}

COMPLETED_SKILL_EVENT_NAMES = {
    "mother_taught_litter_box",
    "mother_taught_box_travel",
    "mother_taught_cat_door_travel",
}


@dataclass(slots=True, frozen=True)
class KittenUpbringingDaySkippedResult:
    kitten: str | None
    day: int
    reason: str

    name: str = field(
        default="kitten_upbringing_day_skipped",
        init=False,
    )

    processed: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "day",
            int(self.day),
        )


@dataclass(slots=True, frozen=True)
class KittenUpbringingDayCompletedEvent:
    kitten: str
    age_days: int
    day: int
    phase: KittenUpbringingPhase
    mother: str | None
    father: str | None
    events: tuple[object, ...]

    name: str = field(
        default="kitten_upbringing_day_completed",
        init=False,
    )

    event_count: int = field(
        init=False,
    )

    processed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.phase,
            KittenUpbringingPhase,
        ):
            raise TypeError(
                "Kitten upbringing result phase "
                "must use KittenUpbringingPhase."
            )

        object.__setattr__(
            self,
            "age_days",
            int(self.age_days),
        )

        object.__setattr__(
            self,
            "day",
            int(self.day),
        )

        events = tuple(
            self.events
        )

        if any(
            isinstance(
                event,
                dict,
            )
            for event
            in events
        ):
            raise TypeError(
                "Kitten upbringing events "
                "must contain objects, not mappings."
            )

        object.__setattr__(
            self,
            "events",
            events,
        )

        object.__setattr__(
            self,
            "event_count",
            len(events),
        )


@dataclass(slots=True, frozen=True)
class KittenDailyCareEvent:
    name: str
    kitten: str
    mother: str | None
    age_days: int
    day: int | None

    care: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if (
            self.name
            not in DAILY_CARE_EVENT_NAMES
        ):
            raise ValueError(
                "Unknown kitten daily care event."
            )

        object.__setattr__(
            self,
            "age_days",
            int(self.age_days),
        )

        if self.day is not None:
            object.__setattr__(
                self,
                "day",
                int(self.day),
            )


@dataclass(slots=True, frozen=True)
class KittenMotherLeftBrieflyEvent:
    kitten: str
    mother: str | None
    age_days: int
    day: int

    name: str = field(
        default="mother_left_kittens_alone_briefly",
        init=False,
    )

    first_time: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class KittenDeadCronenbergDeliveredEvent:
    kitten: str
    mother: str | None
    age_days: int
    day: int

    name: str = field(
        default="mother_brought_small_dead_cronenberg",
        init=False,
    )

    prey_alive: bool = field(
        default=False,
        init=False,
    )

    purpose: str = field(
        default="food_and_prey_recognition",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class KittenSocializationLessonEvent:
    student: str
    teacher: str | None
    skill: str
    age_days: int
    day: int
    previous_progress: float
    progress: float
    learned: bool
    personality: CatPersonalityExperienceAppliedResult

    name: str = field(
        default="kitten_socialization_lesson",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "previous_progress",
            float(self.previous_progress),
        )

        object.__setattr__(
            self,
            "progress",
            float(self.progress),
        )

        object.__setattr__(
            self,
            "learned",
            bool(self.learned),
        )

        if not isinstance(
            self.personality,
            CatPersonalityExperienceAppliedResult,
        ):
            raise TypeError(
                "Socialization personality result "
                "must be an object."
            )


@dataclass(slots=True, frozen=True)
class KittenSiblingPlayLessonEvent:
    kitten: str
    age_days: int
    day: int

    name: str = field(
        default="kitten_played_with_siblings",
        init=False,
    )

    learned: str = field(
        default="play_boundaries",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class KittenSkillCompletedLessonEvent:
    name: str
    student: str
    teacher: str | None
    skill: str
    age_days: int
    day: int

    progress: float = field(
        default=1.0,
        init=False,
    )

    learned: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if (
            self.name
            not in COMPLETED_SKILL_EVENT_NAMES
        ):
            raise ValueError(
                "Unknown completed kitten skill event."
            )


@dataclass(slots=True, frozen=True)
class KittenLiveCronenbergDeliveredEvent:
    kitten: str
    mother: str | None
    age_days: int
    day: int

    name: str = field(
        default="mother_brought_small_live_cronenberg",
        init=False,
    )

    prey_alive: bool = field(
        default=True,
        init=False,
    )

    prey_controlled_by_mother: bool = field(
        default=True,
        init=False,
    )

    purpose: str = field(
        default="live_prey_training",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class KittenHuntingStepPracticedEvent:
    kitten: str
    teacher: str | None
    step: str
    age_days: int
    day: int
    previous_progress: float
    progress: float

    name: str = field(
        default="kitten_hunting_step_practiced",
        init=False,
    )

    learned: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "previous_progress",
            float(self.previous_progress),
        )

        object.__setattr__(
            self,
            "progress",
            float(self.progress),
        )


@dataclass(slots=True, frozen=True)
class KittenFirstTrainingKillEvent:
    kitten: str
    mother: str | None
    age_days: int
    day: int
    successful_kills: int
    hunting_progress: float
    growth: object

    name: str = field(
        default="kitten_completed_first_training_kill",
        init=False,
    )

    prey: str = field(
        default="small_live_cronenberg",
        init=False,
    )

    successful: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.growth,
            GROWTH_EVENT_TYPES,
        ):
            raise TypeError(
                "First-kill growth must be "
                "a kitten growth event object."
            )


@dataclass(slots=True, frozen=True)
class KittenFamilyHuntEvent:
    kitten: str
    mother: str | None
    father: str | None
    father_joined: bool
    teachers: tuple[str, ...]
    age_days: int
    day: int
    family_hunt_number: int
    hunting_progress: float
    hunting_learned: bool
    growth: object

    name: str = field(
        default="kitten_joined_family_cronenberg_hunt",
        init=False,
    )

    successful: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "teachers",
            tuple(self.teachers),
        )

        if not isinstance(
            self.growth,
            GROWTH_EVENT_TYPES,
        ):
            raise TypeError(
                "Family-hunt growth must be "
                "a kitten growth event object."
            )


@dataclass(slots=True, frozen=True)
class KittenAdultVocalizationTeacherUnavailableEvent:
    kitten: str
    age_days: int
    day: int

    name: str = field(
        default="adult_vocalization_teacher_unavailable",
        init=False,
    )

    learned: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class KittenHumanCommunicationLessonDeniedResult:
    kitten: str
    teacher: str | None
    age_days: int
    day: int
    reason: str

    name: str = field(
        default="human_communication_lesson_denied",
        init=False,
    )

    learned: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class KittenHumanCommunicationLearnedEvent:
    kitten: str
    teacher: str
    age_days: int
    day: int
    uses: tuple[str, ...]

    name: str = field(
        default="human_feline_communication_learned",
        init=False,
    )

    learned: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "uses",
            tuple(self.uses),
        )


@dataclass(slots=True, frozen=True)
class KittenMeowTeacherUnavailableEvent:
    kitten: str
    age_days: int
    day: int

    name: str = field(
        default="meow_teacher_unavailable",
        init=False,
    )

    transmitted: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class KittenFatherFoodDeliveryEvent:
    kitten: str
    father: str
    age_days: int
    day: int
    growth: object

    name: str = field(
        default="father_brought_dead_cronenberg",
        init=False,
    )

    prey_alive: bool = field(
        default=False,
        init=False,
    )

    purpose: str = field(
        default="family_food",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.growth,
            GROWTH_EVENT_TYPES,
        ):
            raise TypeError(
                "Father-delivery growth must be "
                "a kitten growth event object."
            )
