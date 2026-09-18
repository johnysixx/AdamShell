from dataclasses import dataclass
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)


@dataclass(slots=True)
class CatKnownScentFollowState:
    active: bool = False
    arrived: bool = False
    route_id: str | None = None

    identity: str | None = None
    source_id: object = None

    destination: object = None
    trail_direction: (
        CatScentTrailDirection | None
    ) = None

    def __post_init__(self):
        if (
            self.trail_direction is not None
            and not isinstance(
                self.trail_direction,
                CatScentTrailDirection,
            )
        ):
            raise TypeError(
                'Known scent follow trail direction must be CatScentTrailDirection.'
            )


@dataclass(slots=True)
class CatScentSearchState:
    active: bool = False
    identity: str | None = None
    layer: str | None = None
    route_id: str | None = None

    attempts: int = 0
    current_attempt: int = 0
    max_attempts: int = 0

    start_position: object = None
    destination: object = None
    trail_direction: (
        CatScentTrailDirection | None
    ) = None
    arrived: bool = False
    reacquired: bool = False
    reacquired_at: object = None
    reacquired_source_id: object = None

    def __post_init__(self):
        if (
            self.trail_direction is not None
            and not isinstance(
                self.trail_direction,
                CatScentTrailDirection,
            )
        ):
            raise TypeError(
                'Scent search trail direction must be CatScentTrailDirection.'
            )



@dataclass(slots=True)
class CatScentBoxFollowState:
    active: bool = False
    arrived_at_box: bool = False

    route_id: str | None = None

    source_box_id: object = None
    target_box_id: object = None
    identity: str | None = None

    destination: object = None
