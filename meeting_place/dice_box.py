import random

from universe.logger import UniverseLogger

class DiceBox:

    def __init__(self):
        self.name = "dice_box"
        self.type = "bar_object"
        self.location = "on_bar_counter"

        self.contents = [
            "d4",
            "d6",
            "d8",
            "d10",
            "d10_percentile",
            "d12"
        ]

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "contents": self.contents,
            "missing": ["d20"],
            "display_state": "closed_box_on_bar_counter",
            "visibility_scope": "inside_bar_only"
        }

        UniverseLogger.boot("DICE BOX PLACED ON BAR COUNTER")

    def rotate_random_die(
        self,
        rng=None
    ):
        if not self.contents:
            return {
                "name": (
                    "dice_box_random_rotation_failed"
                ),
                "result": "dice_box_empty",
                "rotated": False
            }

        rng = rng or random

        die_name = rng.choice(
            list(self.contents)
        )

        is_percentile = (
            die_name == "d10_percentile"
        )

        sides = (
            10
            if is_percentile
            else int(die_name[1:])
        )

        raw_value = int(
            rng.randint(
                1,
                sides
            )
        )

        value = (
            0
            if is_percentile
            and raw_value == 10
            else (
                raw_value * 10
                if is_percentile
                else raw_value
            )
        )

        event = {
            "name": (
                "dice_box_die_secretly_rotated"
            ),
            "die": die_name,
            "sides": sides,
            "value": value,
            "raw_value": raw_value,
            "is_percentile": is_percentile,
            "location": self.location,
            "removed_from_box": False,
            "visibility": (
                "secret_bar_dice_event"
            ),
            "rotated": True
        }

        if not hasattr(
            self,
            "rotation_history"
        ):
            self.rotation_history = []

        self.rotation_history.append(
            dict(event)
        )

        self.public_state[
            "last_secret_rotation"
        ] = {
            "die": die_name,
            "value": value
        }

        UniverseLogger.event(
            "A DIE SECRETLY ROTATES "
            "INSIDE THE BAR DICE BOX"
        )

        return event

    def answer_about_contents(self):
        return "dice"

    def answer_about_d20(self):
        return "I do not know"

    def remove_next_die(self):
        if not self.contents:
            return None

        die = self.contents.pop()

        if die not in self.public_state["missing"]:
            self.public_state["missing"].append(die)

        UniverseLogger.event(
            f"DIE MISSING FROM BOX: {die}"
        )

        return die
