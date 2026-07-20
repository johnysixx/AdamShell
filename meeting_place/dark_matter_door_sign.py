class DarkMatterDoorSign:

    def __init__(self, dark_matter_tank):
        self.name = "dark_matter_door_sign"
        self.type = "bar_door_sign"

        self.dark_matter_tank = dark_matter_tank

    @property
    def location(self):
        if self.dark_matter_tank.is_empty:
            return "inside_front_door"

        return "outside_front_door"

    @property
    def message(self):
        if self.dark_matter_tank.is_empty:
            return (
                "DARK MATTER: COMING SOON TO EVERY "
                "SPACE BAR, INCLUDING YOURS."
            )

        return (
            "DARK MATTER IS SERVED IN THIS BAR."
        )

    @property
    def state(self):
        if self.dark_matter_tank.is_empty:
            return "coming_soon_inside"

        return "available_outside"

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "state": self.state,
            "message": self.message,
            "dark_matter_available": (
                not self.dark_matter_tank.is_empty
            )
        }
