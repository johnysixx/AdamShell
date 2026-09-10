from dataclasses import dataclass


@dataclass(slots=True)
class StellarSystemFormationState:

    stellar_systems_formed: bool = False
    solar_system_formed: bool = False
    planet_formation_possible: bool = False
    water_formation_possible: bool = False
    rocky_worlds_possible: bool = False

    def to_dict(self):
        return {
            "stellar_systems_formed": (
                self.stellar_systems_formed
            ),
            "solar_system_formed": self.solar_system_formed,
            "planet_formation_possible": (
                self.planet_formation_possible
            ),
            "water_formation_possible": (
                self.water_formation_possible
            ),
            "rocky_worlds_possible": (
                self.rocky_worlds_possible
            ),
        }
