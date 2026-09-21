from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PrimordialCosmicComponent:
    name: str
    type: str
    state: str
    origin: str | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError(
                "Primordial component name must not be empty"
            )
        if not self.type:
            raise ValueError(
                "Primordial component type must not be empty"
            )
        if not self.state:
            raise ValueError(
                "Primordial component state must not be empty"
            )

    def to_dict(self):
        snapshot = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
        }

        if self.origin is not None:
            snapshot["origin"] = self.origin

        return snapshot
