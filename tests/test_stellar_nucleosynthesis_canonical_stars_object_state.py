import unittest

from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.stars import Stars
from universe.stars_process_state import StarsProcessState
from universe.stellar_state import StellarFormationState
from universe.stellar_nucleosynthesis import (
    StellarNucleosynthesis,
)
from universe.stellar_nucleosynthesis_process_state import (
    StellarNucleosynthesisProcessState,
)
from universe.stellar_nucleosynthesis_result_state import (
    StellarNucleosynthesisResult,
)
from universe.universe import Universe


class StellarNucleosynthesisCanonicalStarsTests(
    unittest.TestCase
):

    def _formed_stars(self):
        universe = Universe()

        cloud = StellarMaterialCloud(
            name="canonical_source_cloud",
            type="germinal_cloud",
            state="condensing",
            composition={
                "hydrogen": "dominant",
                "helium": "secondary",
            },
            can_form_stars=True,
        )

        layer = Stars(
            universe,
            source_clouds=[cloud],
        )

        result = layer.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )

        self.assertEqual(len(layer.stars), 2)

        return universe, layer, cloud

    def test_stars_register_canonical_layer(self):
        universe = Universe()

        self.assertFalse(
            hasattr(universe, "stars_layer")
        )

        layer = Stars(universe)

        self.assertIs(
            universe.stars_layer,
            layer,
        )

        self.assertEqual(layer.stars, [])

        self.assertFalse(
            layer.stellar_state.stellar_fusion_possible
        )

    def test_nucleosynthesis_uses_canonical_stars(
        self
    ):
        universe, layer, cloud = self._formed_stars()

        process = StellarNucleosynthesis(universe)

        result = process.forge_elements_up_to_iron()

        self.assertIsInstance(
            result,
            StellarNucleosynthesisResult,
        )

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            universe.stars_layer,
            layer,
        )

        self.assertIs(
            layer.stars[0].source_cloud,
            cloud,
        )

        iron = result.elements_up_to_iron["iron"]

        self.assertIsInstance(
            iron,
            ChemicalElement,
        )

        self.assertEqual(iron.atomic_number, 26)
        self.assertEqual(iron.symbol, "Fe")

        self.assertIs(
            iron,
            process.elements_up_to_iron["iron"],
        )

        self.assertTrue(
            process.stellar_nucleosynthesis_state
            .stellar_fusion_active
        )

        self.assertTrue(
            process.stellar_nucleosynthesis_state
            .iron_limit_reached
        )

    def test_public_decoys_do_not_override_stars(
        self
    ):
        universe, layer, _ = self._formed_stars()

        universe.world["first_stars"] = [
            {"name": "legacy_star"},
        ]

        universe.world["stellar_state"] = (
            StellarFormationState(
                stellar_fusion_possible=False,
            )
        )

        process = StellarNucleosynthesis(universe)

        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertEqual(
            len(layer.stars),
            2,
        )

        self.assertIn(
            "iron",
            process.elements_up_to_iron,
        )

    def test_missing_public_aliases_do_not_block_fusion(
        self
    ):
        universe, layer, _ = self._formed_stars()

        universe.world.pop(
            "first_stars",
            None,
        )

        universe.world.pop(
            "stellar_state",
            None,
        )

        result = (
            StellarNucleosynthesis(universe)
            .forge_elements_up_to_iron()
        )

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            universe.stars_layer,
            layer,
        )

    def test_world_only_stars_cannot_enable_fusion(
        self
    ):
        universe = Universe()

        universe.world["first_stars"] = [
            object(),
        ]

        universe.world["stellar_state"] = (
            StellarFormationState(
                stellar_fusion_possible=True,
            )
        )

        process = StellarNucleosynthesis(universe)

        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FAILED,
        )

        self.assertTrue(
            process.stellar_nucleosynthesis_state.failed
        )

        self.assertEqual(
            process.elements_up_to_iron,
            {},
        )

    def test_canonical_fusion_flag_controls_forging(
        self
    ):
        universe, layer, _ = self._formed_stars()

        layer.stellar_state.stellar_fusion_possible = (
            False
        )

        universe.world["stellar_state"] = (
            StellarFormationState(
                stellar_fusion_possible=True,
            )
        )

        process = StellarNucleosynthesis(universe)

        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FAILED,
        )

        self.assertFalse(
            process.stellar_nucleosynthesis_state
            .stellar_fusion_active
        )

        self.assertTrue(
            process.stellar_nucleosynthesis_state.failed
        )

    def test_invalid_canonical_star_is_rejected(
        self
    ):
        universe = Universe()
        layer = Stars(universe)

        layer.stars.append(
            {"name": "legacy_star"}
        )

        layer.stellar_state.stellar_fusion_possible = (
            True
        )

        process = StellarNucleosynthesis(universe)

        with self.assertRaisesRegex(
            TypeError,
            "PrimordialStar",
        ):
            process.forge_elements_up_to_iron()

    def test_forging_does_not_read_public_star_registries(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key in (
                    "first_stars",
                    "stellar_state",
                ):
                    raise AssertionError(
                        "Public star registry read"
                    )

                return super().get(key, default)

            def __getitem__(self, key):
                if key in (
                    "first_stars",
                    "stellar_state",
                ):
                    raise AssertionError(
                        "Public star registry indexed"
                    )

                return super().__getitem__(key)

            def __contains__(self, key):
                if key in (
                    "first_stars",
                    "stellar_state",
                ):
                    raise AssertionError(
                        "Public star registry checked"
                    )

                return super().__contains__(key)

        universe, layer, _ = self._formed_stars()

        universe.world = GuardedWorld(
            universe.world
        )

        process = StellarNucleosynthesis(universe)

        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            universe.stars_layer,
            layer,
        )

        self.assertEqual(
            result.elements_up_to_iron[
                "iron"
            ].atomic_number,
            26,
        )


if __name__ == "__main__":
    unittest.main()
