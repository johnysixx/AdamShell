import io
import random
import unittest
from contextlib import redirect_stdout

from quantum.error_boundary import QuantumErrorResult
from universe.universe import Universe
from universe.universe_statistics import UniverseStatistics
from universe.manifestation_result_state import CatManifestedEvent


class FailOnceAppend(list):
    def __init__(self, values=()):
        super().__init__(values)
        self.armed = True

    def append(self, value):
        super().append(value)
        if self.armed:
            self.armed = False
            raise RuntimeError("A41.3 injected append failure")


class FailOnceRemove(list):
    def __init__(self, values=()):
        super().__init__(values)
        self.armed = True

    def remove(self, value):
        super().remove(value)
        if self.armed:
            self.armed = False
            raise RuntimeError("A41.3 injected remove failure")


class FailOnceCatStats(UniverseStatistics):
    def __init__(self, original):
        super().__init__()
        self.__dict__.update(original.__dict__)
        self.armed = True

    def record_cat_created(self):
        super().record_cat_created()
        if self.armed:
            self.armed = False
            raise RuntimeError("A41.3 injected cat statistics failure")


class FixedChoice:
    def __init__(self, result):
        self.result = result

    def choice(self, possibilities):
        assert self.result in possibilities
        return self.result


class QuantumTickPublicationRollbackTests(unittest.TestCase):

    @staticmethod
    def make_world(identity, count):
        with redirect_stdout(io.StringIO()):
            world = Universe(universe_id=identity)
            world.enable_quantum_layer()
            boxes = [
                world.create_quantum_box(
                    box_id=f"{identity}_{index}",
                    rng=random.Random(413 + index),
                )
                for index in range(count)
            ]
        return world, boxes

    @staticmethod
    def force_result(box, result):
        original = box.collapse_state

        def collapse(*args, **kwargs):
            kwargs["rng"] = FixedChoice(result)
            return original(*args, **kwargs)

        box.collapse_state = collapse

    @staticmethod
    def fingerprint(world, boxes):
        cats_layer = getattr(world, "cats_layer", None)

        return (
            world.quantum_state.to_dict(),
            world.statistics.public_state,
            tuple(world.quantum_boxes),
            tuple(world.quantum_events),
            tuple(world.quantum_clock_events),
            tuple(world.entities),
            tuple(world.cronenbergs),
            world.cronenberg_count,
            tuple(world.universe_history),
            tuple(
                (
                    box.age_ticks,
                    box.state,
                    box.content.resolved,
                    box.collapse.collapsed,
                    box.collapse.cause,
                    box.collapse.observer,
                    box.collapse.tick,
                )
                for box in boxes
            ),
            cats_layer is not None,
            tuple(cats_layer.cats) if cats_layer else (),
            tuple(cats_layer.events) if cats_layer else (),
        )

    def assert_rollback(self, world, boxes):
        before = self.fingerprint(world, boxes)

        random_before = random.getstate()

        references = {
            name: getattr(world, name)
            for name in (
                "quantum_state",
                "statistics",
                "quantum_boxes",
                "quantum_events",
                "quantum_clock_events",
                "entities",
                "cronenbergs",
                "universe_history",
            )
        }

        world_registry = world.world
        world_entries = dict(world_registry)

        with self.assertRaisesRegex(
            RuntimeError, "A41.3 injected"
        ):
            with redirect_stdout(io.StringIO()):
                world.tick_quantum_unprotected()

        self.assertEqual(
            self.fingerprint(world, boxes),
            before,
        )

        self.assertEqual(
            random.getstate(),
            random_before,
        )

        for name, original in references.items():
            self.assertIs(
                getattr(world, name),
                original,
                name,
            )

        self.assertIs(world.world, world_registry)
        self.assertEqual(
            set(world.world),
            set(world_entries),
        )

        for key, value in world_entries.items():
            self.assertIs(world.world[key], value)

    def test_clock_history_rollback_and_retry(self):
        world, boxes = self.make_world("a413_clock", 0)

        world.quantum_clock_events = FailOnceAppend(
            world.quantum_clock_events
        )

        self.assert_rollback(world, boxes)

        with redirect_stdout(io.StringIO()):
            world.tick_quantum_unprotected()

        self.assertEqual(world.quantum_state.tick_count, 1)
        self.assertEqual(len(world.quantum_clock_events), 1)
        self.assertEqual(world.quantum_clock_events[0].tick, 1)

    def test_multiple_boxes_rollback_and_retry(self):
        world, boxes = self.make_world("a413_multi", 2)
        first, second = boxes

        world.quantum_boxes = FailOnceRemove(
            world.quantum_boxes
        )
        world.should_collapse_quantum_box = (
            lambda box: box is first
        )
        self.force_result(first, "empty")

        self.assert_rollback(world, boxes)

        self.assertEqual(first.age_ticks, 0)
        self.assertEqual(second.age_ticks, 0)
        self.assertFalse(first.collapse.collapsed)

        with redirect_stdout(io.StringIO()):
            world.tick_quantum_unprotected()

        self.assertNotIn(first, world.quantum_boxes)
        self.assertIn(second, world.quantum_boxes)
        self.assertEqual(second.age_ticks, 1)
        self.assertTrue(first.collapse.collapsed)

        self.assertEqual(
            world.statistics.total_quantum_boxes_disappeared,
            1,
        )
        self.assertEqual(
            world.statistics.total_quantum_collapses,
            1,
        )

    def test_spontaneous_cat_rollback_and_retry(self):
        world, boxes = self.make_world("a413_cat", 1)
        box = boxes[0]

        world.should_collapse_quantum_box = (
            lambda box: True
        )
        self.force_result(box, "cat")

        world.statistics = FailOnceCatStats(
            world.statistics
        )

        self.assert_rollback(world, boxes)

        self.assertFalse(hasattr(world, "cats_layer"))
        self.assertEqual(
            world.statistics.total_cats_created,
            0,
        )

        with redirect_stdout(io.StringIO()):
            world.tick_quantum_unprotected()

        self.assertEqual(world.quantum_state.tick_count, 1)
        self.assertEqual(
            world.statistics.total_cats_created,
            1,
        )
        self.assertEqual(len(world.cats_layer.cats), 1)
        self.assertNotIn(box, world.quantum_boxes)

        manifested = [
            event for event in world.quantum_events
            if isinstance(event, CatManifestedEvent)
        ]
        self.assertEqual(len(manifested), 1)

    def test_public_boundary_creates_one_cronenberg(self):
        world, boxes = self.make_world(
            "a413_boundary", 0
        )

        world.quantum_clock_events = FailOnceAppend(
            world.quantum_clock_events
        )

        with redirect_stdout(io.StringIO()):
            result = world.tick_quantum()

        self.assertIsInstance(result, QuantumErrorResult)
        self.assertEqual(world.quantum_state.tick_count, 0)
        self.assertEqual(len(world.quantum_clock_events), 0)
        self.assertEqual(len(world.cronenbergs), 1)
        self.assertEqual(world.cronenberg_count, 1)
        self.assertIs(
            result.cronenberg,
            world.cronenbergs[0],
        )

        with redirect_stdout(io.StringIO()):
            world.tick_quantum()

        self.assertEqual(world.quantum_state.tick_count, 1)
        self.assertEqual(len(world.quantum_clock_events), 1)
        self.assertEqual(world.cronenberg_count, 1)


if __name__ == "__main__":
    unittest.main()
