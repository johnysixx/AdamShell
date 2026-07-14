DIGIT_ROOTS = {
    "0": ("nil", "n"),
    "1": ("un", "u"),
    "2": ("bi", "b"),
    "3": ("tri", "t"),
    "4": ("quad", "q"),
    "5": ("pent", "p"),
    "6": ("hex", "h"),
    "7": ("sept", "s"),
    "8": ("oct", "o"),
    "9": ("enn", "e"),
}


KNOWN_ELEMENTS = [
    (1, "H", "hydrogen"),
    (2, "He", "helium"),
    (3, "Li", "lithium"),
    (4, "Be", "beryllium"),
    (5, "B", "boron"),
    (6, "C", "carbon"),
    (7, "N", "nitrogen"),
    (8, "O", "oxygen"),
    (9, "F", "fluorine"),
    (10, "Ne", "neon"),
    (11, "Na", "sodium"),
    (12, "Mg", "magnesium"),
    (13, "Al", "aluminium"),
    (14, "Si", "silicon"),
    (15, "P", "phosphorus"),
    (16, "S", "sulfur"),
    (17, "Cl", "chlorine"),
    (18, "Ar", "argon"),
    (19, "K", "potassium"),
    (20, "Ca", "calcium"),
    (21, "Sc", "scandium"),
    (22, "Ti", "titanium"),
    (23, "V", "vanadium"),
    (24, "Cr", "chromium"),
    (25, "Mn", "manganese"),
    (26, "Fe", "iron"),
    (27, "Co", "cobalt"),
    (28, "Ni", "nickel"),
    (29, "Cu", "copper"),
    (30, "Zn", "zinc"),
    (31, "Ga", "gallium"),
    (32, "Ge", "germanium"),
    (33, "As", "arsenic"),
    (34, "Se", "selenium"),
    (35, "Br", "bromine"),
    (36, "Kr", "krypton"),
    (37, "Rb", "rubidium"),
    (38, "Sr", "strontium"),
    (39, "Y", "yttrium"),
    (40, "Zr", "zirconium"),
    (41, "Nb", "niobium"),
    (42, "Mo", "molybdenum"),
    (43, "Tc", "technetium"),
    (44, "Ru", "ruthenium"),
    (45, "Rh", "rhodium"),
    (46, "Pd", "palladium"),
    (47, "Ag", "silver"),
    (48, "Cd", "cadmium"),
    (49, "In", "indium"),
    (50, "Sn", "tin"),
    (51, "Sb", "antimony"),
    (52, "Te", "tellurium"),
    (53, "I", "iodine"),
    (54, "Xe", "xenon"),
    (55, "Cs", "caesium"),
    (56, "Ba", "barium"),
    (57, "La", "lanthanum"),
    (58, "Ce", "cerium"),
    (59, "Pr", "praseodymium"),
    (60, "Nd", "neodymium"),
    (61, "Pm", "promethium"),
    (62, "Sm", "samarium"),
    (63, "Eu", "europium"),
    (64, "Gd", "gadolinium"),
    (65, "Tb", "terbium"),
    (66, "Dy", "dysprosium"),
    (67, "Ho", "holmium"),
    (68, "Er", "erbium"),
    (69, "Tm", "thulium"),
    (70, "Yb", "ytterbium"),
    (71, "Lu", "lutetium"),
    (72, "Hf", "hafnium"),
    (73, "Ta", "tantalum"),
    (74, "W", "tungsten"),
    (75, "Re", "rhenium"),
    (76, "Os", "osmium"),
    (77, "Ir", "iridium"),
    (78, "Pt", "platinum"),
    (79, "Au", "gold"),
    (80, "Hg", "mercury"),
    (81, "Tl", "thallium"),
    (82, "Pb", "lead"),
    (83, "Bi", "bismuth"),
    (84, "Po", "polonium"),
    (85, "At", "astatine"),
    (86, "Rn", "radon"),
    (87, "Fr", "francium"),
    (88, "Ra", "radium"),
    (89, "Ac", "actinium"),
    (90, "Th", "thorium"),
    (91, "Pa", "protactinium"),
    (92, "U", "uranium"),
    (93, "Np", "neptunium"),
    (94, "Pu", "plutonium"),
    (95, "Am", "americium"),
    (96, "Cm", "curium"),
    (97, "Bk", "berkelium"),
    (98, "Cf", "californium"),
    (99, "Es", "einsteinium"),
    (100, "Fm", "fermium"),
    (101, "Md", "mendelevium"),
    (102, "No", "nobelium"),
    (103, "Lr", "lawrencium"),
    (104, "Rf", "rutherfordium"),
    (105, "Db", "dubnium"),
    (106, "Sg", "seaborgium"),
    (107, "Bh", "bohrium"),
    (108, "Hs", "hassium"),
    (109, "Mt", "meitnerium"),
    (110, "Ds", "darmstadtium"),
    (111, "Rg", "roentgenium"),
    (112, "Cn", "copernicium"),
    (113, "Nh", "nihonium"),
    (114, "Fl", "flerovium"),
    (115, "Mc", "moscovium"),
    (116, "Lv", "livermorium"),
    (117, "Ts", "tennessine"),
    (118, "Og", "oganesson"),
]


