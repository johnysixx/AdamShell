from dataclasses import dataclass


@dataclass(slots=True)
class CatKnownScentFollowState:
    active: bool = False
    arrived: bool = False
    route_id: str | None = None

    identity: str | None = None
    source_id: object = None

    destination: object = None
    trail_direction: object = None



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
    trail_direction: object = None

    arrived: bool = False
    reacquired: bool = False
    reacquired_at: object = None
    reacquired_source_id: object = None
