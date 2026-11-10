import io
import random
import unittest

from contextlib import redirect_stdout

from cats.cats import Cats
from cats.development_resolver import CatDevelopmentResolver
from core.entity.components import SpatialVector3
from universe.aroma_residue import AromaResidue
from universe.universe import Universe
from universe.universe_tick_result_state import (
    UniverseTickPhaseCompletedResult,
)


class A42RealUniverseRuntimeTests(unittest.TestCase):

    def setUp(self):
        before = random.getstate()
        self.addCleanup(random.setstate, before)

    @staticmethod
    def execute(operation, *args, **kwargs):
        with redirect_stdout(io.StringIO()):
            return operation(*args, **kwargs)

    def make_world(self, number):
        random.seed(42000 + number)

        return self.execute(
            Universe,
            universe_id=f"a42_regression_{number}",
        )

    def tick(self, world):
        report = self.execute(world.tick_universe)

        self.assertEqual(
            report.error_count,
            0,
            msg=repr([
                (
                    e.phase,
                    e.error_type,
                    e.error_message,
                )
                for e in report.errors
            ]),
        )

        for phase in report.phases:
            if phase.phase != "cats":
                continue

            # Skipped phases have no .result.
            if not isinstance(
                phase,
                UniverseTickPhaseCompletedResult,
            ):
                continue

            errors = getattr(phase.result, "errors", ())

            self.assertFalse(
                errors,
                msg=f"Internal cat errors: {errors!r}",
            )

        return report

    def run_ticks(self, world, count):
        return [
            self.tick(world)
            for _ in range(count)
        ]

    @staticmethod
    def history_ticks(world):
        return [
            item.tick
            for item in world.universe_history
        ]

    def test_01_prephysical_scheduler(self):
        world = self.make_world(1)
        reports = self.run_ticks(world, 3)

        self.assertEqual(
            [r.tick for r in reports],
            [1, 2, 3],
        )
        self.assertEqual(
            self.history_ticks(world),
            [1, 2, 3],
        )
        self.assertEqual(world.life_cycle_system.day, 0)
        self.assertEqual(world.cronenberg_count, 0)

    def test_02_classical_physics_spacetime(self):
        world = self.make_world(2)
        self.execute(world.boot_physics)

        spacetime = world.spacetime
        axis = spacetime.time_axis

        self.run_ticks(world, 3)

        self.assertIs(world.spacetime, spacetime)
        self.assertIs(spacetime.time_axis, axis)
        self.assertIs(world.world["spacetime"], spacetime)
        self.assertEqual(axis.tick, 3)
        self.assertAlmostEqual(
            spacetime.curvature,
            0.03,
        )
        self.assertEqual(
            self.history_ticks(world),
            [1, 2, 3],
        )

    def test_03_big_bang_and_lifecycle(self):
        world = self.make_world(3)

        first = self.execute(world.start_big_bang)

        self.assertTrue(world.big_bang_started)
        self.assertTrue(world.physical_universe_started)
        self.assertIs(world.big_bang.result, first)
        self.assertIs(
            self.execute(world.start_big_bang),
            first,
        )

        self.run_ticks(world, 2)

        self.assertEqual(world.life_cycle_system.day, 2)
        self.assertEqual(
            self.history_ticks(world),
            [1, 2],
        )

    def test_04_newborn_cat_ageing(self):
        world = self.make_world(4)

        self.execute(world.start_big_bang)
        cats = self.execute(Cats, world)

        kitten = self.execute(
            cats.create_cat,
            name="a42_kitten",
            color="black",
            fur_length="short",
            sex="female",
        )

        self.assertIsNotNone(kitten)

        development = CatDevelopmentResolver(world)

        self.execute(
            development.initialize_newborn,
            kitten,
            birth_day=0,
        )

        self.run_ticks(world, 3)

        self.assertEqual(kitten.age_days, 3)
        self.assertEqual(world.life_cycle_system.day, 3)
        self.assertEqual(cats.tick_count, 3)
        self.assertIn(kitten, cats.cats)

    def test_05_live_quantum_box_lifecycle(self):
        world = self.make_world(5)
        self.execute(world.enable_quantum_layer)

        boxes = [
            self.execute(
                world.create_quantum_box,
                rng=random.Random(seed),
                box_id=f"a42_live_box_{index}",
            )
            for index, seed in enumerate(
                (101, 202), start=1
            )
        ]

        initial_ids = {box.id for box in boxes}

        self.run_ticks(world, 5)

        self.assertEqual(world.quantum_state.tick_count, 5)
        self.assertEqual(
            len(world.quantum_clock_events),
            5,
        )

        surviving = {
            box.id for box in world.quantum_boxes
        }

        disappeared = [
            e.box_id
            for e in world.quantum_events
            if getattr(e, "name", None)
            == "quantum_box_disappeared"
        ]

        created = [
            e
            for e in world.quantum_events
            if getattr(e, "name", None)
            == "quantum_box_created"
        ]

        self.assertEqual(len(created), 2)
        self.assertTrue(
            surviving.isdisjoint(disappeared)
        )
        self.assertEqual(
            surviving | set(disappeared),
            initial_ids,
        )
        self.assertEqual(
            len(disappeared),
            len(set(disappeared)),
        )

        for box in world.quantum_boxes:
            self.assertEqual(box.age_ticks, 5)

    def test_06_open_empty_quantum_box(self):
        world = self.make_world(6)
        self.execute(world.enable_quantum_layer)

        box = self.execute(
            world.create_quantum_box,
            rng=random.Random(300),
            box_id="a42_empty_box",
        )

        event = self.execute(
            world.open_quantum_box,
            box.id,
            observer="a42_observer",
            rng=random.Random(1),
        )

        self.assertEqual(
            event.name,
            "empty_quantum_box_opened",
        )
        self.assertEqual(world.quantum_boxes, [])
        self.assertEqual(
            world.statistics.total_quantum_boxes_created,
            1,
        )
        self.assertEqual(
            world.statistics.total_quantum_boxes_disappeared,
            1,
        )
        self.assertEqual(world.cronenberg_count, 0)

    def test_07_open_box_manifesting_cat(self):
        world = self.make_world(7)
        self.execute(world.enable_quantum_layer)

        box = self.execute(
            world.create_quantum_box,
            rng=random.Random(301),
            box_id="a42_cat_box",
        )

        event = self.execute(
            world.open_quantum_box,
            box.id,
            observer="a42_observer",
            rng=random.Random(0),
        )

        self.assertEqual(event.name, "cat_manifested")
        self.assertEqual(event.box_id, box.id)
        self.assertEqual(world.quantum_boxes, [])

        cats = world.cats_layer

        self.assertEqual(len(cats.cats), 1)

        cat = cats.cats[0]

        self.assertEqual(cat.name, event.cat_name)
        self.assertEqual(cat.age_days, 98)
        self.assertTrue(
            cat.quantum_box_origin.manifested_from_box
        )
        self.assertTrue(any(
            getattr(entity, "cat_data", None) is cat
            for entity in world.entities
        ))

        self.run_ticks(world, 2)

        self.assertEqual(cats.tick_count, 2)

    def test_08_cat_aroma_transfer_and_decay(self):
        world = self.make_world(8)
        cats = self.execute(Cats, world)

        cat = self.execute(
            cats.create_cat,
            name="a42_pazuzu",
            color="black",
            fur_length="short",
        )

        box = self.execute(
            world.create_quantum_box,
            rng=random.Random(801),
            box_id="a42_aroma_box",
        )

        result = self.execute(
            AromaResidue.transfer,
            source_profile=cat.aroma,
            target=box,
            source_identity=cat.name,
            fraction=0.3,
        )

        self.assertTrue(result.transferred)

        component = "individual_cat:a42_pazuzu"
        before = box.aroma.current().amount(component)

        self.run_ticks(world, 2)

        after = box.aroma.current().amount(component)

        self.assertGreater(before, 0)
        self.assertGreater(after, 0)
        self.assertLess(after, before)
        self.assertIn(box, world.quantum_boxes)
        self.assertEqual(cats.tick_count, 2)

    def test_09_integrated_physical_quantum_cat_world(self):
        world = self.make_world(9)

        self.execute(world.start_big_bang)
        self.execute(world.boot_physics)
        self.execute(world.enable_quantum_layer)

        cats = self.execute(Cats, world)

        cat = self.execute(
            cats.create_cat,
            name="a42_integrated_pazuzu",
            color="black",
            fur_length="short",
        )

        self.execute(
            cat.move_to,
            SpatialVector3(x=0.0, y=0.0, z=0.0),
        )

        box = self.execute(
            world.create_quantum_box,
            rng=random.Random(901),
            box_id="a42_integrated_box",
        )

        self.run_ticks(world, 3)

        self.assertEqual(world.universe_tick, 3)
        self.assertEqual(world.quantum_state.tick_count, 3)
        self.assertEqual(
            world.spacetime.time_axis.tick,
            3,
        )
        self.assertEqual(world.life_cycle_system.day, 3)
        self.assertEqual(cats.tick_count, 3)
        self.assertIn(cat, cats.cats)
        self.assertEqual(
            self.history_ticks(world),
            [1, 2, 3],
        )

        disappeared = any(
            getattr(e, "name", None)
            == "quantum_box_disappeared"
            and e.box_id == box.id
            for e in world.quantum_events
        )

        self.assertTrue(
            box in world.quantum_boxes or disappeared
        )
        self.assertEqual(world.cronenberg_count, 0)

    def test_10_seeded_world_reproducibility(self):
        def simulate():
            random.seed(424242)

            world = self.make_world(10)
            random.seed(424242)

            self.execute(world.boot_physics)
            self.execute(world.enable_quantum_layer)
            self.run_ticks(world, 4)

            return (
                world.universe_tick,
                world.quantum_state.tick_count,
                world.spacetime.time_axis.tick,
                world.spacetime.curvature,
                world.energy_pool,
                world.entropy,
                world.pressure,
                tuple(
                    (
                        s.tick,
                        s.energy,
                        s.entropy,
                        s.curvature,
                    )
                    for s in world.universe_history
                ),
            )

        self.assertEqual(simulate(), simulate())

    def test_11_quantum_box_replay_into_live_world(self):
        source = self.make_world(11)

        original = self.execute(
            source.create_quantum_box,
            rng=random.Random(1111),
            box_id="a42_replay_box",
        )

        event = source.quantum_events[-1]

        target = self.execute(
            Universe,
            universe_id="a42_replay_target",
        )

        restored = self.execute(
            target.replay_quantum_box_created,
            event,
        )

        self.assertIsNot(restored, original)
        self.assertEqual(restored.id, original.id)
        self.assertEqual(
            restored.position,
            original.position,
        )
        self.assertEqual(
            restored.public_state,
            original.public_state,
        )
        self.assertEqual(target.quantum_events, [])

        self.run_ticks(source, 2)
        self.run_ticks(target, 2)

        self.assertEqual(
            self.history_ticks(source),
            [1, 2],
        )
        self.assertEqual(
            self.history_ticks(target),
            [1, 2],
        )


if __name__ == "__main__":
    unittest.main()
