from universe.periodic_table import PeriodicTable


class Isotopes:

    def __init__(self, universe):
        self.universe = universe
        self.name = "isotopes"
        self.type = "isotope_layer"
        self.state = "ready"

        self.periodic_table = PeriodicTable(universe)
        self.isotopes = {}

        self.isotope_state = {
            "periodic_table_available": False,
            "reference_isotopes_available": False,
            "radioactive_isotopes_available": False,
            "atomic_time_isotope_available": False,
            "isotope_count": 0
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "isotopes": self.isotopes,
            "isotope_state": self.isotope_state
        }

    def form_reference_isotopes(self):
        self.ensure_periodic_table()

        self.create_isotope(1, 1, "stable", ["atoms", "water"])
        self.create_isotope(1, 2, "stable", ["atoms", "heavy_water"])
        self.create_isotope(2, 4, "stable", ["atoms", "helium_gas"])

        self.create_isotope(6, 14, "radioactive", ["radiocarbon_dating"])
        self.create_isotope(19, 40, "radioactive", ["geological_time"])
        self.create_isotope(55, 133, "stable", ["atomic_time"])
        self.create_isotope(90, 232, "radioactive", ["geological_time"])
        self.create_isotope(92, 238, "radioactive", ["geological_time"])

        self.state = "formed"
        self.public_state["state"] = self.state

        self.isotope_state["reference_isotopes_available"] = True
        self.isotope_state["radioactive_isotopes_available"] = True
        self.isotope_state["atomic_time_isotope_available"] = True
        self.isotope_state["isotope_count"] = len(self.isotopes)

        self.record_history()
        self.write_to_world()

        print("REFERENCE ISOTOPES FORMED")
        print("HYDROGEN-1 FORMED")
        print("DEUTERIUM FORMED")
        print("HELIUM-4 FORMED")
        print("CARBON-14 FORMED")
        print("CAESIUM-133 FORMED")
        print("RADIOACTIVE TIMEKEEPERS FORMED")

        return self.public_state

    def ensure_periodic_table(self):
        if not self.universe.world.get("elements_by_atomic_number"):
            self.periodic_table.build_known_table()

        self.isotope_state["periodic_table_available"] = True

    def create_isotope(self, atomic_number, mass_number, stability, future_use):
        if mass_number < atomic_number:
            raise ValueError("Mass number cannot be smaller than atomic number")

        element = self.periodic_table.get_element(atomic_number)
        neutrons = mass_number - atomic_number

        isotope_name = f"{element['name']}_{mass_number}"

        isotope = {
            "name": isotope_name,
            "type": "isotope",
            "state": "formed",
            "element_name": element["name"],
            "symbol": element["symbol"],
            "atomic_number": atomic_number,
            "mass_number": mass_number,
            "protons": atomic_number,
            "neutrons": neutrons,
            "electrons_if_neutral_atom": atomic_number,
            "stability": stability,
            "official_element": element["official"],
            "discovered_element": element["discovered"],
            "future_use": future_use
        }

        self.isotopes[isotope_name] = isotope

        return isotope

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "reference_isotopes_formed",
            "description": "Reference isotopes form when element nuclei contain specific numbers of neutrons."
        })

    def write_to_world(self):
        self.universe.world["isotopes"] = self.public_state
        self.universe.world["known_isotopes"] = self.isotopes
        self.universe.world["isotope_state"] = self.isotope_state
