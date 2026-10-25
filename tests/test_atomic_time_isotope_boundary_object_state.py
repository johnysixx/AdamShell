import unittest
from unittest.mock import Mock

from universe.atomic_time import AtomicTime
from universe.atomic_time_process_state import (
    AtomicTimeProcessState,
)
from universe.chemical_objects import Isotope
from universe.physical_record_state import (
    AtomicTimeStandard,
)
from universe.physical_time_result_state import (
    AtomicTimeDefinitionResult,
)
from universe.universe import Universe


class AtomicTimeIsotopeBoundaryObjectStateTests(
    unittest.TestCase
):

    def test_world_decoy_does_not_skip_local_formation(
        self
    ):
        universe = Universe()

        universe.world["known_isotopes"] = {
            "caesium_133": object(),
        }

        process = AtomicTime(universe)

        process.ensure_isotopes()

        isotopes = process.isotopes_layer.isotopes

        self.assertEqual(len(isotopes), 8)

        self.assertIsInstance(
            isotopes["caesium_133"],
            Isotope,
        )

        self.assertIs(
            universe.world["known_isotopes"],
            isotopes,
        )

        self.assertTrue(
            process.atomic_time_state.isotopes_available
        )

    def test_si_second_uses_canonical_caesium_object(
        self
    ):
        universe = Universe()
        process = AtomicTime(universe)

        result = process.define_si_second()

        self.assertIsInstance(
            result,
            AtomicTimeDefinitionResult,
        )

        self.assertIs(
            result.state,
            AtomicTimeProcessState.DEFINED,
        )

        caesium = (
            process.isotopes_layer
            .isotopes["caesium_133"]
        )

        standard = process.time_standards[
            "si_second"
        ]

        self.assertIsInstance(
            standard,
            AtomicTimeStandard,
        )

        self.assertIs(standard.isotope, caesium)

        self.assertEqual(
            standard.frequency_hz,
            9_192_631_770,
        )

        self.assertIs(
            result.time_standards["si_second"],
            standard,
        )

    def test_external_registry_cannot_replace_caesium(
        self
    ):
        universe = Universe()
        process = AtomicTime(universe)

        process.ensure_isotopes()

        caesium = (
            process.isotopes_layer
            .isotopes["caesium_133"]
        )

        universe.world["known_isotopes"] = {
            "caesium_133": object(),
        }

        result = process.define_si_second()

        self.assertIs(
            result.state,
            AtomicTimeProcessState.DEFINED,
        )

        self.assertIs(
            process.time_standards[
                "si_second"
            ].isotope,
            caesium,
        )

        self.assertTrue(
            process.atomic_time_state.si_second_defined
        )

    def test_missing_local_caesium_still_fails(
        self
    ):
        universe = Universe()
        process = AtomicTime(universe)

        process.ensure_isotopes()

        caesium = (
            process.isotopes_layer
            .isotopes.pop("caesium_133")
        )

        self.assertTrue(
            process.isotopes_layer.isotopes
        )

        universe.world["known_isotopes"] = {
            "caesium_133": caesium,
        }

        result = process.define_si_second()

        self.assertIsInstance(
            result,
            AtomicTimeDefinitionResult,
        )

        self.assertIs(
            result.state,
            AtomicTimeProcessState.FAILED,
        )

        self.assertFalse(
            process.atomic_time_state.si_second_defined
        )

        self.assertFalse(
            process.atomic_time_state.caesium_133_available
        )

        self.assertNotIn(
            "si_second",
            process.time_standards,
        )

    def test_prepared_local_isotopes_are_not_rebuilt(
        self
    ):
        universe = Universe()
        process = AtomicTime(universe)

        process.ensure_isotopes()

        canonical = process.isotopes_layer.isotopes
        caesium = canonical["caesium_133"]

        universe.world.pop(
            "known_isotopes",
            None,
        )

        process.isotopes_layer.form_reference_isotopes = Mock(
            side_effect=AssertionError(
                "Canonical isotopes must not rebuild"
            )
        )

        process.ensure_isotopes()

        process.isotopes_layer.form_reference_isotopes.assert_not_called()

        self.assertIs(
            process.isotopes_layer.isotopes,
            canonical,
        )

        self.assertIs(
            canonical["caesium_133"],
            caesium,
        )

    def test_runtime_does_not_read_world_isotopes(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key == "known_isotopes":
                    raise AssertionError(
                        "AtomicTime must use its "
                        "canonical isotope layer."
                    )

                return super().get(
                    key,
                    default,
                )

        universe = Universe()

        universe.world = GuardedWorld(
            universe.world
        )

        process = AtomicTime(universe)

        result = process.define_si_second()

        self.assertIs(
            result.state,
            AtomicTimeProcessState.DEFINED,
        )

        self.assertIs(
            process.time_standards[
                "si_second"
            ].isotope,
            process.isotopes_layer.isotopes[
                "caesium_133"
            ],
        )

        self.assertIs(
            universe.world["known_isotopes"],
            process.isotopes_layer.isotopes,
        )

    def test_public_standard_export_is_detached(
        self
    ):
        process = AtomicTime(Universe())

        result = process.define_si_second()

        standard = process.time_standards[
            "si_second"
        ]

        snapshot = result.to_dict()

        exported = snapshot[
            "time_standards"
        ]["si_second"]

        self.assertEqual(
            exported["frequency_hz"],
            9_192_631_770,
        )

        self.assertIsInstance(
            exported["isotope"],
            dict,
        )

        exported["frequency_hz"] = 1

        exported["isotope"]["state"] = (
            "changed"
        )

        self.assertEqual(
            standard.frequency_hz,
            9_192_631_770,
        )

        self.assertEqual(
            standard.isotope.state,
            "formed",
        )

    def test_repeated_definition_keeps_isotope_identity(
        self
    ):
        process = AtomicTime(Universe())

        first = process.define_si_second()

        first_isotope = (
            first.time_standards[
                "si_second"
            ].isotope
        )

        second = process.define_si_second()

        second_isotope = (
            second.time_standards[
                "si_second"
            ].isotope
        )

        self.assertIs(
            first_isotope,
            second_isotope,
        )

        self.assertIs(
            second_isotope,
            process.isotopes_layer.isotopes[
                "caesium_133"
            ],
        )

        self.assertIs(
            second.state,
            AtomicTimeProcessState.DEFINED,
        )

        self.assertEqual(
            len(process.isotopes_layer.isotopes),
            8,
        )


if __name__ == "__main__":
    unittest.main()
