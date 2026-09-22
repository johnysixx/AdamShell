from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector


@dataclass(slots=True)
class CatQuantumTransferState:
    active: bool = False
    state: str = 'inactive'
    cat_name: str | None = None
    source_box_id: str | None = None
    target_box_id: str | None = None
    source_layer: str | None = None
    target_layer: str | None = None
    started_tick: int | None = None
    cat_is_here: bool = False
    cat_is_not_here: bool = False
    resolved_layer: str | None = None
    resolved_position: SpatialVector3 | None = None
    target_box_consumed: bool | None = None
    stable_pair_id: str | None = None

    def collapse(
        self,
        resolved_layer,
        resolved_position,
        target_box_consumed,
        stable_pair_id=None,
    ):
        self.active = False
        self.state = 'collapsed'
        self.cat_is_here = True
        self.cat_is_not_here = False
        self.resolved_layer = resolved_layer
        self.resolved_position = require_optional_spatial_vector(resolved_position, field_name="quantum transfer resolved position")
        self.target_box_consumed = bool(
            target_box_consumed
        )
        self.stable_pair_id = (
            stable_pair_id
        )

        return self
