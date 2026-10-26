import unittest

from universe.big_bang import BigBang
from universe.big_bang_process_state import BigBangProcessState
from universe.cosmic_clouds import CosmicClouds
from universe.cosmic_clouds_process_state import (
    CosmicCloudsProcessState,
)
from universe.primordial_objects import PrimordialCosmicComponent
from universe.stars import Stars
from universe.stars_process_state import StarsProcessState
from universe.universe import Universe


class CosmicCloudsCanonicalBigBangTests(unittest.TestCase):

    def _component(self, name):
        return PrimordialCosmicComponent(
            name=name,
            type="element",
            state="formed",
            origin="big_bang_nucleosynthesis",
        )

    def _canonical_big_bang(self, elements):
        universe = Universe()
        big_bang = BigBang(universe)
        big_bang.primordial_elements = elements
        universe.big_bang = big_bang
        return universe, big_bang

    def _started_big_bang(self):
        universe = Universe()
        result = universe.start_big_bang()

        self.assertIs(
            result.state,
            BigBangProcessState.COMPLETED,
        )
        self.assertIs(
            universe.big_bang.result,
            result,
        )

        return universe, result

    def test_real_big_bang_forms_canonical_clouds(self):
        universe, big_bang_result = self._started_big_bang()

        process = CosmicClouds(universe)
        result = process.form_germinal_clouds()

        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FORMED,
        )
        self.assertEqual(len(process.clouds), 2)

        self.assertIs(
            universe.world["germinal_clouds"],
            process.clouds,
        )
        self.assertIs(
            universe.cosmic_clouds_layer,
            process,
        )
        self.assertIs(
            big_bang_result.primordial_elements["hydrogen"],
            universe.big_bang.primordial_elements["hydrogen"],
        )

        self.assertTrue(
            process.cosmic_cloud_state.hydrogen_available
        )
        self.assertTrue(
            process.cosmic_cloud_state.helium_available
        )

    def test_downstream_stars_keep_canonical_cloud_identity(
        self
    ):
        universe, _ = self._started_big_bang()

        clouds = CosmicClouds(universe)
        clouds.form_germinal_clouds()

        stars = Stars(universe)
        result = stars.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )
        self.assertEqual(len(stars.stars), 2)

        self.assertIs(
            stars.stars[0].source_cloud,
            clouds.clouds[0],
        )
        self.assertIs(
            stars.stars[1].source_cloud,
            clouds.clouds[1],
        )

    def test_public_decoy_cannot_override_big_bang(self):
        universe, _ = self._started_big_bang()

        universe.world["primordial_elements"] = {
            "hydrogen": {"name": "legacy"},
        }

        process = CosmicClouds(universe)
        result = process.form_germinal_clouds()

        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FORMED,
        )
        self.assertEqual(len(process.clouds), 2)

    def test_missing_public_alias_does_not_block(self):
        universe, _ = self._started_big_bang()

        universe.world.pop("primordial_elements", None)

        result = CosmicClouds(
            universe
        ).form_germinal_clouds()

        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FORMED,
        )

    def test_world_only_primordial_elements_cannot_form_clouds(
        self
    ):
        universe = Universe()
        universe.world["primordial_elements"] = {
            "hydrogen": self._component("hydrogen"),
            "helium": self._component("helium"),
        }

        process = CosmicClouds(universe)
        result = process.form_germinal_clouds()

        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FAILED,
        )
        self.assertEqual(process.clouds, [])
        self.assertFalse(
            process.cosmic_cloud_state.hydrogen_available
        )

    def test_missing_canonical_hydrogen_fails(self):
        universe, _ = self._canonical_big_bang({
            "helium": self._component("helium"),
        })

        process = CosmicClouds(universe)
        result = process.form_germinal_clouds()

        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FAILED,
        )
        self.assertFalse(
            process.cosmic_cloud_state.hydrogen_available
        )
        self.assertFalse(
            process.cosmic_cloud_state.helium_available
        )

    def test_missing_canonical_helium_preserves_hydrogen_flag(
        self
    ):
        universe, _ = self._canonical_big_bang({
            "hydrogen": self._component("hydrogen"),
        })

        process = CosmicClouds(universe)
        result = process.form_germinal_clouds()

        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FAILED,
        )
        self.assertTrue(
            process.cosmic_cloud_state.hydrogen_available
        )
        self.assertFalse(
            process.cosmic_cloud_state.helium_available
        )

    def test_invalid_canonical_component_creates_cronenberg(
        self
    ):
        universe, _ = self._canonical_big_bang({
            "hydrogen": {"name": "legacy_hydrogen"},
            "helium": self._component("helium"),
        })

        result = CosmicClouds(
            universe
        ).form_germinal_clouds()

        self.assertEqual(result.type, "quantum_error")
        self.assertIn(
            "PrimordialCosmicComponent",
            result.cronenberg.origin.error_message,
        )
        self.assertEqual(
            result.cronenberg.origin.source_component,
            "cosmic_clouds",
        )
        self.assertEqual(
            result.cronenberg.origin.source_operation,
            "form_germinal_clouds",
        )

    def test_formation_never_reads_public_primordial_registry(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key == "primordial_elements":
                    raise AssertionError(
                        "Read from public primordial registry"
                    )
                return super().get(key, default)

            def __getitem__(self, key):
                if key == "primordial_elements":
                    raise AssertionError(
                        "Indexed public primordial registry"
                    )
                return super().__getitem__(key)

        universe, _ = self._started_big_bang()

        universe.world = GuardedWorld(universe.world)

        clouds = CosmicClouds(universe)
        result = clouds.form_germinal_clouds()

        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FORMED,
        )
        self.assertEqual(len(clouds.clouds), 2)


if __name__ == "__main__":
    unittest.main()
