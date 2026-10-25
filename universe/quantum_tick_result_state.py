from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class UniverseQuantumTickResult:
    tick: int
    collapse_count: int
    fluctuation: float
    uncertainty: float
    entropy_delta: float
    entropy_total: float

    name: str = field(
        default="universe_quantum_tick_completed",
        init=False,
    )

    def __post_init__(self):
        for field_name in (
            "tick",
            "collapse_count",
        ):
            object.__setattr__(
                self,
                field_name,
                int(getattr(self, field_name)),
            )

        for field_name in (
            "fluctuation",
            "uncertainty",
            "entropy_delta",
            "entropy_total",
        ):
            object.__setattr__(
                self,
                field_name,
                float(getattr(self, field_name)),
            )

    def __deepcopy__(self, memo):
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "tick": self.tick,
            "collapse_count": self.collapse_count,
            "fluctuation": self.fluctuation,
            "uncertainty": self.uncertainty,
            "entropy_delta": self.entropy_delta,
            "entropy_total": self.entropy_total,
        }
