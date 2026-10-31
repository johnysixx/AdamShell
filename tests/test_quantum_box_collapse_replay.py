import random
import unittest
from unittest.mock import patch

from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.manifestation_result_state import (
    EmptyQuantumBoxOpenedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.universe import Universe


class FixedChoice:
    def __init__(self, value):
        self.value = value

    def choice(self, options):
        if self.value not in options:
            raise AssertionError("Invalid fixed collapse outcome")
        return self.value


class QuantumBoxCollapseReplayTests(unittest.TestCase):

    def make_collapsed_history(self):
        source = Universe(universe_id="source")
        box = source.create_quantum_box(
            box_id="replay_box",
            rng=random.Random(123),
        )
        returned = source.open_quantum_box(
            box.id,
            observer="tester",
            rng=FixedChoice("empty"),
        )
        return source, box, returned

    def test_open_records_creation_and_collapse(self):
        source, box, returned = self.make_collapsed_history()

        self.assertIsInstance(
            returned,
            EmptyQuantumBoxOpenedEvent,
        )
        self.assertEqual(len(source.quantum_events), 2)

        created, collapsed = source.quantum_events

        self.assertIsInstance(created, QuantumBoxCreatedEvent)
        self.assertIsInstance(collapsed, QuantumBoxCollapsedEvent)
        self.assertEqual(collapsed.quantum_box_id, box.id)
        self.assertEqual(collapsed.result, "empty")
        self.assertEqual(collapsed.cause, "opened")
        self.assertEqual(collapsed.observer, "tester")
        self.assertEqual(collapsed.tick, 0)
        self.assertEqual(source.quantum_boxes, [])

    def test_replay_reconstructs_collapsed_box(self):
        source, original, _ = self.make_collapsed_history()
        created, collapsed = source.quantum_events

        target = Universe(universe_id="target")
        restored = target.replay_quantum_box_created(created)
        result = target.replay_quantum_box_collapsed(collapsed)

        self.assertIsInstance(result, QuantumBoxCollapsedEvent)
        self.assertEqual(result, collapsed)
        self.assertEqual(restored.public_state, original.public_state)
        self.assertEqual(restored.collapse.cause, "opened")
        self.assertEqual(restored.collapse.observer, "tester")
        self.assertEqual(restored.collapse.tick, 0)
        self.assertEqual(
            target.statistics.total_quantum_collapses,
            1,
        )

    def test_collapse_replay_uses_no_randomness(self):
        source, _, _ = self.make_collapsed_history()
        created, collapsed = source.quantum_events

        target = Universe(universe_id="deterministic")
        target.replay_quantum_box_created(created)

        with (
            patch(
                "core.entity.quantum_box.random.choice",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.uuid.uuid4",
                side_effect=AssertionError("UUID used"),
            ),
        ):
            result = target.replay_quantum_box_collapsed(
                collapsed
            )

        self.assertEqual(result.result, "empty")

    def test_replay_does_not_append_history_or_advance_clock(self):
        source, _, _ = self.make_collapsed_history()
        created, collapsed = source.quantum_events

        target = Universe(universe_id="history")
        target.replay_quantum_box_created(created)

        previous = tuple(target.quantum_events)
        original_event = collapsed

        target.replay_quantum_box_collapsed(collapsed)

        self.assertEqual(
            tuple(target.quantum_events),
            previous,
        )
        self.assertIs(collapsed, original_event)
        self.assertEqual(target.quantum_state.tick_count, 0)

    def test_duplicate_collapse_replay_is_rejected(self):
        source, _, _ = self.make_collapsed_history()
        created, collapsed = source.quantum_events

        target = Universe(universe_id="duplicate")
        target.replay_quantum_box_created(created)
        target.replay_quantum_box_collapsed(collapsed)

        before = target.snapshot
        count = target.statistics.total_quantum_collapses

        with self.assertRaises(ValueError):
            target.replay_quantum_box_collapsed(collapsed)

        self.assertEqual(target.snapshot, before)
        self.assertEqual(
            target.statistics.total_quantum_collapses,
            count,
        )

    def test_replay_requires_existing_box(self):
        source, _, _ = self.make_collapsed_history()
        collapsed = source.quantum_events[-1]

        target = Universe(universe_id="missing")

        with self.assertRaises(ValueError):
            target.replay_quantum_box_collapsed(collapsed)

        self.assertEqual(
            target.statistics.total_quantum_collapses,
            0,
        )

    def test_replay_rejects_mapping_event(self):
        target = Universe(universe_id="invalid")

        with self.assertRaises(TypeError):
            target.replay_quantum_box_collapsed(
                {
                    "name": "quantum_box_collapsed",
                    "result": "empty",
                }
            )

    def test_invalid_result_does_not_mutate_box(self):
        target = Universe(universe_id="invalid-outcome")
        target.create_quantum_box(box_id="invalid_result_box")

        bad = QuantumBoxCollapsedEvent(
            quantum_box_id="invalid_result_box",
            result="impossible_result",
            cause="opened",
            observer=None,
            tick=0,
        )

        before = target.snapshot

        with self.assertRaises(ValueError):
            target.replay_quantum_box_collapsed(bad)

        self.assertEqual(target.snapshot, before)
        self.assertEqual(
            target.statistics.total_quantum_collapses,
            0,
        )

    def test_spontaneous_collapse_is_recorded(self):
        universe = Universe(universe_id="spontaneous")
        universe.enable_quantum_layer()
        box = universe.create_quantum_box(
            box_id="spontaneous_box"
        )

        universe.should_collapse_quantum_box = lambda _: True

        with patch(
            "core.entity.quantum_box.random.choice",
            return_value="empty",
        ):
            universe.tick_quantum_unprotected()

        collapsed = universe.quantum_events[-1]

        self.assertIsInstance(
            collapsed,
            QuantumBoxCollapsedEvent,
        )
        self.assertEqual(
            collapsed.quantum_box_id,
            box.id,
        )
        self.assertEqual(collapsed.cause, "spontaneous")
        self.assertEqual(collapsed.result, "empty")
        self.assertEqual(collapsed.tick, 1)
        self.assertNotIn(box, universe.quantum_boxes)


if __name__ == "__main__":
    unittest.main()
