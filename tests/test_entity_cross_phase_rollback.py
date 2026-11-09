import io
import random
import unittest

from contextlib import redirect_stdout
from types import SimpleNamespace

from universe.universe import Universe
from universe.universe_tick_result_state import (
    UniverseTickPhaseErrorResult,
)


class ProbeEntity:
    def __init__(self, name, action):
        self.name = name
        self.type = "a418_cross_phase_probe"
        self.active = True
        self.energy = 10.0
        self.ticks = 0
        self.action = action

    def tick(self, universe):
        self.ticks += 1
        self.action(self, universe)


class EarlierLayer:
    def __init__(self):
        self.calls = 0

    def tick(self):
        self.calls += 1


class EntityCrossPhaseRollbackTests(unittest.TestCase):

    def setUp(self):
        self.addCleanup(
            random.setstate,
            random.getstate(),
        )

    @staticmethod
    def make_world(number, entity=None):
        with redirect_stdout(io.StringIO()):
            world = Universe(
                universe_id=f"a418_cross_phase_{number}"
            )

            if entity is not None:
                world.add_entity(entity)

        return world

    @staticmethod
    def run_tick(world):
        with redirect_stdout(io.StringIO()):
            return world.tick_universe()

    @staticmethod
    def run_entities(world):
        with redirect_stdout(io.StringIO()):
            return world.tick_entities()

    def assert_single_entity_error(
        self,
        world,
        results,
        entity_name,
    ):
        errors = [
            result
            for result in results
            if isinstance(
                result,
                UniverseTickPhaseErrorResult,
            )
        ]

        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0].source_component,
            f"entity:{entity_name}",
        )
        self.assertEqual(
            world.cronenberg_count,
            1,
        )
        self.assertEqual(
            len(world.cronenbergs),
            1,
        )
        self.assertEqual(
            errors[0].cronenberg_id,
            world.cronenbergs[0].id,
        )

    def test_01_biology_commit_survives_entity_failure(self):
        def corrupt(entity, world):
            world.life_cycle_system.day += 7
            world.life_cycle_system.history.append(
                SimpleNamespace(
                    name="a418_partial_day"
                )
            )
            raise RuntimeError(
                "a418 biology corruption"
            )

        entity = ProbeEntity(
            "biology_mutator",
            corrupt,
        )

        world = self.make_world(1, entity)
        world.physical_universe_started = True

        lifecycle = world.life_cycle_system
        lifecycle.handlers = []
        history = lifecycle.history

        report = self.run_tick(world)

        self.assert_single_entity_error(
            world,
            report.phases,
            "biology_mutator",
        )

        self.assertEqual(world.universe_tick, 1)
        self.assertEqual(lifecycle.day, 1)
        self.assertIs(
            world.life_cycle_system,
            lifecycle,
        )
        self.assertIs(
            lifecycle.history,
            history,
        )
        self.assertEqual(len(history), 1)
        self.assertEqual(entity.ticks, 1)
        self.assertEqual(
            len(world.universe_history),
            1,
        )

    def test_02_physical_commit_survives_entity_failure(self):
        def corrupt(entity, world):
            world.entropy += 5.0
            world.pressure += 8.0
            world.energy_pool -= 30.0
            world.universe_tick += 50

            world.spacetime.curvature = 999.0
            world.spacetime.time_axis.tick += 10
            world.physics["gravity"].strength = 999.0

            raise RuntimeError(
                "a418 physics corruption"
            )

        entity = ProbeEntity(
            "physics_mutator",
            corrupt,
        )

        world = self.make_world(2, entity)

        with redirect_stdout(io.StringIO()):
            world.enable_physics("gravity")
            world.bind_spacetime()

            spacetime_phase = world._run_tick_operation(
                phase="spacetime",
                operation=world.tick_spacetime,
                source_component="universe",
                source_operation="tick_spacetime",
            )

            physics_phase = world._run_tick_operation(
                phase="physics",
                operation=world.update_physics,
                source_component="universe",
                source_operation="update_physics",
            )

        self.assertTrue(spacetime_phase.ok)
        self.assertTrue(physics_phase.ok)

        space = world.spacetime
        time_axis = space.time_axis
        gravity = world.physics["gravity"]
        physics = world.physics

        committed_space = space.to_dict()
        committed_gravity = gravity.to_dict()

        committed_scalars = (
            world.entropy,
            world.pressure,
            world.energy_pool,
            world.universe_tick,
            world.classical_entropy_total,
            world.last_classical_entropy_delta,
        )

        results = self.run_entities(world)

        self.assert_single_entity_error(
            world,
            results,
            "physics_mutator",
        )

        current_scalars = (
            world.entropy,
            world.pressure,
            world.energy_pool,
            world.universe_tick,
            world.classical_entropy_total,
            world.last_classical_entropy_delta,
        )

        self.assertEqual(
            current_scalars,
            committed_scalars,
        )
        self.assertEqual(
            space.to_dict(),
            committed_space,
        )
        self.assertEqual(
            gravity.to_dict(),
            committed_gravity,
        )
        self.assertIs(world.spacetime, space)
        self.assertIs(space.time_axis, time_axis)
        self.assertIs(world.physics, physics)
        self.assertIs(
            world.physics["gravity"],
            gravity,
        )
        self.assertEqual(entity.ticks, 1)

    def test_03_entity_failure_restores_canonical_roots(self):
        def corrupt(entity, world):
            world.life_cycle_system = SimpleNamespace(
                day=999,
            )
            world.physics = {
                "gravity": False,
            }
            world.spacetime = SimpleNamespace(
                curvature=999.0,
            )
            world.layers = SimpleNamespace(
                calls=999,
            )

            raise RuntimeError(
                "a418 canonical root corruption"
            )

        entity = ProbeEntity(
            "root_mutator",
            corrupt,
        )

        world = self.make_world(3, entity)

        lifecycle = world.life_cycle_system
        physics = world.physics
        spacetime = world.spacetime

        self.assertFalse(
            hasattr(world, "layers")
        )

        results = self.run_entities(world)

        self.assert_single_entity_error(
            world,
            results,
            "root_mutator",
        )

        self.assertIs(
            world.life_cycle_system,
            lifecycle,
        )
        self.assertIs(world.physics, physics)
        self.assertIs(world.spacetime, spacetime)
        self.assertFalse(
            hasattr(world, "layers")
        )
        self.assertEqual(entity.ticks, 1)

    def test_04_previous_layer_commit_is_preserved(self):
        def corrupt(entity, world):
            world.layers.calls += 100
            raise RuntimeError(
                "a418 earlier layer corruption"
            )

        entity = ProbeEntity(
            "layer_mutator",
            corrupt,
        )

        world = self.make_world(4, entity)
        layer = EarlierLayer()
        world.layers = layer

        report = self.run_tick(world)

        self.assert_single_entity_error(
            world,
            report.phases,
            "layer_mutator",
        )

        layer_results = [
            phase
            for phase in report.phases
            if phase.phase == "layers"
        ]

        self.assertEqual(
            len(layer_results),
            1,
        )
        self.assertTrue(layer_results[0].ok)
        self.assertIs(world.layers, layer)
        self.assertEqual(layer.calls, 1)
        self.assertEqual(entity.ticks, 1)

    def test_05_population_snapshot_recovers_next_tick(self):
        world = self.make_world(5)

        original = world.record_universe_state
        attempts = {"count": 0}

        def fail_first_history():
            attempts["count"] += 1
            original()

            if attempts["count"] == 1:
                raise RuntimeError(
                    "a418 first history publication failure"
                )

        world.record_universe_state = (
            fail_first_history
        )

        first = self.run_tick(world)

        self.assertEqual(
            first.error_count,
            1,
        )
        self.assertEqual(
            first.errors[0].phase,
            "history",
        )
        self.assertEqual(
            world.cronenberg_count,
            1,
        )

        statistics = (
            world.cronenberg_population_statistics
        )

        self.assertEqual(
            len(statistics.history),
            1,
        )
        self.assertEqual(
            statistics.history[-1].snapshot.total_count,
            0,
        )
        self.assertEqual(
            len(world.universe_history),
            0,
        )

        second = self.run_tick(world)

        self.assertEqual(
            second.error_count,
            0,
        )
        self.assertEqual(
            world.universe_tick,
            2,
        )
        self.assertEqual(
            len(statistics.history),
            2,
        )
        self.assertEqual(
            statistics.history[-1].snapshot.total_count,
            1,
        )
        self.assertEqual(
            [
                snapshot.tick
                for snapshot in world.universe_history
            ],
            [2],
        )
        self.assertEqual(
            world.cronenberg_count,
            1,
        )
        self.assertEqual(
            len(world.cronenbergs),
            1,
        )


if __name__ == "__main__":
    unittest.main()
