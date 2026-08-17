from cats.cat_door import CatDoor


class CatDoorFactory:

    @classmethod
    def create(
        cls,
        name,
        source_layer,
        target_layer,
        source_location=None,
        target_location=None,
        source_position=None,
        target_position=None,
        destination_mode="fixed"
    ):
        return CatDoor(
            name=name,
            source_layer=source_layer,
            target_layer=target_layer,
            source_location=source_location,
            target_location=target_location,
            source_position=source_position,
            target_position=target_position,
            destination_mode=destination_mode
        )

    @classmethod
    def create_pair(
        cls,
        name,
        layer_a,
        layer_b,
        location_a=None,
        location_b=None,
        position_a=None,
        position_b=None
    ):
        forward = cls.create(
            name=f"{name}_forward",
            source_layer=layer_a,
            target_layer=layer_b,
            source_location=location_a,
            target_location=location_b,
            source_position=position_a,
            target_position=position_b
        )

        backward = cls.create(
            name=f"{name}_backward",
            source_layer=layer_b,
            target_layer=layer_a,
            source_location=location_b,
            target_location=location_a,
            source_position=position_b,
            target_position=position_a
        )

        return {
            "forward": forward,
            "backward": backward
        }

