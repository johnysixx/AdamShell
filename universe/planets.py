class Planets:

    def __init__(self, universe):
        self.universe = universe
        self.name = "planets"
        self.type = "planetary_layer"
        self.state = "ready"

        self.planets = []

        self.planetary_materials = {
            "water": {
                "name": "water",
                "type": "planetary_material",
                "state": "possible",
                "requires": ["hydrogen", "oxygen"]
            },
            "ice": {
                "name": "ice",
                "type": "planetary_material",
                "state": "possible",
                "requires": ["water", "cold"]
            },
            "minerals": {
                "name": "minerals",
                "type": "planetary_material",
                "state": "possible",
                "requires": ["silicon", "iron", "magnesium", "calcium"]
            },
            "organic_molecules": {
                "name": "organic_molecules",
                "type": "planetary_material",
                "state": "possible",
                "requires": ["carbon", "hydrogen", "oxygen", "nitrogen"]
            }
        }

        self.planetary_state = {
            "planets_formed": False,
            "earth_formed": False,
            "water_possible": False,
            "ice_possible": False,
            "minerals_possible": False,
            "organic_molecules_possible": False
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "planets": self.planets,
            "planetary_materials": self.planetary_materials,
            "planetary_state": self.planetary_state
        }

    def form_planets(self):
        solar_system = self.universe.world.get("solar_system")

        if solar_system is None:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("PLANET FORMATION FAILED: no solar system available")
            self.write_to_world()
            return self.public_state

        disk = solar_system.get("protoplanetary_disk", {})

        if not disk.get("can_form_planets"):
            self.state = "failed"
            self.public_state["state"] = self.state

            print("PLANET FORMATION FAILED: protoplanetary disk cannot form planets")
            self.write_to_world()
            return self.public_state

        available_elements = disk.get("available_elements", [])

        self.state = "formed"
        self.public_state["state"] = self.state

        self.planets.append({
            "name": "mercury",
            "type": "rocky_planet",
            "state": "formed",
            "orbit": 1
        })

        self.planets.append({
            "name": "venus",
            "type": "rocky_planet",
            "state": "formed",
            "orbit": 2
        })

        earth = {
            "name": "earth",
            "type": "rocky_planet",
            "state": "formed",
            "orbit": 3,
            "has_iron_core": "iron" in available_elements,
            "has_rocky_crust": "silicon" in available_elements and "iron" in available_elements,
            "water_possible": "hydrogen" in available_elements and "oxygen" in available_elements,
            "organic_molecules_possible": (
                "carbon" in available_elements
                and "hydrogen" in available_elements
                and "oxygen" in available_elements
                and "nitrogen" in available_elements
            )
        }

        self.planets.append(earth)

        self.planets.append({
            "name": "mars",
            "type": "rocky_planet",
            "state": "formed",
            "orbit": 4
        })

        self.planets.append({
            "name": "jupiter",
            "type": "gas_giant",
            "state": "formed",
            "orbit": 5
        })

        self.planets.append({
            "name": "saturn",
            "type": "gas_giant",
            "state": "formed",
            "orbit": 6
        })

        self.planets.append({
            "name": "uranus",
            "type": "ice_giant",
            "state": "formed",
            "orbit": 7
        })

        self.planets.append({
            "name": "neptune",
            "type": "ice_giant",
            "state": "formed",
            "orbit": 8
        })

        self.planetary_state["planets_formed"] = True
        self.planetary_state["earth_formed"] = True
        self.planetary_state["water_possible"] = earth["water_possible"]
        self.planetary_state["ice_possible"] = earth["water_possible"]
        self.planetary_state["minerals_possible"] = earth["has_rocky_crust"]
        self.planetary_state["organic_molecules_possible"] = earth["organic_molecules_possible"]

        self.record_history()
        self.write_to_world()

        print("PLANETS FORMED")
        print("EARTH FORMED")
        print("WATER, ICE, MINERALS AND ORGANIC MOLECULES BECOME POSSIBLE")

        return self.public_state

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "planets_formed",
            "description": "Planets form from the solar protoplanetary disk. Earth appears as a rocky world with the potential for water and organic molecules."
        })

    def write_to_world(self):
        self.universe.world["planets"] = self.public_state
        self.universe.world["solar_planets"] = self.planets
        self.universe.world["earth"] = self.find_planet("earth")
        self.universe.world["planetary_materials"] = self.planetary_materials
        self.universe.world["planetary_state"] = self.planetary_state

    def find_planet(self, name):
        for planet in self.planets:
            if planet["name"] == name:
                return planet

        return None
