from dataclasses import dataclass

from meeting_place.bar_objects import BarDrink
from meeting_place.bar_payment_state import BarPaymentState
from meeting_place.bar_receipt_state import BarReceiptState


@dataclass(slots=True, frozen=True)
class BarBasicDrinkServiceResult:
    drink: BarDrink
    payment: BarPaymentState
    receipt: BarReceiptState

    def __post_init__(self):
        if not isinstance(self.drink, BarDrink):
            raise TypeError(
                "Basic drink service requires BarDrink."
            )

        if not isinstance(self.payment, BarPaymentState):
            raise TypeError(
                "Basic drink service requires BarPaymentState."
            )

        if not isinstance(self.receipt, BarReceiptState):
            raise TypeError(
                "Basic drink service requires BarReceiptState."
            )
