import unittest

from universe.decay_state import RadioactiveDecayState
from universe.radioactive_decay import RadioactiveDecay
from universe.universe import Universe


class RadioactiveDecayObjectStateTests(
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

    def _defined_decay(self):
        universe = Universe()
        process = RadioactiveDecay(universe)
        result = process.define_reference_decay()

        return universe, process, result

    def test_decay_state_is_object_only(self):
        state = RadioactiveDecayState()

        self._assert_object_only(
            state,
            "decay_pattern_count",
        )

    def test_initial_values_are_preserved(self):
        state = RadioactiveDecayState()

        self.assertFalse(state.isotopes_available)
        self.assertFalse(
            state.radioactive_decay_available
        )
        self.assertFalse(
            state.radiocarbon_time_available
        )
        self.assertFalse(
            state.geological_time_available
        )
        self.assertEqual(state.decay_pattern_count, 0)

    def test_definition_mutates_same_state_object(
        self
    ):
        universe = Universe()
        process = RadioactiveDecay(universe)
        state = process.decay_state

        process.define_reference_decay()

        self.assertIs(process.decay_state, state)
        self.assertTrue(state.isotopes_available)
        self.assertTrue(
            state.radioactive_decay_available
        )
        self.assertTrue(
            state.radiocarbon_time_available
        )
        self.assertTrue(
            state.geological_time_available
        )
        self.assertEqual(state.decay_pattern_count, 4)

    def test_world_registry_stores_state_object(
        self
    ):
        universe, process, _ = self._defined_decay()

        state = universe.world["decay_state"]
        self.assertIsInstance(
            state,
            RadioactiveDecayState,
        )
        self.assertIs(state, process.decay_state)
        self.assertIsInstance(
            universe.world["decay_patterns"],
            dict,
        )
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._defined_decay()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["decay_state"],
            dict,
        )
        self.assertIsInstance(
            result["decay_patterns"],
            dict,
        )
        self.assertEqual(
            result["decay_state"][
                "decay_pattern_count"
            ],
            4,
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._defined_decay()

        result["decay_state"][
            "decay_pattern_count"
        ] = 99
        result["decay_patterns"][
            "carbon_14_decay"
        ]["state"] = "changed"

        self.assertEqual(
            process.decay_state.decay_pattern_count,
            4,
        )
        self.assertEqual(
            process.decay_patterns[
                "carbon_14_decay"
            ]["state"],
            "available",
        )

    def test_definition_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        process = RadioactiveDecay(universe)

        def broken_pattern(*args, **kwargs):
            raise RuntimeError(
                "radioactive decay exploded"
            )

        process.create_decay_pattern = broken_pattern

        result = process.define_reference_decay()
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
            "radioactive_decay",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "define_reference_decay",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "radioactive decay exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = RadioactiveDecayState()
        state.decay_pattern_count = 4

        snapshot = state.to_dict()
        snapshot["decay_pattern_count"] = 99

        self.assertEqual(
            state.decay_pattern_count,
            4,
        )


if __name__ == "__main__":
    unittest.main()
