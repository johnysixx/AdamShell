from dataclasses import dataclass, field

from core.entity.components import (
    SpatialVector3,
)


@dataclass(slots=True, frozen=True)
class NavigationDirectRoutePlan:

    route_number: int
    start_position: SpatialVector3
    destination_position: SpatialVector3
    distance: float
    step_size: float
    route_steps: tuple[SpatialVector3, ...]

    name: str = field(
        default="direct_route_planned",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.start_position,
            SpatialVector3,
        ):
            raise TypeError(
                "Navigation route start must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.destination_position,
            SpatialVector3,
        ):
            raise TypeError(
                "Navigation route destination "
                "must be SpatialVector3."
            )

        route_steps = tuple(
            self.route_steps
        )

        if not all(
            isinstance(
                step,
                SpatialVector3,
            )
            for step
            in route_steps
        ):
            raise TypeError(
                "Navigation route steps must "
                "be SpatialVector3 objects."
            )

        object.__setattr__(
            self,
            "route_number",
            int(self.route_number),
        )

        object.__setattr__(
            self,
            "distance",
            float(self.distance),
        )

        object.__setattr__(
            self,
            "step_size",
            float(self.step_size),
        )

        object.__setattr__(
            self,
            "route_steps",
            route_steps,
        )

    @property
    def step_count(self):
        return len(
            self.route_steps
        )


@dataclass(slots=True, frozen=True)
class NavigationNearestTargetResult:

    target: object
    position: SpatialVector3
    distance: float

    name: str = field(
        default="nearest_navigation_target_found",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Nearest navigation target "
                "position must be SpatialVector3."
            )

        object.__setattr__(
            self,
            "distance",
            float(self.distance),
        )
