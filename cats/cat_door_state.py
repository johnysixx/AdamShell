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

    def to_dict(self):
        snapshot = {
            "name": self.name,
            "door": self.door,
            "cat": self.cat,
            "reason": self.reason,
            "traveled": self.traveled,
        }

        if self.source_layer is not None:
            snapshot[
                "source_layer"
            ] = self.source_layer

        if self.target_layer is not None:
            snapshot[
                "target_layer"
            ] = self.target_layer

        if self.source_location is not None:
            snapshot[
                "source_location"
            ] = self.source_location

        if self.target_location is not None:
            snapshot[
                "target_location"
            ] = self.target_location

        if self.cat_location is not None:
            snapshot[
                "cat_location"
            ] = self.cat_location

        return snapshot


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

    def to_dict(self):
        return {
            "name": self.name,
            "door": self.door,
            "cat": self.cat,
            "source_layer":
                self.source_layer,
            "target_layer":
                self.target_layer,
            "source_location":
                self.source_location,
            "target_location":
                self.target_location,
            "source_position": (
                None
                if self.source_position
                is None
                else (
                    self.source_position
                    .to_dict()
                )
            ),
            "target_position": (
                None
                if self.target_position
                is None
                else (
                    self.target_position
                    .to_dict()
                )
            ),
            "source_registry_updated":
                self.source_registry_updated,
            "target_registry_updated":
                self.target_registry_updated,
            "traveled":
                self.traveled,
        }
