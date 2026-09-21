import unittest

from universe.cosmic_cloud_state import (
    CosmicCloudFormationState,
)
from universe.cosmic_clouds import CosmicClouds
from universe.cosmic_objects import StellarMaterialCloud
from universe.stars import Stars
from universe.universe import Universe


class CosmicCloudObjectStateTests(unittest.TestCase):

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
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def _formed_clouds(self):
        universe = Universe()
        universe.world["primordial_elements"] = {
            "hydrogen": {
                "name": "hydrogen",
                "atomic_number": 1,
            },
            "helium": {
                "name": "helium",
                "atomic_number": 2,
            },
        }

        process = CosmicClouds(universe)
        result = process.form_germinal_clouds()

        return universe, process, result

    def test_state_is_object_only(self):
        state = CosmicCloudFormationState()

        self._assert_object_only(
            state,
            "germinal_clouds_formed",
        )

    def test_initial_values_are_preserved(self):
        state = CosmicCloudFormationState()

        self.assertFalse(state.hydrogen_available)
        self.assertFalse(state.helium_available)
        self.assertFalse(state.germinal_clouds_formed)
        self.assertFalse(state.star_formation_possible)

    def test_formation_mutates_same_state_object(self):
        universe = Universe()
        universe.world["primordial_elements"] = {
            "hydrogen": {},
            "helium": {},
        }
        process = CosmicClouds(universe)
        state = process.cosmic_cloud_state

        process.form_germinal_clouds()

        self.assertIs(process.cosmic_cloud_state, state)
        self.assertTrue(state.hydrogen_available)
        self.assertTrue(state.helium_available)
        self.assertTrue(state.germinal_clouds_formed)
        self.assertTrue(state.star_formation_possible)

    def test_world_stores_state_object_and_registry(self):
        universe, process, _ = self._formed_clouds()

        self.assertIs(
            universe.world["cosmic_cloud_state"],
            process.cosmic_cloud_state,
        )
        self.assertIs(
            universe.world["germinal_clouds"],
            process.clouds,
        )
        self.assertIsInstance(
            universe.world["germinal_clouds"],
            list,
        )

    def test_public_result_remains_dict_boundary(self):
        _, _, result = self._formed_clouds()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["cosmic_cloud_state"],
            dict,
        )
        self.assertIsInstance(result["clouds"], list)
        self.assertTrue(
            result["cosmic_cloud_state"][
                "germinal_clouds_formed"
            ]
        )

    def test_public_result_is_deeply_detached(self):
        _, process, result = self._formed_clouds()

        result["cosmic_cloud_state"][
            "germinal_clouds_formed"
        ] = False
        result["clouds"][0]["composition"][
            "hydrogen"
        ] = "missing"

        self.assertTrue(
            process
            .cosmic_cloud_state
            .germinal_clouds_formed
        )
        self.assertEqual(
            process.clouds[0].composition[
                "hydrogen"
            ],
            "dominant",
        )

    def test_formed_clouds_are_object_only(self):
        _, process, _ = self._formed_clouds()

        cloud = process.clouds[0]

        self.assertIsInstance(cloud, StellarMaterialCloud)
        self._assert_object_only(cloud, "name")
        self.assertEqual(cloud.name, "first_germinal_cloud")
        self.assertTrue(cloud.can_form_stars)

    def test_cloud_composition_is_read_only(self):
        _, process, _ = self._formed_clouds()

        cloud = process.clouds[0]

        with self.assertRaises(TypeError):
            cloud.composition["hydrogen"] = "missing"

        self.assertEqual(
            cloud.composition["hydrogen"],
            "dominant",
        )

    def test_cloud_to_dict_is_detached_boundary(self):
        _, process, _ = self._formed_clouds()

        cloud = process.clouds[0]
        snapshot = cloud.to_dict()
        snapshot["composition"]["hydrogen"] = "missing"

        self.assertEqual(
            cloud.composition["hydrogen"],
            "dominant",
        )

    def test_missing_hydrogen_preserves_initial_state(self):
        universe = Universe()
        universe.world["primordial_elements"] = {
            "helium": {},
        }
        process = CosmicClouds(universe)

        result = process.form_germinal_clouds()

        self.assertEqual(process.state, "failed")
        self.assertFalse(
            process.cosmic_cloud_state.hydrogen_available
        )
        self.assertFalse(
            process.cosmic_cloud_state.helium_available
        )
        self.assertFalse(
            result["cosmic_cloud_state"][
                "germinal_clouds_formed"
            ]
        )

    def test_missing_helium_records_available_hydrogen(self):
        universe = Universe()
        universe.world["primordial_elements"] = {
            "hydrogen": {},
        }
        process = CosmicClouds(universe)

        result = process.form_germinal_clouds()

        self.assertEqual(process.state, "failed")
        self.assertTrue(
            process.cosmic_cloud_state.hydrogen_available
        )
        self.assertFalse(
            process.cosmic_cloud_state.helium_available
        )
        self.assertTrue(
            result["cosmic_cloud_state"][
                "hydrogen_available"
            ]
        )

    def test_downstream_star_formation_works(self):
        universe, _, _ = self._formed_clouds()

        process = Stars(universe)
        result = process.form_first_stars()

        self.assertEqual(result["state"], "formed")
        self.assertTrue(
            process.stellar_state.first_stars_formed
        )
        self.assertEqual(len(process.stars), 2)

    def test_formation_error_creates_cronenberg(self):
        universe = Universe()
        universe.world["primordial_elements"] = {
            "hydrogen": {},
            "helium": {},
        }
        process = CosmicClouds(universe)

        def broken_history():
            raise RuntimeError(
                "cosmic cloud formation exploded"
            )

        process.record_history = broken_history

        result = process.form_germinal_clouds()
        cronenberg = result["cronenberg"]

        self.assertEqual(result["type"], "quantum_error")
        self.assertIn(cronenberg, universe.cronenbergs)
        self.assertEqual(
            cronenberg.origin.source_component,
            "cosmic_clouds",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_germinal_clouds",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "cosmic cloud formation exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = CosmicCloudFormationState()
        state.germinal_clouds_formed = True

        snapshot = state.to_dict()
        snapshot["germinal_clouds_formed"] = False

        self.assertTrue(state.germinal_clouds_formed)


if __name__ == "__main__":
    unittest.main()
