from dataclasses import dataclass, field

from meeting_place.bar_objects import BarTabItem
from meeting_place.bar_payment_state import BarPaymentState
from meeting_place.bar_payment_kind import BarPaymentKind


@dataclass(slots=True)
class BarReceiptState:
    receipt_number: int
    type: str
    guest: str | None
    guest_type: str | None
    receipt_kind: str | None = None
    status: str | None = None
    paid: bool | None = None
    items: list[BarTabItem] = field(default_factory=list)
    payment: BarPaymentState | None = None
    message: str | None = None
    drink: str | None = None
    drink_category: str | None = None
    charge: float | int | None = None

    def __post_init__(self):
        if self.payment is not None and not isinstance(self.payment, BarPaymentState):
            raise TypeError("Receipt payment must be BarPaymentState or None.")

    def to_dict(self):
        payment_state = None

        if self.payment is not None:
            payment_state = {
                "name":
                    self.payment.name,
                "entity":
                    self.payment.entity,
                "payment_kind":
                    self.payment.payment_kind.value,
            }

            for name, value in (
                (
                    "existence_paid_pct",
                    self.payment.existence_paid_pct,
                ),
                (
                    "energy_paid_j",
                    self.payment.energy_paid_j,
                ),
                (
                    "idea_existence_gain_pct",
                    self.payment.idea_existence_gain_pct,
                ),
                (
                    "existence_converted_to_energy_pct",
                    self.payment.existence_converted_to_energy_pct,
                ),
                (
                    "generated_energy_j",
                    self.payment.generated_energy_j,
                ),
                (
                    "bar_energy_j",
                    self.payment.bar_energy_j,
                ),
            ):
                if value is not None:
                    payment_state[
                        name
                    ] = value

            if (
                self.payment.entity_type
                is not None
                or self.payment.payment_kind
                is BarPaymentKind.UNSUPPORTED
            ):
                payment_state[
                    "entity_type"
                ] = (
                    self.payment.entity_type
                )

        result = {
            "receipt_number":
                self.receipt_number,
            "type":
                self.type,
            "guest":
                self.guest,
            "guest_type":
                self.guest_type,
            "payment":
                payment_state,
        }

        if self.receipt_kind is not None:
            result[
                "receipt_kind"
            ] = self.receipt_kind

        if self.status is not None:
            result[
                "status"
            ] = self.status

        if self.paid is not None:
            result[
                "paid"
            ] = self.paid

        if (
            self.items
            or self.type
            == "bar_open_tab_receipt"
            or self.receipt_kind
            == "staff_purchase"
        ):
            result["items"] = [
                {
                    "drink":
                        item.drink,
                    "drink_category":
                        item.drink_category,
                }
                for item
                in self.items
            ]

        if self.message is not None:
            result[
                "message"
            ] = self.message

        if self.drink is not None:
            result[
                "drink"
            ] = self.drink
            result[
                "drink_category"
            ] = self.drink_category

        if self.charge is not None:
            result[
                "charge"
            ] = self.charge

        return result
