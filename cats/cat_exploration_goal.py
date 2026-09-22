from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector


@dataclass(slots=True)
class CatExplorationGoal:
    layer: str | None = None
    position: SpatialVector3 | None = None

    def __post_init__(self):
        self.position = require_optional_spatial_vector(self.position, field_name="cat exploration goal position")
