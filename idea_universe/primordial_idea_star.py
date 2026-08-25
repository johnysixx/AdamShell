class PrimordialIdeaStar:

    def __init__(self):
        self.name = "primordial_idea_star"
        self.type = "primordial_idea_star"
        self.state = "created"

    def ignite(self):
        self.state = "burning"
        return self.state

    def explode(self):
        self.state = "exploded"

        return {
            "type": "primordial_nebula_remnant",
            "source": self.name,
            "elemental_potentials": {
                "hydrogen": 1.0,
                "carbon": 1.0
            }
        }

