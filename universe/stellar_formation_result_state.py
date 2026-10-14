from dataclasses import dataclass, field

from universe.cosmic_cloud_state import (
    CosmicCloudFormationState,
)
from universe.cosmic_clouds_process_state import (
    CosmicCloudsProcessState,
)
from universe.cosmic_objects import (
    StellarMaterialCloud,
)
from universe.stars_process_state import (
    StarsProcessState,
)
from universe.stellar_objects import (
    PrimordialStar,
)
from universe.stellar_state import (
    StellarFormationState,
)


def _freeze_sequence(
    values,
    expected_type,
    label,
):
    items = tuple(
        values
    )

    for item in items:
        if not isinstance(
            item,
            expected_type,
        ):
            raise TypeError(
                f"{label} must contain "
                f"{expected_type.__name__} objects."
            )

    return items


@dataclass(
    slots=True,
    frozen=True,
)
class CosmicCloudFormationResult:

    state: CosmicCloudsProcessState
    clouds: tuple[StellarMaterialCloud, ...]
    cosmic_cloud_state: CosmicCloudFormationState

    name: str = field(
        default="cosmic_clouds",
        init=False,
    )
    type: str = field(
        default="cosmic_structure_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            CosmicCloudsProcessState,
        ):
            raise TypeError(
                "Cosmic cloud result state must use "
                "CosmicCloudsProcessState."
            )

        if not isinstance(
            self.cosmic_cloud_state,
            CosmicCloudFormationState,
        ):
            raise TypeError(
                "Cosmic cloud result formation state "
                "must use CosmicCloudFormationState."
            )

        object.__setattr__(
            self,
            "clouds",
            _freeze_sequence(
                self.clouds,
                StellarMaterialCloud,
                "Cosmic cloud result",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "clouds": [
                cloud.to_dict()
                for cloud in self.clouds
            ],
            "cosmic_cloud_state": (
                self.cosmic_cloud_state.to_dict()
            ),
        }


@dataclass(
    slots=True,
    frozen=True,
)
class StarFormationResult:

    state: StarsProcessState
    stars: tuple[PrimordialStar, ...]
    stellar_state: StellarFormationState

    name: str = field(
        default="stars",
        init=False,
    )
    type: str = field(
        default="stellar_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            StarsProcessState,
        ):
            raise TypeError(
                "Star formation result state must use "
                "StarsProcessState."
            )

        if not isinstance(
            self.stellar_state,
            StellarFormationState,
        ):
            raise TypeError(
                "Star formation result state object "
                "must use StellarFormationState."
            )

        object.__setattr__(
            self,
            "stars",
            _freeze_sequence(
                self.stars,
                PrimordialStar,
                "Star formation result",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "stars": [
                star.to_dict()
                for star in self.stars
            ],
            "stellar_state": (
                self.stellar_state.to_dict()
            ),
        }
