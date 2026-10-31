from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class QuantumBoxDisappearedEvent:
    box_id: str
    cause: str
    tick: int

    name: str = field(
        default="quantum_box_disappeared",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(self.box_id, str) or not self.box_id:
            raise ValueError(
                "Disappearance requires a valid quantum box ID."
            )

        if not isinstance(self.cause, str) or not self.cause:
            raise ValueError(
                "Disappearance requires a non-empty cause."
            )

        tick = int(self.tick)
        if tick < 0:
            raise ValueError(
                "Quantum box disappearance tick cannot be negative."
            )

        object.__setattr__(self, "tick", tick)

    def to_dict(self):
        return {
            "name": self.name,
            "box_id": self.box_id,
            "cause": self.cause,
            "tick": self.tick,
        }
