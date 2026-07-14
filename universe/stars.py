class Stars:

    def __init__(self, universe):
        self.universe = universe
        self.name = "stars"
        self.type = "stellar_layer"
        self.state = "ready"

        self.stars = []

        self.stellar_state = {
            "first_stars_formed": False,
            "stellar_fusion_possible": False,
            "heavy_elements_possible": False
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "stars": self.stars,
            "stellar_state": self.stellar_state
        }

    def form_first_stars(self):
        germinal_clouds = self.universe.world.get("germinal_clouds", [])

        star_forming_clouds = [
            cloud for cloud in germinal_clouds
            if cloud.get("can_form_stars") is True
        ]

        if not star_forming_clouds:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("STAR FORMATION FAILED: no germinal clouds ready")
            self.write_to_world()
            return self.public_state

        self.state = "formed"
        self.public_state["state"] = self.state

        self.stars.append({
            "name": "first_star",
            "type": "primordial_star",
            "generation": 1,
            "state": "ignited",
            "formed_from": star_forming_clouds[0]["name"],
            "composition": {
                "hydrogen": "dominant",
                "helium": "secondary",
                "trace_lithium": "trace"
            },
            "can_fuse_elements": True,
            "can_create_heavy_elements": True
        })

        self.stars.append({
            "name": "deep_star",
            "type": "primordial_star",
            "generation": 1,
            "state": "young",
            "formed_from": star_forming_clouds[-1]["name"],
            "composition": {
                "hydrogen": "dominant",
                "helium": "secondary"
            },
            "can_fuse_elements": True,
            "can_create_heavy_elements": True
        })

        self.stellar_state["first_stars_formed"] = True
        self.stellar_state["stellar_fusion_possible"] = True
        self.stellar_state["heavy_elements_possible"] = True

        self.record_history()
        self.write_to_world()

        print("FIRST STARS FORMED")
        print("HYDROGEN IGNITES INSIDE PRIMORDIAL STARS")
        print("STELLAR FUSION BECOMES POSSIBLE")

        return self.public_state

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "first_stars_formed",
            "description": "The first stars ignite inside germinal cosmic clouds. Stellar fusion becomes possible."
        })

    def write_to_world(self):
        self.universe.world["stars"] = self.public_state
        self.universe.world["first_stars"] = self.stars
        self.universe.world["stellar_state"] = self.stellar_state
