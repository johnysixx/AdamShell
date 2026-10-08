from dataclasses import dataclass, field

from quantum.cat_box_transfer_result_state import (
    CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
)
from quantum.cat_quantum_exploration_result_state import (
    CAT_QUANTUM_EXPLORATION_RESULT_TYPES,
)
from quantum.cat_stable_exploration_pair_result_state import (
    CatStableExplorationPairCreationFailedResult,
)


@dataclass(slots=True, frozen=True)
class CatExplorationPairCreationFailedResult:
    cat: str
    reason: str
    creation_result: (
        CatStableExplorationPairCreationFailedResult
        | None
    ) = None

    name: str = field(
        default=(
            "cat_exploration_pair_creation_failed"
        ),
        init=False,
    )

    intention: str = field(
        default="create_exploration_pair",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatExplorationPairTransferFailedResult:
    cat: str
    reason: str
    pair_id: object = None
    source_box_id: object = None
    target_box_id: object = None
    transfer_result: object = None
    pair_preserved: bool = False

    name: str = field(
        default=(
            "cat_exploration_pair_transfer_failed"
        ),
        init=False,
    )

    intention: str = field(
        default="create_exploration_pair",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if (
            self.transfer_result is not None
            and not isinstance(
                self.transfer_result,
                CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
            )
        ):
            raise TypeError(
                "Exploration pair transfer failure "
                "must contain a quantum transfer "
                "result object."
            )


@dataclass(slots=True, frozen=True)
class CatAutonomousExplorationPairStartedEvent:
    cat: str
    pair_id: object
    source_box_id: object
    target_box_id: object
    source_layer: str
    target_layer: str
    energy_cost_j: float
    remaining_cat_energy: float
    transfer: object
    exploration_route: object = None

    name: str = field(
        default=(
            "cat_started_autonomous_"
            "exploration_through_new_pair"
        ),
        init=False,
    )

    intention: str = field(
        default="create_exploration_pair",
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

    def __post_init__(self):
        if not isinstance(
            self.transfer,
            CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
        ):
            raise TypeError(
                "Autonomous exploration transfer "
                "must be a quantum transfer result "
                "object."
            )

        if (
            self.exploration_route is not None
            and not isinstance(
                self.exploration_route,
                CAT_QUANTUM_EXPLORATION_RESULT_TYPES,
            )
        ):
            raise TypeError(
                "Autonomous exploration route must "
                "be a quantum exploration result "
                "object."
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


CAT_EXPLORATION_PAIR_EXECUTION_RESULT_TYPES = (
    CatExplorationPairCreationFailedResult,
    CatExplorationPairTransferFailedResult,
    CatAutonomousExplorationPairStartedEvent,
)
