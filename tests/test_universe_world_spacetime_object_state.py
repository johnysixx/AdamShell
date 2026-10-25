import unittest

from universe.spacetime import UniverseSpacetimeState
from universe.universe import Universe
from universe.universe_history_state import (
    UniverseHistorySnapshot,
)


class UniverseWorldSpacetimeObjectStateTests(
    unittest.TestCase
):

    def test_binding_creates_canonical_object(self):
        universe = Universe()

        self.assertIsNone(universe.spacetime)
        self.assertNotIn(
            "spacetime",
            universe.world,
        )

        universe.bind_spacetime()

        self.assertIsInstance(
            universe.spacetime,
            UniverseSpacetimeState,
        )

        self.assertIs(
            universe.world["spacetime"],
            universe.spacetime,
        )

        self.assertEqual(
            universe.spacetime.curvature,
            0.0,
        )

    def test_world_record_cannot_bind_spacetime(self):
        universe = Universe()

        decoy = UniverseSpacetimeState(
            curvature=50.0,
        )

        universe.world["spacetime"] = decoy

        universe.tick_spacetime()
        universe.update_physics()
        universe.record_universe_state()

        self.assertIsNone(universe.spacetime)

        self.assertEqual(
            decoy.time_axis.tick,
            0,
        )

        self.assertEqual(
            universe.pressure,
            0.0,
        )

        self.assertEqual(
            universe.universe_history[-1].curvature,
            0.0,
        )

    def test_pressure_uses_canonical_curvature(self):
        universe = Universe()
        universe.bind_spacetime()

        canonical = universe.spacetime

        canonical.curvature = 0.25

        universe.world["spacetime"] = (
            UniverseSpacetimeState(
                curvature=100.0,
            )
        )

        universe.update_physics()

        self.assertAlmostEqual(
            universe.pressure,
            0.25,
        )

        self.assertAlmostEqual(
            universe.last_pressure_cost,
            0.025,
        )

        self.assertAlmostEqual(
            universe.last_energy_gain,
            0.05,
        )

        self.assertAlmostEqual(
            universe.last_energy_delta,
            0.025,
        )

        self.assertAlmostEqual(
            universe.energy_pool,
            100.025,
        )

        self.assertIs(
            universe.spacetime,
            canonical,
        )

    def test_spacetime_tick_uses_canonical_object(
        self
    ):
        universe = Universe()

        universe.enable_physics("gravity")
        universe.bind_spacetime()

        canonical = universe.spacetime

        decoy = UniverseSpacetimeState(
            curvature=500.0,
        )

        universe.world["spacetime"] = decoy

        universe.tick_spacetime()

        self.assertEqual(
            canonical.time_axis.tick,
            1,
        )

        self.assertAlmostEqual(
            canonical.curvature,
            0.01,
        )

        self.assertEqual(
            decoy.time_axis.tick,
            0,
        )

        self.assertEqual(
            decoy.curvature,
            500.0,
        )

    def test_history_reads_canonical_curvature(self):
        universe = Universe()
        universe.bind_spacetime()

        universe.spacetime.curvature = 0.75

        universe.world["spacetime"] = (
            UniverseSpacetimeState(
                curvature=-2.0,
            )
        )

        universe.record_universe_state()

        record = universe.universe_history[-1]

        self.assertIsInstance(
            record,
            UniverseHistorySnapshot,
        )

        self.assertAlmostEqual(
            record.curvature,
            0.75,
        )

        exported = record.to_dict()

        self.assertAlmostEqual(
            exported["curvature"],
            0.75,
        )

    def test_rebinding_replaces_canonical_object(
        self
    ):
        universe = Universe()
        universe.bind_spacetime()

        first = universe.spacetime
        first.advance(0.5)

        universe.bind_spacetime()

        second = universe.spacetime

        self.assertIsNot(first, second)

        self.assertIs(
            universe.world["spacetime"],
            second,
        )

        self.assertEqual(
            first.time_axis.tick,
            1,
        )

        self.assertEqual(
            second.time_axis.tick,
            0,
        )

        self.assertEqual(
            second.curvature,
            0.0,
        )

    def test_full_tick_uses_canonical_spacetime(
        self
    ):
        universe = Universe()

        universe.enable_physics("gravity")
        universe.bind_spacetime()

        report = universe.tick_universe()

        self.assertEqual(report.tick, 1)

        self.assertEqual(
            universe.spacetime.time_axis.tick,
            1,
        )

        self.assertAlmostEqual(
            universe.spacetime.curvature,
            0.01,
        )

        self.assertAlmostEqual(
            universe.pressure,
            0.01,
        )

        self.assertAlmostEqual(
            universe.universe_history[-1].curvature,
            0.01,
        )

        self.assertAlmostEqual(
            universe.universe_history[-1].pressure,
            0.01,
        )

        self.assertTrue(report.ok)

    def test_runtime_operations_do_not_read_world(
        self
    ):
        class GuardedWorld(dict):

            def __getitem__(self, key):
                if key == "spacetime":
                    raise AssertionError(
                        "World spacetime read forbidden."
                    )
                return super().__getitem__(key)

            def __contains__(self, key):
                if key == "spacetime":
                    raise AssertionError(
                        "World spacetime lookup forbidden."
                    )
                return super().__contains__(key)

            def get(self, key, default=None):
                if key == "spacetime":
                    raise AssertionError(
                        "World spacetime get forbidden."
                    )
                return super().get(key, default)

        universe = Universe()

        universe.enable_physics("gravity")
        universe.bind_spacetime()

        universe.world = GuardedWorld(
            universe.world
        )

        universe.spacetime.curvature = 0.2

        universe.tick_spacetime()
        universe.update_physics()
        universe.record_universe_state()

        self.assertAlmostEqual(
            universe.spacetime.curvature,
            0.21,
        )

        self.assertAlmostEqual(
            universe.pressure,
            0.21,
        )

        self.assertAlmostEqual(
            universe.universe_history[-1].curvature,
            0.21,
        )


if __name__ == "__main__":
    unittest.main()
