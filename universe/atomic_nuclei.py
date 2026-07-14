class AtomicNuclei:

    def __init__(self, universe):
        self.universe = universe
        self.name = "atomic_nuclei"
        self.type = "nuclear_layer"
        self.state = "ready"

        self.nuclei = {}

        self.nuclear_state = {
            "nucleons_available": False,
            "hydrogen_nucleus_formed": False,
            "helium_nucleus_formed": False,
            "light_nuclei_formed": False,
            "nuclear_composition_recorded": False
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "nuclei": self.nuclei,
            "nuclear_state": self.nuclear_state
        }

    def form_light_nuclei(self):
        particle_state = self.universe.world.get("particle_state", {})
        nucleons = self.universe.world.get("nucleons", {})

        if not particle_state.get("nucleons_formed"):
            self.state = "failed"
            self.public_state["state"] = self.state

            print("ATOMIC NUCLEI FORMATION FAILED: nucleons are missing")
            self.write_to_world()
            return self.public_state

        if "proton" not in nucleons or "neutron" not in nucleons:
            self.state = "failed"
            self.public_state["state"] = self.state

            print("ATOMIC NUCLEI FORMATION FAILED: proton or neutron is missing")
            self.write_to_world()
            return self.public_state

        self.state = "formed"
        self.public_state["state"] = self.state

        self.add_nucleus(
            name="hydrogen_nucleus",
            protons=1,
            neutrons=0,
            element_name="hydrogen"
        )

        self.add_nucleus(
            name="deuterium_nucleus",
            protons=1,
            neutrons=1,
            element_name="hydrogen"
        )

        self.add_nucleus(
            name="helium_nucleus",
            protons=2,
            neutrons=2,
            element_name="helium"
        )

        self.add_nucleus(
            name="trace_lithium_nucleus",
            protons=3,
            neutrons=4,
            element_name="lithium"
        )

        self.nuclear_state["nucleons_available"] = True
        self.nuclear_state["hydrogen_nucleus_formed"] = True
        self.nuclear_state["helium_nucleus_formed"] = True
        self.nuclear_state["light_nuclei_formed"] = True
        self.nuclear_state["nuclear_composition_recorded"] = True

        self.record_history()
        self.write_to_world()

        print("ATOMIC NUCLEI FORMED")
        print("HYDROGEN NUCLEUS FORMED")
        print("HELIUM NUCLEUS FORMED")
        print("LIGHT NUCLEI COMPOSITION RECORDED")

        return self.public_state

    def add_nucleus(self, name, protons, neutrons, element_name):
        self.nuclei[name] = {
            "name": name,
            "type": "atomic_nucleus",
            "state": "formed",
            "element_name": element_name,
            "protons": protons,
            "neutrons": neutrons,
            "atomic_number": protons,
            "mass_number": protons + neutrons,
            "future_use": ["elements", "atoms", "isotopes"]
        }

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "light_atomic_nuclei_formed",
            "description": "Protons and neutrons combine into the first light atomic nuclei: hydrogen, deuterium, helium, and trace lithium."
        })

    def write_to_world(self):
        self.universe.world["atomic_nuclei"] = self.public_state
        self.universe.world["light_nuclei"] = self.nuclei
        self.universe.world["nuclear_state"] = self.nuclear_state
