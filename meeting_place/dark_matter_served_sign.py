class DarkMatterServedSign:

    def __init__(self):
        self.name = "dark_matter_served_sign"
        self.type = "bar_counter_sign"
        self.location = "outside_front_of_bar"

        self.total_dark_matter_served_kg = 0.0
        self.total_servings = 0

    @property
    def message(self):
        return (
            "TOTAL DARK MATTER SERVED\n\n"
            f"{self.total_servings} SERVINGS"
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "total_dark_matter_served_kg": (
                self.total_dark_matter_served_kg
            ),
            "total_servings": self.total_servings,
            "message": self.message
        }
