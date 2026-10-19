from dataclasses import dataclass

from core.entity.components import (
    SpatialVector3,
)


@dataclass(slots=True, frozen=True)
class CatRouteMemoryDetails:

    route_id: str
    destination: object
    start_position: SpatialVector3
    current_position: SpatialVector3
    current_step_index: int
    next_position: SpatialVector3 | None
    route_state: str
    has_arrived: bool

    route_steps: tuple = ()
    blocked_by: str | None = None
    blocked_position: SpatialVector3 | None = None
    detour_position: SpatialVector3 | None = None
    returns_to_original_route: bool | None = None
    previous_position: SpatialVector3 | None = None
    position: SpatialVector3 | None = None
    arrival_position: SpatialVector3 | None = None

    def __post_init__(
        self,
    ):
        for field_name in (
            "start_position",
            "current_position",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                SpatialVector3,
            ):
                raise TypeError(
                    "Cat route memory "
                    f"{field_name} must be "
                    "SpatialVector3."
                )

        for field_name in (
            "next_position",
            "blocked_position",
            "detour_position",
            "previous_position",
            "position",
            "arrival_position",
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
                    "Cat route memory "
                    f"{field_name} must be "
                    "SpatialVector3 or None."
                )

        route_steps = tuple(
            self.route_steps
        )

        for route_step in route_steps:
            if not isinstance(
                route_step,
                SpatialVector3,
            ):
                raise TypeError(
                    "Cat route memory route step "
                    "must be SpatialVector3."
                )

        object.__setattr__(
            self,
            "route_steps",
            route_steps,
        )
