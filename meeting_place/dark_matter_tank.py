class DarkMatterTank:

    def __init__(self):
        self.name = "dark_matter_tank"
        self.type = "bar_storage_tank"

        self.location = "behind_bar_counter"
        self.state = "empty"

        self.dark_matter_kg = 0.0
        self.capacity_kg = None

    @property
    def is_empty(self):
        return self.dark_matter_kg <= 0.0

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "state": self.state,
            "dark_matter_kg": self.dark_matter_kg,
            "capacity_kg": self.capacity_kg,
            "is_empty": self.is_empty
        }
