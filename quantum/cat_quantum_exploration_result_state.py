from dataclasses import dataclass, field

from cats.cat_exploration_state import (
    CatAfterArrivalDecision,
)
from core.entity.components import SpatialVector3
from core.entity.quantum_cat_route import (
    QuantumCatRoute,
)
from navigation.navigation_result_state import (
    NavigationDirectRoutePlan,
)
from quantum.cat_quantum_return_result_state import (
    CAT_QUANTUM_RETURN_RESULT_TYPES,
)


@dataclass(slots=True, frozen=True)
class CatQuantumExplorationRouteNotStartedResult:
    cat: str
    reason: str

    name: str = field(
        default=(
            "cat_quantum_exploration_"
            "route_not_started"
        ),
        init=False,
    )

    started: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatQuantumExplorationRouteStartedEvent:
    cat: str
    pair_id: object
    route_id: str
    start_position: SpatialVector3
    destination: SpatialVector3
    step_count: int
    route: QuantumCatRoute
    plan: NavigationDirectRoutePlan

    name: str = field(
        default=(
            "cat_quantum_exploration_"
            "route_started"
        ),
        init=False,
    )

    most_direct_possible: bool = field(
        default=True,
        init=False,
    )

    started: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.start_position,
            SpatialVector3,
        ):
            raise TypeError(
                "Exploration route start must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.destination,
            SpatialVector3,
        ):
            raise TypeError(
                "Exploration destination must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.route,
            QuantumCatRoute,
        ):
            raise TypeError(
                "Exploration route must be "
                "QuantumCatRoute."
            )

        if not isinstance(
            self.plan,
            NavigationDirectRoutePlan,
        ):
            raise TypeError(
                "Exploration plan must be "
                "NavigationDirectRoutePlan."
            )

        object.__setattr__(
            self,
            "step_count",
            int(self.step_count),
        )


@dataclass(slots=True, frozen=True)
class CatQuantumExplorationNotAdvancedResult:
    cat: str
    reason: str

    name: str = field(
        default=(
            "cat_quantum_exploration_"
            "not_advanced"
        ),
        init=False,
    )

    advanced: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatQuantumExplorationContinuationFailedResult:
    cat: str
    reason: str

    name: str = field(
        default=(
            "cat_quantum_exploration_"
            "continuation_failed"
        ),
        init=False,
    )

    continued: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatQuantumExplorationContinuedEvent:
    cat: str
    pair_id: object
    stage: int
    route_id: str
    start_position: SpatialVector3
    destination: SpatialVector3

    name: str = field(
        default="cat_continued_quantum_exploration",
        init=False,
    )

    return_pair_preserved: bool = field(
        default=True,
        init=False,
    )

    created_new_pair: bool = field(
        default=False,
        init=False,
    )

    continued: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.start_position,
            SpatialVector3,
        ):
            raise TypeError(
                "Continuation start must be "
                "SpatialVector3."
            )

        if not isinstance(
            self.destination,
            SpatialVector3,
        ):
            raise TypeError(
                "Continuation destination must "
                "be SpatialVector3."
            )

        object.__setattr__(
            self,
            "stage",
            int(self.stage),
        )


CAT_QUANTUM_EXPLORATION_CONTINUATION_TYPES = (
    CatQuantumExplorationContinuationFailedResult,
    CatQuantumExplorationContinuedEvent,
)


@dataclass(slots=True, frozen=True)
class CatQuantumExplorationArrivalNotResolvedResult:
    cat: str
    reason: str

    name: str = field(
        default=(
            "cat_quantum_exploration_"
            "arrival_not_resolved"
        ),
        init=False,
    )

    resolved: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatQuantumExplorationArrivalResolvedEvent:
    cat: str
    pair_id: object
    position: SpatialVector3
    memory: object
    known_place: object
    verified_legends: tuple
    legend: object
    decision: CatAfterArrivalDecision
    action: str
    return_plan: object = None
    continuation_plan: object = None

    name: str = field(
        default=(
            "cat_quantum_exploration_"
            "arrival_resolved"
        ),
        init=False,
    )

    resolved: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Exploration arrival position must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.decision,
            CatAfterArrivalDecision,
        ):
            raise TypeError(
                "Exploration arrival decision must "
                "be CatAfterArrivalDecision."
            )

        if (
            self.return_plan is not None
            and not isinstance(
                self.return_plan,
                CAT_QUANTUM_RETURN_RESULT_TYPES,
            )
        ):
            raise TypeError(
                "Exploration return plan must use "
                "a quantum return result object."
            )

        if (
            self.continuation_plan is not None
            and not isinstance(
                self.continuation_plan,
                CAT_QUANTUM_EXPLORATION_CONTINUATION_TYPES,
            )
        ):
            raise TypeError(
                "Exploration continuation plan must "
                "use an exploration continuation "
                "result object."
            )

        object.__setattr__(
            self,
            "verified_legends",
            tuple(
                self.verified_legends
            ),
        )


CAT_QUANTUM_EXPLORATION_ARRIVAL_TYPES = (
    CatQuantumExplorationArrivalNotResolvedResult,
    CatQuantumExplorationArrivalResolvedEvent,
)


@dataclass(slots=True, frozen=True)
class CatQuantumExplorationAdvancedEvent:
    cat: str
    pair_id: object
    route_id: str | None
    position: SpatialVector3 | None
    result: str
    arrived: bool
    arrival_resolution: object = None
    advanced: bool = True

    name: str = field(
        default=(
            "cat_quantum_exploration_advanced"
        ),
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
                "Exploration position must be "
                "SpatialVector3 or None."
            )

        if (
            self.arrival_resolution is not None
            and not isinstance(
                self.arrival_resolution,
                CAT_QUANTUM_EXPLORATION_ARRIVAL_TYPES,
            )
        ):
            raise TypeError(
                "Exploration arrival resolution "
                "must be an exploration result object."
            )


CAT_QUANTUM_EXPLORATION_RESULT_TYPES = (
    CatQuantumExplorationRouteNotStartedResult,
    CatQuantumExplorationRouteStartedEvent,
    CatQuantumExplorationNotAdvancedResult,
    CatQuantumExplorationContinuationFailedResult,
    CatQuantumExplorationContinuedEvent,
    CatQuantumExplorationArrivalNotResolvedResult,
    CatQuantumExplorationArrivalResolvedEvent,
    CatQuantumExplorationAdvancedEvent,
)
