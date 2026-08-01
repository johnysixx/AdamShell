from universe.logger import UniverseLogger


class LemonadeSigns:

    def __init__(self):
        self.outside_sign = {
            "name": "outside_lemonade_sign",
            "location": "outside_bar",
            "text": "WE HAVE LEMONADE!",
            "visible": False
        }

        self.inside_sign = {
            "name": "inside_lemonade_sign",
            "location": "inside_bar",
            "text": "FREE LEMONADE",
            "visible": False
        }

    def sync_with_reservoir(
        self,
        lemonade_reservoir
    ):
        visible = (
            lemonade_reservoir.is_present
        )

        changed = (
            self.outside_sign["visible"]
            != visible
        )

        self.outside_sign["visible"] = (
            visible
        )

        self.inside_sign["visible"] = (
            visible
        )

        if changed and visible:
            UniverseLogger.event(
                "LEMONADE SIGNS APPEAR: "
                "WE HAVE LEMONADE! / "
                "FREE LEMONADE"
            )

        elif changed and not visible:
            UniverseLogger.event(
                "LEMONADE SIGNS DISAPPEAR"
            )

        return self.public_state

    @property
    def public_state(self):
        return {
            "outside_sign": dict(
                self.outside_sign
            ),
            "inside_sign": dict(
                self.inside_sign
            )
        }
