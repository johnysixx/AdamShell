from dataclasses import dataclass, field


@dataclass(slots=True)
class CatGroupTerritoryState:
    layer: str | None = None
    location: object = None
    strength: float = 0.0
    members: list = field(
        default_factory=list
    )

    def record_claim(
        self,
        layer,
        location,
        strength,
        members,
    ):
        self.layer = layer
        self.location = location
        self.strength = float(
            strength
        )
        self.members = list(
            members
        )

        return self
