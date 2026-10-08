from dataclasses import dataclass, field

from core.entity.components import (
    SpatialVector3,
    require_optional_spatial_vector,
    require_spatial_vector,
)


@dataclass(slots=True, frozen=True)
class CatPositionChangedEvent:
    cat: str
    previous_position: SpatialVector3 | None
    position: SpatialVector3

    name: str = field(
        default="cat_position_changed",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "previous_position",
            require_optional_spatial_vector(
                self.previous_position,
                field_name=(
                    "previous cat position"
                ),
            ),
        )

        object.__setattr__(
            self,
            "position",
            require_spatial_vector(
                self.position,
                field_name=(
                    "cat position"
                ),
            ),
        )

    def __deepcopy__(
        self,
        memo,
    ):
        return self
