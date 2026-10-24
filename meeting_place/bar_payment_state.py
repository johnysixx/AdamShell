from dataclasses import dataclass

from meeting_place.bar_payment_kind import (
    BarPaymentKind,
)


@dataclass(slots=True)
class BarPaymentState:
    name: str
    entity: str | None
    payment_kind: BarPaymentKind
    existence_paid_pct: float | None = None
    energy_paid_j: float | None = None
    idea_existence_gain_pct: float | None = None
    existence_converted_to_energy_pct: float | None = None
    generated_energy_j: float | None = None
    bar_energy_j: float | None = None
    entity_type: str | None = None

    def __post_init__(self):
        if not isinstance(
            self.payment_kind,
            BarPaymentKind,
        ):
            raise TypeError(
                "Bar payment kind must use "
                "BarPaymentKind."
            )
