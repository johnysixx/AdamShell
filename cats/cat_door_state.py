from dataclasses import dataclass, field

from core.entity.components import (
    SpatialVector3,
    require_optional_spatial_vector,
)


@dataclass(slots=True, frozen=True)
class CatDoorTravelDeniedResult:
    door: str
    cat: str | None
    reason: str
    source_layer: str | None = None
    target_layer: str | None = None
    source_location: str | None = None
    target_location: str | None = None
    cat_location: str | None = None

    name: str = field(
        default="cat_door_travel_failed",
        init=False,
    )

    traveled: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "door",
            str(self.door),
        )

        if self.cat is not None:
            object.__setattr__(
                self,
                "cat",
                str(self.cat),
            )

        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )



@dataclass(slots=True, frozen=True)
class CatDoorTravelEvent:
    door: str
    cat: str
    source_layer: str
    target_layer: str
    source_location: str | None
    target_location: str | None
    source_position: SpatialVector3 | None
    target_position: SpatialVector3 | None
    source_registry_updated: bool
    target_registry_updated: bool

    name: str = field(
        default="cat_traveled_through_cat_door",
        init=False,
    )

    traveled: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "door",
            str(self.door),
        )

        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "source_layer",
            str(self.source_layer),
        )

        object.__setattr__(
            self,
            "target_layer",
            str(self.target_layer),
        )

        object.__setattr__(
            self,
            "source_position",
            require_optional_spatial_vector(
                self.source_position,
                field_name=(
                    "cat door source position"
                ),
            ),
        )

        object.__setattr__(
            self,
            "target_position",
            require_optional_spatial_vector(
                self.target_position,
                field_name=(
                    "cat door target position"
                ),
            ),
        )

        object.__setattr__(
            self,
            "source_registry_updated",
            bool(
                self.source_registry_updated
            ),
        )

        object.__setattr__(
            self,
            "target_registry_updated",
            bool(
                self.target_registry_updated
            ),
        )

    def __deepcopy__(
        self,
        memo,
    ):
        return self
