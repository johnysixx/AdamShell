from dataclasses import dataclass, field

from core.entity.quantum_cat_route import (
    QuantumCatRoute,
)
from navigation.navigation_result_state import (
    NavigationDirectRoutePlan,
)


@dataclass(slots=True, frozen=True)
class QuantumCatRoutePlannedResult:

    cat_id: str
    destination: object
    plan: NavigationDirectRoutePlan
    route: QuantumCatRoute
    target: object | None = None
    target_id: str | None = None
    target_distance: float | None = None
    name: str = (
        "cat_direct_route_planned"
    )

    planned: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.plan,
            NavigationDirectRoutePlan,
        ):
            raise TypeError(
                "Quantum cat route requires "
                "NavigationDirectRoutePlan."
            )

        if not isinstance(
            self.route,
            QuantumCatRoute,
        ):
            raise TypeError(
                "Quantum cat route result requires "
                "QuantumCatRoute."
            )

        if self.name not in {
            "cat_direct_route_planned",
            (
                "cat_route_to_nearest_"
                "huntable_cronenberg_planned"
            ),
        }:
            raise ValueError(
                "Unknown quantum cat route "
                "result name."
            )

        if self.target_id is not None:
            object.__setattr__(
                self,
                "target_id",
                str(self.target_id),
            )

        if self.target_distance is not None:
            object.__setattr__(
                self,
                "target_distance",
                float(
                    self.target_distance
                ),
            )


@dataclass(slots=True, frozen=True)
class QuantumCatRouteNotPlannedResult:

    cat_id: str | None
    reason: str

    name: str = field(
        default="cat_hunt_route_not_planned",
        init=False,
    )

    planned: bool = field(
        default=False,
        init=False,
    )
