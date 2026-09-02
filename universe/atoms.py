from copy import deepcopy

from universe.atom_state import AtomFormationState
from universe.periodic_table import PeriodicTable


class Atoms:

    def __init__(self, universe):
        self.universe = universe
        self.name = "atoms"
        self.type = "atomic_layer"
        self.state = "ready"

        self.periodic_table = PeriodicTable(universe)
        self.atoms = {}

        self.atom_state = AtomFormationState()

        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "atoms": deepcopy(self.atoms),
            "atom_state": self.atom_state.to_dict(),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def form_reference_atoms(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=(
                    self._form_reference_atoms_unprotected
                ),
                source_component="atoms",
                source_operation="form_reference_atoms",
            )
        )

    def _form_reference_atoms_unprotected(self):
        self.ensure_periodic_table()

        self.create_neutral_atom(1)
        self.create_neutral_atom(2)
        self.create_neutral_atom(55)
        self.create_neutral_atom(119)

        self.state = "formed"

        self.atom_state.neutral_atoms_available = True
        self.atom_state.atom_count = len(self.atoms)

        self.record_history()
        self.write_to_world()

        print("REFERENCE ATOMS FORMED")
        print("HYDROGEN ATOM FORMED")
        print("HELIUM ATOM FORMED")
        print("CAESIUM ATOM FORMED")
        print("FUTURE ELEMENT 119 ATOM FORMED")

        return self.public_state

    def ensure_periodic_table(self):
        if not self.universe.world.get("elements_by_atomic_number"):
            self.periodic_table.build_known_table()

        self.atom_state.periodic_table_available = True

    def create_neutral_atom(self, atomic_number):
        element = self.periodic_table.get_element(atomic_number)

        atom_name = f"{element['name']}_atom"

        atom = {
            "name": atom_name,
            "type": "neutral_atom",
            "state": "formed",
            "element_name": element["name"],
            "symbol": element["symbol"],
            "atomic_number": atomic_number,
            "protons": atomic_number,
            "electrons": atomic_number,
            "net_charge": 0,
            "official_element": element["official"],
            "discovered_element": element["discovered"],
            "future_use": ["isotopes", "molecules", "materials"]
        }

        self.atoms[atom_name] = atom

        return atom

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "reference_atoms_formed",
            "description": "Neutral reference atoms form when electrons bind to element nuclei according to atomic number."
        })

    def write_to_world(self):
        self._refresh_public_state()
        self.universe.world["atoms"] = self.public_state
        self.universe.world["neutral_atoms"] = self.atoms
        self.universe.world["atom_state"] = self.atom_state
