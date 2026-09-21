from copy import deepcopy

from universe.stellar_objects import PrimordialStar
from universe.primordial_objects import PrimordialCosmicComponent
from universe.stellar_nucleosynthesis_state import (
    StellarNucleosynthesisState,
)


class StellarNucleosynthesis:

    def __init__(self, universe):
        self.universe = universe
        self.name = "stellar_nucleosynthesis"
        self.type = "stellar_element_process"
        self.state = "ready"

        self.elements_up_to_iron = {}

        self.stellar_nucleosynthesis_state = StellarNucleosynthesisState()

        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "elements_up_to_iron": deepcopy(
                self.elements_up_to_iron
            ),
            "stellar_nucleosynthesis_state": (
                self.stellar_nucleosynthesis_state.to_dict()
            ),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def forge_elements_up_to_iron(self):
        stellar_state = self.universe.world.get("stellar_state", {})
        first_stars = self.universe.world.get("first_stars", [])

        if not first_stars:
            self.state = "failed"
            self.stellar_nucleosynthesis_state.failed = True

            print("STELLAR NUCLEOSYNTHESIS FAILED: no stars available")
            self.write_to_world()
            return self.public_state

        for star in first_stars:
            if not isinstance(star, PrimordialStar):
                raise TypeError(
                    "first_stars must contain PrimordialStar objects"
                )

        if not stellar_state.stellar_fusion_possible:
            self.state = "failed"
            self.stellar_nucleosynthesis_state.failed = True

            print(
                "STELLAR NUCLEOSYNTHESIS FAILED: "
                "stellar fusion is not possible yet"
            )
            self.write_to_world()
            return self.public_state

        self.state = "forged"
        self.stellar_nucleosynthesis_state.stellar_fusion_active = True

        primordial_elements = self.universe.world.get(
            "primordial_elements",
            {},
        )

        for element_name, element in primordial_elements.items():
            if not isinstance(
                element,
                PrimordialCosmicComponent,
            ):
                raise TypeError(
                    "primordial_elements must contain "
                    "PrimordialCosmicComponent objects"
                )

            if element.type == "element":
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

        self.stellar_nucleosynthesis_state.elements_up_to_iron_forged = True
        self.stellar_nucleosynthesis_state.iron_limit_reached = True
        self.stellar_nucleosynthesis_state.element_count = len(
            self.elements_up_to_iron
        )

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
            "description": (
                "The first stars forge elements through stellar "
                "nucleosynthesis, reaching the iron limit."
            )
        })

    def write_to_world(self):
        self._refresh_public_state()

        self.universe.world["stellar_nucleosynthesis"] = (
            self.public_state
        )
        self.universe.world["elements_up_to_iron"] = (
            self.elements_up_to_iron
        )
        self.universe.world["elements"] = self.elements_up_to_iron
        self.universe.world["stellar_nucleosynthesis_state"] = (
            self.stellar_nucleosynthesis_state
        )
