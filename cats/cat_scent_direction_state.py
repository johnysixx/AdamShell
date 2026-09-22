from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector


@dataclass(slots=True)
class CatScentTrailDirection:
    inferred: bool = False
    reason: str | None = None

    identity: str | None = None
    layer: str | None = None

    from_position: SpatialVector3 | None = None
    to_position: SpatialVector3 | None = None
    vector: SpatialVector3 | None = None
    unit_vector: SpatialVector3 | None = None

    distance: float | None = None
    tick_delta: int | None = None
    newest_age_ticks: int | None = None
    freshness: float | None = None
    confidence: float | None = None

    from_source_id: object = None
    to_source_id: object = None

    def __post_init__(self):
        for field_name in ("from_position", "to_position", "vector", "unit_vector"):
            setattr(self, field_name, require_optional_spatial_vector(getattr(self, field_name), field_name=f"scent trail {field_name}"))
