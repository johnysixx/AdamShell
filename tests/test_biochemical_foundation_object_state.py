import unittest

from universe.biochemical_foundations import (
    BiochemicalFoundations,
)
from universe.biochemical_objects import (
    BiochemicalCompound,
)
from universe.biochemical_state import (
    BiochemicalFoundationState,
)
from universe.planetary_material_objects import (
    PlanetaryMaterial,
)
from universe.universe import Universe


class BiochemicalFoundationObjectStateTests(
    unittest.TestCase
):

    def _materials(self):
        water = PlanetaryMaterial(
            name="water",
            requires=("hydrogen", "oxygen"),
        )
        organic_molecules = PlanetaryMaterial(
            name="organic_molecules",
            requires=(
                "carbon",
                "hydrogen",
                "oxygen",
                "nitrogen",
            ),
        )
        return {
            "water": water.make_available(
                origin="test_planetary_materialization"
            ),
            "organic_molecules": organic_molecules.make_available(
                origin="test_planetary_materialization"
            ),
        }

    def _formed_process(self):
        universe = Universe()
        universe.world[
            "available_planetary_materials"
        ] = self._materials()
        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()
        return universe, process, result

    def test_state_is_object_only(self):
        state = BiochemicalFoundationState()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(state, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = state["sugars_possible"]

    def test_initial_values_are_false(self):
        state = BiochemicalFoundationState()

        self.assertFalse(
            state.water_based_chemistry_possible
        )
        self.assertFalse(
            state.carbon_chemistry_possible
        )
        self.assertFalse(state.sugars_possible)
        self.assertFalse(state.amino_acids_possible)
        self.assertFalse(state.lipids_possible)
        self.assertFalse(
            state.fermentation_substrate_possible
        )

    def test_formation_mutates_same_state_object(self):
        universe, process, _ = self._formed_process()
        state = process.biochemical_state

        self.assertIs(
            universe.world["biochemical_state"],
            state,
        )
        self.assertTrue(
            state.water_based_chemistry_possible
        )
        self.assertTrue(
            state.carbon_chemistry_possible
        )
        self.assertTrue(state.sugars_possible)
        self.assertTrue(state.amino_acids_possible)
        self.assertTrue(state.lipids_possible)
        self.assertTrue(
            state.fermentation_substrate_possible
        )

    def test_compound_registry_stays_dict_boundary(self):
        universe, process, result = self._formed_process()

        self.assertIs(
            universe.world["biochemical_compounds"],
            process.compounds,
        )
        self.assertIsInstance(process.compounds, dict)
        self.assertEqual(
            set(process.compounds),
            {
                "sugars",
                "amino_acids",
                "lipids",
                "fermentation_substrate",
            },
        )
        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["biochemical_state"],
            dict,
        )
        self.assertIsInstance(result["compounds"], dict)
        self.assertTrue(
            all(
                isinstance(compound, BiochemicalCompound)
                for compound in process.compounds.values()
            )
        )

    def test_public_result_is_deeply_detached(self):
        _, process, result = self._formed_process()

        result["biochemical_state"][
            "sugars_possible"
        ] = False
        result["compounds"]["sugars"][
            "requires"
        ].append("fake_material")

        self.assertTrue(
            process.biochemical_state.sugars_possible
        )
        self.assertNotIn(
            "fake_material",
            process.compounds["sugars"].requires,
        )

    def test_missing_material_preserves_initial_state(self):
        universe = Universe()
        universe.world[
            "available_planetary_materials"
        ] = {"water": self._materials()["water"]}
        process = BiochemicalFoundations(universe)

        result = process.form_biochemical_foundations()

        self.assertEqual(process.state, "failed")
        self.assertFalse(
            process.biochemical_state.sugars_possible
        )
        self.assertFalse(
            result["biochemical_state"][
                "sugars_possible"
            ]
        )

    def test_formation_error_creates_cronenberg(self):
        universe = Universe()
        universe.world[
            "available_planetary_materials"
        ] = self._materials()
        process = BiochemicalFoundations(universe)

        def broken_history():
            raise RuntimeError(
                "biochemical formation exploded"
            )

        process.record_history = broken_history

        result = process.form_biochemical_foundations()
        cronenberg = result["cronenberg"]

        self.assertEqual(result["type"], "quantum_error")
        self.assertIn(cronenberg, universe.cronenbergs)
        self.assertEqual(
            cronenberg.origin.source_component,
            "biochemical_foundations",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_biochemical_foundations",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "biochemical formation exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = BiochemicalFoundationState()
        state.sugars_possible = True

        snapshot = state.to_dict()
        snapshot["sugars_possible"] = False

        self.assertTrue(state.sugars_possible)


if __name__ == "__main__":
    unittest.main()
