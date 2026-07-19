import random


class QuantumDie:

    def __init__(self, sides=20):
        self.sides = sides
        self.name = f"quantum_d{sides}"
        self.last_roll = None

    def roll(self, rng=None):
        if rng is None:
            rng = random

        self.last_roll = rng.randint(
            1,
            self.sides
        )

        return {
            "die": self.name,
            "value": self.last_roll
        }