class PeriodicTable:

    def __init__(self, universe):
        self.universe = universe
        self.name = "periodic_table"
        self.type = "element_registry"
        self.state = "ready"

        self.elements = {}
        self.future_elements = {}

        self.registry_state = {
            "known_elements_registered": False,
            "known_element_count": 0,
            "future_element_generation_available": True,
            "future_element_count": 0
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "registry_state": self.registry_state
        }

    def build_known_table(self):
        for atomic_number, symbol, name in KNOWN_ELEMENTS:
            self.elements[atomic_number] = self.create_known_element(
                atomic_number=atomic_number,
                symbol=symbol,
                name=name
            )

        self.state = "registered"
        self.public_state["state"] = self.state

        self.registry_state["known_elements_registered"] = True
        self.registry_state["known_element_count"] = len(self.elements)

        self.write_to_world()

        print("PERIODIC TABLE REGISTERED")
        print(f"KNOWN ELEMENTS REGISTERED: {len(self.elements)}")
        print("FUTURE ELEMENT GENERATION AVAILABLE")

        return self.public_state

    def create_known_element(self, atomic_number, symbol, name):
        return {
            "name": name,
            "symbol": symbol,
            "type": "chemical_element",
            "state": "recognized",
            "atomic_number": atomic_number,
            "protons": atomic_number,
            "official": True,
            "discovered": True,
            "future_use": ["atoms", "isotopes", "molecules", "materials"]
        }

    def get_element(self, atomic_number):
        if not self.elements:
            self.build_known_table()

        if atomic_number in self.elements:
            return self.elements[atomic_number]

        return self.create_future_element(atomic_number)

    def create_future_element(self, atomic_number):
        if atomic_number <= 0:
            raise ValueError("Atomic number must be positive")

        if atomic_number in self.future_elements:
            return self.future_elements[atomic_number]

        name = self.create_temporary_systematic_name(atomic_number)
        symbol = self.create_temporary_systematic_symbol(atomic_number)

        element = {
            "name": name,
            "symbol": symbol,
            "type": "chemical_element",
            "state": "hypothetical",
            "atomic_number": atomic_number,
            "protons": atomic_number,
            "official": False,
            "discovered": False,
            "temporary_systematic_name": True,
            "future_use": ["atoms", "isotopes", "molecules", "materials"]
        }

        self.future_elements[atomic_number] = element
        self.registry_state["future_element_count"] = len(self.future_elements)

        self.write_to_world()

        print(f"FUTURE ELEMENT GENERATED: {name} ({symbol}), Z={atomic_number}")

        return element

    def create_temporary_systematic_name(self, atomic_number):
        digits = str(atomic_number)
        name_body = "".join(DIGIT_ROOTS[digit][0] for digit in digits)

        name_body = name_body.replace("ennnil", "ennil")

        if name_body.endswith("bi") or name_body.endswith("tri"):
            name_body = name_body[:-1]

        return f"{name_body}ium"

    def create_temporary_systematic_symbol(self, atomic_number):
        digits = str(atomic_number)
        letters = "".join(DIGIT_ROOTS[digit][1] for digit in digits)
        return letters.capitalize()

    def write_to_world(self):
        self.universe.world["periodic_table"] = self.public_state
        self.universe.world["elements_by_atomic_number"] = self.elements
        self.universe.world["chemical_elements"] = {
            element["name"]: element
            for element in self.elements.values()
        }
        self.universe.world["future_elements"] = self.future_elements
        self.universe.world["element_registry_state"] = self.registry_state
