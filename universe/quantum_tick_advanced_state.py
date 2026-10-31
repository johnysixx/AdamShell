from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class UniverseQuantumTickAdvancedEvent:
    """One recorded advancement of the quantum clock."""

    tick: int
    observer: str = "quantum_tick"

    name: str = field(
        default="universe_quantum_tick_advanced",
        init=False,
    )

    def __post_init__(self):
        if type(self.tick) is not int or self.tick < 1:
            raise ValueError(
                "Quantum clock event tick must be "
                "a positive integer."
            )

        if (
            not isinstance(self.observer, str)
            or not self.observer
        ):
            raise ValueError(
                "Quantum clock event requires an observer."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "tick": self.tick,
            "observer": self.observer,
        }
