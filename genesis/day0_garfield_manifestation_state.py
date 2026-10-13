from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    CatD20Profile,
)
from meeting_place.cat_arrival_state import (
    CatBarArrivalResult,
)


@dataclass(slots=True, frozen=True)
class GarfieldArrivesAtBarEvent:
    arrival: CatBarArrivalResult
    created: bool

    name: str = field(
        default="garfield_arrives_at_bar",
        init=False,
    )
    cat: str = field(
        default="garfield",
        init=False,
    )
    source: str = field(
        default="cat_d20",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.arrival,
            CatBarArrivalResult,
        ):
            raise TypeError(
                "Garfield arrival event requires "
                "CatBarArrivalResult."
            )

        object.__setattr__(
            self,
            "created",
            bool(self.created),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "source": self.source,
            "created": self.created,
            "arrival": {
                "name": self.arrival.name,
                "cat": self.arrival.cat,
                "entered":
                    self.arrival.entered,
                "already_inside":
                    self.arrival.already_inside,
                "alarm_before_bartender":
                    self.arrival
                    .alarm_before_bartender,
                "bartender_available":
                    self.arrival
                    .bartender_available,
                "bartender_responded":
                    self.arrival
                    .bartender_responded,
                "alarm_after_bartender":
                    self.arrival
                    .alarm_after_bartender,
            },
        }


@dataclass(slots=True, frozen=True)
class GarfieldArrivalResult:
    garfield: object
    event: GarfieldArrivesAtBarEvent
    profile: CatD20Profile
    ordinary_arrival: CatBarArrivalResult

    def __post_init__(self):
        if not isinstance(
            self.event,
            GarfieldArrivesAtBarEvent,
        ):
            raise TypeError(
                "Garfield arrival result requires "
                "GarfieldArrivesAtBarEvent."
            )

        if not isinstance(
            self.profile,
            CatD20Profile,
        ):
            raise TypeError(
                "Garfield arrival result requires "
                "CatD20Profile."
            )

        if not isinstance(
            self.ordinary_arrival,
            CatBarArrivalResult,
        ):
            raise TypeError(
                "Garfield arrival result requires "
                "CatBarArrivalResult."
            )

        if (
            self.event.arrival
            is not self.ordinary_arrival
        ):
            raise ValueError(
                "Garfield arrival event and result "
                "must share ordinary arrival."
            )
