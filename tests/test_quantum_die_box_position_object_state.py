import unittest
from types import SimpleNamespace

from core.entity.components import SpatialVector3
from core.entity.quantum_die_box import QuantumDieBox


class QuantumDieBoxPositionObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.box = QuantumDieBox(
            SimpleNamespace(name="quantum_die")
        )

    def test_position_is_spatial_vector(self):
        self.assertIsInstance(
            self.box.position,
            SpatialVector3,
        )
        self.assertEqual(
            self.box.position,
            SpatialVector3.zero(),
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    self.box.position,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = self.box.position["x"]

    def test_move_requires_spatial_vector(self):
        with self.assertRaises(TypeError):
            self.box.move_to(
                {
                    "x": 1.0,
                    "y": 2.0,
                    "z": 3.0,
                }
            )

        position = SpatialVector3(
            x=1.0,
            y=2.0,
            z=3.0,
        )
        moved = self.box.move_to(position)

        self.assertIs(moved, position)
        self.assertIs(self.box.position, position)
        self.assertEqual(
            self.box.state,
            "position_resolved",
        )

    def test_public_state_is_detached_dict(self):
        self.box.move_to(
            SpatialVector3(
                x=4.0,
                y=5.0,
                z=6.0,
            )
        )

        snapshot = self.box.public_state
        snapshot["position"]["x"] = 99.0

        self.assertEqual(
            self.box.position.x,
            4.0,
        )


if __name__ == "__main__":
    unittest.main()
