class HeavyElementNucleosynthesis:

    def __init__(self, universe):
        self.universe = universe
        self.name = "heavy_element_nucleosynthesis"
        self.type = "post_iron_element_process"
        self.state = "ready"

        self.heavy_elements = {}

        self.process_state = {
            "iron_seed_available": False,
            "supernova_enrichment_available": False,
            "neutron_capture_possible": False,
            "heavy_elements_forged": False,
            "enriched_clouds_updated": False
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "heavy_elements": self.heavy_elements,
            "process_state": self.process_state
        }

    def forge_heavy_elements(self):
        elements_up_to_iron = self.universe.world.get("elements_up_to_iron", {})
        enriched_clouds = self.universe.world.get("enriched_clouds", [])

        if "iron" not in elements_up_to_iron:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("HEAVY ELEMENT NUCLEOSYNTHESIS FAILED: iron seed is missing")
            self.write_to_world()
            return self.public_state

        if not enriched_clouds:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("HEAVY ELEMENT NUCLEOSYNTHESIS FAILED: no enriched clouds available")
            self.write_to_world()
            return self.public_state

        self.state = "forged"
        self.public_state["state"] = self.state

        self.process_state["iron_seed_available"] = True
        self.process_state["supernova_enrichment_available"] = True
        self.process_state["neutron_capture_possible"] = True

        self.add_heavy_element("cobalt", 27)
        self.add_heavy_element("nickel", 28)
        self.add_heavy_element("copper", 29)
        self.add_heavy_element("zinc", 30)
        self.add_heavy_element("silver", 47)
        self.add_heavy_element("tin", 50)
        self.add_heavy_element("iodine", 53)
        self.add_heavy_element("gold", 79)
        self.add_heavy_element("platinum", 78)
        self.add_heavy_element("lead", 82)
        self.add_heavy_element("uranium", 92)

        self.process_state["heavy_elements_forged"] = True

        self.update_enriched_clouds(enriched_clouds)
        self.record_history()
        self.write_to_world()

        print("HEAVY ELEMENT NUCLEOSYNTHESIS STARTED")
        print("IRON SEEDS CAPTURE NEUTRONS")
        print("HEAVY ELEMENTS FORGED BEYOND IRON")
        print("ENRICHED CLOUDS UPDATED WITH HEAVY ELEMENTS")

        return self.public_state

    def add_heavy_element(self, name, atomic_number):
        self.heavy_elements[name] = {
            "name": name,
            "type": "element",
            "atomic_number": atomic_number,
            "state": "forged",
            "origin": "post_iron_nucleosynthesis",
            "requires": [
                "iron_seed",
                "supernova_enrichment",
                "neutron_capture"
            ]
        }

    def update_enriched_clouds(self, enriched_clouds):
        for cloud in enriched_clouds:
            composition = cloud.setdefault("composition", {})
            composition.update(self.heavy_elements)

            cloud["contains_heavy_elements"] = True
            cloud["can_form_metal_rich_systems"] = True

        self.process_state["enriched_clouds_updated"] = True

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "heavy_elements_forged",
            "description": "After the iron limit, neutron capture and explosive stellar processes forge heavy elements and enrich stellar clouds."
        })

    def write_to_world(self):
        elements_up_to_iron = self.universe.world.get("elements_up_to_iron", {})

        all_elements = {}
        all_elements.update(elements_up_to_iron)
        all_elements.update(self.heavy_elements)

        self.universe.world["heavy_element_nucleosynthesis"] = self.public_state
        self.universe.world["heavy_elements"] = self.heavy_elements
        self.universe.world["elements"] = all_elements
        self.universe.world["heavy_element_state"] = self.process_state
