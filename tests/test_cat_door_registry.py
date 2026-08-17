import unittest

from cats.cat_door_registry import (
    CatDoorRegistry
)


class CatDoorRegistryTests(
    unittest.TestCase
):

    def setUp(self):
        self.registry = (
            CatDoorRegistry()
        )

    def test_registry_creates_and_finds_door(
        self
    ):
        door = self.registry.create(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b"
        )

        found = self.registry.find(
            source_layer="layer_a",
            target_layer="layer_b"
        )

        self.assertIs(
            found,
            door
        )

    def test_registry_creates_pair(
        self
    ):
        pair = self.registry.create_pair(
            name="layer_pair",
            layer_a="layer_a",
            layer_b="layer_b"
        )

        self.assertIs(
            self.registry.find(
                source_layer="layer_a",
                target_layer="layer_b"
            ),
            pair["forward"]
        )

        self.assertIs(
            self.registry.find(
                source_layer="layer_b",
                target_layer="layer_a"
            ),
            pair["backward"]
        )

    def test_active_doors_from_layer(
        self
    ):
        first = self.registry.create(
            name="door_a_to_b",
            source_layer="layer_a",
            target_layer="layer_b"
        )

        second = self.registry.create(
            name="door_a_to_c",
            source_layer="layer_a",
            target_layer="layer_c"
        )

        ignored = self.registry.create(
            name="door_b_to_c",
            source_layer="layer_b",
            target_layer="layer_c"
        )

        ignored.active = False

        doors = (
            self.registry
            .active_doors_from(
                "layer_a"
            )
        )

        self.assertEqual(
            doors,
            [
                first,
                second
            ]
        )


    def test_registry_rejects_non_cat_door(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            self.registry.register(
                {
                    "type": "cat_door"
                }
            )

    def test_find_distinguishes_doors_by_location(
        self
    ):
        self.registry.create_pair(
            name="front",
            layer_a="layer_a",
            layer_b="layer_a",
            location_a="outside_front_door",
            location_b="inside_front_door"
        )

        self.registry.create_pair(
            name="back_room",
            layer_a="layer_a",
            layer_b="layer_a",
            location_a="layer_a",
            location_b="back_room"
        )

        door = self.registry.find(
            source_layer="layer_a",
            target_layer="layer_a",
            source_location="outside_front_door",
            target_location="inside_front_door"
        )

        self.assertEqual(
            door.name,
            "front_forward"
        )

if __name__ == "__main__":
    unittest.main()



