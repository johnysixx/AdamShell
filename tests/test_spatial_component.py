import unittest

from core.entity.components import SpatialComponent
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

        event = spatial.move_to(
            {
                "x": 3.0,
                "y": 4.0,
                "z": 0.0
            },
            zone="hunting_area"
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

        self.assertEqual(
            previous,
            {
                "x": 3.0,
                "y": 4.0,
                "z": 0.0
            }
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

        entity.position = {
            "x": 1.0,
            "y": 2.0,
            "z": 3.0
        }

        self.assertEqual(
            entity.position,
            entity.spatial.position
        )

        event = entity.move_to(
            {
                "x": 4.0,
                "y": 5.0,
                "z": 6.0
            },
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

        self.assertEqual(
            entity.position,
            {
                "x": 4.0,
                "y": 5.0,
                "z": 6.0
            }
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


if __name__ == "__main__":
    unittest.main()