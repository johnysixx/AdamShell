from dataclasses import dataclass


@dataclass(slots=True)
class UniverseTimeState:

    tick: int = 0
    flow: float = 1.0
    state: str = "linear"
    pressure: float = 0.0

    def advance(self):
        self.tick += 1
        self.pressure += 0.1 * self.flow

        return self.pressure

    def to_dict(self):
        return {
            "tick": self.tick,
            "flow": self.flow,
            "state": self.state,
            "pressure": self.pressure,
        }


@dataclass(slots=True)
class UniverseGravityState:

    enabled: bool = True
    strength: float = 1.0
    curvature_effect: float = 0.01

    @property
    def curvature_delta(self):
        if not self.enabled:
            return 0.0

        return (
            self.curvature_effect
            * self.strength
        )

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "strength": self.strength,
            "curvature_effect": (
                self.curvature_effect
            ),
        }
