from cats.cat_door import CatDoor
from cats.cat_door_factory import (
    CatDoorFactory
)


class CatDoorRegistry:

    def __init__(self):
        self.doors = []

    def register(
        self,
        door
    ):
        if not isinstance(
            door,
            CatDoor
        ):
            raise TypeError(
                "CatDoorRegistry accepts only CatDoor instances."
            )

        if door not in self.doors:
            self.doors.append(
                door
            )

        return door

    def create(
        self,
        name,
        source_layer,
        target_layer,
        source_location=None,
        target_location=None,
        source_position=None,
        target_position=None,
        destination_mode="fixed"
    ):
        door = CatDoorFactory.create(
            name=name,
            source_layer=source_layer,
            target_layer=target_layer,
            source_location=source_location,
            target_location=target_location,
            source_position=source_position,
            target_position=target_position,
            destination_mode=destination_mode
        )

        return self.register(
            door
        )

    def create_pair(
        self,
        name,
        layer_a,
        layer_b,
        location_a=None,
        location_b=None,
        position_a=None,
        position_b=None
    ):
        pair = (
            CatDoorFactory
            .create_pair(
                name=name,
                layer_a=layer_a,
                layer_b=layer_b,
                location_a=location_a,
                location_b=location_b,
                position_a=position_a,
                position_b=position_b
            )
        )

        self.register(
            pair["forward"]
        )

        self.register(
            pair["backward"]
        )

        return pair

    def find(
        self,
        source_layer,
        target_layer,
        source_location=None,
        target_location=None
    ):
        for door in self.doors:
            if not door.active:
                continue

            if (
                door.source_layer
                != source_layer
            ):
                continue

            if (
                door.target_layer
                != target_layer
            ):
                continue

            if (
                source_location is not None
                and door.source_location
                != source_location
            ):
                continue

            if (
                target_location is not None
                and door.target_location
                != target_location
            ):
                continue

            return door

        return None

    def active_doors_from(
        self,
        source_layer
    ):
        return [
            door
            for door in self.doors
            if door.active
            and door.source_layer
            == source_layer
        ]

    @property
    def public_state(self):
        return {
            "type": "cat_door_registry",
            "door_count": len(
                self.doors
            ),
            "doors": [
                door.public_state
                for door in self.doors
            ]
        }


