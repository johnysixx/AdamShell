from dataclasses import dataclass

from meeting_place.bar_service_effect_state import (
    BarGodEnergyDrinkEffect,
    BarGodEntropyDrinkEffect,
    BarIdeaEntityEnergyDrinkEffect,
    BarIdeaEntityEntropyDrinkEffect,
)
from meeting_place.reservoir_event_state import (
    BarEnergySpentEvent,
    EntropyServedEvent,
)


@dataclass(slots=True, frozen=True)
class BarEnergyDrinkServiceResult:
    reservoir_event: BarEnergySpentEvent
    service_effect: (
        BarGodEnergyDrinkEffect
        | BarIdeaEntityEnergyDrinkEffect
    )

    def __post_init__(self):
        if not isinstance(
            self.reservoir_event,
            BarEnergySpentEvent,
        ):
            raise TypeError(
                "Energy service requires BarEnergySpentEvent."
            )

        if not isinstance(
            self.service_effect,
            (
                BarGodEnergyDrinkEffect,
                BarIdeaEntityEnergyDrinkEffect,
            ),
        ):
            raise TypeError(
                "Energy service requires a typed energy effect."
            )


@dataclass(slots=True, frozen=True)
class BarEntropyDrinkServiceResult:
    reservoir_event: EntropyServedEvent
    service_effect: (
        BarGodEntropyDrinkEffect
        | BarIdeaEntityEntropyDrinkEffect
    )

    def __post_init__(self):
        if not isinstance(
            self.reservoir_event,
            EntropyServedEvent,
        ):
            raise TypeError(
                "Entropy service requires EntropyServedEvent."
            )

        if not isinstance(
            self.service_effect,
            (
                BarGodEntropyDrinkEffect,
                BarIdeaEntityEntropyDrinkEffect,
            ),
        ):
            raise TypeError(
                "Entropy service requires a typed entropy effect."
            )
