from universe.physical_record_state import CosmicHistoryEvent
from universe.chemical_objects import ChemicalElement
from universe.stellar_objects import PrimordialStar
from universe.primordial_objects import PrimordialCosmicComponent
from universe.stellar_nucleosynthesis_state import (
    StellarNucleosynthesisState,
)
from universe.stellar_nucleosynthesis_process_state import (
    StellarNucleosynthesisProcessState,
)
from universe.stellar_nucleosynthesis_result_state import (
    StellarNucleosynthesisResult,
    public_element_snapshot,
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


class StellarNucleosynthesis:

    def __init__(self, universe):
        self.universe = universe
        self.name = "stellar_nucleosynthesis"
        self.type = "stellar_element_process"
        self.state = (
            StellarNucleosynthesisProcessState.READY
        )

        self.elements_up_to_iron = {}

        self.stellar_nucleosynthesis_state = StellarNucleosynthesisState()
        self.result = None

        self.public_state = self._build_public_state()

        self.universe.stellar_nucleosynthesis_layer = self

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if not isinstance(
            state,
            StellarNucleosynthesisProcessState,
        ):
            raise TypeError(
                "Stellar nucleosynthesis process state "
                "must use "
                "StellarNucleosynthesisProcessState."
            )

        self._state = state

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "elements_up_to_iron": {
                name: public_element_snapshot(element)
                for name, element in self.elements_up_to_iron.items()
            },
            "stellar_nucleosynthesis_state": (
                self.stellar_nucleosynthesis_state.to_dict()
            ),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def forge_elements_up_to_iron(self):
        stars_layer = getattr(
            self.universe,
            "stars_layer",
            None,
        )

        first_stars = (
            stars_layer.stars
            if stars_layer is not None
            else ()
        )

        stellar_state = (
            stars_layer.stellar_state
            if stars_layer is not None
            else None
        )

        if not first_stars:
            self.state = (
                StellarNucleosynthesisProcessState.FAILED
            )
            self.stellar_nucleosynthesis_state.failed = True

            print("STELLAR NUCLEOSYNTHESIS FAILED: no stars available")
            self.write_to_world()

            self.result = StellarNucleosynthesisResult(
                state=self.state,
                elements_up_to_iron=(
                    self.elements_up_to_iron
                ),
                stellar_nucleosynthesis_state=(
                    self.stellar_nucleosynthesis_state
                ),
            )

            return self.result

        for star in first_stars:
            if not isinstance(star, PrimordialStar):
                raise TypeError(
                    "first_stars must contain PrimordialStar objects"
                )

        if not stellar_state.stellar_fusion_possible:
            self.state = (
                StellarNucleosynthesisProcessState.FAILED
            )
            self.stellar_nucleosynthesis_state.failed = True

            print(
                "STELLAR NUCLEOSYNTHESIS FAILED: "
                "stellar fusion is not possible yet"
            )
            self.write_to_world()

            self.result = StellarNucleosynthesisResult(
                state=self.state,
                elements_up_to_iron=(
                    self.elements_up_to_iron
                ),
                stellar_nucleosynthesis_state=(
                    self.stellar_nucleosynthesis_state
                ),
            )

            return self.result

        self.state = (
            StellarNucleosynthesisProcessState.FORGED
        )
        self.stellar_nucleosynthesis_state.stellar_fusion_active = True

        big_bang = getattr(
            self.universe,
            "big_bang",
            None,
        )

        primordial_elements = (
            big_bang.primordial_elements
            if big_bang is not None
            else {}
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

        self.result = StellarNucleosynthesisResult(
            state=self.state,
            elements_up_to_iron=(
                self.elements_up_to_iron
            ),
            stellar_nucleosynthesis_state=(
                self.stellar_nucleosynthesis_state
            ),
        )

        return self.result

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

        history.append(
            CosmicHistoryEvent(
                name="elements_up_to_iron_forged",
                description=(
                    "The first stars forge elements through stellar "
                    "nucleosynthesis, reaching the iron limit."
                ),
            )
        )

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
