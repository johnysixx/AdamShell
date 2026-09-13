from copy import deepcopy
from dataclasses import dataclass, field


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
    fuel: dict = field(default_factory=dict)
    heat_energy_j: float = 0.0
    origin_roll_id: object = None
    meaning: object = None
    guardian: object = None
    fuel_seekers: list = field(default_factory=list)
    fuel_consumed_last_step: object = None

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
                "fuel": deepcopy(self.fuel),
                "heat_energy_j": self.heat_energy_j,
                "origin_roll_id": self.origin_roll_id,
            })

        if self.meaning is not None:
            public_state["meaning"] = deepcopy(self.meaning)

        if self.guardian is not None:
            public_state["guardian"] = self.guardian

        if self.fuel_seekers:
            public_state["fuel_seekers"] = list(
                self.fuel_seekers
            )

        if self.fuel_consumed_last_step is not None:
            public_state["fuel_consumed_last_step"] = deepcopy(
                self.fuel_consumed_last_step
            )

        return public_state
