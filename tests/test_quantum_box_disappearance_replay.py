import random
import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import patch

from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.manifestation_result_state import (
    CatManifestedEvent,
    EmptyQuantumBoxOpenedEvent,
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

    def choice(self, options):
        if self.value not in options:
            raise AssertionError("Invalid collapse outcome")
        return self.value


class QuantumBoxDisappearanceReplayTests(unittest.TestCase):

    def make_history(self):
        universe = Universe(universe_id="lifecycle")
        box = universe.create_quantum_box(
            box_id="lifecycle_box",
            rng=random.Random(42),
        )
        returned = universe.open_quantum_box(
            box.id,
            observer="replay_test",
            rng=FixedChoice("empty"),
        )
        return universe, box, returned

    def test_open_records_ordered_lifecycle(self):
        source, box, returned = self.make_history()

        self.assertIsInstance(
            returned, EmptyQuantumBoxOpenedEvent
        )
        self.assertEqual(len(source.quantum_events), 3)

        created, collapsed, disappeared = source.quantum_events

        self.assertIsInstance(created, QuantumBoxCreatedEvent)
        self.assertIsInstance(collapsed, QuantumBoxCollapsedEvent)
        self.assertIsInstance(
            disappeared, QuantumBoxDisappearedEvent
        )

        self.assertEqual(disappeared.box_id, box.id)
        self.assertEqual(disappeared.cause, "opened")
        self.assertEqual(disappeared.tick, 0)
        self.assertEqual(source.quantum_boxes, [])
        self.assertEqual(
            source.statistics.total_quantum_boxes_disappeared, 1
        )

    def test_complete_empty_lifecycle_replay(self):
        source, _, _ = self.make_history()
        target = Universe(universe_id="lifecycle")

        created, collapsed, disappeared = source.quantum_events

        target.replay_quantum_box_created(created)
        target.replay_quantum_box_collapsed(collapsed)
        removed = target.replay_quantum_box_disappeared(
            disappeared
        )

        self.assertEqual(removed.id, created.box_id)
        self.assertTrue(removed.collapse.collapsed)
        self.assertEqual(target.quantum_boxes, [])
        self.assertEqual(target.snapshot, source.snapshot)
        self.assertEqual(target.quantum_events, [])

    def test_disappearance_requires_prior_collapse(self):
        target = Universe(universe_id="uncollapsed")
        target.create_quantum_box(box_id="uncollapsed_box")

        event = QuantumBoxDisappearedEvent(
            box_id="uncollapsed_box",
            cause="opened",
            tick=0,
        )

        before = target.snapshot
        history = tuple(target.quantum_events)

        with self.assertRaises(ValueError):
            target.replay_quantum_box_disappeared(event)

        self.assertEqual(target.snapshot, before)
        self.assertEqual(tuple(target.quantum_events), history)

    def test_wrong_event_and_missing_box_are_rejected(self):
        target = Universe(universe_id="missing")

        with self.assertRaises(TypeError):
            target.replay_quantum_box_disappeared(
                {"name": "quantum_box_disappeared"}
            )

        event = QuantumBoxDisappearedEvent(
            box_id="missing_box",
            cause="opened",
            tick=0,
        )

        with self.assertRaises(ValueError):
            target.replay_quantum_box_disappeared(event)

        self.assertEqual(
            target.statistics.total_quantum_boxes_disappeared,
            0,
        )

    def test_duplicate_disappearance_is_rejected(self):
        source, _, _ = self.make_history()
        created, collapsed, disappeared = source.quantum_events

        target = Universe(universe_id="duplicate")
        target.replay_quantum_box_created(created)
        target.replay_quantum_box_collapsed(collapsed)
        target.replay_quantum_box_disappeared(disappeared)

        before = target.snapshot

        with self.assertRaises(ValueError):
            target.replay_quantum_box_disappeared(disappeared)

        self.assertEqual(target.snapshot, before)

    def test_event_is_immutable_and_serializable(self):
        event = QuantumBoxDisappearedEvent(
            box_id="immutable_box",
            cause="opened",
            tick=2,
        )

        with self.assertRaises(FrozenInstanceError):
            event.box_id = "changed"

        exported = event.to_dict()
        exported["box_id"] = "changed"

        self.assertEqual(event.box_id, "immutable_box")
        self.assertEqual(event.name, "quantum_box_disappeared")

        with self.assertRaises(TypeError):
            _ = event["box_id"]

    def test_spontaneous_disappearance_is_recorded(self):
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

        self.assertIsInstance(
            universe.quantum_events[-2],
            QuantumBoxCollapsedEvent,
        )

        event = universe.quantum_events[-1]

        self.assertIsInstance(
            event, QuantumBoxDisappearedEvent
        )
        self.assertEqual(event.box_id, box.id)
        self.assertEqual(event.cause, "spontaneous")
        self.assertEqual(event.tick, 1)
        self.assertNotIn(box, universe.quantum_boxes)

    def test_cat_manifestation_precedes_disappearance(self):
        universe = Universe(universe_id="manifestation")
        universe.enable_quantum_layer()

        box = universe.create_quantum_box(box_id="cat_box")

        returned = universe.open_quantum_box(
            box.id,
            observer="test",
            rng=FixedChoice("cat"),
        )

        self.assertIsInstance(returned, CatManifestedEvent)
        self.assertIs(universe.quantum_events[-2], returned)
        self.assertIsInstance(
            universe.quantum_events[-1],
            QuantumBoxDisappearedEvent,
        )
        self.assertEqual(
            universe.quantum_events[-1].box_id,
            box.id,
        )

    def test_replay_has_no_rng_or_new_history(self):
        source, _, _ = self.make_history()
        created, collapsed, disappeared = source.quantum_events

        target = Universe(universe_id="deterministic")
        target.replay_quantum_box_created(created)
        target.replay_quantum_box_collapsed(collapsed)

        original_history = tuple(source.quantum_events)
        clock_before = target.quantum_state.tick_count

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
            target.replay_quantum_box_disappeared(
                disappeared
            )

        self.assertEqual(target.quantum_events, [])
        self.assertEqual(
            target.quantum_state.tick_count,
            clock_before,
        )
        self.assertEqual(
            tuple(source.quantum_events),
            original_history,
        )


if __name__ == "__main__":
    unittest.main()
