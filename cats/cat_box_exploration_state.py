from dataclasses import dataclass


@dataclass(slots=True)
class CatBoxExplorationState:
    active: bool = False
    arrived: bool = False

    box_id: object = None
    route_id: str | None = None
    destination: object = None

    observed: bool = False
