from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrink,
)
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)


@dataclass(slots=True, frozen=True)
class BouncerOrdersTastingDrinksEvent:
    drinks: tuple[str, ...] = (
        "wine",
        "mead",
        "beer",
    )

    name: str = field(
        default="bouncer_orders_tasting_drinks",
        init=False,
    )
    bouncer: str = field(
        default="bouncer",
        init=False,
    )
    purpose: str = field(
        default="judge_wager",
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
            "bouncer": self.bouncer,
            "drinks": list(
                self.drinks
            ),
            "purpose": self.purpose,
        }


@dataclass(slots=True, frozen=True)
class BartenderServesBouncerTastingDrinksEvent:
    receipt_number: int
    drinks: tuple[str, ...] = (
        "wine",
        "mead",
        "beer",
    )

    name: str = field(
        default=(
            "bartender_serves_bouncer_"
            "tasting_drinks"
        ),
        init=False,
    )
    bartender: str = field(
        default="bartender",
        init=False,
    )
    bouncer: str = field(
        default="bouncer",
        init=False,
    )
    receipt_kind: str = field(
        default="staff_purchase",
        init=False,
    )
    paid: bool = field(
        default=False,
        init=False,
    )
    charge: int = field(
        default=0,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "receipt_number",
            int(
                self.receipt_number
            ),
        )

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
            "bartender": self.bartender,
            "bouncer": self.bouncer,
            "drinks": list(
                self.drinks
            ),
            "receipt_number":
                self.receipt_number,
            "receipt_kind":
                self.receipt_kind,
            "paid": self.paid,
            "charge": self.charge,
        }


@dataclass(slots=True, frozen=True)
class BouncerTastingServiceResult:
    drinks: tuple[BarDrink, ...]
    receipt: BarReceiptState
    order_event: BouncerOrdersTastingDrinksEvent
    served_event: BartenderServesBouncerTastingDrinksEvent

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
                "Bouncer tasting service drinks "
                "must be BarDrink objects."
            )

        if not isinstance(
            self.receipt,
            BarReceiptState,
        ):
            raise TypeError(
                "Bouncer tasting service receipt "
                "must be BarReceiptState."
            )

        if not isinstance(
            self.order_event,
            BouncerOrdersTastingDrinksEvent,
        ):
            raise TypeError(
                "Bouncer tasting service order "
                "must be object state."
            )

        if not isinstance(
            self.served_event,
            BartenderServesBouncerTastingDrinksEvent,
        ):
            raise TypeError(
                "Bouncer tasting service served "
                "event must be object state."
            )

        if (
            self.served_event.receipt_number
            != self.receipt.receipt_number
        ):
            raise ValueError(
                "Bouncer tasting service receipt "
                "number mismatch."
            )

        object.__setattr__(
            self,
            "drinks",
            drinks,
        )


@dataclass(slots=True, frozen=True)
class BouncerTastesDrinkEvent:
    drink: str

    name: str = field(
        default="bouncer_tastes_drink",
        init=False,
    )
    bouncer: str = field(
        default="bouncer",
        init=False,
    )
    purpose: str = field(
        default="judge_wager",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(
                self.drink
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "bouncer": self.bouncer,
            "drink": self.drink,
            "purpose": self.purpose,
        }


@dataclass(slots=True, frozen=True)
class BouncerInitialDrinkVerdictEvent:
    drinks: tuple[str, ...] = (
        "wine",
        "mead",
        "beer",
    )

    name: str = field(
        default=(
            "bouncer_gives_initial_"
            "drink_verdict"
        ),
        init=False,
    )
    bouncer: str = field(
        default="bouncer",
        init=False,
    )
    verdict: str = field(
        default="disgusting",
        init=False,
    )
    statement: str = field(
        default="this_is_disgusting",
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
            "bouncer": self.bouncer,
            "drinks": list(
                self.drinks
            ),
            "verdict": self.verdict,
            "statement": self.statement,
        }


@dataclass(slots=True, frozen=True)
class BouncerAcceptsWagerJudgeRoleEvent:
    name: str = field(
        default=(
            "bouncer_accepts_wager_"
            "judge_role"
        ),
        init=False,
    )
    bouncer: str = field(
        default="bouncer",
        init=False,
    )
    role: str = field(
        default="tasting_judge",
        init=False,
    )
    accepted: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "bouncer": self.bouncer,
            "role": self.role,
            "accepted": self.accepted,
        }


@dataclass(slots=True, frozen=True)
class BouncerJudgeAcceptanceResult:
    tastings: tuple[
        BouncerTastesDrinkEvent,
        ...
    ]
    verdict: BouncerInitialDrinkVerdictEvent
    accepted: BouncerAcceptsWagerJudgeRoleEvent
    receipt: BarReceiptState

    def __post_init__(self):
        tastings = tuple(
            self.tastings
        )

        if not all(
            isinstance(
                event,
                BouncerTastesDrinkEvent,
            )
            for event in tastings
        ):
            raise TypeError(
                "Bouncer tasting results must "
                "contain object events."
            )

        if not isinstance(
            self.verdict,
            BouncerInitialDrinkVerdictEvent,
        ):
            raise TypeError(
                "Bouncer verdict must be "
                "object state."
            )

        if not isinstance(
            self.accepted,
            BouncerAcceptsWagerJudgeRoleEvent,
        ):
            raise TypeError(
                "Bouncer judge acceptance must "
                "be object state."
            )

        if not isinstance(
            self.receipt,
            BarReceiptState,
        ):
            raise TypeError(
                "Bouncer judge result receipt "
                "must be BarReceiptState."
            )

        object.__setattr__(
            self,
            "tastings",
            tastings,
        )
