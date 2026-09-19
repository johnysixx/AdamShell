from dataclasses import dataclass, field


@dataclass(slots=True)
class KittenGrowthState:
    milk_feedings: int = 0
    milk_units_consumed: float = 0.0
    cronenberg_portions_eaten: int = 0
    cronenberg_mass_consumed: float = 0.0
    size_gained: float = 0.0
    strength_gained: float = 0.0
    processed_sources: list = field(
        default_factory=list
    )
    history: list = field(
        default_factory=list
    )
