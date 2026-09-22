from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector


@dataclass(slots=True)
class CatQuantumCounterpartObservation:
    source_box_id: object = None
    counterpart_box_id: object = None

    source_layer: str | None = None
    counterpart_layer: str | None = None

    counterpart_position: SpatialVector3 | None = None

    observed_tick: int | None = None
    temporary: bool = True
    pair_currently_valid: bool = False

    def __post_init__(self):
        self.counterpart_position = require_optional_spatial_vector(self.counterpart_position, field_name="quantum counterpart position")

    def to_dict(self):
        return {
            'source_box_id': self.source_box_id,
            'counterpart_box_id': (
                self.counterpart_box_id
            ),
            'source_layer': self.source_layer,
            'counterpart_layer': (
                self.counterpart_layer
            ),
            'counterpart_position': (None if self.counterpart_position is None else self.counterpart_position.to_dict()),
            'observed_tick': self.observed_tick,
            'temporary': self.temporary,
            'pair_currently_valid': (
                self.pair_currently_valid
            ),
        }
