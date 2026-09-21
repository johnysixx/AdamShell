import unittest

from universe.atomic_time import AtomicTime
from universe.chemical_objects import Isotope
from universe.atomic_time_state import AtomicTimeState
from universe.universe import Universe


class AtomicTimeObjectStateTests(
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

    def _defined_atomic_time(self):
        universe = Universe()
        process = AtomicTime(universe)
        result = process.define_si_second()

        return universe, process, result

    def test_atomic_time_state_is_object_only(self):
        state = AtomicTimeState()

        self._assert_object_only(
            state,
            "si_second_defined",
        )

    def test_initial_values_are_preserved(self):
        state = AtomicTimeState()

        self.assertFalse(state.isotopes_available)
        self.assertFalse(state.caesium_133_available)
        self.assertFalse(state.si_second_defined)
        self.assertFalse(
            state.precision_time_available
        )

    def test_definition_mutates_same_state_object(
        self
    ):
        universe = Universe()
        process = AtomicTime(universe)
        state = process.atomic_time_state

        process.define_si_second()

        self.assertIs(process.atomic_time_state, state)
        self.assertTrue(state.isotopes_available)
        self.assertTrue(state.caesium_133_available)
        self.assertTrue(state.si_second_defined)
        self.assertTrue(
            state.precision_time_available
        )

    def test_world_registry_stores_state_object(
        self
    ):
        universe, process, _ = (
            self._defined_atomic_time()
        )

        state = universe.world["atomic_time_state"]
        self.assertIsInstance(state, AtomicTimeState)
        self.assertIs(state, process.atomic_time_state)
        self.assertIsInstance(
            universe.world["time_standards"],
            dict,
        )
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._defined_atomic_time()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["atomic_time_state"],
            dict,
        )
        self.assertIsInstance(
            result["time_standards"],
            dict,
        )
        self.assertTrue(
            result["atomic_time_state"][
                "si_second_defined"
            ]
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = (
            self._defined_atomic_time()
        )

        result["atomic_time_state"][
            "si_second_defined"
        ] = False
        result["time_standards"]["si_second"][
            "isotope"
        ]["state"] = "changed"

        self.assertTrue(
            process.atomic_time_state.si_second_defined
        )
        live_isotope = process.time_standards[
            "si_second"
        ]["isotope"]

        self.assertIsInstance(
            live_isotope,
            Isotope,
        )
        self.assertEqual(
            live_isotope.state,
            "formed",
        )
        self.assertIsInstance(
            result["time_standards"]["si_second"][
                "isotope"
            ],
            dict,
        )

    def test_definition_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        process = AtomicTime(universe)

        def broken_isotopes():
            raise RuntimeError(
                "atomic time exploded"
            )

        process.ensure_isotopes = broken_isotopes

        result = process.define_si_second()
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
            "atomic_time",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "define_si_second",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "atomic time exploded",
        )

    def test_missing_caesium_behavior_is_preserved(
        self
    ):
        universe = Universe()
        process = AtomicTime(universe)

        process.ensure_isotopes = lambda: None

        result = process.define_si_second()

        self.assertEqual(result["state"], "failed")
        self.assertFalse(
            result["atomic_time_state"][
                "si_second_defined"
            ]
        )
        self.assertIs(
            universe.world["atomic_time_state"],
            process.atomic_time_state,
        )

    def test_to_dict_is_detached_boundary(self):
        state = AtomicTimeState()
        state.si_second_defined = True

        snapshot = state.to_dict()
        snapshot["si_second_defined"] = False

        self.assertTrue(state.si_second_defined)


if __name__ == "__main__":
    unittest.main()
