import unittest

from universe.cosmic_clouds import CosmicClouds
from universe.cosmic_objects import StellarMaterialCloud
from universe.primordial_objects import (
    PrimordialElement,
)
from universe.stars import Stars
from universe.stars_process_state import (
    StarsProcessState,
)
from universe.stellar_objects import PrimordialStar
from universe.universe import Universe
from universe.big_bang import BigBang


class StarsCanonicalCloudBoundaryObjectStateTests(
    unittest.TestCase
):

    def _wire_canonical_big_bang(self, universe, elements):
        big_bang = BigBang(universe)
        big_bang.primordial_elements = elements
        universe.big_bang = big_bang

    def _primordial_component(self, name):
        return PrimordialElement(
            name=name,
            state="formed",
            origin="big_bang_nucleosynthesis",
        )

    def _cloud(self, name="custom_cloud"):
        return StellarMaterialCloud(
            name=name,
            type="germinal_cloud",
            state="condensing",
            composition={
                "hydrogen": "dominant",
                "helium": "secondary",
            },
            can_form_stars=True,
        )

    def _formed_clouds(self):
        universe = Universe()

        primordial_elements = {
            "hydrogen": self._primordial_component(
                "hydrogen"
            ),
            "helium": self._primordial_component(
                "helium"
            ),
        }

        self._wire_canonical_big_bang(universe, primordial_elements)

        layer = CosmicClouds(universe)

        result = layer.form_germinal_clouds()

        self.assertTrue(
            result.cosmic_cloud_state.germinal_clouds_formed
        )

        self.assertEqual(
            len(layer.clouds),
            2,
        )

        return universe, layer

    def test_cloud_layer_is_canonical_object(self):
        universe = Universe()

        self.assertFalse(
            hasattr(universe, "cosmic_clouds_layer")
        )

        layer = CosmicClouds(universe)

        self.assertIs(
            universe.cosmic_clouds_layer,
            layer,
        )

        self.assertIsInstance(layer.clouds, list)
        self.assertEqual(layer.clouds, [])

    def test_stars_use_canonical_cloud_identity(self):
        universe, layer = self._formed_clouds()

        process = Stars(universe)

        result = process.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )

        self.assertEqual(len(process.stars), 2)

        self.assertIsInstance(
            process.stars[0],
            PrimordialStar,
        )

        self.assertIs(
            process.stars[0].source_cloud,
            layer.clouds[0],
        )

        self.assertIs(
            process.stars[1].source_cloud,
            layer.clouds[1],
        )

        self.assertNotIn("germinal_clouds", universe.world)
        self.assertIs(
            process.stars[0].source_cloud,
            layer.clouds[0],
        )

        self.assertIs(
            universe.world["first_stars"],
            process.stars,
        )

    def test_world_decoy_cannot_replace_clouds(self):
        universe, layer = self._formed_clouds()

        universe.world["germinal_clouds"] = [
            {"name": "legacy_cloud"},
        ]

        process = Stars(universe)

        result = process.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )

        self.assertIs(
            process.stars[0].source_cloud,
            layer.clouds[0],
        )

        self.assertIs(
            process.stars[1].source_cloud,
            layer.clouds[1],
        )

    def test_missing_public_alias_does_not_break_stars(
        self
    ):
        universe, layer = self._formed_clouds()

        universe.world.pop(
            "germinal_clouds",
            None,
        )

        process = Stars(universe)

        result = process.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )

        self.assertIs(
            process.stars[0].source_cloud,
            layer.clouds[0],
        )

    def test_world_only_clouds_are_not_runtime_input(
        self
    ):
        universe = Universe()
        cloud = self._cloud()

        universe.world["germinal_clouds"] = [
            cloud,
        ]

        process = Stars(universe)

        result = process.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FAILED,
        )

        self.assertEqual(process.stars, [])

        self.assertFalse(
            process.stellar_state.first_stars_formed
        )

    def test_explicit_clouds_override_canonical_layer(
        self
    ):
        universe, layer = self._formed_clouds()

        explicit = self._cloud(
            "explicit_source",
        )

        process = Stars(
            universe,
            source_clouds=[explicit],
        )

        result = process.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )

        self.assertIs(
            process.stars[0].source_cloud,
            explicit,
        )

        self.assertIs(
            process.stars[1].source_cloud,
            explicit,
        )

        self.assertIs(
            universe.cosmic_clouds_layer,
            layer,
        )

    def test_invalid_explicit_cloud_creates_cronenberg(
        self
    ):
        universe = Universe()

        process = Stars(
            universe,
            source_clouds=[
                {
                    "name": "legacy_cloud",
                    "can_form_stars": True,
                }
            ],
        )

        result = process.form_first_stars()

        self.assertEqual(
            result.type,
            "quantum_error",
        )

        self.assertIn(
            "StellarMaterialCloud",
            result.cronenberg.origin.error_message,
        )

        self.assertEqual(
            result.cronenberg.origin.source_component,
            "stars",
        )

    def test_canonical_formation_does_not_read_world(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key == "germinal_clouds":
                    raise AssertionError(
                        "Star formation must not "
                        "read world cloud registry"
                    )

                return super().get(
                    key,
                    default,
                )

            def __getitem__(self, key):
                if key == "germinal_clouds":
                    raise AssertionError(
                        "Star formation must not "
                        "index world cloud registry"
                    )

                return super().__getitem__(key)

        universe, layer = self._formed_clouds()

        universe.world = GuardedWorld(
            universe.world
        )

        process = Stars(universe)

        result = process.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )

        self.assertIs(
            process.stars[0].source_cloud,
            layer.clouds[0],
        )

        self.assertEqual(
            len(process.stars),
            2,
        )


if __name__ == "__main__":
    unittest.main()
