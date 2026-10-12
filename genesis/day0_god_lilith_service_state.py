from dataclasses import dataclass, field

from core.entity.cronenberg import Cronenberg
from meeting_place.bar_objects import BarDrink
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)


@dataclass(slots=True, frozen=True)
class GodsLilithFailsWithoutLemonEvent:
    name: str = field(
        default="gods_lilith_fails_without_lemon",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    reason: str = field(
        default="no_lemon",
        init=False,
    )
    cronenberg_created: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "reason": self.reason,
            "cronenberg_created":
                self.cronenberg_created,
        }


@dataclass(slots=True, frozen=True)
class GodsLilithFailureResult:
    event: GodsLilithFailsWithoutLemonEvent
    cronenberg: Cronenberg

    def __post_init__(self):
        if not isinstance(
            self.event,
            GodsLilithFailsWithoutLemonEvent,
        ):
            raise TypeError(
                "God's Lilith failure requires "
                "GodsLilithFailsWithoutLemonEvent."
            )

        if not isinstance(
            self.cronenberg,
            Cronenberg,
        ):
            raise TypeError(
                "God's Lilith failure requires "
                "a Cronenberg object."
            )


@dataclass(slots=True, frozen=True)
class BartenderMixesGodsLilithEvent:
    sugar_cubes_used: int
    lemons_remaining: int

    name: str = field(
        default="bartender_mixes_gods_lilith",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    lemon_used: int = field(
        default=1,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "sugar_cubes_used",
            int(self.sugar_cubes_used),
        )
        object.__setattr__(
            self,
            "lemons_remaining",
            int(self.lemons_remaining),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "lemon_used": self.lemon_used,
            "sugar_cubes_used":
                self.sugar_cubes_used,
            "lemons_remaining":
                self.lemons_remaining,
        }


@dataclass(slots=True, frozen=True)
class BartenderServesGodsLilithEvent:
    receipt_number: int

    name: str = field(
        default="bartender_serves_gods_lilith",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    paid: bool = field(
        default=False,
        init=False,
    )
    drunk: bool = field(
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
            "drunk": self.drunk,
        }


@dataclass(slots=True, frozen=True)
class GodsLilithServiceResult:
    drink: BarDrink
    receipt: BarReceiptState

    def __post_init__(self):
        if not isinstance(
            self.drink,
            BarDrink,
        ):
            raise TypeError(
                "God's Lilith service requires "
                "a BarDrink object."
            )

        if not isinstance(
            self.receipt,
            BarReceiptState,
        ):
            raise TypeError(
                "God's Lilith service requires "
                "a BarReceiptState object."
            )

    def to_dict(self):
        return {
            "drink": self.drink.to_dict(),
            "receipt": self.receipt.to_dict(),
        }
