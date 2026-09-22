import unittest

from core.entity.components import SpatialVector3
from universe.quantum_universe_space import (
    QuantumLandmark,
    QuantumUniverseSpace,
)


class QuantumLandmarkObjectStateTests(unittest.TestCase):

    def test_landmark_uses_spatial_vector_position(self):
        position = SpatialVector3(x=1.0, y=2.0, z=3.0)
        landmark = QuantumLandmark(
            name="test_landmark",
            position=position,
        )

        self.assertEqual(landmark.name, "test_landmark")
        self.assertIs(landmark.position, position)

    def test_landmark_rejects_mapping_position(self):
        with self.assertRaises(TypeError):
            QuantumLandmark(
                name="legacy_landmark",
                position={"x": 1.0, "y": 2.0, "z": 3.0},
            )

    def test_to_dict_returns_detached_position_snapshot(self):
        landmark = QuantumLandmark(
            name="snapshot",
            position=SpatialVector3(x=1.0, y=2.0, z=3.0),
        )

        snapshot = landmark.to_dict()
        snapshot["position"]["x"] = 99.0

        self.assertEqual(landmark.position.x, 1.0)

    def test_quantum_space_stores_bar_front_door_as_landmark(self):
        class DieBoxStub:
            public_state = {}

            def move_to(self, position):
                self.position = position

        space = QuantumUniverseSpace(DieBoxStub())

        self.assertIsInstance(space.bar_front_door, QuantumLandmark)
        self.assertEqual(space.bar_front_door.name, "bar_front_door")
        self.assertEqual(space.bar_front_door.position, SpatialVector3.zero())

    def test_public_state_serializes_landmark_without_exposing_live_state(self):
        class DieBoxStub:
            public_state = {}

            def move_to(self, position):
                self.position = position

        space = QuantumUniverseSpace(DieBoxStub())

        snapshot = space.public_state
        snapshot["bar_front_door"]["position"]["x"] = 99.0

        self.assertEqual(space.bar_front_door.position.x, 0.0)


if __name__ == "__main__":
    unittest.main()
