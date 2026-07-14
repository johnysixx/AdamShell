class BigBang:

    def __init__(self, universe):
        self.universe = universe
        self.name = "big_bang"
        self.state = "ready"

        self.primordial_elements = {
            "energy": {
                "name": "energy",
                "type": "primordial_force",
                "state": "released"
            },
            "matter": {
                "name": "matter",
                "type": "primordial_substance",
                "state": "formed"
            },
            "hydrogen": {
                "name": "hydrogen",
                "type": "element",
                "state": "available"
            },
            "oxygen": {
                "name": "oxygen",
                "type": "element",
                "state": "potential"
            },
            "carbon": {
                "name": "carbon",
                "type": "element",
                "state": "potential"
            },
            "nitrogen": {
                "name": "nitrogen",
                "type": "element",
                "state": "potential"
            }
        }

        self.drink_foundations = {
            "water_potential": {
                "name": "water_potential",
                "type": "drink_foundation",
                "requires": ["hydrogen", "oxygen"],
                "state": "possible"
            },
            "organic_potential": {
                "name": "organic_potential",
                "type": "drink_foundation",
                "requires": ["carbon", "hydrogen", "oxygen", "nitrogen"],
                "state": "possible"
            },
            "fermentation_potential": {
                "name": "fermentation_potential",
                "type": "drink_process_foundation",
                "requires": ["organic_potential", "time"],
                "state": "possible"
            },
            "cold_potential": {
                "name": "cold_potential",
                "type": "drink_storage_foundation",
                "requires": ["energy", "space"],
                "state": "possible"
            }
        }

        self.public_state = {
            "name": self.name,
            "type": "cosmic_origin_event",
            "state": self.state,
            "primordial_elements": self.primordial_elements,
            "drink_foundations": self.drink_foundations
        }

    def explode(self):
        self.state = "exploded"
        self.public_state["state"] = self.state

        self.universe.world["big_bang"] = self.public_state
        self.universe.world["primordial_elements"] = self.primordial_elements
        self.universe.world["drink_foundations"] = self.drink_foundations

        print("💥 BIG BANG")
        print("PRIMORDIAL ENERGY RELEASED")
        print("MATTER FORMED")
        print("DRINK FOUNDATIONS SEEDED INTO UNIVERSE")

        return self.public_state
