from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrink,
)
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)


@dataclass(slots=True, frozen=True)
class SerpentGrimacesAtLilithEvent:
    name: str = field(
        default=(
            "serpent_grimaces_at_lilith_"
            "and_turns_to_god"
        ),
        init=False,
    )
    serpent: str = field(
        default="serpent",
        init=False,
    )
    reaction: str = field(
        default="grimace",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    turns_to: str = field(
        default="god",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "serpent": self.serpent,
            "reaction": self.reaction,
            "drink": self.drink,
            "turns_to": self.turns_to,
        }


@dataclass(slots=True, frozen=True)
class GodOrdersWineToJudgeDiscussionEvent:
    name: str = field(
        default=(
            "god_orders_wine_to_"
            "judge_discussion"
        ),
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="wine",
        init=False,
    )
    purpose: str = field(
        default="judge_wine_discussion",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "purpose": self.purpose,
        }


@dataclass(slots=True, frozen=True)
class BartenderServesGodWineEvent:
    receipt_number: int

    name: str = field(
        default=(
            "bartender_serves_god_"
            "wine_and_receipt"
        ),
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="wine",
        init=False,
    )
    paid: bool = field(
        default=False,
        init=False,
    )
    tasted: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "receipt_number",
            int(self.receipt_number),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "receipt_number":
                self.receipt_number,
            "paid": self.paid,
            "tasted": self.tasted,
        }


@dataclass(slots=True, frozen=True)
class GodWineServiceResult:
    drink: BarDrink
    receipt: BarReceiptState
    event: BartenderServesGodWineEvent

    def __post_init__(self):
        if not isinstance(
            self.drink,
            BarDrink,
        ):
            raise TypeError(
                "God wine service requires "
                "a BarDrink object."
            )

        if not isinstance(
            self.receipt,
            BarReceiptState,
        ):
            raise TypeError(
                "God wine service requires "
                "a BarReceiptState object."
            )

        if not isinstance(
            self.event,
            BartenderServesGodWineEvent,
        ):
            raise TypeError(
                "God wine service requires "
                "BartenderServesGodWineEvent."
            )

    def to_dict(self):
        return {
            "drink":
                self.drink.to_dict(),
            "receipt":
                self.receipt.to_dict(),
            "event":
                self.event.to_dict(),
        }
