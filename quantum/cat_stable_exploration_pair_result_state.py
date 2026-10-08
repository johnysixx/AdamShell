from dataclasses import dataclass, field

from quantum.cat_stable_exploration_pair_state import (
    CatStableExplorationPairState,
)


@dataclass(slots=True, frozen=True)
class CatStableExplorationPairCreationFailedResult:
    cat: str | None
    reason: str

    name: str = field(
        default=(
            "cat_stable_exploration_pair_"
            "creation_failed"
        ),
        init=False,
    )

    created: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatStableExplorationPairCreatedEvent:
    cat: str
    pair_id: str
    source_box_id: object
    target_box_id: object
    source_layer: str
    target_layer: str
    energy_cost_j: float
    remaining_cat_energy: float

    name: str = field(
        default=(
            "cat_created_stable_"
            "exploration_box_pair"
        ),
        init=False,
    )

    available_to_other_cats: bool = field(
        default=True,
        init=False,
    )

    stable: bool = field(
        default=True,
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatStableExplorationPairCreatedResult:
    cat: str
    pair_id: str
    source_box_id: object
    target_box_id: object
    source_layer: str
    target_layer: str
    energy_cost_j: float
    remaining_cat_energy: float
    source_box: object
    target_box: object
    pair: CatStableExplorationPairState

    name: str = field(
        default=(
            "cat_created_stable_"
            "exploration_box_pair"
        ),
        init=False,
    )

    available_to_other_cats: bool = field(
        default=True,
        init=False,
    )

    stable: bool = field(
        default=True,
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.pair,
            CatStableExplorationPairState,
        ):
            raise TypeError(
                "Created stable pair result must "
                "contain "
                "CatStableExplorationPairState."
            )

        if (
            self.pair.pair_id
            != self.pair_id
        ):
            raise ValueError(
                "Stable pair result pair_id "
                "does not match pair state."
            )


CAT_STABLE_EXPLORATION_PAIR_CREATION_RESULT_TYPES = (
    CatStableExplorationPairCreationFailedResult,
    CatStableExplorationPairCreatedResult,
)
