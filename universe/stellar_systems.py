class StellarSystems:

    def __init__(self, universe):
        self.universe = universe
        self.name = "stellar_systems"
        self.type = "stellar_system_layer"
        self.state = "ready"

        self.systems = []

        self.system_state = {
            "stellar_systems_formed": False,
            "solar_system_formed": False,
            "planet_formation_possible": False,
            "water_formation_possible": False,
            "rocky_worlds_possible": False
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "systems": self.systems,
            "system_state": self.system_state
        }

    def form_stellar_systems(self):
        enriched_clouds = self.universe.world.get("enriched_clouds", [])

        system_forming_clouds = [
            cloud for cloud in enriched_clouds
            if cloud.get("can_form_stellar_systems") is True
        ]

        if not system_forming_clouds:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("STELLAR SYSTEM FORMATION FAILED: no enriched clouds available")
            self.write_to_world()
            return self.public_state

        source_cloud = system_forming_clouds[0]
        composition = source_cloud.get("composition", {})
        available_elements = list(composition.keys())

        self.state = "formed"
        self.public_state["state"] = self.state

        solar_system = {
            "name": "solar_system",
            "type": "stellar_system",
            "state": "forming",
            "generation": 2,
            "formed_from": source_cloud["name"],
            "star": {
                "name": "sun",
                "type": "main_sequence_star",
                "state": "ignited",
                "generation": 2
            },
            "protoplanetary_disk": {
                "name": "solar_protoplanetary_disk",
                "type": "protoplanetary_disk",
                "state": "rotating",
                "available_elements": available_elements,
                "can_form_planets": True,
                "can_form_water": "hydrogen" in composition and "oxygen" in composition,
                "can_form_iron_cores": "iron" in composition,
                "can_form_rocky_worlds": "silicon" in composition and "iron" in composition
            }
        }

        deep_system = {
            "name": "deep_system",
            "type": "stellar_system",
            "state": "forming",
            "generation": 2,
            "formed_from": source_cloud["name"],
            "star": {
                "name": "deep_star_second_generation",
                "type": "main_sequence_star",
                "state": "young",
                "generation": 2
            },
            "protoplanetary_disk": {
                "name": "deep_protoplanetary_disk",
                "type": "protoplanetary_disk",
                "state": "rotating",
                "available_elements": available_elements,
                "can_form_planets": True,
                "can_form_water": "hydrogen" in composition and "oxygen" in composition,
                "can_form_iron_cores": "iron" in composition,
                "can_form_rocky_worlds": "silicon" in composition and "iron" in composition
            }
        }

        self.systems.append(solar_system)
        self.systems.append(deep_system)

        self.system_state["stellar_systems_formed"] = True
        self.system_state["solar_system_formed"] = True
        self.system_state["planet_formation_possible"] = True
        self.system_state["water_formation_possible"] = solar_system["protoplanetary_disk"]["can_form_water"]
        self.system_state["rocky_worlds_possible"] = solar_system["protoplanetary_disk"]["can_form_rocky_worlds"]

        self.record_history()
        self.write_to_world()

        print("STELLAR SYSTEMS FORMED")
        print("SOLAR SYSTEM BEGINS TO FORM")
        print("PROTOPLANETARY DISKS CREATED")
        print("PLANET FORMATION BECOMES POSSIBLE")

        return self.public_state

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "stellar_systems_formed",
            "description": "Enriched clouds collapse into second-generation stellar systems, including the solar system."
        })

    def write_to_world(self):
        self.universe.world["stellar_systems"] = self.public_state
        self.universe.world["systems"] = self.systems
        self.universe.world["solar_system"] = self.systems[0] if self.systems else None
        self.universe.world["stellar_system_state"] = self.system_state
