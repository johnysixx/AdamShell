import io
import random
import unittest

from contextlib import redirect_stdout
from types import SimpleNamespace

from universe.universe import Universe
from universe.universe_tick_result_state import (
    UniverseTickPhaseCompletedResult,
    UniverseTickPhaseErrorResult,
)


class FailAfterAppend(list):
    def __init__(self, values=()):
        super().__init__(values)
        self.failed = False

    def append(self, value):
        super().append(value)

        if not self.failed:
            self.failed = True
            raise RuntimeError(
                "A41.7 injected publication failure"
            )


class SuccessfulBiologyHandler:
    def __init__(self, universe):
        self.universe = universe
        self.calls = 0

    def tick_day(self, day):
        self.calls += 1
        self.universe.energy_pool -= 4.0
        self.universe.quantum_events.append(
            SimpleNamespace(
                name="a417_partial_biology"
            )
        )
        return SimpleNamespace(
            name="a417_handler_completed",
            day=day,
        )


class FailingBiologyHandler:
    def tick_day(self, day):
        raise RuntimeError(
            "A41.7 biology handler failure"
        )


class OptionalFailingLayer:
    def __init__(self):
        self.tick_count = 0

    def tick(self):
        self.tick_count += 1
        raise RuntimeError(
            "A41.7 optional layer failure"
        )


