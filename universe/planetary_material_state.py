from dataclasses import dataclass


@dataclass(slots=True)
class PlanetaryMaterialState:

    water_available: bool = False
    ice_available: bool = False
    minerals_available: bool = False
    organic_molecules_available: bool = False

    def to_dict(self):
        return {
            "water_available": self.water_available,
            "ice_available": self.ice_available,
            "minerals_available": self.minerals_available,
            "organic_molecules_available": (
                self.organic_molecules_available
            ),
        }
