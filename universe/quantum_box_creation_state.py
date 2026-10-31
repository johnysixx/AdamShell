from dataclasses import dataclass, field

from core.entity.components import (
    SpatialVector3,
    require_spatial_vector,
)


@dataclass(slots=True, frozen=True)
class QuantumBoxCreatedEvent:
    box_id: str
    position: SpatialVector3
    layer: object
    tick: int

    name: str = field(
        default="quantum_box_created",
        init=False,
    )

    def __post_init__(self):
        if (
            not isinstance(self.box_id, str)
            or not self.box_id
        ):
            raise ValueError(
                "Quantum box creation requires a valid ID."
            )

        object.__setattr__(
            self,
            "position",
            require_spatial_vector(
                self.position,
                field_name="quantum box creation position",
            ),
        )

        object.__setattr__(
            self,
            "tick",
            int(self.tick),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "box_id": self.box_id,
            "position": self.position.to_dict(),
            "layer": self.layer,
            "tick": self.tick,
        }
