import unittest

from universe.atomic_time import AtomicTime
from universe.chemical_objects import Isotope
from universe.atomic_time_state import AtomicTimeState
from universe.atomic_time_process_state import (
    AtomicTimeProcessState,
)
from universe.physical_time_result_state import (
    AtomicTimeDefinitionResult,
)
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

    def test_world_keeps_snapshot_without_live_state(
        self
    ):
        universe, process, _ = (
            self._defined_atomic_time()
        )

        state = process.atomic_time_state

        self.assertNotIn(
            "atomic_time_state",
            universe.world,
        )
        self.assertIsInstance(
            state,
            AtomicTimeState,
        )
        self.assertIs(
            process.result.atomic_time_state,
            state,
        )
        self.assertIsInstance(
            universe.world["atomic_time"],
            dict,
        )
        self.assertIsInstance(
            universe.world["atomic_time"][
                "atomic_time_state"
            ],
            dict,
        )
        self.assertNotIn(
            "time_standards",
            universe.world,
        )
        self.assertIsInstance(
            process.time_standards,
            dict,
        )
        self.assertIs(
            process.result.time_standards["si_second"],
            process.time_standards["si_second"],
        )
        self.assertIsInstance(
            universe.world["atomic_time"]["time_standards"],
            dict,
        )
        self.assertIsInstance(universe.world, dict)

    def test_runtime_result_is_object_and_snapshot_is_dict(
        self
    ):
        _, process, result = self._defined_atomic_time()

        self.assertIsInstance(
            result,
            AtomicTimeDefinitionResult,
        )
        self._assert_object_only(
            result,
            "state",
        )
        self.assertIs(
            result.atomic_time_state,
            process.atomic_time_state,
        )
        self.assertIs(
            result.time_standards["si_second"],
            process.time_standards["si_second"],
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["atomic_time_state"],
            dict,
        )
        self.assertIsInstance(
            snapshot["time_standards"],
            dict,
        )
        self.assertTrue(
            snapshot["atomic_time_state"][
                "si_second_defined"
            ]
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = (
            self._defined_atomic_time()
        )

        snapshot = result.to_dict()

        snapshot["atomic_time_state"][
            "si_second_defined"
        ] = False
        snapshot["time_standards"]["si_second"][
            "isotope"
        ]["state"] = "changed"

        self.assertTrue(
            process.atomic_time_state.si_second_defined
        )
        live_isotope = process.time_standards[
            "si_second"
        ].isotope

        self.assertIsInstance(
            live_isotope,
            Isotope,
        )
        self.assertEqual(
            live_isotope.state,
            "formed",
        )
        self.assertIsInstance(
            snapshot["time_standards"]["si_second"][
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
        cronenberg = result.cronenberg

        self.assertEqual(
            result.type,
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

        self.assertIsInstance(
            result,
            AtomicTimeDefinitionResult,
        )
        self.assertIs(
            result.state,
            AtomicTimeProcessState.FAILED,
        )
        self.assertFalse(
            result.atomic_time_state.si_second_defined
        )

        snapshot = result.to_dict()

        self.assertEqual(
            snapshot["state"],
            "failed",
        )
        self.assertNotIn(
            "atomic_time_state",
            universe.world,
        )
        self.assertIs(
            result.atomic_time_state,
            process.atomic_time_state,
        )
        self.assertIsInstance(
            universe.world["atomic_time"][
                "atomic_time_state"
            ],
            dict,
        )

    def test_to_dict_is_detached_boundary(self):
        state = AtomicTimeState()
        state.si_second_defined = True

        snapshot = state.to_dict()
        snapshot["si_second_defined"] = False

        self.assertTrue(state.si_second_defined)


if __name__ == "__main__":
    unittest.main()
