from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector


@dataclass(slots=True)
class CatQuantumReturnState:
    active: bool = False
    arrived_at_box: bool = False
    pair_id: str | None = None
    route_id: str | None = None
    remote_box_id: object = None
    anchor_box_id: object = None
    destination: SpatialVector3 | None = None
    stabilized_path: object = None

    def __post_init__(self):
        self.destination = require_optional_spatial_vector(self.destination, field_name="quantum return destination")
