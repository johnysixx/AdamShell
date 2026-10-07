from dataclasses import dataclass, field

from cats.cat_maternal_care_result_state import (
    CatFosterMaternalCareEvent,
)


@dataclass(slots=True, frozen=True)
class CatOrphanRescueAssessment:
    kitten: str
    mother: str | None
    mother_available: bool
    needs_teaching: bool
    needs_milk: bool
    orphan_rescue_needed: bool

    name: str = field(
        default="cat_orphan_rescue_assessment",
        init=False,
    )

    def __post_init__(self):
        for attribute in (
            "mother_available",
            "needs_teaching",
            "needs_milk",
            "orphan_rescue_needed",
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
class CatEmergencyLactationAdviceEvent:
    instructor: str
    cat: str
    kittens: tuple[str, ...]
    advice: tuple[str, ...]

    name: str = field(
        default="garfield_advised_emergency_lactation",
        init=False,
    )

    advised: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "kittens",
            tuple(self.kittens),
        )

        object.__setattr__(
            self,
            "advice",
            tuple(self.advice),
        )


@dataclass(slots=True, frozen=True)
class CatOrphanArrivalRecord:
    name: str
    cat: str
    entered: bool
    already_inside: bool
    alarm_before_bartender: bool | None = None
    bartender_available: bool | None = None
    bartender_responded: bool | None = None
    alarm_after_bartender: bool | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "entered",
            bool(self.entered),
        )

        object.__setattr__(
            self,
            "already_inside",
            bool(self.already_inside),
        )

        for attribute in (
            "alarm_before_bartender",
            "bartender_available",
            "bartender_responded",
            "alarm_after_bartender",
        ):
            value = getattr(
                self,
                attribute,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    attribute,
                    bool(value),
                )


@dataclass(slots=True, frozen=True)
class CatOrphanTransportEvent:
    cat: str
    kittens: tuple[str, ...]
    arrivals: tuple[
        CatOrphanArrivalRecord,
        ...
    ]

    name: str = field(
        default="cat_brought_orphaned_kittens_to_bar",
        init=False,
    )

    transported: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "kittens",
            tuple(self.kittens),
        )

        object.__setattr__(
            self,
            "arrivals",
            tuple(self.arrivals),
        )


@dataclass(slots=True, frozen=True)
class CatOrphanRescueDeniedResult:
    reason: str
    cat: str | None = None
    assessments: tuple[
        CatOrphanRescueAssessment,
        ...
    ] = ()

    name: str = field(
        default="orphan_kitten_rescue_denied",
        init=False,
    )

    rescued: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "assessments",
            tuple(self.assessments),
        )


@dataclass(slots=True, frozen=True)
class CatOrphanRescueEvent:
    cat: str
    kittens: tuple[str, ...]
    bar: str
    transport: CatOrphanTransportEvent
    garfield_advice: CatEmergencyLactationAdviceEvent
    foster_events: tuple[
        CatFosterMaternalCareEvent,
        ...
    ]

    name: str = field(
        default="cat_rescued_orphaned_kittens",
        init=False,
    )

    lactation_induced: bool = field(
        default=True,
        init=False,
    )

    rescued: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "kittens",
            tuple(self.kittens),
        )

        object.__setattr__(
            self,
            "foster_events",
            tuple(self.foster_events),
        )
