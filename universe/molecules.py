from universe.chemical_objects import ChemicalMolecule
from universe.molecule_state import MoleculeFormationState
from universe.periodic_table import PeriodicTable


class Molecules:

    def __init__(self, universe):
        self.universe = universe
        self.name = "molecules"
        self.type = "molecular_layer"
        self.state = "ready"

        self.periodic_table = PeriodicTable(universe)

        self.molecules = {}

        self.molecule_state = MoleculeFormationState()

        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "molecules": {
                name: molecule.to_dict()
                for name, molecule in self.molecules.items()
            },
            "molecule_state": self.molecule_state.to_dict(),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def form_reference_molecules(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=(
                    self._form_reference_molecules_unprotected
                ),
                source_component="molecules",
                source_operation="form_reference_molecules",
            )
        )

    def _form_reference_molecules_unprotected(self):
        self.ensure_periodic_table()

        self.create_molecule(
            name="water",
            formula="H2O",
            components={"hydrogen": 2, "oxygen": 1},
            category="simple_molecule",
            meaning="water molecule",
            future_use=["oceans", "ice", "life", "bar_drinks"]
        )

        self.create_molecule(
            name="carbon_dioxide",
            formula="CO2",
            components={"carbon": 1, "oxygen": 2},
            category="simple_molecule",
            meaning="carbon dioxide molecule",
            future_use=["atmosphere", "carbon_cycle", "bar_bubbles"]
        )

        self.create_molecule(
            name="methane",
            formula="CH4",
            components={"carbon": 1, "hydrogen": 4},
            category="organic_molecule",
            meaning="simple hydrocarbon",
            future_use=["organic_chemistry", "planetary_atmospheres"]
        )

        self.create_molecule(
            name="ammonia",
            formula="NH3",
            components={"nitrogen": 1, "hydrogen": 3},
            category="simple_molecule",
            meaning="nitrogen hydride molecule",
            future_use=["prebiotic_chemistry", "planetary_chemistry"]
        )

        self.create_alcohol(
            name="methanol",
            formula="CH3OH",
            components={"carbon": 1, "hydrogen": 4, "oxygen": 1},
            meaning="simple alcohol molecule"
        )

        self.create_alcohol(
            name="ethanol",
            formula="C2H5OH",
            components={"carbon": 2, "hydrogen": 6, "oxygen": 1},
            meaning="ethyl alcohol molecule"
        )

        self.state = "formed"

        self.molecule_state.simple_molecules_available = True
        self.molecule_state.organic_molecules_available = True
        self.molecule_state.alcohols_available = True
        self.molecule_state.molecule_count = len(
            self.molecules
        )

        self.record_history()
        self.write_to_world()

        print("REFERENCE MOLECULES FORMED")
        print("WATER FORMED")
        print("CARBON DIOXIDE FORMED")
        print("METHANE FORMED")
        print("AMMONIA FORMED")
        print("SIMPLE ALCOHOLS FORMED")

        return self.public_state

    def ensure_periodic_table(self):
        if not self.universe.world.get("elements_by_atomic_number"):
            self.periodic_table.build_known_table()

        self.molecule_state.periodic_table_available = True

    def create_molecule(
        self,
        name,
        formula,
        components,
        category,
        meaning,
        future_use,
    ):
        molecule = ChemicalMolecule(
            name=name,
            formula=formula,
            components=self.resolve_elements(components),
            category=category,
            meaning=meaning,
            future_use=tuple(future_use),
        )

        self.molecules[name] = molecule

        return molecule

    def create_alcohol(self, name, formula, components, meaning):
        molecule = ChemicalMolecule(
            name=name,
            formula=formula,
            components=self.resolve_elements(components),
            category="alcohol",
            functional_group="hydroxyl",
            functional_group_symbol="-OH",
            meaning=meaning,
            future_use=(
                "organic_chemistry",
                "solvents",
                "bar_drinks",
            ),
        )

        self.molecules[name] = molecule

        return molecule

    def resolve_elements(self, components):
        if not isinstance(components, dict):
            raise TypeError(
                "components must be an element-name-to-count map"
            )

        chemical_elements = self.universe.world.get(
            "chemical_elements",
            {},
        )
        resolved_components = {}

        for element_name, count in components.items():
            try:
                element = chemical_elements[element_name]
            except KeyError as error:
                raise ValueError(
                    f"Missing element for molecule: {element_name}"
                ) from error

            resolved_components[element] = count

        return resolved_components

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "reference_molecules_formed",
            "description": "Simple molecules and simple alcohols form from available elements."
        })

    def write_to_world(self):
        self._refresh_public_state()
        self.universe.world["molecules"] = self.public_state
        self.universe.world["known_molecules"] = self.molecules
        self.universe.world["molecule_state"] = self.molecule_state
