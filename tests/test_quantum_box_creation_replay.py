import random
import unittest
from unittest.mock import patch

from core.entity.quantum_box import QuantumBox
from universe.universe import Universe
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)


class QuantumBoxCreationReplayTests(unittest.TestCase):

    def make_event(
        self,
        box_id="replay_box",
        layer="quantum_layer",
    ):
        source = Universe(universe_id="source")
        box = source.create_quantum_box(
            rng=random.Random(12345),
            box_id=box_id,
            layer=layer,
        )
        return source, box, source.quantum_events[-1]

    def test_replay_restores_complete_initial_box_state(self):
        source, original, event = self.make_event()
        target = Universe(universe_id="target")

        restored = target.replay_quantum_box_created(event)

        self.assertIsNot(restored, original)
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.position, original.position)
        self.assertEqual(
            restored.current_layer,
            original.current_layer,
        )
        self.assertEqual(
            restored.public_state,
            original.public_state,
        )
        self.assertEqual(
            target.statistics.total_quantum_boxes_created,
            1,
        )

    def test_replay_uses_no_randomness_or_uuid(self):
        _, _, event = self.make_event()
        target = Universe(universe_id="no-randomness")

        with (
            patch(
                "core.entity.quantum_box.random.uniform",
                side_effect=AssertionError("RNG was used"),
            ),
            patch(
                "core.entity.quantum_box.uuid.uuid4",
                side_effect=AssertionError("UUID was used"),
            ),
        ):
            restored = target.replay_quantum_box_created(
                event
            )

        self.assertEqual(restored.id, event.box_id)
        self.assertEqual(
            restored.position,
            event.position,
        )

    def test_duplicate_replay_is_rejected_atomically(self):
        _, _, event = self.make_event()
        target = Universe(universe_id="duplicate")

        first = target.replay_quantum_box_created(event)
        snapshot_before = target.snapshot
        history_before = tuple(target.quantum_events)

        with self.assertRaises(ValueError):
            target.replay_quantum_box_created(event)

        self.assertEqual(len(target.quantum_boxes), 1)
        self.assertIs(target.quantum_boxes[0], first)
        self.assertEqual(target.snapshot, snapshot_before)
        self.assertEqual(
            tuple(target.quantum_events),
            history_before,
        )

    def test_replay_rejects_mapping_and_wrong_event_type(self):
        target = Universe(universe_id="invalid")

        for invalid in (
            {"name": "quantum_box_created"},
            "quantum_box_created",
            None,
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    target.replay_quantum_box_created(invalid)

        self.assertEqual(target.quantum_boxes, [])
        self.assertEqual(target.quantum_events, [])

    def test_replay_does_not_emit_another_creation_event(self):
        source, original, event = self.make_event()
        target = Universe(universe_id="history")

        original_history = tuple(source.quantum_events)
        original_export = event.to_dict()

        restored = target.replay_quantum_box_created(event)

        self.assertIsNot(restored, original)
        self.assertEqual(target.quantum_events, [])
        self.assertEqual(
            tuple(source.quantum_events),
            original_history,
        )
        self.assertIs(source.quantum_events[-1], event)
        self.assertEqual(event.to_dict(), original_export)

    def test_replay_preserves_nonquantum_layer(self):
        _, original, event = self.make_event(
            layer="meeting_place"
        )
        target = Universe(universe_id="layer")

        restored = target.replay_quantum_box_created(event)

        self.assertEqual(
            restored.current_layer,
            "meeting_place",
        )
        self.assertEqual(
            restored.public_state,
            original.public_state,
        )
        self.assertEqual(
            target.snapshot["quantum_layer_map"]["boxes"],
            [],
        )

    def test_replay_does_not_advance_quantum_clock(self):
        source = Universe(universe_id="clock-source")
        source.quantum_state.advance_tick()
        source.quantum_state.advance_tick()

        source.create_quantum_box(
            box_id="clock_box",
            rng=random.Random(42),
        )
        event = source.quantum_events[-1]

        target = Universe(universe_id="clock-target")
        self.assertEqual(event.tick, 2)

        target.replay_quantum_box_created(event)

        self.assertEqual(
            target.quantum_state.tick_count,
            0,
        )

    def test_constructor_requires_object_position(self):
        with self.assertRaises(TypeError):
            QuantumBox(
                box_id="invalid_position",
                position={"x": 1, "y": 2, "z": 3},
            )

    def test_multiple_events_rebuild_same_box_snapshot(self):
        source = Universe(universe_id="same-world")

        for index, layer in enumerate(
            ("quantum_layer", "meeting_place", "quantum_layer")
        ):
            source.create_quantum_box(
                rng=random.Random(100 + index),
                box_id=f"replay_box_{index}",
                layer=layer,
            )

        target = Universe(universe_id="same-world")

        events = tuple(source.quantum_events)

        self.assertTrue(
            all(
                isinstance(event, QuantumBoxCreatedEvent)
                for event in events
            )
        )

        for event in events:
            target.replay_quantum_box_created(event)

        self.assertEqual(
            [box.public_state for box in source.quantum_boxes],
            [box.public_state for box in target.quantum_boxes],
        )
        self.assertEqual(source.snapshot, target.snapshot)
        self.assertEqual(
            source.statistics.total_quantum_boxes_created,
            target.statistics.total_quantum_boxes_created,
        )
        self.assertEqual(
            len(target.quantum_events),
            0,
        )


if __name__ == "__main__":
    unittest.main()
