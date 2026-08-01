import random


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

        event = {
            "die": self.name,
            "value": self.last_roll,
            "roll_number": self.roll_count,
            "visibility": "universe_only"
        }

        self.history.append(
            dict(event)
        )

        resolution = None

        if self.resolver is not None:
            resolution = self.resolver.resolve(
                roll_event=event,
                source="quantum_die_roll"
            )

        result = dict(event)

        if resolution is not None:
            result["resolution"] = resolution

        return result