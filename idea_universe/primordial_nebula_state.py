from copy import deepcopy
from dataclasses import dataclass, field

from idea_universe.primordial_stellar_state import (
    PrimordialNebulaRemnant,
)


@dataclass(slots=True)
class PrimordialNebulaState:

    tick_count: int = 0
    size: float = 0.0

    stars: list = field(
        default_factory=list,
    )

    source_remnants: list = field(
        default_factory=list,
    )

    source_remnant_count: int = 0

    elemental_potentials: dict = field(
        default_factory=dict,
    )

    previous_liquid_hydrocarbon_level: (
        float | None
    ) = None

    current_liquid_hydrocarbon_level: float = 0.0

    mined_from_current_growth: float = 0.0

    def __post_init__(self):
        remnants = list(
            self.source_remnants
        )

        for remnant in remnants:
            if not isinstance(
                remnant,
                PrimordialNebulaRemnant,
            ):
                raise TypeError(
                    "Primordial nebula source "
                    "remnants must be "
                    "PrimordialNebulaRemnant."
                )

        self.source_remnants = (
            remnants
        )

        self.source_remnant_count = len(
            remnants
        )

        self.elemental_potentials = {
            str(element): float(amount)
            for element, amount
            in self.elemental_potentials.items()
        }

    def to_dict(self):
        return {
            "tick_count":
                self.tick_count,

            "size":
                self.size,

            "stars":
                deepcopy(
                    self.stars
                ),

            "source_remnants": [
                remnant.to_dict()
                for remnant
                in self.source_remnants
            ],

            "source_remnant_count":
                self.source_remnant_count,

            "elemental_potentials":
                deepcopy(
                    self.elemental_potentials
                ),

            "previous_liquid_hydrocarbon_level":
                self.previous_liquid_hydrocarbon_level,

            "current_liquid_hydrocarbon_level":
                self.current_liquid_hydrocarbon_level,

            "mined_from_current_growth":
                self.mined_from_current_growth,
        }
