from copy import deepcopy
from dataclasses import dataclass, field

from idea_entities.eternal_fire_objects import (
    EternalFireFuel,
    EternalFireFuelConsumption,
    EternalFireMeaning,
)


@dataclass(slots=True)
class EternalFirePotential:

    name: str = "eternal_fire"
    type: str = "idea_fire_potential"
    state: str = "unignited"
    actualized: bool = False
    physical_time: object = None
    physical_location: object = None
    requires_maintenance: bool = True
    maintainer: str = "pazuzu_masculine_principle"
    interactions: list = field(default_factory=list)
    ignited_by: object = None
    ignited_at_idea_tick: object = None
    ignited_at_logical_step: object = None
    flame_state: object = None
    heat_energy_j: float = 0.0
    origin_roll_id: object = None
    guardian: object = None
    fuel_seekers: list = field(default_factory=list)
    _fuel: EternalFireFuel = field(
        default_factory=EternalFireFuel,
        repr=False,
    )
    _meaning: EternalFireMeaning | None = field(
        default=None,
        repr=False,
    )
    _fuel_consumed_last_step: EternalFireFuelConsumption | None = field(
        default=None,
        repr=False,
    )

    @property
    def fuel(self):
        return self._fuel

    def set_fuel(self, fuel):
        if not isinstance(fuel, EternalFireFuel):
            raise TypeError(
                "Eternal fire fuel must be an EternalFireFuel object"
            )
        self._fuel = fuel

    @property
    def meaning(self):
        return self._meaning

    def set_meaning(self, meaning):
        if not isinstance(meaning, EternalFireMeaning):
            raise TypeError(
                "Eternal fire meaning must be an EternalFireMeaning object"
            )
        self._meaning = meaning

    @property
    def fuel_consumed_last_step(self):
        return self._fuel_consumed_last_step

    def record_fuel_consumption(self, consumption):
        if not isinstance(
            consumption,
            EternalFireFuelConsumption,
        ):
            raise TypeError(
                "Fuel consumption must be an "
                "EternalFireFuelConsumption object"
            )
        self._fuel_consumed_last_step = consumption

    def to_dict(self):
        public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "actualized": self.actualized,
            "physical_time": self.physical_time,
            "physical_location": self.physical_location,
            "requires_maintenance": self.requires_maintenance,
            "maintainer": self.maintainer,
            "interactions": deepcopy(self.interactions),
        }

        if self.actualized:
            public_state.update({
                "ignited_by": self.ignited_by,
                "ignited_at_idea_tick": self.ignited_at_idea_tick,
                "ignited_at_logical_step": (
                    self.ignited_at_logical_step
                ),
                "flame_state": self.flame_state,
                "fuel": self.fuel.to_dict(),
                "heat_energy_j": self.heat_energy_j,
                "origin_roll_id": self.origin_roll_id,
            })

        if self.meaning is not None:
            public_state["meaning"] = self.meaning.to_dict()

        if self.guardian is not None:
            public_state["guardian"] = self.guardian

        if self.fuel_seekers:
            public_state["fuel_seekers"] = list(
                self.fuel_seekers
            )

        if self.fuel_consumed_last_step is not None:
            public_state["fuel_consumed_last_step"] = (
                self.fuel_consumed_last_step.to_dict()
            )

        return public_state
