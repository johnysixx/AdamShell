import random
import unittest
from dataclasses import FrozenInstanceError

from core.entity.components import SpatialVector3
from universe.universe import Universe
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)


class QuantumBoxCreationHistoryTests(unittest.TestCase):

    def test_creation_records_complete_event(self):
        universe = Universe(universe_id="event-test")

        box = universe.create_quantum_box(
            rng=random.Random(123),
            box_id="box_event_1",
            layer="meeting_place",
        )

        event = universe.quantum_events[-1]

        self.assertIsInstance(event, QuantumBoxCreatedEvent)
        self.assertEqual(event.name, "quantum_box_created")
        self.assertEqual(event.box_id, box.id)
        self.assertEqual(event.position, box.position)
        self.assertEqual(event.layer, "meeting_place")
        self.assertEqual(event.tick, 0)

    def test_same_inputs_record_equal_events(self):
        first = Universe(universe_id="first")
        second = Universe(universe_id="second")

        first.create_quantum_box(
            rng=random.Random(987),
            box_id="box_replay_1",
        )

        second.create_quantum_box(
            rng=random.Random(987),
            box_id="box_replay_1",
        )

        self.assertEqual(
            first.quantum_events[-1],
            second.quantum_events[-1],
        )

    def test_duplicate_id_does_not_record_event(self):
        universe = Universe(universe_id="duplicate")

        universe.create_quantum_box(
            box_id="existing_box",
        )

        previous_events = tuple(universe.quantum_events)
        previous_count = (
            universe.statistics.total_quantum_boxes_created
        )

        with self.assertRaises(ValueError):
            universe.create_quantum_box(
                box_id="existing_box",
            )

        self.assertEqual(
            tuple(universe.quantum_events),
            previous_events,
        )
        self.assertEqual(
            universe.statistics.total_quantum_boxes_created,
            previous_count,
        )

    def test_event_is_object_state_with_detached_export(self):
        universe = Universe(universe_id="boundary")
        box = universe.create_quantum_box(
            box_id="boundary_box",
        )
        event = universe.quantum_events[-1]

        with self.assertRaises(TypeError):
            _ = event["box_id"]

        with self.assertRaises(FrozenInstanceError):
            event.box_id = "modified"

        snapshot = event.to_dict()
        snapshot["position"]["x"] = 999.0

        self.assertNotEqual(box.position.x, 999.0)
        self.assertNotEqual(event.position.x, 999.0)

    def test_automatic_id_is_recorded(self):
        universe = Universe(universe_id="automatic")

        box = universe.create_quantum_box(
            rng=random.Random(42),
        )
        event = universe.quantum_events[-1]

        self.assertRegex(
            box.id,
            r"^quantum_box_[0-9a-f]{8}$",
        )
        self.assertEqual(event.box_id, box.id)
        self.assertEqual(event.position, box.position)

    def test_creation_event_rejects_mapping_position(self):
        with self.assertRaises(TypeError):
            QuantumBoxCreatedEvent(
                box_id="invalid_box",
                position={"x": 0, "y": 0, "z": 0},
                layer="quantum_layer",
                tick=0,
            )


if __name__ == "__main__":
    unittest.main()
