import unittest

from universe.physics_state import (
    UniverseGravityState,
    UniverseTimeState,
)
from universe.universe import Universe


class UniversePhysicsStateObjectStateTests(
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

    def test_time_state_is_object_only(
        self
    ):
        universe = Universe()
        universe.enable_physics("time")
        time_state = universe.physics["time"]

        self.assertIsInstance(
            time_state,
            UniverseTimeState,
        )
        self._assert_object_only(
            time_state,
            "tick",
        )

    def test_time_initial_values_are_preserved(
        self
    ):
        state = UniverseTimeState()

        self.assertEqual(state.tick, 0)
        self.assertEqual(state.flow, 1.0)
        self.assertEqual(state.state, "linear")
        self.assertEqual(state.pressure, 0.0)

    def test_time_ticks_mutate_same_object(
        self
    ):
        universe = Universe()
        universe.enable_physics("time")
        time_state = universe.physics["time"]

        universe.tick_time()
        universe.tick_time()

        self.assertIs(
            universe.physics["time"],
            time_state,
        )
        self.assertEqual(time_state.tick, 2)
        self.assertAlmostEqual(
            time_state.pressure,
            0.2,
        )
        self.assertAlmostEqual(
            universe.energy_pool,
            99.97,
        )
        self.assertEqual(universe.get_time(), 2)

    def test_reenabling_time_resets_state(
        self
    ):
        universe = Universe()
        universe.enable_physics("time")
        first = universe.physics["time"]
        universe.tick_time()

        universe.enable_physics("time")
        second = universe.physics["time"]

        self.assertIsNot(first, second)
        self.assertEqual(second.tick, 0)
        self.assertEqual(second.pressure, 0.0)

    def test_time_snapshot_is_detached_dict(
        self
    ):
        state = UniverseTimeState()
        state.advance()
        snapshot = state.to_dict()

        self.assertIsInstance(snapshot, dict)
        snapshot["tick"] = 99
        snapshot["pressure"] = 99.0

        self.assertEqual(state.tick, 1)
        self.assertAlmostEqual(
            state.pressure,
            0.1,
        )

    def test_gravity_state_is_object_only(
        self
    ):
        universe = Universe()
        universe.enable_physics("gravity")
        gravity = universe.physics["gravity"]

        self.assertIsInstance(
            gravity,
            UniverseGravityState,
        )
        self._assert_object_only(
            gravity,
            "strength",
        )
        self.assertTrue(gravity.enabled)
        self.assertEqual(gravity.strength, 1.0)
        self.assertEqual(
            gravity.curvature_effect,
            0.01,
        )

    def test_gravity_updates_dict_boundary(
        self
    ):
        universe = Universe()
        universe.enable_physics("gravity")
        gravity = universe.physics["gravity"]
        universe.bind_spacetime()

        universe.tick_spacetime()

        spacetime = universe.world["spacetime"]
        self.assertIsInstance(spacetime, dict)
        self.assertEqual(
            spacetime["time_axis"]["tick"],
            1,
        )
        self.assertAlmostEqual(
            spacetime["curvature"],
            0.01,
        )
        self.assertAlmostEqual(
            gravity.curvature_delta,
            0.01,
        )

    def test_gravity_snapshot_is_detached_dict(
        self
    ):
        gravity = UniverseGravityState()
        snapshot = gravity.to_dict()

        self.assertIsInstance(snapshot, dict)
        snapshot["enabled"] = False
        snapshot["strength"] = 99.0

        self.assertTrue(gravity.enabled)
        self.assertEqual(gravity.strength, 1.0)


if __name__ == "__main__":
    unittest.main()
