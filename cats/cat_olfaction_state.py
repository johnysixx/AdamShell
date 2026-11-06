from dataclasses import dataclass, field

from core.entity.components import (
    SpatialVector3,
    require_spatial_vector,
)
from universe.aroma_composition import (
    AromaComposition,
    require_aroma_composition,
)


@dataclass(slots=True, frozen=True)
class CatAromaMatch:

    identity: str
    similarity: float
    confidence: float
    encounters: int


@dataclass(slots=True, frozen=True)
class CatAromaRecognition:

    recognized: bool = False
    identity: str | None = None
    similarity: float = 0.0

    matches: tuple[CatAromaMatch, ...] = ()

    def __post_init__(self):
        if (
            not isinstance(self.matches, tuple)
            or any(
                not isinstance(match, CatAromaMatch)
                for match in self.matches
            )
        ):
            raise TypeError(
                "Aroma recognition matches must be "
                "a tuple of CatAromaMatch objects."
            )


@dataclass(slots=True)
class CatDetectedAroma:

    entity_id: object
    actual_identity: str | None
    position: SpatialVector3
    distance: float

    components: AromaComposition
    raw_components: AromaComposition

    perceived_intensity: float
    recognition: CatAromaRecognition

    def __post_init__(self):
        self.position = (
            require_spatial_vector(
                self.position,
                field_name=(
                    "detected aroma position"
                ),
            )
        )

        self.components = (
            require_aroma_composition(
                self.components,
                field_name=(
                    "detected aroma components"
                ),
            )
        )

        self.raw_components = (
            require_aroma_composition(
                self.raw_components,
                field_name=(
                    "detected raw aroma components"
                ),
            )
        )


@dataclass(slots=True)
class CatAmbientAroma:

    source: str | None
    components: AromaComposition
    recognition: CatAromaRecognition

    def __post_init__(self):
        self.components = (
            require_aroma_composition(
                self.components,
                field_name=(
                    "ambient aroma components"
                ),
            )
        )


@dataclass(slots=True)
class CatOlfactionState:

    cat: str | None = None
    radius: float = 0.0

    detected_aromas: list[
        CatDetectedAroma
    ] = field(
        default_factory=list
    )

    ambient_aroma: (
        CatAmbientAroma | None
    ) = None

    ozone_detected: bool = False
    sniffed: bool = False

    @property
    def detected_count(self):
        return len(
            self.detected_aromas
        )
