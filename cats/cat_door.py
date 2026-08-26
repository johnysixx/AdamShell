from cats.cat import Cat

class CatDoor:

    def __init__(
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
        self.name = str(name)
        self.type = "cat_door"

        self.destination_mode = str(
            destination_mode
        )

        if self.destination_mode not in {
            "fixed",
            "cat_choice"
        }:
            raise ValueError(
                "Unknown cat door destination mode."
            )

        self.source_layer = str(
            source_layer
        )

        self.target_layer = (
            str(target_layer)
            if target_layer is not None
            else None
        )

        if (
            self.destination_mode == "fixed"
            and self.target_layer is None
        ):
            raise ValueError(
                "Fixed cat door requires target_layer."
            )

        self.source_location = (
            str(source_location)
            if source_location is not None
            else None
        )

        self.target_location = (
            str(target_location)
            if target_location is not None
            else None
        )

        self.source_position = (
            dict(source_position)
            if source_position is not None
            else None
        )

        self.target_position = (
            dict(target_position)
            if target_position is not None
            else None
        )

        self.active = True
        self.cats_only = True

    def travel(
        self,
        cat,
        source_entities=None,
        target_entities=None,
        chosen_target_layer=None
    ):
        if not self.active:
            return {
                "name": "cat_door_travel_failed",
                "door": self.name,
                "cat": getattr(
                    cat,
                    "name",
                    None
                ),
                "reason": "door_inactive",
                "traveled": False
            }

        if not isinstance(
            cat,
            Cat
        ):
            return {
                "name": "cat_door_travel_failed",
                "door": self.name,
                "cat": getattr(
                    cat,
                    "name",
                    None
                ),
                "reason": "entity_is_not_cat",
                "traveled": False
            }

        if self.destination_mode == "cat_choice":
            if chosen_target_layer is None:
                return {
                    "name": "cat_door_travel_failed",
                    "door": self.name,
                    "cat": cat.name,
                    "reason": "cat_target_layer_missing",
                    "traveled": False
                }

            target_layer = str(
                chosen_target_layer
            )
        else:
            target_layer = (
                self.target_layer
            )

        if cat.current_layer != self.source_layer:
            return {
                "name": "cat_door_travel_failed",
                "door": self.name,
                "cat": cat.name,
                "reason": "cat_not_in_source_layer",
                "source_layer": self.source_layer,
                "target_layer": target_layer,
                "traveled": False
            }

        if (
            self.source_location is not None
            and cat.location != self.source_location
        ):
            return {
                "name": "cat_door_travel_failed",
                "door": self.name,
                "cat": cat.name,
                "reason": "cat_not_in_source_location",
                "source_layer": self.source_layer,
                "target_layer": target_layer,
                "source_location": self.source_location,
                "target_location": self.target_location,
                "cat_location": cat.location,
                "traveled": False
            }

        skill = (
            cat.learning
            .get(
                "skills",
                {}
            )
            .get(
                "cat_door_travel",
                {}
            )
        )

        if not skill.get(
            "learned",
            False
        ):
            return {
                "name": "cat_door_travel_failed",
                "door": self.name,
                "cat": cat.name,
                "reason": "cat_door_travel_not_learned",
                "source_layer": self.source_layer,
                "target_layer": target_layer,
                "traveled": False
            }

        if source_entities is not None:
            if cat not in source_entities:
                return {
                    "name": "cat_door_travel_failed",
                    "door": self.name,
                    "cat": cat.name,
                    "reason": "cat_missing_from_source_registry",
                    "source_layer": self.source_layer,
                    "target_layer": target_layer,
                    "traveled": False
                }

            source_entities.remove(
                cat
            )

        if target_entities is not None:
            if cat not in target_entities:
                target_entities.append(
                    cat
                )

        cat.current_layer = (
            target_layer
        )

        if self.target_location is not None:
            cat.location = (
                self.target_location
            )

        if self.target_position is not None:
            cat.position = dict(
                self.target_position
            )

        cat.state = (
            "traveled_through_cat_door"
        )

        return {
            "name": "cat_traveled_through_cat_door",
            "door": self.name,
            "cat": cat.name,
            "source_layer": self.source_layer,
            "target_layer": target_layer,
            "source_location": (
                self.source_location
            ),
            "target_location": (
                self.target_location
            ),
            "source_position": (
                dict(self.source_position)
                if self.source_position is not None
                else None
            ),
            "target_position": (
                dict(self.target_position)
                if self.target_position is not None
                else None
            ),
            "source_registry_updated": (
                source_entities is not None
            ),
            "target_registry_updated": (
                target_entities is not None
            ),
            "traveled": True
        }

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "destination_mode": (
                self.destination_mode
            ),
            "source_layer": (
                self.source_layer
            ),
            "target_layer": (
                self.target_layer
            ),
            "source_location": (
                self.source_location
            ),
            "target_location": (
                self.target_location
            ),
            "source_position": (
                dict(self.source_position)
                if self.source_position is not None
                else None
            ),
            "target_position": (
                dict(self.target_position)
                if self.target_position is not None
                else None
            ),
            "active": self.active,
            "cats_only": self.cats_only
        }


