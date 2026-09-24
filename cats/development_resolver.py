from dataclasses import dataclass, field

from cats.physical_biology_gate import (
    PhysicalBiologyGate
)
from cats.cat_learning import (
    CatLearning
)
from cats.cat import Cat
from cats.cat_parentage_state import (
    CatParentageState
)


@dataclass(slots=True, frozen=True)
class CatDevelopmentStageTransition:

    day: int
    stage: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "day",
            int(self.day),
        )

        object.__setattr__(
            self,
            "stage",
            str(self.stage),
        )

    def to_dict(self):
        return {
            "day": self.day,
            "stage": self.stage,
        }


@dataclass(slots=True, frozen=True)
class NewbornCatDevelopmentInitializedEvent:

    cat: str
    birth_day: int | None = None

    name: str = field(
        default=(
            "newborn_cat_development_initialized"
        ),
        init=False,
    )

    age_days: int = field(
        default=0,
        init=False,
    )

    stage: str = field(
        default="newborn",
        init=False,
    )

    fertile: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        if self.birth_day is not None:
            object.__setattr__(
                self,
                "birth_day",
                int(self.birth_day),
            )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "age_days": self.age_days,
            "stage": self.stage,
            "fertile": self.fertile,
            "birth_day": self.birth_day,
        }


@dataclass(slots=True, frozen=True)
class CatAgeAdvancedEvent:

    cat: str
    days_advanced: int
    previous_age_days: int
    age_days: int
    previous_stage: str
    stage: str
    transitions: tuple[
        CatDevelopmentStageTransition,
        ...,
    ]
    reproductive_maturity: bool
    fertile: bool

    name: str = field(
        default="cat_age_advanced",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        for field_name in (
            "days_advanced",
            "previous_age_days",
            "age_days",
        ):
            object.__setattr__(
                self,
                field_name,
                int(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

        object.__setattr__(
            self,
            "previous_stage",
            str(self.previous_stage),
        )

        object.__setattr__(
            self,
            "stage",
            str(self.stage),
        )

        transitions = tuple(
            self.transitions
        )

        if not all(
            isinstance(
                transition,
                CatDevelopmentStageTransition,
            )
            for transition
            in transitions
        ):
            raise TypeError(
                "Development transitions require "
                "CatDevelopmentStageTransition "
                "objects."
            )

        object.__setattr__(
            self,
            "transitions",
            transitions,
        )

        object.__setattr__(
            self,
            "reproductive_maturity",
            bool(
                self.reproductive_maturity
            ),
        )

        object.__setattr__(
            self,
            "fertile",
            bool(self.fertile),
        )

    @property
    def stage_changed(self):
        return (
            self.previous_stage
            != self.stage
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "days_advanced": (
                self.days_advanced
            ),
            "previous_age_days": (
                self.previous_age_days
            ),
            "age_days": self.age_days,
            "previous_stage": (
                self.previous_stage
            ),
            "stage": self.stage,
            "stage_changed": (
                self.stage_changed
            ),
            "transitions": [
                transition.to_dict()
                for transition
                in self.transitions
            ],
            "reproductive_maturity": (
                self.reproductive_maturity
            ),
            "fertile": self.fertile,
        }


class CatDevelopmentResolver:

    SEXUAL_MATURITY_DAY = 180
    ADULTHOOD_DAY = 365

    STAGES = (
        (0, "newborn"),
        (14, "socializing_kitten"),
        (49, "playful_kitten"),
        (98, "juvenile"),
        (180, "adolescent"),
        (365, "adult")
    )

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

        self.biology_gate = (
            PhysicalBiologyGate(
                universe
            )
        )

    def initialize_newborn(
        self,
        cat,
        birth_day=None
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatDevelopmentResolver requires Cat."
            )

        reproduction = (
            cat.reproduction
        )

        cat.age_days = 0
        cat.birth_day = birth_day
        cat.developmental_stage = (
            "newborn"
        )

        parentage = (
            CatParentageState
            .require_from_cat(cat)
        )

        parentage.mother = (
            cat.mother_name
        )

        cat.learning = (
            CatLearning.create_newborn_state(
                mother_name=cat.mother_name
            )
        )

        reproduction.developmental_stage = "newborn"

        reproduction.reproductive_maturity = False

        reproduction.fertile = False

        event = (
            NewbornCatDevelopmentInitializedEvent(
                cat=cat.name,
                birth_day=birth_day,
            )
        )

        self.record_event(
            event
        )

        return event.to_dict()

    def advance_age(
        self,
        cat,
        days=1
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatDevelopmentResolver requires Cat."
            )

        biology = (
            self.biology_gate
            .require_physical_world(
                operation="advance_cat_age",
                cat=cat
            )
        )

        if not biology["allowed"]:
            return biology

        days = int(days)

        if days < 1:
            raise ValueError(
                "Cat age must advance by at "
                "least one day."
            )

        previous_age = int(
            cat.age_days
        )

        previous_stage = (
            cat.developmental_stage
            or self.stage_for_age(
                previous_age
            )
        )

        new_age = previous_age + days
        new_stage = self.stage_for_age(
            new_age
        )

        cat.age_days = new_age
        cat.developmental_stage = (
            new_stage
        )

        reproduction = (
            cat.reproduction
        )

        reproduction.developmental_stage = new_stage

        sexually_mature = (
            new_age
            >= self.SEXUAL_MATURITY_DAY
        )

        reproduction.reproductive_maturity = sexually_mature

        if reproduction.neutered:
            reproduction.fertile = False

        else:
            reproduction.fertile = (
                sexually_mature
            )

        transitions = self._collect_transitions(
            previous_age=previous_age,
            new_age=new_age
        )

        event = CatAgeAdvancedEvent(
            cat=cat.name,
            days_advanced=days,
            previous_age_days=previous_age,
            age_days=new_age,
            previous_stage=previous_stage,
            stage=new_stage,
            transitions=tuple(
                transitions
            ),
            reproductive_maturity=(
                sexually_mature
            ),
            fertile=reproduction.fertile,
        )

        self.record_event(
            event
        )

        snapshot = event.to_dict()

        if hasattr(
            self.universe,
            "quantum_events"
        ):
            self.universe.quantum_events.append(
                event.to_dict()
            )

        return snapshot

    @classmethod
    def stage_for_age(
        cls,
        age_days
    ):
        age_days = int(age_days)

        if age_days < 0:
            raise ValueError(
                "Cat age cannot be negative."
            )

        stage = "newborn"

        for minimum_age, candidate in (
            cls.STAGES
        ):
            if age_days >= minimum_age:
                stage = candidate
            else:
                break

        return stage

    @classmethod
    def _collect_transitions(
        cls,
        previous_age,
        new_age
    ):
        return [
            CatDevelopmentStageTransition(
                day=minimum_age,
                stage=stage,
            )
            for minimum_age, stage
            in cls.STAGES
            if (
                previous_age
                < minimum_age
                <= new_age
            )
        ]

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                NewbornCatDevelopmentInitializedEvent,
                CatAgeAdvancedEvent,
            ),
        ):
            raise TypeError(
                "Cat development history requires "
                "a development event object."
            )

        self.history.append(
            event
        )

        return event
