from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from universe.cosmic_objects import StellarMaterialCloud


@dataclass(frozen=True, slots=True)
class PrimordialStar:
    name: str
    type: str
    generation: int
    state: str
    source_cloud: StellarMaterialCloud
    composition: Mapping[str, str]
    can_fuse_elements: bool
    can_create_heavy_elements: bool

    def __post_init__(self):
        if not self.name:
            raise ValueError("Star name must not be empty")
        if not isinstance(self.generation, int) or isinstance(
            self.generation,
            bool,
        ):
            raise TypeError("generation must be an integer")
        if self.generation < 1:
            raise ValueError("generation must be positive")
        if not isinstance(self.source_cloud, StellarMaterialCloud):
            raise TypeError(
                "source_cloud must be a StellarMaterialCloud object"
            )
        if not isinstance(self.composition, Mapping):
            raise TypeError("composition must be a stellar material mapping")

        normalized = {}
        for component, abundance in self.composition.items():
            if not isinstance(component, str):
                raise TypeError("Star composition keys must be strings")
            if not isinstance(abundance, str):
                raise TypeError("Star composition values must be strings")
            normalized[component] = abundance

        object.__setattr__(
            self,
            "composition",
            MappingProxyType(normalized),
        )

    @property
    def formed_from(self):
        return self.source_cloud.name

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "generation": self.generation,
            "state": self.state,
            "formed_from": self.formed_from,
            "composition": dict(self.composition),
            "can_fuse_elements": self.can_fuse_elements,
            "can_create_heavy_elements": self.can_create_heavy_elements,
        }
