import unittest

from universe.universe import Universe
from meeting_place.bar_geometry_terminal import (
    BarGeometryTerminal,
    BarQuantumLayerMapState,
)


class BarQuantumLayerMapTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

    def test_snapshot_contains_only_quantum_layer_boxes(
        self
    ):
        quantum_box = (
            self.universe
            .create_quantum_box(
                layer="quantum_layer"
            )
        )

        remote_box = (
            self.universe
            .create_quantum_box(
                layer="meeting_place"
            )
        )

        snapshot = self.universe.snapshot

        quantum_map = snapshot[
            "quantum_layer_map"
        ]

        box_ids = [
            box["id"]
            for box in quantum_map[
                "boxes"
            ]
        ]

        self.assertIn(
            quantum_box.id,
            box_ids
        )

        self.assertNotIn(
            remote_box.id,
            box_ids
        )

        self.assertNotIn(
            "cats",
            quantum_map
        )

        self.assertIn(
            "space",
            quantum_map
        )

    def test_terminal_map_is_typed_object_state(self):
        terminal = BarGeometryTerminal()
        state = terminal.quantum_layer_map

        self.assertIsInstance(
            state,
            BarQuantumLayerMapState,
        )

        self.assertIsNone(state.tick)
        self.assertEqual(state.boxes, ())
        self.assertEqual(state.space, {})

        for method in ("get", "keys", "items", "values"):
            self.assertFalse(
                hasattr(state, method)
            )

        with self.assertRaises(TypeError):
            _ = state["boxes"]

        self.assertEqual(
            terminal.public_state["quantum_layer_map"],
            {
                "tick": None,
                "boxes": [],
                "space": {},
            },
        )

    def test_terminal_map_snapshots_are_detached(self):
        terminal = BarGeometryTerminal()

        source = {
            "quantum_layer_map": {
                "tick": 7,
                "boxes": [
                    {
                        "id": "test_box",
                        "metadata": {
                            "tags": ["original"],
                        },
                    },
                ],
                "space": {
                    "nested": {
                        "value": 1,
                    },
                },
            },
        }

        terminal.refresh(source)

        state = terminal.quantum_layer_map
        self.assertIsInstance(
            state,
            BarQuantumLayerMapState,
        )

        source["quantum_layer_map"]["boxes"][0][
            "metadata"
        ]["tags"].append("external")

        source["quantum_layer_map"]["space"][
            "nested"
        ]["value"] = 99

        self.assertEqual(
            state.boxes[0]["metadata"]["tags"],
            ["original"],
        )

        self.assertEqual(
            state.space["nested"]["value"],
            1,
        )

        first = terminal.public_state["quantum_layer_map"]
        second = terminal.public_state["quantum_layer_map"]

        first["boxes"][0]["metadata"][
            "tags"
        ].append("snapshot_only")

        first["space"]["nested"]["value"] = -1

        self.assertEqual(
            second["boxes"][0]["metadata"]["tags"],
            ["original"],
        )

        self.assertEqual(
            second["space"]["nested"]["value"],
            1,
        )

        self.assertEqual(
            state.boxes[0]["metadata"]["tags"],
            ["original"],
        )

    def test_terminal_refresh_replaces_typed_map_atomically(
        self
    ):
        terminal = BarGeometryTerminal()

        original = terminal.quantum_layer_map

        terminal.refresh({
            "quantum_layer_map": {
                "tick": 2,
                "boxes": [{"id": "first"}],
                "space": {},
            },
        })

        first_state = terminal.quantum_layer_map

        self.assertIsNot(
            first_state,
            original,
        )

        terminal.refresh({
            "quantum_layer_map": {
                "tick": 3,
                "boxes": [{"id": "second"}],
                "space": {},
            },
        })

        second_state = terminal.quantum_layer_map

        self.assertIsNot(
            second_state,
            first_state,
        )

        self.assertEqual(
            first_state.boxes[0]["id"],
            "first",
        )

        self.assertEqual(
            second_state.boxes[0]["id"],
            "second",
        )

        with self.assertRaises(TypeError):
            terminal.refresh({
                "quantum_layer_map": {
                    "boxes": [object()],
                    "space": {},
                },
            })

        self.assertIs(
            terminal.quantum_layer_map,
            second_state,
        )

    def test_terminal_replaces_old_quantum_map(
        self
    ):
        terminal = BarGeometryTerminal()

        first_box = (
            self.universe
            .create_quantum_box()
        )

        terminal.refresh(
            self.universe.snapshot
        )

        first_ids = [
            box["id"]
            for box in terminal.quantum_layer_map.boxes
        ]

        self.assertIn(
            first_box.id,
            first_ids
        )

        self.universe.quantum_boxes.remove(
            first_box
        )

        second_box = (
            self.universe
            .create_quantum_box()
        )

        terminal.refresh(
            self.universe.snapshot
        )

        second_ids = [
            box["id"]
            for box in terminal.quantum_layer_map.boxes
        ]

        self.assertNotIn(
            first_box.id,
            second_ids
        )

        self.assertIn(
            second_box.id,
            second_ids
        )


    def test_cat_status_sign_switches_lights(
        self
    ):
        terminal = BarGeometryTerminal()

        terminal.cat_detected(
            "traveler"
        )

        self.assertTrue(
            terminal.status_sign.cat_detected_light
        )

        self.assertFalse(
            terminal.status_sign.cat_arrived_light
        )

        self.assertEqual(
            terminal.detected_cat_id,
            "traveler"
        )

        terminal.cat_arrived(
            "traveler"
        )

        self.assertFalse(
            terminal.status_sign.cat_detected_light
        )

        self.assertTrue(
            terminal.status_sign.cat_arrived_light
        )

        self.assertIsNone(
            terminal.detected_cat_id
        )

        self.assertEqual(
            terminal.arrived_cat_id,
            "traveler"
        )

if __name__ == "__main__":
    unittest.main()

