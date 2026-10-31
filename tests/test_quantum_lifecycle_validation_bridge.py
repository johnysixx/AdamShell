import random
import unittest
from dataclasses import replace

from universe.quantum_lifecycle_timeline import (
    UniverseQuantumLifecycleTimeline,
)
from universe.universe import Universe


class FixedChoice:
    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError("Missing empty possibility")
        return "empty"


class OnePass:
    def __init__(self, values):
        self.values = tuple(values)
        self.iterations = 0

    def __iter__(self):
        self.iterations += 1
        if self.iterations != 1:
            raise AssertionError("History consumed more than once")
        return iter(self.values)


class QuantumLifecycleValidationBridgeTests(unittest.TestCase):

    def make_source(self):
        source = Universe(universe_id="validation-bridge")
        source.enable_quantum_layer()
        source.should_collapse_quantum_box = (
            lambda _box: False
        )

        source.create_quantum_box(
            box_id="early",
            rng=random.Random(1),
        )

        source.tick_quantum_unprotected()

        source.create_quantum_box(
            box_id="late",
            rng=random.Random(2),
        )

        source.tick_quantum_unprotected()

        source.open_quantum_box(
            "early",
            rng=FixedChoice(),
        )

        return source

    def make_target(self):
        target = Universe(universe_id="validation-bridge")
        target.enable_quantum_layer()
        return target

    def assert_target_unchanged(self, target, before, clock):
        self.assertEqual(target.snapshot, before)
        self.assertEqual(
            target.quantum_state.to_dict(),
            clock,
        )
        self.assertEqual(target.quantum_events, [])
        self.assertEqual(target.quantum_clock_events, [])

    def test_validated_timeline_preserves_existing_merge_api(self):
        source = self.make_source()

        validated = UniverseQuantumLifecycleTimeline.validate(
            box_events=source.quantum_events,
            clock_events=source.quantum_clock_events,
        )

        self.assertEqual(
            validated.events,
            source.quantum_lifecycle_timeline(),
        )
        self.assertIsInstance(validated.events, tuple)

        self.assertEqual(
            [event.tick for event in validated.events],
            [0, 1, 1, 2, 2, 2],
        )

        self.assertEqual(
            [event.name for event in validated.events],
            [
                "quantum_box_created",
                "universe_quantum_tick_advanced",
                "quantum_box_created",
                "universe_quantum_tick_advanced",
                "quantum_box_collapsed",
                "quantum_box_disappeared",
            ],
        )

    def test_validation_returns_active_box_records(self):
        source = self.make_source()

        validated = UniverseQuantumLifecycleTimeline.validate(
            box_events=source.quantum_events,
            clock_events=source.quantum_clock_events,
        )

        self.assertEqual(len(validated.active_boxes), 1)

        active = validated.active_boxes[0]

        self.assertEqual(active.box_id, "late")
        self.assertEqual(active.created_tick, 1)
        self.assertIsNone(active.collapse_tick)

    def test_combined_replay_uses_validated_chronology(self):
        source = self.make_source()
        target = self.make_target()

        original_clock = target.quantum_state
        original_statistics = target.statistics

        result = target.replay_quantum_history(
            box_events=source.quantum_events,
            clock_events=source.quantum_clock_events,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "late")
        self.assertEqual(result[0].age_ticks, 1)

        self.assertIs(target.quantum_state, original_clock)
        self.assertIs(target.statistics, original_statistics)

        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )
        self.assertEqual(
            target.statistics.total_quantum_boxes_created,
            2,
        )
        self.assertEqual(
            target.statistics.total_quantum_collapses,
            1,
        )
        self.assertEqual(
            target.statistics.total_quantum_boxes_disappeared,
            1,
        )

    def test_validation_accepts_one_pass_streams(self):
        source = self.make_source()

        boxes = OnePass(source.quantum_events)
        clocks = OnePass(source.quantum_clock_events)

        validated = UniverseQuantumLifecycleTimeline.validate(
            box_events=boxes,
            clock_events=clocks,
        )

        self.assertEqual(
            validated.events,
            source.quantum_lifecycle_timeline(),
        )
        self.assertEqual(boxes.iterations, 1)
        self.assertEqual(clocks.iterations, 1)

    def test_future_box_tick_rejected_by_both_paths(self):
        source = self.make_source()

        future_event = replace(
            source.quantum_events[0],
            tick=3,
        )
        invalid_boxes = (future_event,)

        with self.assertRaises(ValueError):
            UniverseQuantumLifecycleTimeline.validate(
                box_events=invalid_boxes,
                clock_events=source.quantum_clock_events,
            )

        target = self.make_target()
        before = target.snapshot
        clock = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            target.replay_quantum_history(
                box_events=invalid_boxes,
                clock_events=source.quantum_clock_events,
            )

        self.assert_target_unchanged(target, before, clock)

    def test_duplicate_clock_rejected_by_both_paths(self):
        source = self.make_source()

        clock_event = source.quantum_clock_events[0]
        invalid_clocks = (clock_event, clock_event)

        with self.assertRaises(ValueError):
            UniverseQuantumLifecycleTimeline.validate(
                box_events=source.quantum_events,
                clock_events=invalid_clocks,
            )

        target = self.make_target()
        before = target.snapshot
        clock = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            target.replay_quantum_history(
                box_events=source.quantum_events,
                clock_events=invalid_clocks,
            )

        self.assert_target_unchanged(target, before, clock)

    def test_tick_zero_history_remains_supported(self):
        source = Universe(universe_id="tick-zero")
        source.create_quantum_box(
            box_id="only",
            rng=random.Random(3),
        )
        source.open_quantum_box(
            "only",
            rng=FixedChoice(),
        )

        validated = UniverseQuantumLifecycleTimeline.validate(
            box_events=source.quantum_events,
            clock_events=(),
        )

        self.assertEqual(
            validated.events,
            tuple(source.quantum_events),
        )
        self.assertEqual(validated.active_boxes, ())

        target = Universe(universe_id="tick-zero")
        result = target.replay_quantum_history(
            box_events=source.quantum_events,
            clock_events=(),
        )

        self.assertEqual(result, ())
        self.assertEqual(target.quantum_state.tick_count, 0)


if __name__ == "__main__":
    unittest.main()
