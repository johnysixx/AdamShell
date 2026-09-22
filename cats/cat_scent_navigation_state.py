from dataclasses import dataclass
from core.entity.components import SpatialVector3, require_optional_spatial_vector
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

    destination: SpatialVector3 | None = None
    trail_direction: (
        CatScentTrailDirection | None
    ) = None

    def __post_init__(self):
        self.destination = require_optional_spatial_vector(self.destination, field_name="known scent follow destination")
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

    start_position: SpatialVector3 | None = None
    destination: SpatialVector3 | None = None
    trail_direction: (
        CatScentTrailDirection | None
    ) = None
    arrived: bool = False
    reacquired: bool = False
    reacquired_at: SpatialVector3 | None = None
    reacquired_source_id: object = None

    def __post_init__(self):
        self.start_position = require_optional_spatial_vector(self.start_position, field_name="scent search start position")
        self.destination = require_optional_spatial_vector(self.destination, field_name="scent search destination")
        self.reacquired_at = require_optional_spatial_vector(self.reacquired_at, field_name="scent search reacquired position")
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

    destination: SpatialVector3 | None = None

    def __post_init__(self):
        self.destination = require_optional_spatial_vector(self.destination, field_name="scent box follow destination")
