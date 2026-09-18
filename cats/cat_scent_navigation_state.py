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
