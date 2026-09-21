from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Planet:
    name: str
    type: str
    state: str
    orbit: int

    def __post_init__(self):
        if not self.name:
            raise ValueError("Planet name must not be empty")
        if not self.type:
            raise ValueError("Planet type must not be empty")
        if not self.state:
            raise ValueError("Planet state must not be empty")
        if not isinstance(self.orbit, int) or isinstance(
            self.orbit,
            bool,
        ):
            raise TypeError("orbit must be an integer")
        if self.orbit < 1:
            raise ValueError("orbit must be positive")

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "orbit": self.orbit,
        }


@dataclass(frozen=True, slots=True)
class EarthPlanet(Planet):
    has_iron_core: bool
    has_rocky_crust: bool
    water_possible: bool
    organic_molecules_possible: bool

    def __post_init__(self):
        Planet.__post_init__(self)

        capability_fields = (
            self.has_iron_core,
            self.has_rocky_crust,
            self.water_possible,
            self.organic_molecules_possible,
        )
        if not all(
            isinstance(value, bool)
            for value in capability_fields
        ):
            raise TypeError(
                "Earth capability fields must be booleans"
            )

    def to_dict(self):
        snapshot = Planet.to_dict(self)
        snapshot.update({
            "has_iron_core": self.has_iron_core,
            "has_rocky_crust": self.has_rocky_crust,
            "water_possible": self.water_possible,
            "organic_molecules_possible": (
                self.organic_molecules_possible
            ),
        })
        return snapshot
