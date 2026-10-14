from dataclasses import dataclass, field
from types import MappingProxyType

from universe.planetary_material_objects import (
    AvailablePlanetaryMaterial,
)
from universe.planetary_material_state import (
    PlanetaryMaterialState,
)
from universe.planetary_materials_process_state import (
    PlanetaryMaterialsProcessState,
)


def _freeze_material_registry(
    registry,
):
    values = dict(
        registry
    )

    for material in values.values():
        if not isinstance(
            material,
            AvailablePlanetaryMaterial,
        ):
            raise TypeError(
                "Available material result registry "
                "must contain "
                "AvailablePlanetaryMaterial objects."
            )

    return MappingProxyType(
        values
    )


@dataclass(
    slots=True,
    frozen=True,
)
class PlanetaryMaterializationResult:

    state: PlanetaryMaterialsProcessState
    available_materials: object
    material_state: PlanetaryMaterialState

    name: str = field(
        default="planetary_materials",
        init=False,
    )
    type: str = field(
        default="planetary_material_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            PlanetaryMaterialsProcessState,
        ):
            raise TypeError(
                "Planetary material result state "
                "must use "
                "PlanetaryMaterialsProcessState."
            )

        if not isinstance(
            self.material_state,
            PlanetaryMaterialState,
        ):
            raise TypeError(
                "Planetary material result state "
                "object must use "
                "PlanetaryMaterialState."
            )

        object.__setattr__(
            self,
            "available_materials",
            _freeze_material_registry(
                self.available_materials
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "available_materials": {
                name: material.to_dict()
                for name, material
                in self.available_materials.items()
            },
            "material_state": (
                self.material_state.to_dict()
            ),
        }
