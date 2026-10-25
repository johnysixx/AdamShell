from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrink,
)
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)
from meeting_place.bartender_event_state import (
    BartenderRefusedBetEvent,
)


@dataclass(slots=True, frozen=True)
class SerpentBornEvent:
    name: str = field(
        default="serpent_born",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class SerpentEnteredBarEvent:
    bar_time: str
    bar_hour: int
    bar_minute: int

    name: str = field(
        default="serpent_entered_bar",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "bar_time",
            str(
                self.bar_time
            ),
        )

        object.__setattr__(
            self,
            "bar_hour",
            int(
                self.bar_hour
            ),
        )

        object.__setattr__(
            self,
            "bar_minute",
            int(
                self.bar_minute
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "bar_time": self.bar_time,
            "bar_hour": self.bar_hour,
            "bar_minute": self.bar_minute,
        }


@dataclass(slots=True, frozen=True)
class SerpentOrdersFirstDrinksEvent:
    drinks: tuple[str, ...] = (
        "wine",
        "beer",
        "mead",
    )

    name: str = field(
        default=(
            "serpent_orders_"
            "wine_beer_and_mead"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drinks",
            tuple(
                str(drink)
                for drink
                in self.drinks
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class SerpentFirstDrinksServiceResult:
    drinks: tuple[BarDrink, ...]
    receipt: BarReceiptState
    payment: object | None
    tab_status: str
    event: SerpentOrdersFirstDrinksEvent

    def __post_init__(self):
        drinks = tuple(
            self.drinks
        )

        if not all(
            isinstance(
                drink,
                BarDrink,
            )
            for drink in drinks
        ):
            raise TypeError(
                "Serpent first drinks must "
                "contain BarDrink objects."
            )

        if not isinstance(
            self.receipt,
            BarReceiptState,
        ):
            raise TypeError(
                "Serpent first drinks receipt "
                "must be BarReceiptState."
            )

        if not isinstance(
            self.event,
            SerpentOrdersFirstDrinksEvent,
        ):
            raise TypeError(
                "Serpent first drinks event "
                "must be object state."
            )

        object.__setattr__(
            self,
            "drinks",
            drinks,
        )

        object.__setattr__(
            self,
            "tab_status",
            str(
                self.tab_status
            ),
        )


@dataclass(slots=True, frozen=True)
class SerpentProposesBetEvent:
    name: str = field(
        default="serpent_proposes_bet",
        init=False,
    )
    guest: str = field(
        default="serpent",
        init=False,
    )
    target: str = field(
        default="bartender",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "target": self.target,
        }


@dataclass(slots=True, frozen=True)
class SerpentBetProposalResult:
    proposal: SerpentProposesBetEvent
    response: BartenderRefusedBetEvent

    def __post_init__(self):
        if not isinstance(
            self.proposal,
            SerpentProposesBetEvent,
        ):
            raise TypeError(
                "Serpent bet proposal must "
                "be object state."
            )

        if not isinstance(
            self.response,
            BartenderRefusedBetEvent,
        ):
            raise TypeError(
                "Serpent bet response must "
                "be BartenderRefusedBetEvent."
            )
