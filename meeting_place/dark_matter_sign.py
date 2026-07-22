class DarkMatterSign:

    def __init__(self):
        self.name = "dark_matter_sign"

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
        if not self.has_tank:
            return "behind_bar_dark_matter_mount"

        return "above_dark_matter_tank"

    @property
    def type(self):
        if not self.dark_matter_available:
            return "bar_sign"

        return "bar_terminal"

    @property
    def message(self):
        if not self.dark_matter_available:
            return (
                "DARK MATTER: COMING SOON TO EVERY "
                "SPACE BAR, INCLUDING YOURS."
            )

        return (
            "DARK MATTER: AVAILABLE TODAY IN EVERY "
            "SPACE BAR. "
            "ONLY FOR THE PRICE OF EXISTENCE."
        )

    @property
    def state(self):
        if not self.dark_matter_available:
            return "coming_soon"

        return "available"

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
