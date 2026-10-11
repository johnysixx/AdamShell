from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CronenbergLayerCrossedResult:
    old_size: float
    new_size: float
    growth: float
    layers_crossed: int


@dataclass(slots=True, frozen=True)
class CronenbergTravelStepResult:
    energy_cost: float
    energy_spent: float
    dark_energy_produced: float
    travel_steps: int


@dataclass(slots=True, frozen=True)
class CronenbergGrowthResult:
    cause: str
    old_size: float
    new_size: float
    growth: float = 0.0
    mass_gained: float = 0.0
    mass_lost: float = 0.0


@dataclass(slots=True, frozen=True)
class CronenbergHungerDayResult:
    state: str
    hungry_days: int
    satiety_days_remaining: int
    can_hunt: bool


@dataclass(slots=True, frozen=True)
class CronenbergDigestionStartedEvent:
    state: str
    consumed_mass: float
    digestion_days: int
    satiety_days_remaining: int


@dataclass(slots=True, frozen=True)
class CronenbergEnergyReceivedEvent:
    energy_received: float
    required_energy: float
    dark_energy_produced: float
    daily_energy_received: float
