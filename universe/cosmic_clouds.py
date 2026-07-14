class CosmicClouds:

    def __init__(self, universe):
        self.universe = universe
        self.name = "cosmic_clouds"
        self.type = "cosmic_structure_layer"
        self.state = "ready"

        self.clouds = []

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "clouds": self.clouds
        }

    def form_germinal_clouds(self):
        primordial_elements = self.universe.world.get("primordial_elements", {})

        if "hydrogen" not in primordial_elements or "helium" not in primordial_elements:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("COSMIC CLOUD FORMATION FAILED: missing hydrogen or helium")
            self.write_to_world()
            return self.public_state

        self.state = "formed"
        self.public_state["state"] = self.state

        self.clouds.append({
            "name": "first_germinal_cloud",
            "type": "germinal_cloud",
            "state": "condensing",
            "composition": {
                "hydrogen": "dominant",
                "helium": "secondary",
                "trace_lithium": "trace"
            },
            "can_form_stars": True
        })

        self.clouds.append({
            "name": "deep_germinal_cloud",
            "type": "germinal_cloud",
            "state": "quiet",
            "composition": {
                "hydrogen": "dominant",
                "helium": "secondary"
            },
            "can_form_stars": True
        })

        self.record_history()
        self.write_to_world()

        print("GERMINAL COSMIC CLOUDS FORMED")
        print("HYDROGEN AND HELIUM BEGIN TO GATHER")
        print("STAR FORMATION POTENTIAL CREATED")

        return self.public_state

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "germinal_clouds_formed",
            "description": "Hydrogen and helium gather into the first germinal clouds, preparing the universe for star formation."
        })

    def write_to_world(self):
        self.universe.world["cosmic_clouds"] = self.public_state
        self.universe.world["germinal_clouds"] = self.clouds
