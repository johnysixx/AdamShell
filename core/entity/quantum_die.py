import random
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class QuantumDieRollEvent:
    die: str
    value: int
    roll_number: int
    visibility: str = field(
        default="universe_only",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "die",
            str(self.die),
        )
        object.__setattr__(
            self,
            "value",
            int(self.value),
        )
        object.__setattr__(
            self,
            "roll_number",
            int(self.roll_number),
        )

    def to_dict(self):
        return {
            "die": self.die,
            "value": self.value,
            "roll_number": self.roll_number,
            "visibility": self.visibility,
        }


class QuantumDie:

    def __init__(
        self,
        sides=20,
        resolver=None
    ):
        self.sides = sides
        self.name = f"quantum_d{sides}"
        self.last_roll = None
        self.roll_count = 0
        self.history = []
        self.resolver = resolver

    def roll(self, rng=None):
        rng = rng or random

        self.roll_count += 1

        self.last_roll = rng.randint(
            1,
            self.sides
        )

        event = QuantumDieRollEvent(
            die=self.name,
            value=self.last_roll,
            roll_number=self.roll_count,
        )

        self.history.append(
            event
        )

        roll_snapshot = event.to_dict()

        resolution = None

        if self.resolver is not None:
            resolution = self.resolver.resolve(
                roll_event=event,
                source="quantum_die_roll"
            )

        result = dict(
            roll_snapshot
        )

        if resolution is not None:
            result["resolution"] = (
                resolution.to_dict()
            )

        return result