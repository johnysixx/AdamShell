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
            "type": "d12",
            "state": "floating"
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "container": self.container,
            "medium": self.medium,
            "dice": self.dice,
            "display_state": "displayed"
        }

        self._secret_roll = None

        print("DICE VIAL CREATED")
        print("D12 FLOATS IN GLOWING OILY LIQUID")

    def roll_secretly(self):
        self._secret_roll = random.randint(1, 12)

    def clear_secret(self):
        self._secret_roll = None
