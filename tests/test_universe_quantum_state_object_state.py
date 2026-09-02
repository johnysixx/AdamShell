import unittest

from universe.quantum_state import (
    UniverseQuantumState
)
from universe.universe import Universe


class UniverseQuantumStateObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(self, value):
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
            _ = value["tick_count"]

    def test_quantum_state_is_object_only(
        self
    ):
        universe = Universe()

        self.assertIsInstance(
            universe.quantum_state,
            UniverseQuantumState,
        )
        self._assert_object_only(
            universe.quantum_state
        )

    def test_initial_state_is_preserved(
        self
    ):
        state = Universe().quantum_state

        self.assertFalse(state.enabled)
        self.assertFalse(state.superposition)
        self.assertIsNone(state.observer)
        self.assertFalse(state.collapsed)
        self.assertEqual(state.tick_count, 0)
        self.assertEqual(state.collapse_count, 0)
        self.assertIsNone(
            state.last_collapse_tick
        )
        self.assertEqual(state.uncertainty, 0.0)
        self.assertEqual(state.fluctuation, 0.0)
        self.assertEqual(state.entropy_delta, 0.0)
        self.assertEqual(state.entropy_total, 0.0)

    def test_enabling_keeps_same_state_object(
        self
    ):
        universe = Universe()
        state = universe.quantum_state

        universe.enable_quantum_layer()

        self.assertIs(
            universe.quantum_state,
            state,
        )
        self.assertTrue(state.enabled)

    def test_quantum_ticks_mutate_attributes(
        self
    ):
        universe = Universe()
        universe.enable_quantum_layer()
        state = universe.quantum_state

        universe.tick_quantum_unprotected()
        universe.tick_quantum_unprotected()

        self.assertIs(
            universe.quantum_state,
            state,
        )
        self.assertEqual(state.tick_count, 2)
        self.assertFalse(state.superposition)
        self.assertTrue(state.collapsed)
        self.assertEqual(
            state.observer,
            "quantum_tick",
        )
        self.assertEqual(state.collapse_count, 2)
        self.assertEqual(
            state.last_collapse_tick,
            2,
        )
        self.assertAlmostEqual(
            state.fluctuation,
            0.02,
        )
        self.assertAlmostEqual(
            state.uncertainty,
            0.01,
        )
        self.assertAlmostEqual(
            state.entropy_delta,
            0.001,
        )
        self.assertAlmostEqual(
            state.entropy_total,
            0.0015,
        )

    def test_to_dict_returns_detached_snapshot(
        self
    ):
        state = UniverseQuantumState()
        state.enable()
        state.advance_tick()

        snapshot = state.to_dict()

        self.assertIsInstance(snapshot, dict)
        snapshot["enabled"] = False
        snapshot["tick_count"] = 99

        self.assertTrue(state.enabled)
        self.assertEqual(state.tick_count, 1)

    def test_universe_history_remains_boundary_dict(
        self
    ):
        universe = Universe()
        universe.enable_quantum_layer()
        universe.tick_quantum_unprotected()

        universe.record_universe_state()
        snapshot = universe.universe_history[-1]

        self.assertIsInstance(snapshot, dict)
        self.assertEqual(
            snapshot["quantum_fluctuation"],
            universe.quantum_state.fluctuation,
        )
        snapshot["quantum_fluctuation"] = 99.0

        self.assertAlmostEqual(
            universe.quantum_state.fluctuation,
            0.01,
        )


if __name__ == "__main__":
    unittest.main()
