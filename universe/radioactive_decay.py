from universe.isotopes import Isotopes


class RadioactiveDecay:

    def __init__(self, universe):
        self.universe = universe
        self.name = "radioactive_decay"
        self.type = "decay_time_layer"
        self.state = "ready"

        self.isotopes_layer = Isotopes(universe)
        self.decay_patterns = {}

        self.decay_state = {
            "isotopes_available": False,
            "radioactive_decay_available": False,
            "radiocarbon_time_available": False,
            "geological_time_available": False,
            "decay_pattern_count": 0
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "decay_patterns": self.decay_patterns,
            "decay_state": self.decay_state
        }

    def define_reference_decay(self):
        self.ensure_isotopes()

        self.create_decay_pattern(
            isotope_name="carbon_14",
            daughter_product="nitrogen_14",
            half_life_years=5730,
            time_scale="archaeological_and_biological_time",
            use="radiocarbon_dating"
        )

        self.create_decay_pattern(
            isotope_name="potassium_40",
            daughter_product="argon_40",
            half_life_years=1_250_000_000,
            time_scale="geological_time",
            use="potassium_argon_dating"
        )

        self.create_decay_pattern(
            isotope_name="thorium_232",
            daughter_product="lead_208",
            half_life_years=14_000_000_000,
            time_scale="geological_time",
            use="thorium_lead_dating"
        )

        self.create_decay_pattern(
            isotope_name="uranium_238",
            daughter_product="lead_206",
            half_life_years=4_500_000_000,
            time_scale="geological_time",
            use="uranium_lead_dating"
        )

        self.state = "defined"
        self.public_state["state"] = self.state

        self.decay_state["radioactive_decay_available"] = True
        self.decay_state["radiocarbon_time_available"] = True
        self.decay_state["geological_time_available"] = True
        self.decay_state["decay_pattern_count"] = len(self.decay_patterns)

        self.record_history()
        self.write_to_world()

        print("RADIOACTIVE DECAY PATTERNS RECORDED")
        print("CARBON-14 DECAY AVAILABLE")
        print("POTASSIUM-40 DECAY AVAILABLE")
        print("THORIUM-232 DECAY AVAILABLE")
        print("URANIUM-238 DECAY AVAILABLE")
        print("GEOLOGICAL TIMEKEEPERS AVAILABLE")

        return self.public_state

    def ensure_isotopes(self):
        if not self.universe.world.get("known_isotopes"):
            self.isotopes_layer.form_reference_isotopes()

        self.decay_state["isotopes_available"] = True

    def create_decay_pattern(
        self,
        isotope_name,
        daughter_product,
        half_life_years,
        time_scale,
        use
    ):
        known_isotopes = self.universe.world.get("known_isotopes", {})

        if isotope_name not in known_isotopes:
            raise ValueError(f"Missing isotope: {isotope_name}")

        isotope = known_isotopes[isotope_name]
        decay_name = f"{isotope_name}_decay"

        decay_pattern = {
            "name": decay_name,
            "type": "radioactive_decay_pattern",
            "state": "available",
            "parent_isotope": isotope_name,
            "parent_element": isotope["element_name"],
            "parent_symbol": isotope["symbol"],
            "daughter_product": daughter_product,
            "half_life_years": half_life_years,
            "half_life_precision": "reference_approximation",
            "time_scale": time_scale,
            "use": use,
            "future_use": ["age_estimation", "cosmic_history", "geological_history"]
        }

        self.decay_patterns[decay_name] = decay_pattern

        return decay_pattern

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "radioactive_decay_patterns_recorded",
            "description": "Radioactive isotopes provide decay patterns that can be used as long-scale timekeepers."
        })

    def write_to_world(self):
        self.universe.world["radioactive_decay"] = self.public_state
        self.universe.world["decay_patterns"] = self.decay_patterns
        self.universe.world["decay_state"] = self.decay_state
