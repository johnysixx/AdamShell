import unittest

from core.entity.components import SpatialVector3
from universe.quantum_universe_space import (
    QuantumStaircase,
    QuantumUniverseSpace,
)


class QuantumStaircaseObjectStateTests(unittest.TestCase):

    def test_staircase_uses_spatial_vector_objects(self):
        origin = SpatialVector3(x=1.0, y=2.0, z=3.0)
        destination = SpatialVector3(x=4.0, y=5.0, z=6.0)

        staircase = QuantumStaircase(
            id="staircase_test",
            origin=origin,
            destination=destination,
            orientation="up",
            length=2.5,
        )

        self.assertIs(staircase.origin, origin)
        self.assertIs(staircase.destination, destination)
        self.assertEqual(staircase.orientation, "up")
        self.assertEqual(staircase.length, 2.5)

    def test_staircase_rejects_mapping_positions(self):
        with self.assertRaises(TypeError):
            QuantumStaircase(
                id="legacy_origin",
                origin={"x": 1.0, "y": 2.0, "z": 3.0},
                destination=SpatialVector3.zero(),
                orientation="up",
                length=1.0,
            )

        with self.assertRaises(TypeError):
            QuantumStaircase(
                id="legacy_destination",
                origin=SpatialVector3.zero(),
                destination={"x": 1.0, "y": 2.0, "z": 3.0},
                orientation="down",
                length=1.0,
            )

    def test_to_dict_returns_detached_spatial_snapshots(self):
        staircase = QuantumStaircase(
            id="snapshot",
            origin=SpatialVector3(x=1.0, y=2.0, z=3.0),
            destination=SpatialVector3(x=4.0, y=5.0, z=6.0),
            orientation="left",
            length=3.0,
        )

        snapshot = staircase.to_dict()
        snapshot["origin"]["x"] = 99.0
        snapshot["destination"]["z"] = 99.0

        self.assertEqual(staircase.origin.x, 1.0)
        self.assertEqual(staircase.destination.z, 6.0)

    def test_generated_space_sample_contains_staircase_objects(self):
        space = QuantumUniverseSpace.__new__(QuantumUniverseSpace)
        space.configuration_seed = 12345

        sample = space.generate_space_sample("object-state", count=3)

        self.assertEqual(len(sample), 3)
        self.assertTrue(
            all(isinstance(item, QuantumStaircase) for item in sample)
        )
        self.assertTrue(
            all(isinstance(item.origin, SpatialVector3) for item in sample)
        )
        self.assertTrue(
            all(
                isinstance(item.destination, SpatialVector3)
                for item in sample
            )
        )

    def test_reconfigure_stores_staircase_objects(self):
        class DieBoxStub:
            def __init__(self):
                self.position = None

            def move_to(self, position):
                self.position = position

        die_box = DieBoxStub()
        space = QuantumUniverseSpace(die_box)

        self.assertGreaterEqual(len(space.staircases), 8)
        self.assertTrue(
            all(
                isinstance(staircase, QuantumStaircase)
                for staircase in space.staircases
            )
        )
        self.assertIsInstance(die_box.position, SpatialVector3)


if __name__ == "__main__":
    unittest.main()
