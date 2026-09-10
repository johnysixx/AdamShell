from copy import deepcopy

from universe.planet_state import PlanetFormationState
from universe.planetary_material_state import (
    PlanetaryMaterialState,
)


class PlanetaryMaterials:

    def __init__(self, universe):
        self.universe = universe
        self.name = "planetary_materials"
        self.type = "planetary_material_layer"
        self.state = "ready"

        self.available_materials = {}

        self.material_state = PlanetaryMaterialState()

        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "available_materials": deepcopy(
                self.available_materials
            ),
            "material_state": self.material_state.to_dict(),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def materialize(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=self._materialize_unprotected,
                source_component="planetary_materials",
                source_operation="materialize",
            )
        )

    def _materialize_unprotected(self):
        planetary_state = self.universe.world.get(
            "planetary_state",
            PlanetFormationState(),
        )
        possible_materials = self.universe.world.get("planetary_materials", {})

        if not planetary_state.earth_formed:
            self.state = "failed"

            print("PLANETARY MATERIALIZATION FAILED: Earth has not formed yet")
            self.write_to_world()
            return self.public_state

        self.state = "materialized"

        if planetary_state.water_possible:
            self.make_available("water", possible_materials)

        if planetary_state.ice_possible:
            self.make_available("ice", possible_materials)

        if planetary_state.minerals_possible:
            self.make_available("minerals", possible_materials)

        if planetary_state.organic_molecules_possible:
            self.make_available("organic_molecules", possible_materials)

        self.material_state.water_available = (
            "water" in self.available_materials
        )
        self.material_state.ice_available = (
            "ice" in self.available_materials
        )
        self.material_state.minerals_available = (
            "minerals" in self.available_materials
        )
        self.material_state.organic_molecules_available = (
            "organic_molecules" in self.available_materials
        )

        self.record_history()
        self.write_to_world()

        print("PLANETARY MATERIALS MATERIALIZED")
        print("WATER AVAILABLE")
        print("ICE AVAILABLE")
        print("MINERALS AVAILABLE")
        print("ORGANIC MOLECULES AVAILABLE")

        return self.public_state

    def make_available(self, material_name, possible_materials):
        material = possible_materials.get(material_name)

        if material is None:
            return

        self.available_materials[material_name] = {
            **material,
            "state": "available",
            "origin": "earth_planetary_materialization"
        }

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "planetary_materials_materialized",
            "description": "Earth makes water, ice, minerals, and organic molecules available as planetary materials."
        })

    def write_to_world(self):
        self._refresh_public_state()
        self.universe.world["planetary_material_layer"] = self.public_state
        self.universe.world["available_planetary_materials"] = self.available_materials
        self.universe.world["planetary_material_state"] = self.material_state
