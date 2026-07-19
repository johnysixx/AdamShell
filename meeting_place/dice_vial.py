import random


class DiceVial:

    def __init__(self):
        self.name = "dice_vial"
        self.type = "bar_artifact"
        self.location = "on_bar_counter"

        self.container = {
            "type": "glass_vial",
            "state": "sealed"
        }

        self.medium = {
            "type": "glowing_oily_liquid",
            "state": "shimmering"
        }

        self.dice = {
            "type": "d20",
            "state": "floating"
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "container": self.container,
            "medium": self.medium,
            "dice": self.dice,
            "display_state": "displayed",
            "visibility_scope": "inside_bar_only"
        }

        self._secret_roll = None
        self._secret_event = None

        print("DICE VIAL CREATED")
        print("D20 FLOATS IN GLOWING OILY LIQUID")

    def roll_secretly(self, rng=None):
        rng = rng or random

        self._secret_roll = rng.randint(1, 20)

        box_created = rng.choice([True, False])

        quantum_tick_requested = rng.choice([True, False])

        self._secret_event = {
            "name": "dice_vial_secret_rotation",
            "roll": self._secret_roll,
            "box_created": box_created,
            "quantum_tick_requested": quantum_tick_requested
        }

        return self._secret_event.copy()

    def resolve_missing_universe(self, rng=None):
        event = self.roll_secretly(rng)

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
