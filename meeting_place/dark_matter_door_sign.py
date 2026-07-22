class DarkMatterDoorSign:

    def __init__(self):
        self.name = "dark_matter_door_sign"
        self.type = "bar_door_sign"

        self.dark_matter_tank = None

    def attach_tank(self, dark_matter_tank):
        if self.dark_matter_tank is not None:
            return False

        self.dark_matter_tank = dark_matter_tank

        return True

    @property
    def has_tank(self):
        return self.dark_matter_tank is not None

    @property
    def dark_matter_available(self):
        return (
            self.has_tank
            and not self.dark_matter_tank.is_empty
        )

    @property
    def location(self):
        if not self.dark_matter_available:
            return "inside_front_door"

        return "outside_front_door"

    @property
    def message(self):
        if not self.dark_matter_available:
            return (
                "DARK MATTER: COMING SOON TO EVERY "
                "SPACE BAR, INCLUDING YOURS."
            )

        return (
            "DARK MATTER IS SERVED IN THIS BAR."
        )

    @property
    def state(self):
        if not self.dark_matter_available:
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
            "tank_installed": self.has_tank,
            "dark_matter_available": (
                self.dark_matter_available
            )
        }
