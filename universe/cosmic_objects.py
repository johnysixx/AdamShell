from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType


def _snapshot_component(value):
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return to_dict()
    return deepcopy(value)


@dataclass(slots=True)
class StellarMaterialCloud:
    name: str
    type: str
    state: str
    composition: Mapping[str, object]
    can_form_stars: bool | None = None
    origin: str | None = None
    contains_elements_up_to_iron: bool | None = None
    can_form_stellar_systems: bool | None = None
    contains_heavy_elements: bool | None = None
    can_form_metal_rich_systems: bool | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Cloud name must not be empty")
        if not isinstance(self.composition, Mapping):
            raise TypeError("composition must be a material mapping")

        normalized = {}
        for component, value in self.composition.items():
            if not isinstance(component, str):
                raise TypeError("Cloud composition keys must be strings")
            normalized[component] = value

        self.composition = MappingProxyType(normalized)

    def add_components(self, components):
        if not isinstance(components, Mapping):
            raise TypeError("components must be a material mapping")

        updated = dict(self.composition)
        for component, value in components.items():
            if not isinstance(component, str):
                raise TypeError("Cloud composition keys must be strings")
            updated[component] = value

        self.composition = MappingProxyType(updated)

    def mark_heavy_enrichment(self):
        self.contains_heavy_elements = True
        self.can_form_metal_rich_systems = True

    def to_dict(self):
        snapshot = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "composition": {
                component: _snapshot_component(value)
                for component, value in self.composition.items()
            },
        }

        optional_fields = (
            "can_form_stars",
            "origin",
            "contains_elements_up_to_iron",
            "can_form_stellar_systems",
            "contains_heavy_elements",
            "can_form_metal_rich_systems",
        )
        for field_name in optional_fields:
            value = getattr(self, field_name)
            if value is not None:
                snapshot[field_name] = deepcopy(value)

        return snapshot
