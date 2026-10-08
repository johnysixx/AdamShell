from dataclasses import dataclass, field

from quantum.cat_quantum_trail_state import (
    QuantumCatTrail,
)


@dataclass(slots=True, frozen=True)
class CatQuantumBoxTransferFailedResult:
    cat: str | None
    reason: str
    source_box_id: object = None
    target_box_id: object = None

    name: str = field(
        default="cat_quantum_box_transfer_failed",
        init=False,
    )

    transferred: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class StableCatBoxPairDissolutionEvent:
    pair_id: object
    creator_cat: str
    returning_cat: str
    removed_boxes: tuple
    energy_total_j: float
    energy_distributed_j: float
    energy_conserved: bool
    energy_difference_j: float
    cronenberg_id: object
    cronenberg_energy_j: float
    global_pool_energy_j: float
    anchor_layer: str | None
    anchor_layer_energy_j: float
    remote_layer: str | None
    remote_layer_energy_j: float
    quantum_dark_energy_j: float

    name: str = field(
        default="stable_cat_box_pair_dissolved",
        init=False,
    )

    dissolved: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "removed_boxes",
            tuple(self.removed_boxes),
        )


@dataclass(slots=True, frozen=True)
class CatQuantumBoxTransferCompletedEvent:
    cat: str
    source_box_id: object
    target_box_id: object
    source_layer: str | None
    target_layer: str | None
    cat_state: str
    trail: QuantumCatTrail
    energy_j: float

    name: str = field(
        default="cat_quantum_box_transfer_completed",
        init=False,
    )

    source_box_survived: bool = field(
        default=True,
        init=False,
    )

    target_box_consumed: bool = field(
        default=True,
        init=False,
    )

    target_box_energy_used: bool = field(
        default=True,
        init=False,
    )

    energy_use: str = field(
        default="cat_layer_transfer",
        init=False,
    )

    energy_conserved: bool = field(
        default=True,
        init=False,
    )

    transferred: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.trail,
            QuantumCatTrail,
        ):
            raise TypeError(
                "Quantum box transfer trail must "
                "be QuantumCatTrail."
            )

        object.__setattr__(
            self,
            "energy_j",
            float(self.energy_j),
        )


@dataclass(slots=True, frozen=True)
class CatStableExplorationPairTransferEvent:
    cat: str
    pair_id: object
    source_box_id: object
    target_box_id: object
    source_layer: str | None
    target_layer: str | None
    use_count: int
    trail: QuantumCatTrail
    pair_remains_stable: bool
    creator_returned: bool
    pair_dissolution: (
        StableCatBoxPairDissolutionEvent
        | None
    ) = None

    name: str = field(
        default=(
            "cat_used_stable_exploration_box_pair"
        ),
        init=False,
    )

    target_box_consumed: bool = field(
        default=False,
        init=False,
    )

    source_box_survived: bool = field(
        default=True,
        init=False,
    )

    target_box_survived: bool = field(
        default=True,
        init=False,
    )

    transferred: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.trail,
            QuantumCatTrail,
        ):
            raise TypeError(
                "Stable pair transfer trail must "
                "be QuantumCatTrail."
            )

        if (
            self.pair_dissolution is not None
            and not isinstance(
                self.pair_dissolution,
                StableCatBoxPairDissolutionEvent,
            )
        ):
            raise TypeError(
                "Stable pair dissolution must be "
                "StableCatBoxPairDissolutionEvent."
            )

        object.__setattr__(
            self,
            "use_count",
            int(self.use_count),
        )


CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES = (
    CatQuantumBoxTransferFailedResult,
    CatQuantumBoxTransferCompletedEvent,
    CatStableExplorationPairTransferEvent,
)
