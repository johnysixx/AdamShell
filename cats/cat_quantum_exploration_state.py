from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector
from quantum.cat_quantum_path_state import (
    CatQuantumDirectPathStabilizedEvent,
)


@dataclass(slots=True)
class CatQuantumExplorationState:
    active: bool = False
    arrived: bool = False
    pair_id: str | None = None
    route_id: str | None = None
    destination: SpatialVector3 | None = None
    stabilized_path: (
        CatQuantumDirectPathStabilizedEvent
        | None
    ) = None
    stage: int = 1
    continuation: bool = False

    def __post_init__(self):
        self.destination = require_optional_spatial_vector(self.destination, field_name="quantum exploration destination")

        if (
            self.stabilized_path is not None
            and not isinstance(
                self.stabilized_path,
                CatQuantumDirectPathStabilizedEvent,
            )
        ):
            raise TypeError(
                "Quantum exploration stabilized path "
                "must be "
                "CatQuantumDirectPathStabilizedEvent."
            )
