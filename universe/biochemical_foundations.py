from copy import deepcopy

from universe.biochemical_state import (
    BiochemicalFoundationState,
)
from universe.planetary_material_objects import (
    AvailablePlanetaryMaterial,
)


class BiochemicalFoundations:

    def __init__(self, universe):
        self.universe = universe
        self.name = "biochemical_foundations"
        self.type = "biochemical_foundation_layer"
        self.state = "ready"

        self.compounds = {}

        self.biochemical_state = BiochemicalFoundationState()
        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "compounds": deepcopy(self.compounds),
            "biochemical_state": self.biochemical_state.to_dict(),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def form_biochemical_foundations(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=(
                    self._form_biochemical_foundations_unprotected
                ),
                source_component="biochemical_foundations",
                source_operation="form_biochemical_foundations",
            )
        )

    def _form_biochemical_foundations_unprotected(self):
        materials = self.universe.world.get("available_planetary_materials", {})

        if "water" not in materials or "organic_molecules" not in materials:
            self.state = "failed"

            print("BIOCHEMICAL FOUNDATION FAILED: missing water or organic molecules")
            self.write_to_world()
            return self.public_state

        for material_name in ("water", "organic_molecules"):
            material = materials[material_name]
            if not isinstance(material, AvailablePlanetaryMaterial):
                raise TypeError(
                    "available planetary material registry values must be "
                    "AvailablePlanetaryMaterial objects"
                )

        self.state = "formed"

        self.add_compound(
            name="sugars",
            compound_type="biochemical_compound",
            requires=["water", "organic_molecules", "carbon", "hydrogen", "oxygen"],
            future_use=["plant_energy", "fruit_sweetness", "fermentation"]
        )

        self.add_compound(
            name="amino_acids",
            compound_type="biochemical_compound",
            requires=["water", "organic_molecules", "carbon", "hydrogen", "oxygen", "nitrogen"],
            future_use=["proteins", "life", "milk_proteins"]
        )

        self.add_compound(
            name="lipids",
            compound_type="biochemical_compound",
            requires=["water", "organic_molecules", "carbon", "hydrogen", "oxygen"],
            future_use=["cell_membranes", "milk_fat"]
        )

        self.add_compound(
            name="fermentation_substrate",
            compound_type="biochemical_process_material",
            requires=["sugars", "water", "time"],
            future_use=["fermentation", "alcohol_base", "bar_drinks"]
        )

        self.biochemical_state.water_based_chemistry_possible = True
        self.biochemical_state.carbon_chemistry_possible = True
        self.biochemical_state.sugars_possible = True
        self.biochemical_state.amino_acids_possible = True
        self.biochemical_state.lipids_possible = True
        self.biochemical_state.fermentation_substrate_possible = True

        self.record_history()
        self.write_to_world()

        print("BIOCHEMICAL FOUNDATIONS FORMED")
        print("SUGARS BECOME POSSIBLE")
        print("AMINO ACIDS BECOME POSSIBLE")
        print("LIPIDS BECOME POSSIBLE")
        print("FERMENTATION SUBSTRATE BECOMES POSSIBLE")

        return self.public_state

    def add_compound(self, name, compound_type, requires, future_use):
        self.compounds[name] = {
            "name": name,
            "type": compound_type,
            "state": "possible",
            "requires": requires,
            "future_use": future_use,
            "origin": "planetary_biochemistry"
        }

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "biochemical_foundations_formed",
            "description": "Water and organic molecules allow sugars, amino acids, lipids, and fermentation substrates to become possible."
        })

    def write_to_world(self):
        self._refresh_public_state()
        self.universe.world["biochemical_foundations"] = self.public_state
        self.universe.world["biochemical_compounds"] = self.compounds
        self.universe.world["biochemical_state"] = self.biochemical_state
