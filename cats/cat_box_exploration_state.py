from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector


@dataclass(slots=True)
class CatBoxExplorationState:
    active: bool = False
    arrived: bool = False

    box_id: object = None
    route_id: str | None = None
    destination: SpatialVector3 | None = None

    observed: bool = False

    def __post_init__(self):
        self.destination = require_optional_spatial_vector(self.destination, field_name="box exploration destination")
