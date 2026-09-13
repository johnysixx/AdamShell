from dataclasses import dataclass, field


@dataclass(slots=True)
class PrefysicalFireMaterials:

    wood_sticks: int = 2
    dry_grass: bool = True
    found_by: str = "serpent"
    handed_to: object = None

    def to_dict(self):
        return {
            "wood_sticks": self.wood_sticks,
            "dry_grass": self.dry_grass,
            "found_by": self.found_by,
            "handed_to": self.handed_to,
        }


@dataclass(slots=True)
class PrefysicalFireEnergyConversion:

    masculine_energy_spent_j: float = 0.0
    friction_heat_j: float = 0.0

    def to_dict(self):
        return {
            "masculine_energy_spent_j": (
                self.masculine_energy_spent_j
            ),
            "friction_heat_j": self.friction_heat_j,
        }


@dataclass(slots=True)
class PrefysicalFireRoles:

    fire_guardian: object = None
    fuel_seekers: list = field(default_factory=list)

    def to_dict(self):
        return {
            "fire_guardian": self.fire_guardian,
            "fuel_seekers": list(self.fuel_seekers),
        }
