from dataclasses import dataclass


@dataclass(slots=True)
class RootTransitionState:

    target: str = "root_universe"
    status: str = "created"
    creator: str | None = None
    existence_cost_pct: float = 25.0
    energy_cost_j: float = 1000.0
    can_enter: bool = False

    def to_dict(self):
        return {
            "target": self.target,
            "state": self.status,
            "creator": self.creator,
            "existence_cost_pct": self.existence_cost_pct,
            "energy_cost_j": self.energy_cost_j,
            "can_enter": self.can_enter,
        }
