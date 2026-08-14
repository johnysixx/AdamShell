import unittest

from universe.universe import Universe
from meeting_place.bar_geometry_terminal import BarGeometryTerminal


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
            for box in terminal
            .quantum_layer_map[
                "boxes"
            ]
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
            for box in terminal
            .quantum_layer_map[
                "boxes"
            ]
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
            terminal.status_sign[
                "cat_detected_light"
            ]
        )

        self.assertFalse(
            terminal.status_sign[
                "cat_arrived_light"
            ]
        )

        self.assertEqual(
            terminal.detected_cat_id,
            "traveler"
        )

        terminal.cat_arrived(
            "traveler"
        )

        self.assertFalse(
            terminal.status_sign[
                "cat_detected_light"
            ]
        )

        self.assertTrue(
            terminal.status_sign[
                "cat_arrived_light"
            ]
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

