from dataclasses import dataclass


@dataclass(slots=True)
class CatNavigationDecisionState:
    route_id: str | None = None
    destination: object = None
    suggested_intent: str | None = None
    decision_roll: float = 0.0
    acceptance_chance: float = 0.0
    decision: str | None = None
    decided: bool = False
