from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector


@dataclass(slots=True)
class CatQuantumExplorationState:
    active: bool = False
    arrived: bool = False
    pair_id: str | None = None
    route_id: str | None = None
    destination: SpatialVector3 | None = None
    stabilized_path: object = None
    stage: int = 1
    continuation: bool = False

    def __post_init__(self):
        self.destination = require_optional_spatial_vector(self.destination, field_name="quantum exploration destination")
