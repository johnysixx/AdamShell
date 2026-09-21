import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.stars import Stars
from universe.stellar_objects import PrimordialStar
from universe.stellar_nucleosynthesis import (
    StellarNucleosynthesis,
)
from universe.stellar_state import StellarFormationState
from universe.universe import Universe


class StellarFormationObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def _formed_stars(self):
        universe = Universe()
        universe.world["germinal_clouds"] = [
            StellarMaterialCloud(
                name="first_germinal_cloud",
                type="germinal_cloud",
                state="condensing",
                composition={},
                can_form_stars=True,
            ),
            StellarMaterialCloud(
                name="deep_germinal_cloud",
                type="germinal_cloud",
                state="quiet",
                composition={},
                can_form_stars=True,
            ),
        ]
        process = Stars(universe)
        result = process.form_first_stars()

        return universe, process, result

    def test_stellar_state_is_object_only(self):
        state = StellarFormationState()

        self._assert_object_only(
            state,
            "first_stars_formed",
        )

    def test_initial_values_are_preserved(self):
        state = StellarFormationState()

        self.assertFalse(state.first_stars_formed)
        self.assertFalse(
            state.stellar_fusion_possible
        )
        self.assertFalse(
            state.heavy_elements_possible
        )

    def test_formation_mutates_same_state_object(
        self
    ):
        universe = Universe()
        universe.world["germinal_clouds"] = [
            StellarMaterialCloud(
                name="first_germinal_cloud",
                type="germinal_cloud",
                state="condensing",
                composition={},
                can_form_stars=True,
            ),
        ]
        process = Stars(universe)
        state = process.stellar_state

        process.form_first_stars()

        self.assertIs(process.stellar_state, state)
        self.assertTrue(state.first_stars_formed)
        self.assertTrue(
            state.stellar_fusion_possible
        )
        self.assertTrue(
            state.heavy_elements_possible
        )

    def test_world_stores_state_object_and_registry(
        self
    ):
        universe, process, _ = self._formed_stars()

        state = universe.world["stellar_state"]
        self.assertIsInstance(
            state,
            StellarFormationState,
        )
        self.assertIs(state, process.stellar_state)
        self.assertIsInstance(
            universe.world["first_stars"],
            list,
        )
        self.assertTrue(
            all(
                isinstance(star, PrimordialStar)
                for star in universe.world["first_stars"]
            )
        )
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._formed_stars()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["stellar_state"],
            dict,
        )
        self.assertIsInstance(result["stars"], list)
        self.assertTrue(
            result["stellar_state"][
                "first_stars_formed"
            ]
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_stars()

        result["stellar_state"][
            "first_stars_formed"
        ] = False
        result["stars"][0]["composition"][
            "hydrogen"
        ] = "missing"

        self.assertTrue(
            process.stellar_state.first_stars_formed
        )
        self.assertEqual(
            process.stars[0].composition[
                "hydrogen"
            ],
            "dominant",
        )

    def test_stellar_nucleosynthesis_reads_object(
        self
    ):
        universe, _, _ = self._formed_stars()
        process = StellarNucleosynthesis(universe)

        result = process.forge_elements_up_to_iron()

        self.assertEqual(result["state"], "forged")
        self.assertIn("iron", process.elements_up_to_iron)

    def test_rejects_legacy_cloud_dict(self):
        universe = Universe()
        universe.world["germinal_clouds"] = [
            {
                "name": "legacy_cloud",
                "can_form_stars": True,
            },
        ]
        process = Stars(universe)

        result = process.form_first_stars()

        self.assertEqual(result["type"], "quantum_error")
        self.assertIn(
            "StellarMaterialCloud",
            result["cronenberg"].origin.error_message,
        )

    def test_formation_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        universe.world["germinal_clouds"] = [
            StellarMaterialCloud(
                name="broken_cloud",
                type="germinal_cloud",
                state="condensing",
                composition={},
                can_form_stars=True,
            ),
        ]
        process = Stars(universe)

        def broken_history():
            raise RuntimeError(
                "stellar formation exploded"
            )

        process.record_history = broken_history

        result = process.form_first_stars()
        cronenberg = result["cronenberg"]

        self.assertEqual(
            result["type"],
            "quantum_error",
        )
        self.assertIn(
            cronenberg,
            universe.cronenbergs,
        )
        self.assertEqual(
            cronenberg.origin.source_component,
            "stars",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_first_stars",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "stellar formation exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = StellarFormationState()
        state.first_stars_formed = True

        snapshot = state.to_dict()
        snapshot["first_stars_formed"] = False

        self.assertTrue(state.first_stars_formed)


if __name__ == "__main__":
    unittest.main()
