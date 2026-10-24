from dataclasses import dataclass, field

from cats.duplicate_consumption_energy import (
    DuplicateConsumptionEnergyResolvedEvent,
    DuplicateConsumptionEnergyResolutionSkippedResult,
)
from meeting_place.bar_objects import (
    CatD20TurnEvent,
)


@dataclass(slots=True, frozen=True)
class CatD20ValueInterpretation:
    value: int

    name: str = field(
        default="cat_d20_value_interpreted",
        init=False,
    )

    meaning: str = field(
        init=False,
    )

    def __post_init__(self):
        value = int(
            self.value
        )

        if not 1 <= value <= 20:
            raise ValueError(
                "CatD20 value must be "
                "between 1 and 20."
            )

        if value <= 14:
            meaning = (
                "accept_navigation_offer"
            )

        elif value <= 18:
            meaning = (
                "decline_navigation_offer"
            )

        elif value == 19:
            meaning = (
                "cat_does_something_else"
            )

        else:
            meaning = (
                "cat_d20_surge"
            )

        object.__setattr__(
            self,
            "value",
            value,
        )

        object.__setattr__(
            self,
            "meaning",
            meaning,
        )

@dataclass(slots=True, frozen=True)
class CatD20TurnFailedResult:
    reason: str
    cat: str | None = None

    name: str = field(
        default="cat_d20_turn_failed",
        init=False,
    )

    turned: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "reason",
            str(
                self.reason
            ),
        )

        if self.cat is not None:
            object.__setattr__(
                self,
                "cat",
                str(
                    self.cat
                ),
            )

@dataclass(slots=True, frozen=True)
class CatD20TurnResult:
    turn: CatD20TurnEvent
    interpretation: CatD20ValueInterpretation
    duplicate_consumption_energy: (
        DuplicateConsumptionEnergyResolvedEvent
        | DuplicateConsumptionEnergyResolutionSkippedResult
    )

    def __post_init__(self):
        if not isinstance(
            self.turn,
            CatD20TurnEvent,
        ):
            raise TypeError(
                "CatD20 turn result requires "
                "CatD20TurnEvent."
            )

        if not isinstance(
            self.interpretation,
            CatD20ValueInterpretation,
        ):
            raise TypeError(
                "CatD20 turn result requires "
                "CatD20ValueInterpretation."
            )

        if (
            self.interpretation.value
            != self.turn.value
        ):
            raise ValueError(
                "CatD20 interpretation value "
                "must match turn value."
            )

        if not isinstance(
            self.duplicate_consumption_energy,
            (
                DuplicateConsumptionEnergyResolvedEvent,
                DuplicateConsumptionEnergyResolutionSkippedResult,
            ),
        ):
            raise TypeError(
                "CatD20 turn result requires "
                "a duplicate consumption "
                "energy result object."
            )

    @property
    def name(self):
        return self.turn.name

    @property
    def cat(self):
        return self.turn.cat

    @property
    def box(self):
        return self.turn.box

    @property
    def previous_value(self):
        return self.turn.previous_value

    @property
    def value(self):
        return self.turn.value

    @property
    def turn_number(self):
        return self.turn.turn_number

    @property
    def turned_by(self):
        return self.turn.turned_by

    @property
    def was_thrown(self):
        return self.turn.was_thrown

    @property
    def visibility(self):
        return self.turn.visibility

    @property
    def tick(self):
        return self.turn.tick

    @property
    def turned(self):
        return self.turn.turned
