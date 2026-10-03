import unittest

from cats.cat_door import CatDoor
from cats.cat_door_state import (
    CatDoorTravelDeniedResult,
    CatDoorTravelEvent,
)
from cats.cats import Cats
from core.entity.components import (
    SpatialVector3,
)
from universe.universe import Universe


class CatDoorTravelObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cat = (
            Cats(
                self.universe
            )
            .create_cat(
                name="traveler",
                color="black",
                fur_length="short",
            )
        )

        self.cat.current_layer = (
            "layer_a"
        )

        self.cat.learning.skills[
            "cat_door_travel"
        ].learned = True

    def assert_not_mapping(
        self,
        result,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "traveled"
            ]

    def test_success_returns_travel_event_object(
        self
    ):
        source_position = (
            SpatialVector3(
                x=1.0,
                y=2.0,
                z=3.0,
            )
        )

        target_position = (
            SpatialVector3(
                x=4.0,
                y=5.0,
                z=6.0,
            )
        )

        door = CatDoor(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b",
            source_position=(
                source_position
            ),
            target_position=(
                target_position
            ),
        )

        result = door.travel(
            self.cat
        )

        self.assertIsInstance(
            result,
            CatDoorTravelEvent,
        )

        self.assertTrue(
            result.traveled
        )

        self.assertIs(
            result.source_position,
            source_position,
        )

        self.assertIs(
            result.target_position,
            target_position,
        )

        self.assertIs(
            self.cat.position,
            target_position,
        )

        self.assert_not_mapping(
            result
        )

    def test_denied_travel_returns_result_object(
        self
    ):
        door = CatDoor(
            name="door_a_to_b",
            source_layer="wrong_layer",
            target_layer="layer_b",
        )

        result = door.travel(
            self.cat
        )

        self.assertIsInstance(
            result,
            CatDoorTravelDeniedResult,
        )

        self.assertFalse(
            result.traveled
        )

        self.assertEqual(
            result.reason,
            "cat_not_in_source_layer",
        )

        self.assertEqual(
            result.source_layer,
            "wrong_layer",
        )

        self.assertEqual(
            result.target_layer,
            "layer_b",
        )

        self.assert_not_mapping(
            result
        )

    def test_success_boundary_snapshot_is_detached(
        self
    ):
        target_position = (
            SpatialVector3(
                x=4.0,
                y=5.0,
                z=6.0,
            )
        )

        door = CatDoor(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b",
            target_position=(
                target_position
            ),
        )

        result = door.travel(
            self.cat
        )

        boundary = (
            result.to_dict()
        )

        boundary[
            "target_position"
        ][
            "x"
        ] = 999.0

        self.assertEqual(
            result.target_position.x,
            4.0,
        )

        self.assertIs(
            result.target_position,
            target_position,
        )


if __name__ == "__main__":
    unittest.main()
