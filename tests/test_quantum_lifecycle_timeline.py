import random
import unittest

from universe.quantum_lifecycle_timeline import (
    UniverseQuantumLifecycleTimeline,
)
from universe.universe import Universe


class FixedChoice:
    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError("Missing empty possibility")
        return "empty"


class QuantumLifecycleTimelineTests(unittest.TestCase):

    def make_source(self):
        source = Universe(universe_id="timeline")
        source.create_quantum_box(
            box_id="first",
            rng=random.Random(1),
        )

        source.enable_quantum_layer()
        source.should_collapse_quantum_box = (
            lambda _box: False
        )

        source.tick_quantum_unprotected()

        source.create_quantum_box(
            box_id="second",
            rng=random.Random(2),
        )

        source.open_quantum_box(
            "first",
            rng=FixedChoice(),
        )

        source.tick_quantum_unprotected()

        source.open_quantum_box(
            "second",
            rng=FixedChoice(),
        )

        return source

    def test_merges_events_in_clock_order(self):
        source = self.make_source()

        timeline = source.quantum_lifecycle_timeline()

        self.assertEqual(
            [event.name for event in timeline],
            [
                "quantum_box_created",
                "universe_quantum_tick_advanced",
                "quantum_box_created",
                "quantum_box_collapsed",
                "quantum_box_disappeared",
                "universe_quantum_tick_advanced",
                "quantum_box_collapsed",
                "quantum_box_disappeared",
            ],
        )

        self.assertEqual(
            [event.tick for event in timeline],
            [0, 1, 1, 1, 1, 2, 2, 2],
        )

    def test_preserves_original_event_identity(self):
        source = self.make_source()
        timeline = source.quantum_lifecycle_timeline()

        original = (
            tuple(source.quantum_events)
            + tuple(source.quantum_clock_events)
        )

        self.assertEqual(len(timeline), len(original))

        self.assertEqual(
            {id(event) for event in timeline},
            {id(event) for event in original},
        )

        self.assertTrue(
            all(
                any(event is original_event for original_event in original)
                for event in timeline
            )
        )

    def test_is_read_only(self):
        source = self.make_source()

        boxes_before = tuple(source.quantum_events)
        clocks_before = tuple(source.quantum_clock_events)
        state_before = source.quantum_state.to_dict()

        first = source.quantum_lifecycle_timeline()
        second = source.quantum_lifecycle_timeline()

        self.assertEqual(first, second)
        self.assertIsInstance(first, tuple)
        self.assertEqual(tuple(source.quantum_events), boxes_before)
        self.assertEqual(tuple(source.quantum_clock_events), clocks_before)
        self.assertEqual(source.quantum_state.to_dict(), state_before)

    def test_preserves_multiple_actions_in_one_tick(self):
        source = Universe(universe_id="same-tick")

        source.create_quantum_box(
            box_id="one",
            rng=random.Random(3),
        )
        source.create_quantum_box(
            box_id="two",
            rng=random.Random(4),
        )

        source.open_quantum_box(
            "two",
            rng=FixedChoice(),
        )
        source.open_quantum_box(
            "one",
            rng=FixedChoice(),
        )

        timeline = source.quantum_lifecycle_timeline()

        self.assertEqual(
            timeline,
            tuple(source.quantum_events),
        )
        self.assertEqual(
            [event.tick for event in timeline],
            [0] * 6,
        )

    def test_empty_timeline(self):
        source = Universe(universe_id="empty-timeline")
        self.assertEqual(
            source.quantum_lifecycle_timeline(),
            (),
        )

    def test_generator_inputs(self):
        source = self.make_source()

        timeline = UniverseQuantumLifecycleTimeline.merge(
            box_events=(
                event for event in source.quantum_events
            ),
            clock_events=(
                event for event in source.quantum_clock_events
            ),
        )

        self.assertEqual(
            timeline,
            source.quantum_lifecycle_timeline(),
        )

    def test_future_box_tick_is_rejected(self):
        source = self.make_source()

        with self.assertRaises(ValueError):
            UniverseQuantumLifecycleTimeline.merge(
                box_events=source.quantum_events,
                clock_events=source.quantum_clock_events[:1],
            )

    def test_duplicate_clock_tick_is_rejected(self):
        source = self.make_source()
        clock = tuple(source.quantum_clock_events)

        with self.assertRaises(ValueError):
            UniverseQuantumLifecycleTimeline.merge(
                box_events=source.quantum_events,
                clock_events=(clock[0], clock[0]),
            )

    def test_invalid_lifecycle_order_is_rejected(self):
        source = self.make_source()
        events = tuple(source.quantum_events)

        with self.assertRaises(ValueError):
            UniverseQuantumLifecycleTimeline.merge(
                box_events=(events[2], events[0]),
                clock_events=source.quantum_clock_events,
            )

    def test_unsupported_events_are_not_silently_skipped(self):
        source = self.make_source()

        with self.assertRaises(TypeError):
            UniverseQuantumLifecycleTimeline.merge(
                box_events=(
                    *source.quantum_events,
                    object(),
                ),
                clock_events=source.quantum_clock_events,
            )


if __name__ == "__main__":
    unittest.main()
