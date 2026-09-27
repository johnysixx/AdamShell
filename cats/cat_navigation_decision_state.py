from dataclasses import dataclass

from cats.cat_navigation_decision import (
    CatNavigationDecision,
)


@dataclass(slots=True)
class CatNavigationDecisionState:
    route_id: str | None = None
    destination: object = None
    suggested_intent: str | None = None
    decision_roll: float = 0.0
    acceptance_chance: float = 0.0
    decision: CatNavigationDecision | None = None
    decided: bool = False

    def __post_init__(self):
        if (
            self.decision is not None
            and not isinstance(
                self.decision,
                CatNavigationDecision,
            )
        ):
            raise TypeError(
                "Cat navigation decision must use "
                "CatNavigationDecision."
            )
