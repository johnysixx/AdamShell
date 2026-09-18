from copy import deepcopy
from dataclasses import dataclass


@dataclass(slots=True)
class CatQuantumCounterpartObservation:
    source_box_id: object = None
    counterpart_box_id: object = None

    source_layer: str | None = None
    counterpart_layer: str | None = None

    counterpart_position: object = None

    observed_tick: int | None = None
    temporary: bool = True
    pair_currently_valid: bool = False

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
            'counterpart_position': deepcopy(
                self.counterpart_position
            ),
            'observed_tick': self.observed_tick,
            'temporary': self.temporary,
            'pair_currently_valid': (
                self.pair_currently_valid
            ),
        }
