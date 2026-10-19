from dataclasses import dataclass

from core.entity.components import (
    SpatialVector3,
)


@dataclass(slots=True, frozen=True)
class CatExplorationMemoryDetails:

    target_layer: str
    position: SpatialVector3 | None = None
    pair_id: str | None = None

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "target_layer",
            str(
                self.target_layer
            ),
        )

        if self.pair_id is not None:
            object.__setattr__(
                self,
                "pair_id",
                str(
                    self.pair_id
                ),
            )

        if (
            self.position is not None
            and not isinstance(
                self.position,
                SpatialVector3,
            )
        ):
            raise TypeError(
                "Cat exploration memory "
                "position must be "
                "SpatialVector3 or None."
            )
