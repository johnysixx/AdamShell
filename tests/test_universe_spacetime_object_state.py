import unittest

from universe.spacetime import (
    UniverseSpacetimeSpaceAxis,
    UniverseSpacetimeState,
    UniverseSpacetimeTimeAxis,
)
from universe.universe import Universe


class UniverseSpacetimeObjectStateTests(
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

    def test_world_registry_stores_object_state(
        self
    ):
        universe = Universe()
        universe.bind_spacetime()
        spacetime = universe.world["spacetime"]

        self.assertIsInstance(universe.world, dict)
        self.assertIsInstance(
            spacetime,
            UniverseSpacetimeState,
        )
        self._assert_object_only(
            spacetime,
            "curvature",
        )

    def test_axes_are_object_only(
        self
    ):
        spacetime = UniverseSpacetimeState()

        self.assertIsInstance(
            spacetime.time_axis,
            UniverseSpacetimeTimeAxis,
        )
        self.assertIsInstance(
            spacetime.space_axis,
            UniverseSpacetimeSpaceAxis,
        )
        self._assert_object_only(
            spacetime.time_axis,
            "tick",
        )
        self._assert_object_only(
            spacetime.space_axis,
            "dimensions",
        )

    def test_initial_state_is_preserved(
        self
    ):
        spacetime = UniverseSpacetimeState()

        self.assertTrue(spacetime.linked)
        self.assertEqual(spacetime.curvature, 0.0)
        self.assertEqual(spacetime.time_axis.tick, 0)
        self.assertEqual(spacetime.time_axis.flow, 1.0)
        self.assertEqual(
            spacetime.time_axis.state,
            "global",
        )
        self.assertEqual(
            spacetime.space_axis.dimensions,
            3,
        )
        self.assertEqual(
            spacetime.space_axis.state,
            "global",
        )
        self.assertTrue(
            spacetime.space_axis.expanded
        )

    def test_tick_mutates_same_aggregate(
        self
    ):
        universe = Universe()
        universe.enable_physics("gravity")
        universe.bind_spacetime()
        spacetime = universe.world["spacetime"]
        time_axis = spacetime.time_axis

        universe.tick_spacetime()
        universe.tick_spacetime()

        self.assertIs(
            universe.world["spacetime"],
            spacetime,
        )
        self.assertIs(
            spacetime.time_axis,
            time_axis,
        )
        self.assertEqual(time_axis.tick, 2)
        self.assertAlmostEqual(
            spacetime.curvature,
            0.02,
        )

    def test_disabled_gravity_still_ticks_time(
        self
    ):
        universe = Universe()
        universe.enable_physics("gravity")
        universe.physics["gravity"].enabled = False
        universe.bind_spacetime()

        universe.tick_spacetime()
        spacetime = universe.world["spacetime"]

        self.assertEqual(spacetime.time_axis.tick, 1)
        self.assertEqual(spacetime.curvature, 0.0)

    def test_to_dict_is_deeply_detached(
        self
    ):
        spacetime = UniverseSpacetimeState()
        spacetime.advance(0.01)
        snapshot = spacetime.to_dict()

        self.assertIsInstance(snapshot, dict)
        self.assertIsInstance(
            snapshot["time_axis"],
            dict,
        )
        self.assertIsInstance(
            snapshot["space_axis"],
            dict,
        )
        snapshot["curvature"] = 99.0
        snapshot["time_axis"]["tick"] = 99
        snapshot["space_axis"][
            "dimensions"
        ] = 99

        self.assertAlmostEqual(
            spacetime.curvature,
            0.01,
        )
        self.assertEqual(spacetime.time_axis.tick, 1)
        self.assertEqual(
            spacetime.space_axis.dimensions,
            3,
        )

    def test_history_remains_boundary_dict(
        self
    ):
        universe = Universe()
        universe.enable_physics("gravity")
        universe.bind_spacetime()
        universe.tick_spacetime()

        universe.record_universe_state()
        snapshot = universe.universe_history[-1]

        self.assertIsInstance(snapshot, dict)
        self.assertAlmostEqual(
            snapshot["curvature"],
            0.01,
        )
        snapshot["curvature"] = 99.0

        self.assertAlmostEqual(
            universe.world[
                "spacetime"
            ].curvature,
            0.01,
        )


if __name__ == "__main__":
    unittest.main()
