from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PlanetaryMaterial:
    name: str
    requires: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not self.name:
            raise ValueError("Planetary material name must not be empty")

        normalized_requires = tuple(self.requires)
        if any(
            not isinstance(requirement, str) or not requirement
            for requirement in normalized_requires
        ):
            raise TypeError(
                "Planetary material requirements must be non-empty strings"
            )

        object.__setattr__(self, "requires", normalized_requires)

    @property
    def type(self):
        return "planetary_material"

    @property
    def state(self):
        return "possible"

    def make_available(self, *, origin):
        return AvailablePlanetaryMaterial(
            material=self,
            origin=origin,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "requires": list(self.requires),
        }


@dataclass(frozen=True, slots=True)
class AvailablePlanetaryMaterial:
    material: PlanetaryMaterial
    origin: str

    def __post_init__(self):
        if not isinstance(self.material, PlanetaryMaterial):
            raise TypeError(
                "material must be a PlanetaryMaterial object"
            )
        if not isinstance(self.origin, str) or not self.origin:
            raise TypeError("origin must be a non-empty string")

    @property
    def name(self):
        return self.material.name

    @property
    def type(self):
        return self.material.type

    @property
    def state(self):
        return "available"

    @property
    def requires(self):
        return self.material.requires

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "requires": list(self.requires),
            "origin": self.origin,
        }
