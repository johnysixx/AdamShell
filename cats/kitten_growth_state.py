from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType

from cats.duplicate_consumption_energy_state import (
    DuplicateConsumptionEnergyState,
)


@dataclass(slots=True, frozen=True)
class KittenGrowthAppliedEvent:

    kitten: str
    source: str
    day: int
    previous_size: float
    size_gain: float
    size: float
    previous_strength: float
    strength_gain: float
    strength: float
    cronenberg_mass: float
    metadata: object = field(
        default_factory=dict
    )
    name: str = field(
        default="kitten_growth_applied",
        init=False,
    )
    grew: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "kitten",
            str(self.kitten),
        )

        object.__setattr__(
            self,
            "source",
            str(self.source),
        )

        object.__setattr__(
            self,
            "day",
            int(self.day),
        )

        for field_name in (
            "previous_size",
            "size_gain",
            "size",
            "previous_strength",
            "strength_gain",
            "strength",
            "cronenberg_mass",
        ):
            object.__setattr__(
                self,
                field_name,
                float(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                deepcopy(
                    dict(
                        self.metadata or {}
                    )
                )
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "kitten": self.kitten,
            "source": self.source,
            "day": self.day,
            "previous_size": (
                self.previous_size
            ),
            "size_gain": self.size_gain,
            "size": self.size,
            "previous_strength": (
                self.previous_strength
            ),
            "strength_gain": (
                self.strength_gain
            ),
            "strength": self.strength,
            "cronenberg_mass": (
                self.cronenberg_mass
            ),
            "metadata": deepcopy(
                dict(self.metadata)
            ),
            "grew": self.grew,
        }


@dataclass(slots=True, frozen=True)
class KittenGrowthAlreadyProcessedEvent:

    kitten: str
    source: str
    day: int
    amount_not_absorbed: float
    stored_energy: (
        DuplicateConsumptionEnergyState
    )
    name: str = field(
        default=(
            "kitten_growth_already_processed"
        ),
        init=False,
    )
    energy_conserved: bool = field(
        default=True,
        init=False,
    )
    grew: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "kitten",
            str(self.kitten),
        )

        object.__setattr__(
            self,
            "source",
            str(self.source),
        )

        object.__setattr__(
            self,
            "day",
            int(self.day),
        )

        object.__setattr__(
            self,
            "amount_not_absorbed",
            float(
                self.amount_not_absorbed
            ),
        )

        if not isinstance(
            self.stored_energy,
            DuplicateConsumptionEnergyState,
        ):
            raise TypeError(
                "Stored duplicate energy must be "
                "DuplicateConsumptionEnergyState."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "kitten": self.kitten,
            "source": self.source,
            "day": self.day,
            "amount_not_absorbed": (
                self.amount_not_absorbed
            ),
            "stored_energy": (
                self.stored_energy
            ),
            "energy_conserved": (
                self.energy_conserved
            ),
            "grew": self.grew,
        }


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

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            KittenGrowthAppliedEvent,
        ):
            raise TypeError(
                "Kitten growth state history "
                "requires a "
                "KittenGrowthAppliedEvent object."
            )

        self.history.append(
            event
        )

        return event
