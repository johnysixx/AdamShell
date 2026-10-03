from cats.cat import Cat
from core.entity.components import require_optional_spatial_vector
from cats.cat_door_state import (
    CatDoorTravelDeniedResult,
    CatDoorTravelEvent,
)

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

        self.source_position = require_optional_spatial_vector(
            source_position,
            field_name="cat door source position",
        )
        self.target_position = require_optional_spatial_vector(
            target_position,
            field_name="cat door target position",
        )

        self.active = True
        self.cats_only = True

    def _travel_denied(
        self,
        cat,
        reason,
        target_layer=None,
        include_layers=False,
        include_locations=False,
    ):
        return (
            CatDoorTravelDeniedResult(
                door=self.name,
                cat=getattr(
                    cat,
                    "name",
                    None,
                ),
                reason=reason,
                source_layer=(
                    self.source_layer
                    if include_layers
                    else None
                ),
                target_layer=(
                    target_layer
                    if include_layers
                    else None
                ),
                source_location=(
                    self.source_location
                    if include_locations
                    else None
                ),
                target_location=(
                    self.target_location
                    if include_locations
                    else None
                ),
                cat_location=(
                    getattr(
                        cat,
                        "location",
                        None,
                    )
                    if include_locations
                    else None
                ),
            )
        )

    def travel(
        self,
        cat,
        source_entities=None,
        target_entities=None,
        chosen_target_layer=None
    ):
        if not self.active:
            return self._travel_denied(
                cat=cat,
                reason="door_inactive",
            )

        if not isinstance(
            cat,
            Cat
        ):
            return self._travel_denied(
                cat=cat,
                reason="entity_is_not_cat",
            )

        if (
            self.destination_mode
            == "cat_choice"
        ):
            if chosen_target_layer is None:
                return self._travel_denied(
                    cat=cat,
                    reason=(
                        "cat_target_layer_missing"
                    ),
                )

            target_layer = str(
                chosen_target_layer
            )
        else:
            target_layer = (
                self.target_layer
            )

        if (
            cat.current_layer
            != self.source_layer
        ):
            return self._travel_denied(
                cat=cat,
                reason=(
                    "cat_not_in_source_layer"
                ),
                target_layer=target_layer,
                include_layers=True,
            )

        if (
            self.source_location
            is not None
            and cat.location
            != self.source_location
        ):
            return self._travel_denied(
                cat=cat,
                reason=(
                    "cat_not_in_source_location"
                ),
                target_layer=target_layer,
                include_layers=True,
                include_locations=True,
            )

        learning = getattr(
            cat,
            "learning",
            None
        )

        skill = (
            learning.skills.get(
                "cat_door_travel"
            )
            if learning is not None
            else None
        )

        if (
            skill is None
            or not skill.learned
        ):
            return self._travel_denied(
                cat=cat,
                reason=(
                    "cat_door_travel_not_learned"
                ),
                target_layer=target_layer,
                include_layers=True,
            )

        if source_entities is not None:
            if cat not in source_entities:
                return self._travel_denied(
                    cat=cat,
                    reason=(
                        "cat_missing_from_"
                        "source_registry"
                    ),
                    target_layer=target_layer,
                    include_layers=True,
                )

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
            cat.move_to(
                self.target_position
            )

        cat.state = (
            "traveled_through_cat_door"
        )

        return (
            CatDoorTravelEvent(
                door=self.name,
                cat=cat.name,
                source_layer=(
                    self.source_layer
                ),
                target_layer=target_layer,
                source_location=(
                    self.source_location
                ),
                target_location=(
                    self.target_location
                ),
                source_position=(
                    self.source_position
                ),
                target_position=(
                    self.target_position
                ),
                source_registry_updated=(
                    source_entities
                    is not None
                ),
                target_registry_updated=(
                    target_entities
                    is not None
                ),
            )
        )

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
                self.source_position.to_dict()
                if self.source_position is not None
                else None
            ),
            "target_position": (
                self.target_position.to_dict()
                if self.target_position is not None
                else None
            ),
            "active": self.active,
            "cats_only": self.cats_only
        }


