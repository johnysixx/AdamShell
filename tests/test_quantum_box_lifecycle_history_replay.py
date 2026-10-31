import random
import unittest
from unittest.mock import patch

from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.quantum_box_disappearance_state import (
    QuantumBoxDisappearedEvent,
)
from universe.universe import Universe


class FixedChoice:
    def __init__(self, value):
        self.value = value

    def choice(self, possibilities):
        if self.value not in possibilities:
            raise AssertionError("Invalid collapse result")
        return self.value


class QuantumBoxLifecycleHistoryReplayTests(unittest.TestCase):

    def make_complete_history(self):
        source = Universe(universe_id="replay-world")

        box = source.create_quantum_box(
            rng=random.Random(123),
            box_id="box_alpha",
        )

        source.open_quantum_box(
            box.id,
            observer="test",
            rng=FixedChoice("empty"),
        )

        return source, tuple(source.quantum_events)

    def test_empty_history_is_noop(self):
        target = Universe(universe_id="empty")
        before = target.snapshot

        result = target.replay_quantum_box_history([])

        self.assertEqual(result, ())
        self.assertEqual(target.snapshot, before)
        self.assertEqual(target.quantum_events, [])

    def test_complete_empty_lifecycle(self):
        source, events = self.make_complete_history()
        target = Universe(universe_id="replay-world")

        result = target.replay_quantum_box_history(events)

        self.assertEqual(result, ())
        self.assertEqual(target.snapshot, source.snapshot)
        self.assertEqual(target.quantum_events, [])
        self.assertEqual(tuple(source.quantum_events), events)

    def test_multiple_interleaved_lifecycles(self):
        source = Universe(universe_id="multi")

        for index, layer in enumerate((
            "quantum_layer",
            "meeting_place",
            "quantum_layer",
        )):
            source.create_quantum_box(
                rng=random.Random(100 + index),
                box_id=f"multi_box_{index}",
                layer=layer,
            )

        source.open_quantum_box(
            "multi_box_0",
            rng=FixedChoice("empty"),
        )
        source.open_quantum_box(
            "multi_box_1",
            rng=FixedChoice("empty"),
        )

        target = Universe(universe_id="multi")
        result = target.replay_quantum_box_history(
            source.quantum_events
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "multi_box_2")
        self.assertEqual(target.snapshot, source.snapshot)
        self.assertEqual(target.quantum_events, [])

    def test_partial_lifecycle_preserves_collapsed_box(self):
        source, events = self.make_complete_history()
        target = Universe(universe_id="partial")

        result = target.replay_quantum_box_history(
            events[:2]
        )

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].collapse.collapsed)
        self.assertEqual(result[0].content.resolved, "empty")
        self.assertEqual(
            target.statistics.total_quantum_boxes_disappeared,
            0,
        )

    def test_out_of_order_events_are_atomic(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="bad-order")
        before = target.snapshot

        with self.assertRaises(ValueError):
            target.replay_quantum_box_history(
                (events[1], events[0])
            )

        self.assertEqual(target.snapshot, before)

    def test_duplicate_creation_is_atomic(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="duplicate")
        before = target.snapshot

        with self.assertRaises(ValueError):
            target.replay_quantum_box_history(
                (events[0], events[0])
            )

        self.assertEqual(target.snapshot, before)
        self.assertEqual(target.quantum_boxes, [])

    def test_disappearance_before_collapse_is_atomic(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="early-removal")
        before = target.snapshot

        with self.assertRaises(ValueError):
            target.replay_quantum_box_history(
                (events[0], events[2])
            )

        self.assertEqual(target.snapshot, before)

    def test_invalid_collapse_result_is_atomic(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="invalid-result")

        bad_event = QuantumBoxCollapsedEvent(
            quantum_box_id=events[0].box_id,
            result="impossible",
            cause="opened",
            observer=None,
            tick=0,
        )

        before = target.snapshot

        with self.assertRaises(ValueError):
            target.replay_quantum_box_history(
                (events[0], bad_event)
            )

        self.assertEqual(target.snapshot, before)
        self.assertEqual(target.quantum_events, [])

    def test_unsupported_event_is_not_silently_skipped(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="unsupported")
        before = target.snapshot

        with self.assertRaises(TypeError):
            target.replay_quantum_box_history(
                (events[0], object())
            )

        self.assertEqual(target.snapshot, before)

    def test_decreasing_timestamps_are_rejected(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="timestamps")

        late_creation = QuantumBoxCreatedEvent(
            box_id="late_box",
            position=events[0].position,
            layer="quantum_layer",
            tick=5,
        )

        early_collapse = QuantumBoxCollapsedEvent(
            quantum_box_id="late_box",
            result="empty",
            cause="opened",
            observer=None,
            tick=4,
        )

        with self.assertRaises(ValueError):
            target.replay_quantum_box_history(
                (late_creation, early_collapse)
            )

        self.assertEqual(target.quantum_boxes, [])

    def test_disappearance_cause_must_match_collapse(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="cause")

        bad_disappearance = QuantumBoxDisappearedEvent(
            box_id=events[2].box_id,
            cause="spontaneous",
            tick=0,
        )

        before = target.snapshot

        with self.assertRaises(ValueError):
            target.replay_quantum_box_history(
                (events[0], events[1], bad_disappearance)
            )

        self.assertEqual(target.snapshot, before)

    def test_no_randomness_or_uuid_during_replay(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="deterministic")

        with (
            patch(
                "core.entity.quantum_box.random.uniform",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.random.choice",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.uuid.uuid4",
                side_effect=AssertionError("UUID used"),
            ),
        ):
            target.replay_quantum_box_history(events)

        self.assertEqual(target.quantum_boxes, [])

    def test_existing_target_lifecycle_is_preserved(self):
        _, events = self.make_complete_history()
        target = Universe(universe_id="occupied")
        existing = target.create_quantum_box(
            box_id="existing"
        )
        before = target.snapshot
        history = tuple(target.quantum_events)

        with self.assertRaises(ValueError):
            target.replay_quantum_box_history(events)

        self.assertEqual(target.snapshot, before)
        self.assertIs(target.quantum_boxes[0], existing)
        self.assertEqual(tuple(target.quantum_events), history)

    def test_id_reuse_after_disappearance(self):
        source = Universe(universe_id="reuse")

        source.create_quantum_box(
            box_id="reused",
            rng=random.Random(1),
        )
        source.open_quantum_box(
            "reused",
            rng=FixedChoice("empty"),
        )
        source.create_quantum_box(
            box_id="reused",
            rng=random.Random(2),
        )

        target = Universe(universe_id="reuse")
        target.replay_quantum_box_history(
            source.quantum_events
        )

        self.assertEqual(target.snapshot, source.snapshot)
        self.assertEqual(len(target.quantum_boxes), 1)
        self.assertEqual(
            target.statistics.total_quantum_boxes_created,
            2,
        )
        self.assertEqual(
            target.statistics.total_quantum_boxes_disappeared,
            1,
        )

    def test_spontaneous_history_does_not_replay_clock(self):
        source = Universe(universe_id="spontaneous")
        source.enable_quantum_layer()
        source.create_quantum_box(box_id="spontaneous_box")
        source.should_collapse_quantum_box = lambda _: True

        with patch(
            "core.entity.quantum_box.random.choice",
            return_value="empty",
        ):
            source.tick_quantum_unprotected()

        target = Universe(universe_id="spontaneous")
        target.replay_quantum_box_history(
            source.quantum_events
        )

        self.assertEqual(target.quantum_boxes, [])
        self.assertEqual(
            target.statistics.public_state,
            source.statistics.public_state,
        )
        self.assertEqual(target.quantum_state.tick_count, 0)
        self.assertEqual(source.quantum_state.tick_count, 1)


if __name__ == "__main__":
    unittest.main()
