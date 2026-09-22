from universe.chemical_objects import ChemicalElement
from universe.stellar_objects import PrimordialStar
from universe.primordial_objects import PrimordialCosmicComponent
from universe.stellar_nucleosynthesis_state import (
    StellarNucleosynthesisState,
)


STELLAR_ELEMENT_SPECS = (
    ("beryllium", "Be", 4), ("boron", "B", 5),
    ("carbon", "C", 6), ("nitrogen", "N", 7),
    ("oxygen", "O", 8), ("fluorine", "F", 9),
    ("neon", "Ne", 10), ("sodium", "Na", 11),
    ("magnesium", "Mg", 12), ("aluminium", "Al", 13),
    ("silicon", "Si", 14), ("phosphorus", "P", 15),
    ("sulfur", "S", 16), ("chlorine", "Cl", 17),
    ("argon", "Ar", 18), ("potassium", "K", 19),
    ("calcium", "Ca", 20), ("scandium", "Sc", 21),
    ("titanium", "Ti", 22), ("vanadium", "V", 23),
    ("chromium", "Cr", 24), ("manganese", "Mn", 25),
    ("iron", "Fe", 26),
)


def _public_element_snapshot(element):
    if isinstance(element, PrimordialCosmicComponent):
        return element.to_dict()

    if not isinstance(element, ChemicalElement):
        raise TypeError(
            "elements_up_to_iron must contain primordial "
            "or ChemicalElement objects"
        )

    snapshot = {
        "name": element.name,
        "type": "element",
        "atomic_number": element.atomic_number,
        "state": element.state,
    }

    if element.origin is not None:
        snapshot["origin"] = element.origin

    return snapshot


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
            "elements_up_to_iron": {
                name: _public_element_snapshot(element)
                for name, element in self.elements_up_to_iron.items()
            },
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

        for name, symbol, atomic_number in STELLAR_ELEMENT_SPECS:
            self.add_stellar_element(
                name,
                symbol,
                atomic_number,
            )

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

    def add_stellar_element(
        self,
        name,
        symbol,
        atomic_number,
    ):
        self.elements_up_to_iron[name] = ChemicalElement(
            name=name,
            symbol=symbol,
            atomic_number=atomic_number,
            official=True,
            discovered=True,
            state="forged",
            origin="stellar_nucleosynthesis",
        )

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
