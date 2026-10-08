from dataclasses import dataclass, field

from core.entity.components import SpatialVector3


@dataclass(slots=True, frozen=True)
class CatQuantumDirectPathStabilizedEvent:
    cat: str
    start: SpatialVector3
    destination: SpatialVector3
    distance: float

    name: str = field(
        default="cat_stabilized_direct_quantum_path",
        init=False,
    )

    path_kind: str = field(
        default="most_direct_possible",
        init=False,
    )

    stability: float = field(
        default=1.0,
        init=False,
    )

    stabilized: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.start,
            SpatialVector3,
        ):
            raise TypeError(
                "Quantum direct path start must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.destination,
            SpatialVector3,
        ):
            raise TypeError(
                "Quantum direct path destination "
                "must be SpatialVector3."
            )

        object.__setattr__(
            self,
            "distance",
            float(self.distance),
        )
