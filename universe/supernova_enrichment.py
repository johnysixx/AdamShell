class SupernovaEnrichment:

    def __init__(self, universe):
        self.universe = universe
        self.name = "supernova_enrichment"
        self.type = "stellar_enrichment_process"
        self.state = "ready"

        self.supernovae = []
        self.enriched_clouds = []

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "supernovae": self.supernovae,
            "enriched_clouds": self.enriched_clouds
        }

    def enrich_space(self):
        first_stars = self.universe.world.get("first_stars", [])
        elements = self.universe.world.get("elements_up_to_iron", {})

        if not first_stars:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("SUPERNOVA ENRICHMENT FAILED: no stars available")
            self.write_to_world()
            return self.public_state

        if "iron" not in elements:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("SUPERNOVA ENRICHMENT FAILED: iron has not been forged yet")
            self.write_to_world()
            return self.public_state

        self.state = "enriched"
        self.public_state["state"] = self.state

        self.supernovae.append({
            "name": "first_supernova",
            "type": "supernova",
            "state": "exploded",
            "source_star": first_stars[0]["name"],
            "released_elements": list(elements.keys())
        })

        self.enriched_clouds.append({
            "name": "first_enriched_cloud",
            "type": "enriched_stellar_cloud",
            "state": "expanding",
            "origin": "first_supernova",
            "composition": elements,
            "contains_elements_up_to_iron": True,
            "can_form_stellar_systems": True
        })

        self.record_history()
        self.write_to_world()

        print("FIRST SUPERNOVA EXPLODED")
        print("ELEMENTS UP TO IRON RELEASED INTO SPACE")
        print("ENRICHED CLOUDS FORMED")
        print("STELLAR SYSTEM FORMATION BECOMES POSSIBLE")

        return self.public_state

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "supernova_enrichment",
            "description": "The first supernova releases elements up to iron into space, forming enriched clouds for future stellar systems."
        })

    def write_to_world(self):
        self.universe.world["supernova_enrichment"] = self.public_state
        self.universe.world["supernovae"] = self.supernovae
        self.universe.world["enriched_clouds"] = self.enriched_clouds