class UniversePhaseRollbackTests(unittest.TestCase):

    @staticmethod
    def make_world(number):
        with redirect_stdout(io.StringIO()):
            return Universe(
                universe_id=f"a417_regression_{number}"
            )

    @staticmethod
    def physics_state(world):
        names = (
            "entropy",
            "pressure",
            "energy_pool",
            "classical_entropy_total",
            "last_classical_entropy_delta",
            "last_energy_gain",
            "last_pressure_cost",
            "last_energy_delta",
        )
        return {
            name: getattr(world, name)
            for name in names
        }

    @staticmethod
    def enable_spacetime(world):
        with redirect_stdout(io.StringIO()):
            world.enable_physics("gravity")
            world.bind_spacetime()

    @staticmethod
    def add_physics_probe(world):
        with redirect_stdout(io.StringIO()):
            world.add_entity(
                SimpleNamespace(
                    name="a417_physics_probe",
                    active=False,
                )
            )

    def run_failed_phase(
        self,
        world,
        phase,
        operation,
    ):
        before = world.cronenberg_count

        with redirect_stdout(io.StringIO()):
            result = world._run_tick_operation(
                phase=phase,
                operation=operation,
                source_component="a417_regression",
                source_operation=phase,
            )

        self.assertIsInstance(
            result,
            UniverseTickPhaseErrorResult,
        )
        self.assertEqual(result.phase, phase)
        self.assertEqual(
            world.cronenberg_count,
            before + 1,
        )
        self.assertIsNotNone(
            result.cronenberg_id
        )
        self.assertIn(
            result.cronenberg_id,
            {
                item.id
                for item in world.cronenbergs
            },
        )
        return result

    def test_01_spacetime_late_failure_rolls_back(self):
        world = self.make_world(1)
        self.enable_spacetime(world)

        spacetime = world.spacetime
        time_axis = spacetime.time_axis
        space_axis = spacetime.space_axis
        before = spacetime.to_dict()

        original = world.tick_spacetime

        def broken():
            original()
            raise RuntimeError(
                "a417-spacetime-late"
            )

        self.run_failed_phase(
            world,
            "spacetime",
            broken,
        )

        self.assertEqual(
            spacetime.to_dict(),
            before,
        )
        self.assertIs(
            world.spacetime,
            spacetime,
        )
        self.assertIs(
            spacetime.time_axis,
            time_axis,
        )
        self.assertIs(
            spacetime.space_axis,
            space_axis,
        )

    def test_02_spacetime_partial_advance_rolls_back(self):
        world = self.make_world(2)
        self.enable_spacetime(world)

        spacetime = world.spacetime
        time_axis = spacetime.time_axis
        before = spacetime.to_dict()

        spacetime_class = type(spacetime)
        original_advance = spacetime_class.advance

        def failing_advance(
            self,
            curvature_delta=0.0,
        ):
            self.time_axis.advance()
            raise RuntimeError(
                "a417-spacetime-mid-advance"
            )

        try:
            spacetime_class.advance = failing_advance

            self.run_failed_phase(
                world,
                "spacetime",
                world.tick_spacetime,
            )
        finally:
            spacetime_class.advance = original_advance

        self.assertEqual(
            spacetime.to_dict(),
            before,
        )
        self.assertIs(
            spacetime.time_axis,
            time_axis,
        )

    def test_03_physics_late_failure_rolls_back(self):
        world = self.make_world(3)
        self.add_physics_probe(world)

        before = self.physics_state(world)
        original = world.update_physics

        def broken():
            original()
            raise RuntimeError(
                "a417-physics-late"
            )

        self.run_failed_phase(
            world,
            "physics",
            broken,
        )

        self.assertEqual(
            self.physics_state(world),
            before,
        )

    def test_04_physics_mid_update_error_rolls_back(self):
        world = self.make_world(4)
        self.add_physics_probe(world)

        world.spacetime = SimpleNamespace(
            curvature="invalid_curvature"
        )

        before = self.physics_state(world)

        result = self.run_failed_phase(
            world,
            "physics",
            world.update_physics,
        )

        self.assertEqual(
            result.error_type,
            "TypeError",
        )
        self.assertEqual(
            self.physics_state(world),
            before,
        )

    def test_05_biology_second_handler_failure_is_atomic(self):
        world = self.make_world(5)
        world.physical_universe_started = True

        first = SuccessfulBiologyHandler(world)
        handlers = [
            first,
            FailingBiologyHandler(),
        ]

        lifecycle = world.life_cycle_system
        lifecycle.handlers = handlers

        history = lifecycle.history
        events_before = tuple(
            world.quantum_events
        )
        day_before = lifecycle.day
        energy_before = world.energy_pool

        self.run_failed_phase(
            world,
            "biology",
            lifecycle.tick_day,
        )

        self.assertEqual(
            lifecycle.day,
            day_before,
        )
        self.assertEqual(first.calls, 0)
        self.assertEqual(
            world.energy_pool,
            energy_before,
        )
        self.assertIs(
            lifecycle.history,
            history,
        )
        self.assertEqual(len(history), 0)
        self.assertIs(
            lifecycle.handlers,
            handlers,
        )

        self.assertEqual(
            len(world.quantum_events),
            len(events_before) + 1,
        )

        self.assertFalse(any(
            getattr(event, "name", None)
            == "a417_partial_biology"
            for event in world.quantum_events
        ))

    def test_06_biology_history_append_failure_is_atomic(self):
        world = self.make_world(6)
        world.physical_universe_started = True

        lifecycle = world.life_cycle_system
        lifecycle.handlers = []

        history = FailAfterAppend(
            lifecycle.history
        )
        lifecycle.history = history

        before_day = lifecycle.day

        self.run_failed_phase(
            world,
            "biology",
            lifecycle.tick_day,
        )

        self.assertEqual(
            lifecycle.day,
            before_day,
        )
        self.assertIs(
            lifecycle.history,
            history,
        )
        self.assertEqual(
            len(history),
            0,
        )

    def test_07_universe_history_append_failure_is_atomic(self):
        world = self.make_world(7)

        history = FailAfterAppend(
            world.universe_history
        )
        world.universe_history = history

        self.run_failed_phase(
            world,
            "history",
            world.record_universe_state,
        )

        self.assertIs(
            world.universe_history,
            history,
        )
        self.assertEqual(
            len(history),
            0,
        )

    def test_08_optional_layer_failure_restores_target(self):
        world = self.make_world(8)
        layer = OptionalFailingLayer()

        before = world.cronenberg_count

        with redirect_stdout(io.StringIO()):
            result = world._run_optional_tick(
                phase="layers",
                target=layer,
                source_component="layers",
            )

        self.assertIsInstance(
            result,
            UniverseTickPhaseErrorResult,
        )
        self.assertEqual(
            world.cronenberg_count,
            before + 1,
        )
        self.assertEqual(
            layer.tick_count,
            0,
        )
        self.assertEqual(
            result.source_component,
            "layers",
        )

    def test_09_scheduler_continues_after_biology_failure(self):
        world = self.make_world(9)
        world.physical_universe_started = True

        lifecycle = world.life_cycle_system
        lifecycle.handlers = [
            FailingBiologyHandler()
        ]

        with redirect_stdout(io.StringIO()):
            report = world.tick_universe()

        self.assertEqual(report.tick, 1)
        self.assertEqual(
            world.universe_tick,
            1,
        )
        self.assertEqual(
            report.error_count,
            1,
        )
        self.assertEqual(
            report.errors[0].phase,
            "biology",
        )
        self.assertEqual(
            world.cronenberg_count,
            1,
        )
        self.assertEqual(
            lifecycle.day,
            0,
        )
        self.assertEqual(
            len(world.universe_history),
            1,
        )
        self.assertTrue(any(
            phase.phase == "history" and phase.ok
            for phase in report.phases
        ))

    def test_10_rng_restored_before_error_manifestation(self):
        world = self.make_world(10)

        before_rng = random.getstate()
        before_energy = world.energy_pool

        # Do not leak RNG modifications into other tests.
        self.addCleanup(
            random.setstate,
            before_rng,
        )

        seen_rng = []

        original = (
            world.create_cronenberg_from_quantum_error
        )

        def observe_manifestation(*args, **kwargs):
            seen_rng.append(
                random.getstate()
            )
            return original(*args, **kwargs)

        world.create_cronenberg_from_quantum_error = (
            observe_manifestation
        )

        def broken():
            world.energy_pool -= 13.0
            random.random()
            random.random()
            raise RuntimeError(
                "a417-rng-failure"
            )

        self.run_failed_phase(
            world,
            "spacetime",
            broken,
        )

        self.assertEqual(
            seen_rng,
            [before_rng],
        )
        self.assertEqual(
            world.energy_pool,
            before_energy,
        )
        self.assertNotEqual(
            random.getstate(),
            before_rng,
        )

    def test_11_previous_successful_phase_is_preserved(self):
        world = self.make_world(11)
        self.enable_spacetime(world)

        spacetime = world.spacetime
        time_axis = spacetime.time_axis

        with redirect_stdout(io.StringIO()):
            success = world._run_tick_operation(
                phase="spacetime",
                operation=world.tick_spacetime,
                source_component="universe",
                source_operation="tick_spacetime",
            )

        self.assertIsInstance(
            success,
            UniverseTickPhaseCompletedResult,
        )

        committed_spacetime = (
            spacetime.to_dict()
        )
        committed_energy = (
            world.energy_pool
        )

        def broken():
            spacetime.curvature = 999.0
            world.energy_pool -= 25.0
            raise RuntimeError(
                "a417-later-physics-failure"
            )

        self.run_failed_phase(
            world,
            "physics",
            broken,
        )

        self.assertEqual(
            spacetime.to_dict(),
            committed_spacetime,
        )
        self.assertEqual(
            world.energy_pool,
            committed_energy,
        )
        self.assertIs(
            world.spacetime,
            spacetime,
        )
        self.assertIs(
            spacetime.time_axis,
            time_axis,
        )


if __name__ == "__main__":
    unittest.main()
