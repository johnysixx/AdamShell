from dataclasses import dataclass


@dataclass(slots=True)
class PlanetFormationState:

    planets_formed: bool = False
    earth_formed: bool = False
    water_possible: bool = False
    ice_possible: bool = False
    minerals_possible: bool = False
    organic_molecules_possible: bool = False

    def to_dict(self):
        return {
            "planets_formed": self.planets_formed,
            "earth_formed": self.earth_formed,
            "water_possible": self.water_possible,
            "ice_possible": self.ice_possible,
            "minerals_possible": self.minerals_possible,
            "organic_molecules_possible": (
                self.organic_molecules_possible
            ),
        }
