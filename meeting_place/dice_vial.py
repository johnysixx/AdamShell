import random

from universe.logger import UniverseLogger
from .bar_objects import DiceVialContainer, DiceVialMedium, DiceVialDie


class DiceVial:

    def __init__(self):
        self.name = "dice_vial"
        self.type = "bar_artifact"
        self.location = "on_bar_counter"

        self.container = DiceVialContainer(
            type="glass_vial",
            state="sealed"
        )

        self.medium = DiceVialMedium(
            type="glowing_oily_liquid",
            state="shimmering"
        )

        self.dice = DiceVialDie(
            type="d20",
            state="floating"
        )

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "container": self.container.to_dict(),
            "medium": self.medium.to_dict(),
            "dice": self.dice.to_dict(),
            "display_state": "displayed",
            "visibility_scope": "inside_bar_only"
        }

        self._secret_roll = None
        self._secret_event = None

        UniverseLogger.boot("DICE VIAL CREATED")
        UniverseLogger.boot(
            "D20 FLOATS IN GLOWING OILY LIQUID"
        )

    def roll(self, rng=None):
        rng = rng or random

        self._secret_roll = rng.randint(
            1,
            20
        )

        box_created = rng.choice(
            [True, False]
        )

        quantum_tick_requested = rng.choice(
            [True, False]
        )

        self._secret_event = {
            "name": "dice_vial_secret_rotation",
            "roll": self._secret_roll,
            "box_created": box_created,
            "quantum_tick_requested": (
                quantum_tick_requested
            )
        }

        return self._secret_event.copy()

    def resolve_missing_universe(self, rng=None):
        event = self.roll(
            rng=rng
        )

        if event["roll"] <= 10:
            return {
                "layer": "multiverse",
                "universe_id": 0,
                "secret_event": event
            }

        return {
            "layer": "quantum_layer",
            "universe_id": 0.5,
            "secret_event": event
        }

    def clear_secret(self):
        self._secret_roll = None
        self._secret_event = None