from universe.nuclear_objects import AtomicNucleus
from universe.nuclear_state import (
    NuclearFormationState,
)


class AtomicNuclei:

    def __init__(self, universe):
        self.universe = universe
        self.name = "atomic_nuclei"
        self.type = "nuclear_layer"
        self.state = "ready"

        self.nuclei = {}

        self.nuclear_state = NuclearFormationState()

        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "nuclei": {
                name: nucleus.to_dict()
                for name, nucleus in self.nuclei.items()
            },
            "nuclear_state": (
                self.nuclear_state.to_dict()
            ),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def form_light_nuclei(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=(
                    self._form_light_nuclei_unprotected
                ),
                source_component="atomic_nuclei",
                source_operation="form_light_nuclei",
            )
        )

    def _form_light_nuclei_unprotected(self):
        self.state = "formed"

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

        self.nuclear_state.nucleons_available = True
        self.nuclear_state.hydrogen_nucleus_formed = True
        self.nuclear_state.helium_nucleus_formed = True
        self.nuclear_state.light_nuclei_formed = True
        (
            self.nuclear_state
            .nuclear_composition_recorded
        ) = True

        self.record_history()
        self.write_to_world()

        print("ATOMIC NUCLEI FORMED")
        print("HYDROGEN NUCLEUS FORMED")
        print("HELIUM NUCLEUS FORMED")
        print("LIGHT NUCLEI COMPOSITION RECORDED")

        return self.public_state

    def add_nucleus(self, name, protons, neutrons, element_name):
        self.nuclei[name] = AtomicNucleus(
            name=name,
            element_name=element_name,
            protons=protons,
            neutrons=neutrons,
        )

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "light_atomic_nuclei_formed",
            "description": "Protons and neutrons combine into the first light atomic nuclei: hydrogen, deuterium, helium, and trace lithium."
        })

    def write_to_world(self):
        self._refresh_public_state()
        self.universe.world["atomic_nuclei"] = self.public_state
        self.universe.world["light_nuclei"] = self.nuclei
        self.universe.world["nuclear_state"] = self.nuclear_state
