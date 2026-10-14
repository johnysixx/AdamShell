from dataclasses import dataclass, field
from types import MappingProxyType

from universe.planet_objects import (
    Planet,
)
from universe.planet_state import (
    PlanetFormationState,
)
from universe.planetary_material_objects import (
    PlanetaryMaterial,
)
from universe.planets_process_state import (
    PlanetsProcessState,
)


def _freeze_planets(
    planets,
):
    values = tuple(
        planets
    )

    for planet in values:
        if not isinstance(
            planet,
            Planet,
        ):
            raise TypeError(
                "Planet formation result must contain "
                "Planet objects."
            )

    return values


def _freeze_material_registry(
    registry,
):
    values = dict(
        registry
    )

    for material in values.values():
        if not isinstance(
            material,
            PlanetaryMaterial,
        ):
            raise TypeError(
                "Planetary material result registry "
                "must contain PlanetaryMaterial objects."
            )

    return MappingProxyType(
        values
    )


@dataclass(
    slots=True,
    frozen=True,
)
class PlanetFormationResult:

    state: PlanetsProcessState
    planets: tuple[Planet, ...]
    planetary_materials: object
    planetary_state: PlanetFormationState

    name: str = field(
        default="planets",
        init=False,
    )
    type: str = field(
        default="planetary_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            PlanetsProcessState,
        ):
            raise TypeError(
                "Planet formation result state must use "
                "PlanetsProcessState."
            )

        if not isinstance(
            self.planetary_state,
            PlanetFormationState,
        ):
            raise TypeError(
                "Planet formation result state object "
                "must use PlanetFormationState."
            )

        object.__setattr__(
            self,
            "planets",
            _freeze_planets(
                self.planets
            ),
        )
        object.__setattr__(
            self,
            "planetary_materials",
            _freeze_material_registry(
                self.planetary_materials
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "planets": [
                planet.to_dict()
                for planet in self.planets
            ],
            "planetary_materials": {
                name: material.to_dict()
                for name, material
                in self.planetary_materials.items()
            },
            "planetary_state": (
                self.planetary_state.to_dict()
            ),
        }
