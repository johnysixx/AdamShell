from dataclasses import dataclass

from meeting_place.bar_objects import BarDrink
from meeting_place.bar_receipt_state import BarReceiptState
from meeting_place.bar_payment_state import BarPaymentState


@dataclass(slots=True, frozen=True)
class BarBasicDrinksOnTabResult:
    drinks: tuple[BarDrink, ...]
    receipt: BarReceiptState
    payment: BarPaymentState | None
    tab_status: str

    def __post_init__(self):
        drinks = tuple(self.drinks)

        if not drinks or not all(
            isinstance(drink, BarDrink)
            for drink in drinks
        ):
            raise TypeError(
                "Basic tab drinks must be BarDrink objects."
            )

        if not isinstance(self.receipt, BarReceiptState):
            raise TypeError(
                "Basic tab receipt must be BarReceiptState."
            )

        if (
            self.payment is not None
            and not isinstance(self.payment, BarPaymentState)
        ):
            raise TypeError(
                "Payment must be BarPaymentState or None."
            )

        object.__setattr__(self, "drinks", drinks)
        object.__setattr__(
            self, "tab_status", str(self.tab_status)
        )
