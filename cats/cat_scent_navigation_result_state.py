from dataclasses import dataclass, field

from cats.cat_olfaction_state import (
    CatOlfactionState,
)
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)
from core.entity.components import (
    SpatialVector3,
)


def _require_optional_position(
    value,
    field_name,
):
    if (
        value is not None
        and not isinstance(
            value,
            SpatialVector3,
        )
    ):
        raise TypeError(
            f"{field_name} must be "
            "SpatialVector3 or None."
        )

    return value


def _require_optional_direction(
    value,
    field_name,
):
    if (
        value is not None
        and not isinstance(
            value,
            CatScentTrailDirection,
        )
    ):
        raise TypeError(
            f"{field_name} must be "
            "CatScentTrailDirection or None."
        )

    return value


@dataclass(slots=True, frozen=True)
class CatScentSearchFailedResult:

    cat: str
    reason: str
    identity: str | None = None

    name: str = field(
        default="cat_scent_search_failed",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatScentSearchingEvent:

    cat: str
    identity: str
    attempt: int
    max_attempts: int
    route_id: str | None
    destination: SpatialVector3 | None
    start_position: SpatialVector3 | None = None
    position: SpatialVector3 | None = None
    executed: bool = True

    name: str = field(
        default="cat_searching_for_scent",
        init=False,
    )

    arrived: bool = field(
        default=False,
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "attempt",
            int(self.attempt),
        )

        object.__setattr__(
            self,
            "max_attempts",
            int(self.max_attempts),
        )

        _require_optional_position(
            self.start_position,
            "Scent search start position",
        )

        _require_optional_position(
            self.position,
            "Scent search current position",
        )

        _require_optional_position(
            self.destination,
            "Scent search destination",
        )


@dataclass(slots=True, frozen=True)
class CatScentReacquiredEvent:

    cat: str
    identity: str
    source_id: object
    position: SpatialVector3 | None
    olfaction: CatOlfactionState

    name: str = field(
        default=(
            "cat_reacquired_scent_during_search"
        ),
        init=False,
    )

    search_interrupted: bool = field(
        default=True,
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
        _require_optional_position(
            self.position,
            "Reacquired scent position",
        )

        if not isinstance(
            self.olfaction,
            CatOlfactionState,
        ):
            raise TypeError(
                "Reacquired scent olfaction must "
                "be CatOlfactionState."
            )


@dataclass(slots=True, frozen=True)
class CatScentSearchStepCompletedEvent:

    cat: str
    identity: str
    attempt: int
    max_attempts: int
    position: SpatialVector3 | None
    trail_direction: CatScentTrailDirection | None

    name: str = field(
        default=(
            "cat_completed_scent_search_step"
        ),
        init=False,
    )

    arrived: bool = field(
        default=True,
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
        object.__setattr__(
            self,
            "attempt",
            int(self.attempt),
        )

        object.__setattr__(
            self,
            "max_attempts",
            int(self.max_attempts),
        )

        _require_optional_position(
            self.position,
            "Completed scent search position",
        )

        _require_optional_direction(
            self.trail_direction,
            "Completed scent search direction",
        )


@dataclass(slots=True, frozen=True)
class CatKnownScentFollowFailedResult:

    cat: str
    reason: str
    identity: str | None = None

    name: str = field(
        default=(
            "cat_known_scent_follow_failed"
        ),
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatKnownScentFollowingEvent:

    cat: str
    identity: str
    layer: str | None
    destination: SpatialVector3 | None
    route_id: str | None
    position: SpatialVector3 | None = None
    executed: bool = True

    name: str = field(
        default="cat_following_known_scent",
        init=False,
    )

    arrived: bool = field(
        default=False,
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    def __post_init__(self):
        _require_optional_position(
            self.destination,
            "Known scent destination",
        )

        _require_optional_position(
            self.position,
            "Known scent current position",
        )


@dataclass(slots=True, frozen=True)
class CatKnownScentReachedEvent:

    cat: str
    identity: str
    layer: str | None
    destination: SpatialVector3
    trail_direction: CatScentTrailDirection | None

    name: str = field(
        default="cat_reached_known_scent",
        init=False,
    )

    arrived: bool = field(
        default=True,
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
            self.destination,
            SpatialVector3,
        ):
            raise TypeError(
                "Reached known scent destination "
                "must be SpatialVector3."
            )

        _require_optional_direction(
            self.trail_direction,
            "Reached known scent direction",
        )


CAT_SCENT_NAVIGATION_RESULT_TYPES = (
    CatScentSearchFailedResult,
    CatScentSearchingEvent,
    CatScentReacquiredEvent,
    CatScentSearchStepCompletedEvent,
    CatKnownScentFollowFailedResult,
    CatKnownScentFollowingEvent,
    CatKnownScentReachedEvent,
)
