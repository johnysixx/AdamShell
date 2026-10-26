from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PrimordialEnergy:
    state: str = "released"
    name: str = field(default="energy", init=False)
    type: str = field(default="primordial_energy", init=False)

    def __post_init__(self):
        if not self.state:
            raise ValueError("Primordial energy state is required.")

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
        }


@dataclass(frozen=True, slots=True)
class PrimordialMatter:
    state: str = "forming"
    name: str = field(default="matter", init=False)
    type: str = field(default="primordial_matter", init=False)

    def __post_init__(self):
        if not self.state:
            raise ValueError("Primordial matter state is required.")

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
        }


@dataclass(frozen=True, slots=True)
class PrimordialElement:
    name: str
    state: str
    origin: str | None = None
    type: str = field(default="element", init=False)

    def __post_init__(self):
        if not self.name:
            raise ValueError("Primordial element name is required.")
        if not self.state:
            raise ValueError("Primordial element state is required.")

    def to_dict(self):
        result = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
        }
        if self.origin is not None:
            result["origin"] = self.origin
        return result
