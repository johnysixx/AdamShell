from dataclasses import dataclass, field

from core.entity.components import SpatialVector3
from quantum.cat_box_transfer_result_state import (
    CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
)


@dataclass(slots=True, frozen=True)
class CatQuantumReturnRouteNotStartedResult:
    cat: str
    reason: str

    name: str = field(
        default="cat_quantum_return_route_not_started",
        init=False,
    )

    started: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatQuantumReturnRouteStartedEvent:
    cat: str
    pair_id: object
    route_id: str
    destination: SpatialVector3

    name: str = field(
        default="cat_quantum_return_route_started",
        init=False,
    )

    started: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.destination,
            SpatialVector3,
        ):
            raise TypeError(
                "Quantum return destination must "
                "be SpatialVector3."
            )


@dataclass(slots=True, frozen=True)
class CatQuantumReturnNotAdvancedResult:
    cat: str
    reason: str

    name: str = field(
        default="cat_quantum_return_not_advanced",
        init=False,
    )

    advanced: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatQuantumReturnAdvancedEvent:
    cat: str
    pair_id: object
    position: SpatialVector3 | None
    arrived_at_box: bool
    transfer_result: object = None

    name: str = field(
        default="cat_quantum_return_advanced",
        init=False,
    )

    advanced: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if (
            self.position is not None
            and not isinstance(
                self.position,
                SpatialVector3,
            )
        ):
            raise TypeError(
                "Quantum return position must be "
                "SpatialVector3 or None."
            )

        if (
            self.transfer_result is not None
            and not isinstance(
                self.transfer_result,
                CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
            )
        ):
            raise TypeError(
                "Quantum return transfer result must "
                "be a quantum box transfer result object."
            )


CAT_QUANTUM_RETURN_RESULT_TYPES = (
    CatQuantumReturnRouteNotStartedResult,
    CatQuantumReturnRouteStartedEvent,
    CatQuantumReturnNotAdvancedResult,
    CatQuantumReturnAdvancedEvent,
)
