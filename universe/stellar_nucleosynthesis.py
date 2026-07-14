class StellarNucleosynthesis:

    def __init__(self, universe):
        self.universe = universe
        self.name = "stellar_nucleosynthesis"
        self.type = "stellar_element_process"
        self.state = "ready"

        self.elements_up_to_iron = {}

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "elements_up_to_iron": self.elements_up_to_iron
        }

    def forge_elements_up_to_iron(self):
        stellar_state = self.universe.world.get("stellar_state", {})
        first_stars = self.universe.world.get("first_stars", [])

        if not first_stars:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("STELLAR NUCLEOSYNTHESIS FAILED: no stars available")
            self.write_to_world()
            return self.public_state

        if not stellar_state.get("stellar_fusion_possible"):
            self.state = "failed"
            self.public_state["state"] = self.state

            print("STELLAR NUCLEOSYNTHESIS FAILED: stellar fusion is not possible yet")
            self.write_to_world()
            return self.public_state

        self.state = "forged"
        self.public_state["state"] = self.state

        primordial_elements = self.universe.world.get("primordial_elements", {})

        for element_name, element in primordial_elements.items():
            if element.get("type") == "element":
                self.elements_up_to_iron[element_name] = element


        self.add_stellar_element("beryllium", 4)
        self.add_stellar_element("boron", 5)
        self.add_stellar_element("carbon", 6)
        self.add_stellar_element("nitrogen", 7)
        self.add_stellar_element("oxygen", 8)
        self.add_stellar_element("fluorine", 9)
        self.add_stellar_element("neon", 10)
        self.add_stellar_element("sodium", 11)
        self.add_stellar_element("magnesium", 12)
        self.add_stellar_element("aluminium", 13)
        self.add_stellar_element("silicon", 14)
        self.add_stellar_element("phosphorus", 15)
        self.add_stellar_element("sulfur", 16)
        self.add_stellar_element("chlorine", 17)
        self.add_stellar_element("argon", 18)
        self.add_stellar_element("potassium", 19)
        self.add_stellar_element("calcium", 20)
        self.add_stellar_element("scandium", 21)
        self.add_stellar_element("titanium", 22)
        self.add_stellar_element("vanadium", 23)
        self.add_stellar_element("chromium", 24)
        self.add_stellar_element("manganese", 25)
        self.add_stellar_element("iron", 26)

        self.record_history()
        self.write_to_world()

        print("STELLAR NUCLEOSYNTHESIS STARTED")
        print("STARS FORGE ELEMENTS UP TO IRON")
        print("IRON LIMIT REACHED")

        return self.public_state

    def add_stellar_element(self, name, atomic_number):
        self.elements_up_to_iron[name] = {
            "name": name,
            "type": "element",
            "atomic_number": atomic_number,
            "state": "forged",
            "origin": "stellar_nucleosynthesis"
        }

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "elements_up_to_iron_forged",
            "description": "The first stars forge elements through stellar nucleosynthesis, reaching the iron limit."
        })

    def write_to_world(self):
        self.universe.world["stellar_nucleosynthesis"] = self.public_state
        self.universe.world["elements_up_to_iron"] = self.elements_up_to_iron
        self.universe.world["elements"] = self.elements_up_to_iron
