import unittest
from unittest.mock import Mock

from universe.chemical_objects import Isotope
from universe.physical_record_state import (
    CosmicHistoryEvent,
    RadioactiveDecayPattern,
)
from universe.physical_time_result_state import (
    RadioactiveDecayDefinitionResult,
)
from universe.radioactive_decay import RadioactiveDecay
from universe.radioactive_decay_process_state import (
    RadioactiveDecayProcessState,
)
from universe.universe import Universe


class RadioactiveDecayIsotopeBoundaryObjectStateTests(
    unittest.TestCase
):

    def test_world_decoy_does_not_skip_local_formation(
        self
    ):
        universe = Universe()

        universe.world["known_isotopes"] = {
            "carbon_14": object(),
        }

        process = RadioactiveDecay(universe)

        process.ensure_isotopes()

        registry = process.isotopes_layer.isotopes

        self.assertEqual(len(registry), 8)

        self.assertIsInstance(
            registry["carbon_14"],
            Isotope,
        )

        self.assertTrue(
            process.decay_state.isotopes_available
        )

        self.assertIs(
            universe.world["known_isotopes"],
            registry,
        )

    def test_definition_uses_canonical_isotopes(
        self
    ):
        universe = Universe()
        process = RadioactiveDecay(universe)

        process.ensure_isotopes()

        local_carbon = (
            process.isotopes_layer
            .isotopes["carbon_14"]
        )

        universe.world["known_isotopes"] = {
            "carbon_14": object(),
        }

        result = process.define_reference_decay()

        self.assertIsInstance(
            result,
            RadioactiveDecayDefinitionResult,
        )

        self.assertIs(
            result.state,
            RadioactiveDecayProcessState.DEFINED,
        )

        carbon = process.decay_patterns[
            "carbon_14_decay"
        ]

        self.assertIsInstance(
            carbon,
            RadioactiveDecayPattern,
        )

        self.assertEqual(
            carbon.parent_element,
            local_carbon.element_name,
        )

        self.assertEqual(
            carbon.parent_symbol,
            local_carbon.symbol,
        )

        self.assertEqual(
            carbon.half_life_years,
            5730,
        )

        self.assertEqual(
            process.decay_state.decay_pattern_count,
            4,
        )

    def test_all_reference_half_lives_preserved(
        self
    ):
        process = RadioactiveDecay(Universe())

        result = process.define_reference_decay()

        expected = {
            "carbon_14_decay": (
                "carbon",
                "C",
                "nitrogen_14",
                5730,
            ),
            "potassium_40_decay": (
                "potassium",
                "K",
                "argon_40",
                1_250_000_000,
            ),
            "thorium_232_decay": (
                "thorium",
                "Th",
                "lead_208",
                14_000_000_000,
            ),
            "uranium_238_decay": (
                "uranium",
                "U",
                "lead_206",
                4_500_000_000,
            ),
        }

        self.assertEqual(
            set(result.decay_patterns),
            set(expected),
        )

        for name, details in expected.items():
            with self.subTest(pattern=name):
                (
                    element,
                    symbol,
                    daughter,
                    half_life,
                ) = details

                pattern = result.decay_patterns[name]

                self.assertIsInstance(
                    pattern,
                    RadioactiveDecayPattern,
                )

                self.assertEqual(
                    pattern.parent_element,
                    element,
                )

                self.assertEqual(
                    pattern.parent_symbol,
                    symbol,
                )

                self.assertEqual(
                    pattern.daughter_product,
                    daughter,
                )

                self.assertEqual(
                    pattern.half_life_years,
                    half_life,
                )

                self.assertEqual(
                    pattern.half_life_precision,
                    "reference_approximation",
                )

    def test_missing_local_isotope_is_rejected(
        self
    ):
        universe = Universe()
        process = RadioactiveDecay(universe)

        process.ensure_isotopes()

        carbon = (
            process.isotopes_layer
            .isotopes.pop("carbon_14")
        )

        universe.world["known_isotopes"] = {
            "carbon_14": carbon,
        }

        with self.assertRaisesRegex(
            ValueError,
            "Missing isotope: carbon_14",
        ):
            process.create_decay_pattern(
                isotope_name="carbon_14",
                daughter_product="nitrogen_14",
                half_life_years=5730,
                time_scale="archaeological_time",
                use="radiocarbon_dating",
            )

        self.assertNotIn(
            "carbon_14_decay",
            process.decay_patterns,
        )

    def test_prepared_local_registry_is_not_rebuilt(
        self
    ):
        universe = Universe()
        process = RadioactiveDecay(universe)

        process.ensure_isotopes()

        registry = process.isotopes_layer.isotopes
        carbon = registry["carbon_14"]

        universe.world.pop(
            "known_isotopes",
            None,
        )

        process.isotopes_layer.form_reference_isotopes = Mock(
            side_effect=AssertionError(
                "Prepared isotope registry rebuilt"
            )
        )

        process.ensure_isotopes()

        process.isotopes_layer.form_reference_isotopes.assert_not_called()

        self.assertIs(
            process.isotopes_layer.isotopes,
            registry,
        )

        self.assertIs(
            registry["carbon_14"],
            carbon,
        )

    def test_runtime_does_not_read_world_isotopes(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key == "known_isotopes":
                    raise AssertionError(
                        "RadioactiveDecay must not "
                        "read public isotope registry"
                    )

                return super().get(
                    key,
                    default,
                )

        universe = Universe()

        universe.world = GuardedWorld(
            universe.world
        )

        process = RadioactiveDecay(universe)

        result = process.define_reference_decay()

        self.assertIs(
            result.state,
            RadioactiveDecayProcessState.DEFINED,
        )

        self.assertEqual(
            len(process.decay_patterns),
            4,
        )

        self.assertIs(
            universe.world["known_isotopes"],
            process.isotopes_layer.isotopes,
        )

        self.assertTrue(
            process.decay_state.radioactive_decay_available
        )

    def test_history_and_public_exports_remain_intact(
        self
    ):
        universe = Universe()
        process = RadioactiveDecay(universe)

        result = process.define_reference_decay()

        self.assertIs(
            universe.world["decay_patterns"],
            process.decay_patterns,
        )

        self.assertIs(
            universe.world["decay_state"],
            process.decay_state,
        )

        self.assertTrue(
            process.decay_state.radiocarbon_time_available
        )

        self.assertTrue(
            process.decay_state.geological_time_available
        )

        history = universe.world["cosmic_history"]

        self.assertIsInstance(
            history[-1],
            CosmicHistoryEvent,
        )

        self.assertEqual(
            history[-1].name,
            "radioactive_decay_patterns_recorded",
        )

        snapshot = result.to_dict()

        snapshot["decay_patterns"][
            "carbon_14_decay"
        ]["half_life_years"] = 1

        self.assertEqual(
            process.decay_patterns[
                "carbon_14_decay"
            ].half_life_years,
            5730,
        )

    def test_repeated_definition_reuses_local_isotopes(
        self
    ):
        process = RadioactiveDecay(Universe())

        first = process.define_reference_decay()

        registry = process.isotopes_layer.isotopes
        carbon = registry["carbon_14"]

        process.isotopes_layer.form_reference_isotopes = Mock(
            side_effect=AssertionError(
                "Canonical isotopes rebuilt"
            )
        )

        second = process.define_reference_decay()

        process.isotopes_layer.form_reference_isotopes.assert_not_called()

        self.assertIs(
            process.isotopes_layer.isotopes,
            registry,
        )

        self.assertIs(
            registry["carbon_14"],
            carbon,
        )

        self.assertIs(
            first.state,
            RadioactiveDecayProcessState.DEFINED,
        )

        self.assertIs(
            second.state,
            RadioactiveDecayProcessState.DEFINED,
        )

        self.assertEqual(
            len(second.decay_patterns),
            4,
        )

        self.assertEqual(
            process.decay_state.decay_pattern_count,
            4,
        )


if __name__ == "__main__":
    unittest.main()
