from dataclasses import dataclass, field

from core.entity.components import SpatialVector3
from core.entity.quantum_box_pairing_result_state import (
    QuantumBoxesPairedEvent,
)


@dataclass(slots=True, frozen=True)
class CatReturnCounterpartCreationFailedResult:
    cat: str | None
    reason: str

    name: str = field(
        default=(
            "cat_return_box_counterpart_"
            "creation_failed"
        ),
        init=False,
    )

    created: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatReturnCounterpartCreatedEvent:
    cat: str
    source_box_id: object
    counterpart_box_id: object
    source_layer: str
    counterpart_layer: str
    position: SpatialVector3
    energy_cost_j: float
    remaining_cat_energy: float
    pair_event: QuantumBoxesPairedEvent

    name: str = field(
        default=(
            "cat_created_return_box_counterpart"
        ),
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Return counterpart position must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.pair_event,
            QuantumBoxesPairedEvent,
        ):
            raise TypeError(
                "Return counterpart pair event must "
                "be QuantumBoxesPairedEvent."
            )

        object.__setattr__(
            self,
            "energy_cost_j",
            float(
                self.energy_cost_j
            ),
        )

        object.__setattr__(
            self,
            "remaining_cat_energy",
            float(
                self.remaining_cat_energy
            ),
        )


@dataclass(slots=True, frozen=True)
class CatReturnCounterpartCreatedResult:
    cat: str
    source_box_id: object
    counterpart_box_id: object
    source_layer: str
    counterpart_layer: str
    position: SpatialVector3
    energy_cost_j: float
    remaining_cat_energy: float
    pair_event: QuantumBoxesPairedEvent
    counterpart: object

    name: str = field(
        default=(
            "cat_created_return_box_counterpart"
        ),
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Return counterpart position must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.pair_event,
            QuantumBoxesPairedEvent,
        ):
            raise TypeError(
                "Return counterpart pair event must "
                "be QuantumBoxesPairedEvent."
            )

        object.__setattr__(
            self,
            "energy_cost_j",
            float(
                self.energy_cost_j
            ),
        )

        object.__setattr__(
            self,
            "remaining_cat_energy",
            float(
                self.remaining_cat_energy
            ),
        )


CAT_RETURN_COUNTERPART_RESULT_TYPES = (
    CatReturnCounterpartCreationFailedResult,
    CatReturnCounterpartCreatedResult,
)
