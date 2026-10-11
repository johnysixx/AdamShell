from dataclasses import (
    dataclass,
    field,
)

from core.entity.components import (
    SpatialVector3,
)
from core.entity.quantum_box_cat_observation import (
    QuantumBoxCatObservation,
)
from cats.cat_quantum_observation_state import (
    CatQuantumCounterpartObservation,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatQuantumBoxTravelFailedResult:

    cat: str
    reason: str

    source_box_id: object = None
    counterpart_box_id: object = None
    source_layer: str | None = None
    transfer: object = None
    cronenberg_id: str | None = None
    memory: object = None

    name: str = field(
        default="cat_quantum_box_travel_failed",
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatQuantumBoxTraveledEvent:

    cat: str
    source_box_id: object
    counterpart_box_id: object
    source_layer: str | None
    transfer: object

    name: str = field(
        default=(
            "cat_traveled_through_known_quantum_box"
        ),
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatQuantumCounterpartSensingFailedResult:

    cat: str
    reason: str
    source_box_id: object = None

    name: str = field(
        default=(
            "cat_quantum_counterpart_sensing_failed"
        ),
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatQuantumCounterpartSensedEvent:

    cat: str
    observation: CatQuantumCounterpartObservation

    name: str = field(
        default="cat_sensed_quantum_counterpart",
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.observation,
            CatQuantumCounterpartObservation,
        ):
            raise TypeError(
                "Quantum counterpart sensing event "
                "requires "
                "CatQuantumCounterpartObservation."
            )


@dataclass(
    slots=True,
    frozen=True,
)
class CatBoxExplorationFailedResult:

    cat: str
    reason: str
    box_id: object = None

    name: str = field(
        default="cat_box_exploration_failed",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatApproachingBoxToExploreEvent:

    cat: str
    box_id: object
    route_id: object

    destination: SpatialVector3 | None
    position: SpatialVector3 | None = None
    executed: bool = True

    name: str = field(
        default="cat_approaching_box_to_explore",
        init=False,
    )

    arrived: bool = field(
        default=False,
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    def __post_init__(
        self,
    ):
        for field_name in (
            "destination",
            "position",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                value is not None
                and not isinstance(
                    value,
                    SpatialVector3,
                )
            ):
                raise TypeError(
                    f"{field_name} must be "
                    "SpatialVector3 or None."
                )

        object.__setattr__(
            self,
            "executed",
            bool(
                self.executed
            ),
        )


@dataclass(
    slots=True,
    frozen=True,
)
class CatExploredQuantumBoxEvent:

    cat: str
    box_id: object
    position: SpatialVector3 | None
    observation: QuantumBoxCatObservation
    memory: object = None

    name: str = field(
        default="cat_explored_quantum_box",
        init=False,
    )

    arrived: bool = field(
        default=True,
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if (
            self.position is not None
            and not isinstance(
                self.position,
                SpatialVector3,
            )
        ):
            raise TypeError(
                "Explored box position must be "
                "SpatialVector3 or None."
            )

        if not isinstance(
            self.observation,
            QuantumBoxCatObservation,
        ):
            raise TypeError(
                "Explored box observation must be "
                "QuantumBoxCatObservation."
            )
