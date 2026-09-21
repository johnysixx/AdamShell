from dataclasses import dataclass

from universe.cosmic_objects import StellarMaterialCloud


@dataclass(frozen=True, slots=True)
class SecondGenerationStar:
    name: str
    type: str
    state: str
    generation: int

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

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "generation": self.generation,
        }


@dataclass(frozen=True, slots=True)
class ProtoplanetaryDisk:
    name: str
    type: str
    state: str
    available_elements: tuple[str, ...]
    can_form_planets: bool
    can_form_water: bool
    can_form_iron_cores: bool
    can_form_rocky_worlds: bool

    def __post_init__(self):
        if not self.name:
            raise ValueError("Disk name must not be empty")
        if not isinstance(self.available_elements, tuple):
            raise TypeError("available_elements must be a tuple")
        for element_name in self.available_elements:
            if not isinstance(element_name, str):
                raise TypeError(
                    "available_elements must contain strings"
                )

    def has_element(self, element_name):
        return element_name in self.available_elements

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "available_elements": list(self.available_elements),
            "can_form_planets": self.can_form_planets,
            "can_form_water": self.can_form_water,
            "can_form_iron_cores": self.can_form_iron_cores,
            "can_form_rocky_worlds": self.can_form_rocky_worlds,
        }


@dataclass(frozen=True, slots=True)
class StellarSystem:
    name: str
    type: str
    state: str
    generation: int
    source_cloud: StellarMaterialCloud
    star: SecondGenerationStar
    protoplanetary_disk: ProtoplanetaryDisk

    def __post_init__(self):
        if not self.name:
            raise ValueError("Stellar system name must not be empty")
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
        if not isinstance(self.star, SecondGenerationStar):
            raise TypeError(
                "star must be a SecondGenerationStar object"
            )
        if not isinstance(
            self.protoplanetary_disk,
            ProtoplanetaryDisk,
        ):
            raise TypeError(
                "protoplanetary_disk must be a ProtoplanetaryDisk object"
            )

    @property
    def formed_from(self):
        return self.source_cloud.name

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "generation": self.generation,
            "formed_from": self.formed_from,
            "star": self.star.to_dict(),
            "protoplanetary_disk": self.protoplanetary_disk.to_dict(),
        }
