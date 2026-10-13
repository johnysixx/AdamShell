from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrink,
    BarWagerDecisionMethod,
)


@dataclass(slots=True, frozen=True)
class SerpentOrdersWaterEvent:
    name: str = field(
        default="serpent_orders_water",
        init=False,
    )
    guest: str = field(
        default="serpent",
        init=False,
    )
    drink: str = field(
        default="water",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class BartenderServesSerpentWaterEvent:
    name: str = field(
        default=(
            "bartender_serves_serpent_water_"
            "with_free_lemon_slice"
        ),
        init=False,
    )
    guest: str = field(
        default="serpent",
        init=False,
    )
    drink: str = field(
        default="water",
        init=False,
    )
    lemon_slice: bool = field(
        default=True,
        init=False,
    )
    lemon_slice_price: int = field(
        default=0,
        init=False,
    )
    whole_lemon_consumed: bool = field(
        default=False,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "lemon_slice": self.lemon_slice,
            "lemon_slice_price":
                self.lemon_slice_price,
            "whole_lemon_consumed":
                self.whole_lemon_consumed,
        }


@dataclass(slots=True, frozen=True)
class SerpentWaterServiceResult:
    drink: BarDrink
    event: BartenderServesSerpentWaterEvent

    def __post_init__(self):
        if not isinstance(
            self.drink,
            BarDrink,
        ):
            raise TypeError(
                "Water service result requires "
                "BarDrink."
            )

        if not isinstance(
            self.event,
            BartenderServesSerpentWaterEvent,
        ):
            raise TypeError(
                "Water service result requires "
                "BartenderServesSerpentWaterEvent."
            )

    def to_dict(self):
        return {
            "drink": self.drink.to_dict(),
            "event": self.event.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class WagerDecisionMethodSnapshot:
    type: str
    voters: tuple[str, ...] = ()
    judges: tuple[str, ...] = ()
    judge: str | None = None
    proposed_by: str | None = None
    proposed: bool | None = None
    accepted: bool | None = None

    @classmethod
    def from_method(
        cls,
        method,
    ):
        if not isinstance(
            method,
            BarWagerDecisionMethod,
        ):
            raise TypeError(
                "Decision method snapshot requires "
                "BarWagerDecisionMethod."
            )

        return cls(
            type=method.type,
            voters=tuple(
                method.voters
            ),
            judges=tuple(
                method.judges
            ),
            judge=method.judge,
            proposed_by=method.proposed_by,
            proposed=method.proposed,
            accepted=method.accepted,
        )

    def to_dict(self):
        result = {
            "type": self.type,
        }

        if self.voters:
            result["voters"] = list(
                self.voters
            )

        if self.judges:
            result["judges"] = list(
                self.judges
            )

        if self.judge is not None:
            result["judge"] = self.judge

        if self.proposed_by is not None:
            result["proposed_by"] = (
                self.proposed_by
            )

        if self.proposed is not None:
            result["proposed"] = (
                self.proposed
            )

        if self.accepted is not None:
            result["accepted"] = (
                self.accepted
            )

        return result


@dataclass(slots=True, frozen=True)
class GodRejectsParticipantVoteEvent:
    rejects: WagerDecisionMethodSnapshot
    proposes: WagerDecisionMethodSnapshot

    name: str = field(
        default=(
            "god_rejects_participant_vote_"
            "and_proposes_bartender"
        ),
        init=False,
    )
    speaker: str = field(
        default="god",
        init=False,
    )

    def __post_init__(self):
        for value in (
            self.rejects,
            self.proposes,
        ):
            if not isinstance(
                value,
                WagerDecisionMethodSnapshot,
            ):
                raise TypeError(
                    "Judge proposal event requires "
                    "WagerDecisionMethodSnapshot."
                )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "rejects": self.rejects.to_dict(),
            "proposes": self.proposes.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class LilithGodMoveToBarEvent:
    guests: tuple[str, ...] = (
        "lilith",
        "god",
    )

    name: str = field(
        default="lilith_and_god_move_to_bar",
        init=False,
    )
    from_location: str = field(
        default="table",
        init=False,
    )
    to_location: str = field(
        default="bar_counter",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "guests",
            tuple(
                str(guest)
                for guest
                in self.guests
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guests": list(
                self.guests
            ),
            "from": self.from_location,
            "to": self.to_location,
        }
