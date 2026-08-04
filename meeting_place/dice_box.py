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

    def rotate_named_die(
        self,
        die_name,
        rng=None
    ):
        if die_name not in self.contents:
            return {
                "name": "dice_box_named_rotation_failed",
                "die": die_name,
                "result": "die_not_in_box",
                "rotated": False
            }

        rng = rng or random

        result = self._roll_die(
            die_name,
            rng
        )

        self._record_rotation(
            result
        )

        UniverseLogger.event(
            f"{die_name.upper()} SECRETLY ROTATES "
            "INSIDE THE BAR DICE BOX"
        )

        return result

    def rotate_all_dice(
        self,
        rng=None
    ):
        rng = rng or random

        results = []

        for die_name in list(
            self.contents
        ):
            result = self._roll_die(
                die_name,
                rng
            )

            results.append(
                result
            )

            self._record_rotation(
                result
            )

        event = {
            "name": "dice_box_all_rotation",
            "rotated_count": len(
                results
            ),
            "results": results,
            "visibility": (
                "secret_bar_dice_event"
            )
        }

        if not hasattr(
            self,
            "all_rotation_history"
        ):
            self.all_rotation_history = []

        self.all_rotation_history.append(
            {
                "name": event["name"],
                "rotated_count": (
                    event["rotated_count"]
                ),
                "results": [
                    dict(result)
                    for result in results
                ],
                "visibility": (
                    event["visibility"]
                )
            }
        )

        self.public_state[
            "last_all_rotation"
        ] = {
            result["die"]: (
                result["value"]
            )
            for result in results
        }

        UniverseLogger.event(
            "ALL DICE SECRETLY ROTATE "
            "INSIDE THE BAR DICE BOX"
        )

        return event

    def _roll_die(
        self,
        die_name,
        rng
    ):
        is_percentile = (
            die_name == "d10_percentile"
        )

        sides = (
            10
            if is_percentile
            else int(die_name[1:])
        )

        face_value = int(
            rng.randint(
                1,
                sides
            )
        )

        percentile_tens = None

        if is_percentile:
            percentile_tens = (
                0
                if face_value == 10
                else face_value * 10
            )

            value = percentile_tens

        else:
            value = face_value

        return {
            "name": (
                "dice_box_die_secretly_rotated"
            ),
            "die": die_name,
            "sides": sides,

            # Jednozna?n? nov? pole.
            "face_value": face_value,
            "percentile_tens": (
                percentile_tens
            ),

            # Kompatibilita se st?vaj?c?m k?dem.
            "raw_value": face_value,
            "value": value,

            "is_percentile": is_percentile,
            "location": self.location,
            "removed_from_box": False,
            "visibility": (
                "secret_bar_dice_event"
            ),
            "rotated": True
        }

    def _record_rotation(
        self,
        event
    ):
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
            "die": event["die"],
            "value": event["value"]
        }

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

        event = self._roll_die(
            die_name,
            rng
        )

        self._record_rotation(
            event
        )

        UniverseLogger.event(
            "A DIE SECRETLY ROTATES "
            "INSIDE THE BAR DICE BOX"
        )

        return event

    def rotate_percentile_pair(
        self,
        rng=None
    ):
        """
        Provede skute?n? hod d100 pomoc?:
        - d10_percentile jako des?tek,
        - oby?ejn? d10 jako jednotek.

        00 znamen? 100.
        """
        rng = rng or random

        tens = self._roll_die(
            "d10_percentile",
            rng
        )

        units_die = self._roll_die(
            "d10",
            rng
        )

        units = (
            0
            if units_die["face_value"] == 10
            else units_die["face_value"]
        )

        percentile_value = (
            tens["percentile_tens"]
            + units
        )

        if percentile_value == 0:
            percentile_value = 100

        self._record_rotation(
            tens
        )

        self._record_rotation(
            units_die
        )

        event = {
            "name": (
                "dice_box_percentile_pair_rotated"
            ),
            "dice": [
                "d10_percentile",
                "d10"
            ],
            "tens": dict(tens),
            "units": {
                **dict(units_die),
                "percentile_units": units
            },
            "value": percentile_value,
            "minimum": 1,
            "maximum": 100,
            "location": self.location,
            "removed_from_box": False,
            "visibility": (
                "secret_bar_dice_event"
            ),
            "rotated": True
        }

        if not hasattr(
            self,
            "percentile_history"
        ):
            self.percentile_history = []

        self.percentile_history.append(
            dict(event)
        )

        self.public_state[
            "last_percentile_rotation"
        ] = percentile_value

        UniverseLogger.event(
            "PERCENTILE DICE SECRETLY ROTATE "
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
            self.public_state["missing"].append(
                die
            )

        UniverseLogger.event(
            f"DIE MISSING FROM BOX: {die}"
        )

        return die

