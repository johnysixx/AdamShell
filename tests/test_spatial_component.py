from core.entity.components import SpatialVector3
import unittest

from core.entity.components import (
    SpatialComponent,
    SpatialVector3,
)
from core.entity.entity import Entity


class SpatialComponentTests(
    unittest.TestCase
):

    def test_spatial_component_moves_and_clears_position(self):
        spatial = SpatialComponent(
            layer="quantum_layer"
        )

        self.assertIsNone(
            spatial.position
        )

        self.assertFalse(
            spatial.has_position
        )

        position = SpatialVector3(
            x=3.0,
            y=4.0,
            z=0.0,
        )

        event = spatial.move_to(
            position,
            zone="hunting_area"
        )

        self.assertIs(
            spatial.position,
            position,
        )

        self.assertEqual(
            event["current_position"],
            {
                "x": 3.0,
                "y": 4.0,
                "z": 0.0
            }
        )

        self.assertEqual(
            spatial.layer,
            "quantum_layer"
        )

        self.assertEqual(
            spatial.zone,
            "hunting_area"
        )

        previous = spatial.clear_position()

        self.assertIs(
            previous,
            position,
        )

        self.assertIsNone(
            spatial.position
        )

    def test_entity_position_uses_spatial_component(self):
        entity = Entity(
            "spatial_entity"
        )

        self.assertIsNone(
            entity.position
        )

        original_position = SpatialVector3(
            x=1.0,
            y=2.0,
            z=3.0,
        )
        entity.position = original_position

        self.assertIs(
            entity.position,
            original_position,
        )
        self.assertIs(
            entity.position,
            entity.spatial.position,
        )

        new_position = SpatialVector3(
            x=4.0,
            y=5.0,
            z=6.0,
        )
        event = entity.move_to(
            new_position,
            layer="quantum_layer",
            zone="test_zone"
        )

        self.assertEqual(
            event["previous_position"],
            {
                "x": 1.0,
                "y": 2.0,
                "z": 3.0
            }
        )

        self.assertIs(
            entity.position,
            new_position,
        )

        self.assertEqual(
            entity.spatial.layer,
            "quantum_layer"
        )

        self.assertEqual(
            entity.spatial.zone,
            "test_zone"
        )

        entity.position = None

        self.assertIsNone(
            entity.position
        )

        self.assertFalse(
            entity.spatial.has_position
        )

    def test_spatial_component_requires_vector_objects(self):
        spatial = SpatialComponent()

        with self.assertRaises(TypeError):
            spatial.set_position({
                "x": 1.0,
                "y": 2.0,
                "z": 3.0,
            })

        with self.assertRaises(TypeError):
            spatial.set_velocity({
                "x": 1.0,
                "y": 0.0,
                "z": 0.0,
            })

        with self.assertRaises(TypeError):
            spatial.set_rotation({
                "x": 0.0,
                "y": 90.0,
                "z": 0.0,
            })

    def test_spatial_vectors_are_objects_with_detached_snapshots(self):
        vector = SpatialVector3(
            x=1,
            y=2,
            z=3,
        )

        self.assertEqual(vector.x, 1.0)
        self.assertEqual(vector.y, 2.0)
        self.assertEqual(vector.z, 3.0)
        self.assertEqual(
            vector.distance_to(
                SpatialVector3(
                    x=4,
                    y=6,
                    z=3,
                )
            ),
            5.0,
        )

        snapshot = vector.to_dict()
        snapshot["x"] = 99.0

        self.assertEqual(vector.x, 1.0)


if __name__ == "__main__":
    unittest.main()
