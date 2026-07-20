class DarkMatterSign:

    def __init__(self, dark_matter_tank):
        self.name = "dark_matter_sign"
        self.location = "above_dark_matter_tank"

        self.dark_matter_tank = dark_matter_tank

    @property
    def type(self):
        if self.dark_matter_tank.is_empty:
            return "bar_sign"

        return "bar_terminal"

    @property
    def message(self):
        if self.dark_matter_tank.is_empty:
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
        if self.dark_matter_tank.is_empty:
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
            "dark_matter_available": (
                not self.dark_matter_tank.is_empty
            )
        }
