import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from cats.cats import Cats
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)


class CatDoorIntegrationTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        bootstrap = UniverseBootstrap(
            UniverseRegistry(),
            self.universe
        )

        (
            self.root_transition,
            self.layers,
            self.idea_universe
        ) = bootstrap.run()

        self.meeting_place = (
            self.universe.meeting_place
        )

    def test_cat_travels_through_front_cat_door(
        self
    ):
        cats = Cats(
            self.universe
        )

        cat = cats.create_cat(
            name="door_traveler",
            color="black",
            fur_length="short"
        )

        cat.origin_layer = (
            "quantum_layer"
        )

        cat.current_layer = (
            "meeting_place"
        )

        cat.location = (
            "outside_front_door"
        )

        cat.learning[
            "skills"
        ][
            "cat_door_travel"
        ][
            "learned"
        ] = True

        door = (
            self.universe
            .cat_door_registry
            .find(
                source_layer="meeting_place",
                target_layer="meeting_place",
                source_location="outside_front_door",
                target_location="inside_front_door"
            )
        )

        self.assertIsNotNone(
            door
        )

        result = door.travel(
            cat
        )

        self.assertTrue(
            result["traveled"]
        )

        self.assertEqual(
            cat.current_layer,
            "meeting_place"
        )

        self.assertEqual(
            cat.location,
            "inside_front_door"
        )

        self.assertEqual(
            cat.origin_layer,
            "quantum_layer"
        )

    def test_boot_registers_all_fixed_cat_doors(
        self
    ):
        registry = (
            self.universe.cat_door_registry
        )

        front_in = registry.find(
            source_layer="meeting_place",
            target_layer="meeting_place",
            source_location="outside_front_door",
            target_location="inside_front_door"
        )

        front_out = registry.find(
            source_layer="meeting_place",
            target_layer="meeting_place",
            source_location="inside_front_door",
            target_location="outside_front_door"
        )

        back_in = registry.find(
            source_layer="meeting_place",
            target_layer="meeting_place",
            source_location="meeting_place",
            target_location="back_room"
        )

        back_out = registry.find(
            source_layer="meeting_place",
            target_layer="meeting_place",
            source_location="back_room",
            target_location="meeting_place"
        )

        self.assertIsNotNone(
            front_in
        )

        self.assertIsNotNone(
            front_out
        )

        self.assertIsNotNone(
            back_in
        )

        self.assertIsNotNone(
            back_out
        )

        self.assertEqual(
            front_in.name,
            "front_cat_door_forward"
        )

        self.assertEqual(
            front_out.name,
            "front_cat_door_backward"
        )

        self.assertEqual(
            back_in.name,
            "back_room_cat_door_forward"
        )

        self.assertEqual(
            back_out.name,
            "back_room_cat_door_backward"
        )

        fixed_doors = [
            door
            for door in registry.doors
            if door.destination_mode == "fixed"
        ]

        self.assertEqual(
            len(fixed_doors),
            4
        )


    def test_boot_registers_world_cat_door(
        self
    ):
        registry = (
            self.universe.cat_door_registry
        )

        door = registry.find(
            source_layer="meeting_place",
            target_layer=None,
            source_location="back_room"
        )

        self.assertIsNotNone(
            door
        )

        self.assertEqual(
            door.name,
            "world_cat_door"
        )

        self.assertEqual(
            door.destination_mode,
            "cat_choice"
        )

        self.assertEqual(
            door.source_layer,
            "meeting_place"
        )

        self.assertEqual(
            door.source_location,
            "back_room"
        )

        self.assertIsNone(
            door.target_layer
        )


    def test_back_room_references_registered_world_cat_door(
        self
    ):
        registry = (
            self.universe.cat_door_registry
        )

        registered_door = registry.find(
            source_layer="meeting_place",
            target_layer=None,
            source_location="back_room"
        )

        attached_door = (
            self.meeting_place
            .back_room
            .world_door
            .cat_door
        )

        self.assertIsNotNone(
            registered_door
        )

        self.assertIs(
            attached_door,
            registered_door
        )

        self.assertNotIn(
            "has_cat_door",
            vars(self.meeting_place.back_room.world_door)
        )


    def test_back_room_public_state_exposes_world_cat_door_state(
        self
    ):
        state = (
            self.meeting_place
            .back_room
            .public_state
        )

        cat_door_state = (
            state["world_door"][
                "cat_door"
            ]
        )

        self.assertIsInstance(
            cat_door_state,
            dict
        )

        self.assertEqual(
            cat_door_state["name"],
            "world_cat_door"
        )

        self.assertEqual(
            cat_door_state["destination_mode"],
            "cat_choice"
        )

        self.assertIsNone(
            cat_door_state["target_layer"]
        )


if __name__ == "__main__":
    unittest.main()



