from dataclasses import dataclass


@dataclass(slots=True)
class CatNavigationOfferState:
    suggested_intent: str | None = None
    route_id: str | None = None
    destination: object = None
    route_step_count: int = 0
    accepted: bool = False
    declined: bool = False
    offered: bool = True
