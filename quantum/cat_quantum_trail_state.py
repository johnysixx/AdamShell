from dataclasses import dataclass

from core.entity.components import SpatialVector3


@dataclass(slots=True, frozen=True)
class QuantumCatTrail:
    trail_id: str
    cat: str
    from_box: object
    to_box: object
    from_layer: str | None
    to_layer: str | None
    start_position: SpatialVector3
    end_position: SpatialVector3
    stability: float = 0.50
    uses: int = 1
    age_ticks: int = 0

    def __post_init__(self):
        if not isinstance(
            self.start_position,
            SpatialVector3,
        ):
            raise TypeError(
                "Quantum cat trail start position "
                "must be SpatialVector3."
            )

        if not isinstance(
            self.end_position,
            SpatialVector3,
        ):
            raise TypeError(
                "Quantum cat trail end position "
                "must be SpatialVector3."
            )

        object.__setattr__(
            self,
            "stability",
            float(self.stability),
        )

        object.__setattr__(
            self,
            "uses",
            int(self.uses),
        )

        object.__setattr__(
            self,
            "age_ticks",
            int(self.age_ticks),
        )
