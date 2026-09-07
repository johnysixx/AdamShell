import unittest

from universe.isotope_state import (
    IsotopeFormationState,
)
from universe.isotopes import Isotopes
from universe.universe import Universe


class IsotopeFormationObjectStateTests(
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

    def _formed_isotopes(self):
        universe = Universe()
        process = Isotopes(universe)
        result = process.form_reference_isotopes()

        return universe, process, result

    def test_isotope_state_is_object_only(self):
        state = IsotopeFormationState()

        self._assert_object_only(
            state,
            "isotope_count",
        )

    def test_initial_values_are_preserved(self):
        state = IsotopeFormationState()

        self.assertFalse(
            state.periodic_table_available
        )
        self.assertFalse(
            state.reference_isotopes_available
        )
        self.assertFalse(
            state.radioactive_isotopes_available
        )
        self.assertFalse(
            state.atomic_time_isotope_available
        )
        self.assertEqual(state.isotope_count, 0)

    def test_formation_mutates_same_state_object(
        self
    ):
        universe = Universe()
        process = Isotopes(universe)
        state = process.isotope_state

        process.form_reference_isotopes()

        self.assertIs(process.isotope_state, state)
        self.assertTrue(
            state.periodic_table_available
        )
        self.assertTrue(
            state.reference_isotopes_available
        )
        self.assertTrue(
            state.radioactive_isotopes_available
        )
        self.assertTrue(
            state.atomic_time_isotope_available
        )
        self.assertEqual(state.isotope_count, 8)

    def test_world_registry_stores_state_object(
        self
    ):
        universe, process, _ = (
            self._formed_isotopes()
        )

        state = universe.world["isotope_state"]
        self.assertIsInstance(
            state,
            IsotopeFormationState,
        )
        self.assertIs(state, process.isotope_state)
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._formed_isotopes()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["isotope_state"],
            dict,
        )
        self.assertIsInstance(
            result["isotopes"],
            dict,
        )
        self.assertEqual(
            result["isotope_state"][
                "isotope_count"
            ],
            8,
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_isotopes()

        result["isotope_state"][
            "isotope_count"
        ] = 99
        result["isotopes"]["hydrogen_1"][
            "state"
        ] = "changed"

        self.assertEqual(
            process.isotope_state.isotope_count,
            8,
        )
        self.assertEqual(
            process.isotopes["hydrogen_1"][
                "state"
            ],
            "formed",
        )

    def test_formation_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        process = Isotopes(universe)

        def broken_isotope(*args, **kwargs):
            raise RuntimeError(
                "isotope formation exploded"
            )

        process.create_isotope = broken_isotope

        result = process.form_reference_isotopes()
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
            "isotopes",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_reference_isotopes",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "isotope formation exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = IsotopeFormationState()
        state.isotope_count = 8

        snapshot = state.to_dict()
        snapshot["isotope_count"] = 99

        self.assertEqual(state.isotope_count, 8)


if __name__ == "__main__":
    unittest.main()
