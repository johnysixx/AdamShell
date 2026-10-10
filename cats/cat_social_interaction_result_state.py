from dataclasses import (
    dataclass,
    field,
)

from cats.cat_social_assessment_state import (
    CatSocialAssessment,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatSocialMeetingFailedResult:

    cat: str
    other_cat: str
    reason: str

    name: str = field(
        default="cat_social_meeting_failed",
        init=False,
    )

    socialized: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatSocialMeetingSkippedResult:

    cat: str
    other_cat: str
    reason: str

    name: str = field(
        default="cat_social_meeting_skipped",
        init=False,
    )

    socialized: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatSniffedCatEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_sniffed_cat",
        init=False,
    )

    contact: str = field(
        default="scent_inspection",
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatNoseTouchEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_nose_touch",
        init=False,
    )

    contact: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatSlowBlinkEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_slow_blink",
        init=False,
    )

    signal: str = field(
        default="friendly",
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatHeadBuntEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_head_bunt",
        init=False,
    )

    shared_scent: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatBodyRubEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_body_rub",
        init=False,
    )

    shared_scent: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatKeptSocialDistanceEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_kept_social_distance",
        init=False,
    )

    signal: str = field(
        default="uncertain",
        init=False,
    )

    escalated: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatHissedAtCatEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_hissed_at_cat",
        init=False,
    )

    warning: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatWarningSwatEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_warning_swat",
        init=False,
    )

    warning: bool = field(
        default=True,
        init=False,
    )

    injury: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatFightStartedEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_fight_started",
        init=False,
    )

    escalated: bool = field(
        default=True,
        init=False,
    )


CAT_SOCIAL_STEP_EVENT_TYPES = (
    CatSniffedCatEvent,
    CatNoseTouchEvent,
    CatSlowBlinkEvent,
    CatHeadBuntEvent,
    CatBodyRubEvent,
    CatKeptSocialDistanceEvent,
    CatHissedAtCatEvent,
    CatWarningSwatEvent,
    CatFightStartedEvent,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatSocialMeetingEvent:

    cat: str
    other_cat: str
    attitude: str

    cat_assessment: CatSocialAssessment
    other_cat_assessment: CatSocialAssessment

    steps: tuple[object, ...]
    outcome: str

    bond: object = None

    name: str = field(
        default="cat_social_meeting",
        init=False,
    )

    socialized: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.cat_assessment,
            CatSocialAssessment,
        ):
            raise TypeError(
                "Cat meeting assessment must be "
                "CatSocialAssessment."
            )

        if not isinstance(
            self.other_cat_assessment,
            CatSocialAssessment,
        ):
            raise TypeError(
                "Other cat meeting assessment must be "
                "CatSocialAssessment."
            )

        normalized_steps = tuple(
            self.steps
        )

        for step in normalized_steps:
            if not isinstance(
                step,
                CAT_SOCIAL_STEP_EVENT_TYPES,
            ):
                raise TypeError(
                    "Cat social meeting steps must "
                    "contain social step event objects."
                )

        object.__setattr__(
            self,
            "steps",
            normalized_steps,
        )
