import io
import math
import random
import unittest

from contextlib import redirect_stdout

from universe.universe import Universe
from cats.cats import Cats
from core.entity.components import SpatialVector3
from quantum.error_boundary import QuantumErrorResult
from universe.universe_tick_result_state import (
    UniverseTickPhaseCompletedResult,
    UniverseTickPhaseErrorResult,
)


class RecoveringEntity:

    def __init__(self):
        self.name = "a42_longrun_recovery"
        self.type = "a42_probe"
        self.active = True
        self.ticks = 0
        self.age = 0

    def tick(self, universe):
        self.ticks += 1
        self.age += 1

        universe.world["a42_probe"]["tokens"].append(
            self.ticks
        )

        if self.ticks == 25:
            universe.energy_pool += 1000.0

            raise RuntimeError(
                "a42_injected_entity_failure"
            )


class A42LongRunIntegrationTests(unittest.TestCase):

    def setUp(self):
        previous_rng = random.getstate()
        self.addCleanup(
            random.setstate,
            previous_rng,
        )

    @staticmethod
    def quiet(operation, *args, **kwargs):
        with redirect_stdout(io.StringIO()):
            return operation(*args, **kwargs)

    def make_world(self, number):
        random.seed(420000 + number)

        return self.quiet(
            Universe,
            universe_id=f"a42_longrun_corrected_{number}",
        )

    def assert_tick(self, report, expected_failure=False):
        errors = tuple(report.errors)

        if expected_failure:
            self.assertEqual(
                len(errors),
                1,
                msg=repr(errors),
            )
            self.assertEqual(
                errors[0].phase,
                "entities",
            )
            self.assertEqual(
                errors[0].error_message,
                "a42_injected_entity_failure",
            )
        else:
            self.assertFalse(
                errors,
                msg=repr(errors),
            )

        for phase in report.phases:
            if isinstance(
                phase,
                UniverseTickPhaseErrorResult,
            ):
                continue

            if not isinstance(
                phase,
                UniverseTickPhaseCompletedResult,
            ):
                continue

            result = phase.result

            if isinstance(result, QuantumErrorResult):
                self.fail(
                    f"Hidden quantum error at tick "
                    f"{report.tick}, phase {phase.phase}: "
                    f"{result.error_type}: "
                    f"{result.error_message}"
                )

            if phase.phase == "cats":
                internal_errors = getattr(
                    result,
                    "errors",
                    (),
                )

                self.assertFalse(
                    internal_errors,
                    msg=(
                        f"Internal cat error at tick "
                        f"{report.tick}: {internal_errors!r}"
                    ),
                )

    def run_ticks(
        self,
        world,
        count,
        failure_tick=None,
    ):
        failures = []

        for tick_number in range(1, count + 1):
            report = self.quiet(
                world.tick_universe
            )

            self.assertEqual(
                report.tick,
                tick_number,
            )

            self.assert_tick(
                report,
                expected_failure=(
                    tick_number == failure_tick
                ),
            )

            if report.errors:
                failures.append((
                    report.tick,
                    tuple(
                        error.phase
                        for error in report.errors
                    ),
                ))

            # Defensive diagnostic bounds.
            self.assertLessEqual(
                len(world.entities),
                256,
            )
            self.assertLessEqual(
                len(world.quantum_boxes),
                96,
            )

        return failures

    def assert_common_state(self, world, count):
        self.assertEqual(
            world.universe_tick,
            count,
        )

        history = world.universe_history
        statistics = (
            world.cronenberg_population_statistics
            .history
        )

        self.assertEqual(len(history), count)
        self.assertEqual(len(statistics), count)

        self.assertEqual(
            [event.tick for event in history],
            list(range(1, count + 1)),
        )

        self.assertEqual(
            world.cronenberg_count,
            len(world.cronenbergs),
        )

        for field in (
            "energy_pool",
            "entropy",
            "pressure",
            "classical_entropy_total",
        ):
            with self.subTest(field=field):
                self.assertTrue(
                    math.isfinite(
                        float(getattr(world, field))
                    )
                )

    def test_01_prephysical_500_ticks(self):
        world = self.make_world(1)

        failures = self.run_ticks(
            world,
            500,
        )

        self.assert_common_state(world, 500)

        self.assertEqual(failures, [])
        self.assertEqual(
            world.life_cycle_system.day,
            0,
        )
        self.assertEqual(
            world.quantum_state.tick_count,
            0,
        )
        self.assertEqual(
            world.cronenberg_count,
            0,
        )

    def test_02_physical_world_200_ticks(self):
        world = self.make_world(2)

        self.quiet(world.start_big_bang)
        self.quiet(world.boot_physics)

        spacetime = world.spacetime
        axis = spacetime.time_axis

        failures = self.run_ticks(
            world,
            200,
        )

        self.assert_common_state(world, 200)

        self.assertEqual(failures, [])
        self.assertEqual(
            world.life_cycle_system.day,
            200,
        )
        self.assertEqual(axis.tick, 200)
        self.assertIs(
            world.spacetime,
            spacetime,
        )
        self.assertIs(
            spacetime.time_axis,
            axis,
        )
        self.assertIs(
            world.world["spacetime"],
            spacetime,
        )
        self.assertEqual(
            world.cronenberg_count,
            0,
        )

    def test_03_quantum_world_150_ticks(self):
        world = self.make_world(3)

        self.quiet(
            world.enable_quantum_layer
        )

        for index, seed in enumerate(
            (303, 404),
            start=1,
        ):
            self.quiet(
                world.create_quantum_box,
                rng=random.Random(seed),
                box_id=f"a42_stress_box_{index}",
            )

        failures = self.run_ticks(
            world,
            150,
        )

        self.assert_common_state(world, 150)

        self.assertEqual(failures, [])
        self.assertEqual(
            world.quantum_state.tick_count,
            150,
        )
        self.assertEqual(
            len(world.quantum_clock_events),
            150,
        )

        def count_events(name):
            return sum(
                getattr(event, "name", None) == name
                for event in world.quantum_events
            )

        created = count_events(
            "quantum_box_created"
        )
        disappeared = count_events(
            "quantum_box_disappeared"
        )
        collapsed = count_events(
            "quantum_box_collapsed"
        )
        manifested = count_events(
            "cat_manifested"
        )

        self.assertEqual(
            created,
            world.statistics.total_quantum_boxes_created,
        )
        self.assertEqual(
            disappeared,
            world.statistics.total_quantum_boxes_disappeared,
        )
        self.assertEqual(
            collapsed,
            world.statistics.total_quantum_collapses,
        )
        self.assertEqual(
            manifested,
            world.statistics.total_cats_created,
        )
        self.assertEqual(
            created,
            len(world.quantum_boxes) + disappeared,
        )

    def test_04_multicat_world_100_ticks(self):
        world = self.make_world(4)

        self.quiet(world.start_big_bang)
        self.quiet(world.boot_physics)
        self.quiet(world.enable_quantum_layer)

        cats = self.quiet(Cats, world)

        first = self.quiet(
            cats.create_cat,
            name="a42_longrun_pazuzu",
            color="black",
            fur_length="short",
        )

        second = self.quiet(
            cats.create_cat,
            name="a42_longrun_observer",
            color="gray",
            fur_length="short",
        )

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)

        first.position = SpatialVector3(
            x=0.0,
            y=0.0,
            z=0.0,
        )

        second.position = SpatialVector3(
            x=2.0,
            y=0.0,
            z=0.0,
        )

        cat_registry = cats.cats
        spacetime = world.spacetime

        self.quiet(
            world.create_quantum_box,
            rng=random.Random(505),
            box_id="a42_longrun_live_box",
        )

        failures = self.run_ticks(
            world,
            100,
        )

        self.assert_common_state(world, 100)

        self.assertEqual(failures, [])

        self.assertEqual(
            world.quantum_state.tick_count,
            100,
        )
        self.assertEqual(
            world.spacetime.time_axis.tick,
            100,
        )
        self.assertEqual(
            world.life_cycle_system.day,
            100,
        )
        self.assertEqual(
            cats.tick_count,
            100,
        )
        self.assertIs(
            cats.cats,
            cat_registry,
        )
        self.assertIs(
            world.spacetime,
            spacetime,
        )
        self.assertIn(
            first,
            cat_registry,
        )
        self.assertIn(
            second,
            cat_registry,
        )

    def test_05_failure_recovery_100_ticks(self):
        world = self.make_world(5)

        self.quiet(
            world.enable_quantum_layer
        )

        probe = RecoveringEntity()

        world.world["a42_probe"] = {
            "tokens": [],
        }

        self.quiet(
            world.add_entity,
            probe,
        )

        failures = self.run_ticks(
            world,
            100,
            failure_tick=25,
        )

        self.assert_common_state(world, 100)

        self.assertEqual(
            failures,
            [(25, ("entities",))],
        )
        self.assertEqual(
            probe.ticks,
            100,
        )
        self.assertEqual(
            probe.age,
            99,
        )

        expected_tokens = [
            tick
            for tick in range(1, 101)
            if tick != 25
        ]

        self.assertEqual(
            world.world["a42_probe"]["tokens"],
            expected_tokens,
        )
        self.assertEqual(
            world.cronenberg_count,
            1,
        )
        self.assertEqual(
            world.quantum_state.tick_count,
            100,
        )


if __name__ == "__main__":
    unittest.main()
