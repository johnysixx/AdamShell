import unittest

from cats.cat_door import CatDoor
from cats.cat_door_factory import (
    CatDoorFactory
)
from cats.cats import Cats
from universe.universe import Universe


class CatDoorFactoryTests(
    unittest.TestCase
):

    def make_cat(
        self,
        name,
        current_layer,
        location=None,
        trained=True,
        origin_layer=None
    ):
        universe = Universe()

        cats = Cats(
            universe
        )

        cat = cats.create_cat(
            name=name,
            color="black",
            fur_length="short"
        )

        cat.current_layer = (
            current_layer
        )

        cat.location = location

        if origin_layer is not None:
            cat.origin_layer = (
                origin_layer
            )

        cat.learning[
            "skills"
        ][
            "cat_door_travel"
        ][
            "learned"
        ] = bool(
            trained
        )

        return cat

    def test_create_cat_door(
        self
    ):
        door = CatDoorFactory.create(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b"
        )

        self.assertIsInstance(
            door,
            CatDoor
        )

        self.assertEqual(
            door.name,
            "door_a_to_b"
        )

        self.assertEqual(
            door.source_layer,
            "layer_a"
        )

        self.assertEqual(
            door.target_layer,
            "layer_b"
        )

        self.assertTrue(
            door.active
        )

        self.assertTrue(
            door.cats_only
        )

    def test_create_cat_door_pair(
        self
    ):
        pair = (
            CatDoorFactory
            .create_pair(
                name="layer_pair",
                layer_a="layer_a",
                layer_b="layer_b"
            )
        )

        forward = pair[
            "forward"
        ]

        backward = pair[
            "backward"
        ]

        self.assertEqual(
            forward.source_layer,
            "layer_a"
        )

        self.assertEqual(
            forward.target_layer,
            "layer_b"
        )

        self.assertEqual(
            backward.source_layer,
            "layer_b"
        )

        self.assertEqual(
            backward.target_layer,
            "layer_a"
        )

        self.assertNotEqual(
            forward.name,
            backward.name
        )


    def test_cat_can_travel_through_door(
        self
    ):
        door = CatDoorFactory.create(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b"
        )

        cat = self.make_cat(
            name="traveler",
            current_layer="layer_a"
        )

        result = door.travel(
            cat
        )

        self.assertTrue(
            result["traveled"]
        )

        self.assertEqual(
            cat.current_layer,
            "layer_b"
        )

        self.assertEqual(
            result["source_layer"],
            "layer_a"
        )

        self.assertEqual(
            result["target_layer"],
            "layer_b"
        )

    def test_cat_door_rejects_cat_in_wrong_layer(
        self
    ):
        door = CatDoorFactory.create(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b"
        )

        cat = self.make_cat(
            name="traveler",
            current_layer="quantum_layer"
        )

        result = door.travel(
            cat
        )

        self.assertFalse(
            result["traveled"]
        )

        self.assertEqual(
            result["reason"],
            "cat_not_in_source_layer"
        )

        self.assertEqual(
            cat.current_layer,
            "quantum_layer"
        )

    def test_cat_door_rejects_untrained_kitten(
        self
    ):
        door = CatDoorFactory.create(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b"
        )

        kitten = self.make_cat(
            name="kitten",
            current_layer="layer_a",
            trained=False
        )

        result = door.travel(
            kitten
        )

        self.assertFalse(
            result["traveled"]
        )

        self.assertEqual(
            result["reason"],
            "cat_door_travel_not_learned"
        )

        self.assertEqual(
            kitten.current_layer,
            "layer_a"
        )

    def test_cat_door_moves_cat_between_layer_registries(
        self
    ):
        door = CatDoorFactory.create(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b"
        )

        cat = self.make_cat(
            name="traveler",
            current_layer="layer_a",
            origin_layer="quantum_layer"
        )

        source_entities = [
            cat
        ]

        target_entities = []

        result = door.travel(
            cat,
            source_entities=source_entities,
            target_entities=target_entities
        )

        self.assertTrue(
            result["traveled"]
        )

        self.assertNotIn(
            cat,
            source_entities
        )

        self.assertIn(
            cat,
            target_entities
        )

        self.assertEqual(
            cat.current_layer,
            "layer_b"
        )

        self.assertEqual(
            cat.origin_layer,
            "quantum_layer"
        )

    def test_cat_door_can_have_positions(
        self
    ):
        door = CatDoorFactory.create(
            name="positioned_door",
            source_layer="layer_a",
            target_layer="layer_b",
            source_position={
                "x": 5.0,
                "y": 1.0,
                "z": 0.0
            },
            target_position={
                "x": 2.0,
                "y": 3.0,
                "z": 0.0
            }
        )

        self.assertEqual(
            door.source_position,
            {
                "x": 5.0,
                "y": 1.0,
                "z": 0.0
            }
        )

        self.assertEqual(
            door.target_position,
            {
                "x": 2.0,
                "y": 3.0,
                "z": 0.0
            }
        )

        self.assertEqual(
            door.public_state[
                "source_position"
            ],
            {
                "x": 5.0,
                "y": 1.0,
                "z": 0.0
            }
        )

    def test_cat_door_can_have_semantic_locations(
        self
    ):
        door = CatDoorFactory.create(
            name="front_cat_door",
            source_layer="layer_a",
            target_layer="layer_a",
            source_location="outside_front_door",
            target_location="inside_front_door",
            source_position={
                "x": 1.0,
                "y": 0.0,
                "z": 0.0
            },
            target_position={
                "x": 1.2,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.assertEqual(
            door.source_location,
            "outside_front_door"
        )

        self.assertEqual(
            door.target_location,
            "inside_front_door"
        )

        self.assertEqual(
            door.public_state[
                "source_location"
            ],
            "outside_front_door"
        )

        self.assertEqual(
            door.public_state[
                "target_location"
            ],
            "inside_front_door"
        )

    def test_cat_door_rejects_cat_in_wrong_location(
        self
    ):
        door = CatDoorFactory.create(
            name="front_cat_door",
            source_layer="layer_a",
            target_layer="layer_a",
            source_location="outside_front_door",
            target_location="inside_front_door"
        )

        cat = self.make_cat(
            name="micka",
            current_layer="layer_a",
            location="behind_bar"
        )

        result = door.travel(cat)

        self.assertFalse(
            result["traveled"]
        )

        self.assertEqual(
            result["reason"],
            "cat_not_in_source_location"
        )

        self.assertEqual(
            cat.location,
            "behind_bar"
        )

    def test_cat_door_moves_cat_to_target_location(
        self
    ):
        door = CatDoorFactory.create(
            name="front_cat_door",
            source_layer="layer_a",
            target_layer="layer_a",
            source_location="outside_front_door",
            target_location="inside_front_door"
        )

        cat = self.make_cat(
            name="micka",
            current_layer="layer_a",
            location="outside_front_door"
        )

        result = door.travel(cat)

        self.assertTrue(
            result["traveled"]
        )

        self.assertEqual(
            cat.current_layer,
            "layer_a"
        )

        self.assertEqual(
            cat.location,
            "inside_front_door"
        )

    def test_cat_choice_door_uses_cat_selected_target_layer(
        self
    ):
        door = CatDoorFactory.create(
            name="world_cat_door",
            source_layer="meeting_place",
            target_layer=None,
            source_location="back_room",
            destination_mode="cat_choice"
        )

        cat = self.make_cat(
            name="micka",
            current_layer="meeting_place",
            location="back_room"
        )

        result = door.travel(
            cat,
            chosen_target_layer="root_universe"
        )

        self.assertTrue(
            result["traveled"]
        )

        self.assertEqual(
            door.destination_mode,
            "cat_choice"
        )

        self.assertIsNone(
            door.target_layer
        )

        self.assertEqual(
            cat.current_layer,
            "root_universe"
        )

        self.assertEqual(
            result["target_layer"],
            "root_universe"
        )


    def test_cat_choice_door_requires_cat_selected_target_layer(
        self
    ):
        door = CatDoorFactory.create(
            name="world_cat_door",
            source_layer="meeting_place",
            target_layer=None,
            source_location="back_room",
            destination_mode="cat_choice"
        )

        cat = self.make_cat(
            name="micka",
            current_layer="meeting_place",
            location="back_room"
        )

        result = door.travel(
            cat
        )

        self.assertFalse(
            result["traveled"]
        )

        self.assertEqual(
            result["reason"],
            "cat_target_layer_missing"
        )

        self.assertEqual(
            cat.current_layer,
            "meeting_place"
        )

        self.assertEqual(
            cat.location,
            "back_room"
        )


if __name__ == "__main__":
    unittest.main()








