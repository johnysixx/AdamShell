from universe.isotopes import Isotopes


class AtomicTime:

    def __init__(self, universe):
        self.universe = universe
        self.name = "atomic_time"
        self.type = "precision_time_layer"
        self.state = "ready"

        self.isotopes_layer = Isotopes(universe)

        self.time_standards = {}

        self.atomic_time_state = {
            "isotopes_available": False,
            "caesium_133_available": False,
            "si_second_defined": False,
            "precision_time_available": False
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "time_standards": self.time_standards,
            "atomic_time_state": self.atomic_time_state
        }

    def define_si_second(self):
        self.ensure_isotopes()

        isotopes = self.universe.world.get("known_isotopes", {})

        if "caesium_133" not in isotopes:
            self.state = "failed"
            self.public_state["state"] = self.state
            print("ATOMIC TIME FAILED: caesium-133 is missing")
            self.write_to_world()
            return self.public_state

        caesium_133 = isotopes["caesium_133"]

        self.time_standards["si_second"] = {
            "name": "si_second",
            "type": "atomic_time_standard",
            "state": "defined",
            "based_on": "caesium_133",
            "isotope": caesium_133,
            "transition": "unperturbed_ground_state_hyperfine_transition",
            "frequency_hz": 9_192_631_770,
            "frequency_unit": "Hz",
            "meaning": "one second is defined through the caesium-133 transition frequency",
            "future_use": ["clocks", "calendars", "simulation_time", "cosmic_history"]
        }

        self.state = "defined"
        self.public_state["state"] = self.state

        self.atomic_time_state["caesium_133_available"] = True
        self.atomic_time_state["si_second_defined"] = True
        self.atomic_time_state["precision_time_available"] = True

        self.record_history()
        self.write_to_world()

        print("ATOMIC TIME DEFINED")
        print("CAESIUM-133 TIME STANDARD AVAILABLE")
        print("SI SECOND DEFINED")
        print("PRECISION TIME AVAILABLE")

        return self.public_state

    def ensure_isotopes(self):
        if not self.universe.world.get("known_isotopes"):
            self.isotopes_layer.form_reference_isotopes()

        self.atomic_time_state["isotopes_available"] = True

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "atomic_time_defined",
            "description": "The SI second is defined using the caesium-133 atomic transition frequency."
        })

    def write_to_world(self):
        self.universe.world["atomic_time"] = self.public_state
        self.universe.world["time_standards"] = self.time_standards
        self.universe.world["atomic_time_state"] = self.atomic_time_state
