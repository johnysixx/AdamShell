from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrinkOrder,
    BarIngredientStock,
)
from meeting_place.bar_yard_event_state import (
    LemonPickedResult,
)
from meeting_place.bartender_event_state import (
    BartenderLeftForLemonEvent,
    BartenderReturnedWithLemonEvent,
)


@dataclass(slots=True, frozen=True)
class LilithVodkaWithLemonOrderedEvent:
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="vodka_with_lemon",
        init=False,
    )
    name: str = field(
        default="lilith_orders_vodka_with_lemon",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class BartenderReportsMissingLemonEvent:
    guest: str

    name: str = field(
        default="bartender_reports_missing_lemon",
        init=False,
    )
    ingredient: str = field(
        default="lemon",
        init=False,
    )
    available: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "guest",
            str(self.guest),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "ingredient": self.ingredient,
            "available": self.available,
        }


@dataclass(slots=True, frozen=True)
class LilithPointsOutLemonTreeEvent:
    guest: str = field(
        default="lilith",
        init=False,
    )
    location: str = field(
        default="bar_yard",
        init=False,
    )
    tree: str = field(
        default="lemon_tree",
        init=False,
    )
    name: str = field(
        default="lilith_points_out_lemon_tree",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "location": self.location,
            "tree": self.tree,
        }


@dataclass(slots=True, frozen=True)
class LemonAddedToBarStockEvent:
    amount: int

    name: str = field(
        default="lemon_added_to_bar_stock",
        init=False,
    )
    ingredient: str = field(
        default="lemon",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "amount",
            int(self.amount),
        )

        if self.amount <= 0:
            raise ValueError(
                "Lemon stock addition must be positive."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "amount": self.amount,
        }


@dataclass(slots=True, frozen=True)
class BartenderLemonRestockStartedEvent:
    target_amount: int

    name: str = field(
        default="bartender_runs_to_yard_for_more_lemons",
        init=False,
    )
    destination: str = field(
        default="bar_yard",
        init=False,
    )
    reason: str = field(
        default="restock_lemons",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "target_amount",
            int(self.target_amount),
        )

        if self.target_amount <= 1:
            raise ValueError(
                "Lemon restock must request more than one lemon."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "destination": self.destination,
            "reason": self.reason,
            "target_amount": self.target_amount,
        }


@dataclass(slots=True, frozen=True)
class BartenderLemonRestockReturnedEvent:
    amount: int
    stock_after: int

    name: str = field(
        default="bartender_returns_with_lemon_stock",
        init=False,
    )
    source: str = field(
        default="bar_yard",
        init=False,
    )
    ingredient: str = field(
        default="lemon",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "amount",
            int(self.amount),
        )
        object.__setattr__(
            self,
            "stock_after",
            int(self.stock_after),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "source": self.source,
            "ingredient": self.ingredient,
            "amount": self.amount,
            "stock_after": self.stock_after,
        }


@dataclass(slots=True, frozen=True)
class LilithVodkaWithLemonOrderResult:
    order: BarDrinkOrder
    bartender: BartenderLeftForLemonEvent

    def __post_init__(self):
        if not isinstance(
            self.order,
            BarDrinkOrder,
        ):
            raise TypeError(
                "Lilith lemon order result requires "
                "a BarDrinkOrder object."
            )

        if not isinstance(
            self.bartender,
            BartenderLeftForLemonEvent,
        ):
            raise TypeError(
                "Lilith lemon order result requires "
                "a BartenderLeftForLemonEvent object."
            )

    def to_dict(self):
        return {
            "order": self.order.to_dict(),
            "bartender": self.bartender.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class BartenderLemonReturnResult:
    picked: LemonPickedResult
    stock: BarIngredientStock
    returned: BartenderReturnedWithLemonEvent

    def __post_init__(self):
        if not isinstance(
            self.picked,
            LemonPickedResult,
        ):
            raise TypeError(
                "Bartender lemon return requires "
                "a LemonPickedResult object."
            )

        if not isinstance(
            self.stock,
            BarIngredientStock,
        ):
            raise TypeError(
                "Bartender lemon return requires "
                "a BarIngredientStock object."
            )

        if not isinstance(
            self.returned,
            BartenderReturnedWithLemonEvent,
        ):
            raise TypeError(
                "Bartender lemon return requires "
                "a BartenderReturnedWithLemonEvent object."
            )

    def to_dict(self):
        return {
            "picked": self.picked.to_dict(),
            "stock": self.stock.to_dict(),
            "returned": self.returned.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class BartenderLemonRestockResult:
    picked: tuple
    returned: BartenderLemonRestockReturnedEvent
    stock: BarIngredientStock

    def __post_init__(self):
        picked = tuple(
            self.picked
        )

        for result in picked:
            if not isinstance(
                result,
                LemonPickedResult,
            ):
                raise TypeError(
                    "Lemon restock requires typed "
                    "LemonPickedResult objects."
                )

        if not isinstance(
            self.returned,
            BartenderLemonRestockReturnedEvent,
        ):
            raise TypeError(
                "Lemon restock requires a typed "
                "return event."
            )

        if not isinstance(
            self.stock,
            BarIngredientStock,
        ):
            raise TypeError(
                "Lemon restock requires a "
                "BarIngredientStock object."
            )

        if (
            len(picked)
            != self.returned.amount
        ):
            raise ValueError(
                "Picked lemon count must match "
                "the returned amount."
            )

        object.__setattr__(
            self,
            "picked",
            picked,
        )

    def to_dict(self):
        return {
            "picked": [
                result.to_dict()
                for result in self.picked
            ],
            "returned":
                self.returned.to_dict(),
            "stock":
                self.stock.to_dict(),
        }
