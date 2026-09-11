from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True)
class PrimordialNebulaState:

    tick_count: int = 0
    size: float = 0.0
    stars: list = field(default_factory=list)
    source_remnants: list = field(default_factory=list)
    source_remnant_count: int = 0
    elemental_potentials: dict = field(default_factory=dict)
    previous_liquid_hydrocarbon_level: float | None = None
    current_liquid_hydrocarbon_level: float = 0.0
    mined_from_current_growth: float = 0.0

    def to_dict(self):
        return {
            "tick_count": self.tick_count,
            "size": self.size,
            "stars": deepcopy(self.stars),
            "source_remnants": deepcopy(
                self.source_remnants
            ),
            "source_remnant_count": (
                self.source_remnant_count
            ),
            "elemental_potentials": deepcopy(
                self.elemental_potentials
            ),
            "previous_liquid_hydrocarbon_level": (
                self.previous_liquid_hydrocarbon_level
            ),
            "current_liquid_hydrocarbon_level": (
                self.current_liquid_hydrocarbon_level
            ),
            "mined_from_current_growth": (
                self.mined_from_current_growth
            ),
        }
