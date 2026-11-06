from dataclasses import dataclass

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


@dataclass(slots=True, frozen=True)
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
        object.__setattr__(
            self,
            "position",
            require_spatial_vector(
                self.position,
                field_name="detected aroma position",
            ),
        )

        object.__setattr__(
            self,
            "components",
            require_aroma_composition(
                self.components,
                field_name="detected aroma components",
            ),
        )

        object.__setattr__(
            self,
            "raw_components",
            require_aroma_composition(
                self.raw_components,
                field_name="detected raw aroma components",
            ),
        )

        if not isinstance(
            self.recognition,
            CatAromaRecognition,
        ):
            raise TypeError(
                "Detected aroma recognition must "
                "be CatAromaRecognition."
            )


@dataclass(slots=True, frozen=True)
class CatAmbientAroma:

    source: str | None
    components: AromaComposition
    recognition: CatAromaRecognition

    def __post_init__(self):
        object.__setattr__(
            self,
            "components",
            require_aroma_composition(
                self.components,
                field_name=(
                    "ambient aroma components"
                ),
            ),
        )

        if not isinstance(
            self.recognition,
            CatAromaRecognition,
        ):
            raise TypeError(
                "Ambient aroma recognition must "
                "be CatAromaRecognition."
            )


@dataclass(slots=True, frozen=True)
class CatOlfactionState:

    cat: str | None = None
    radius: float = 0.0

    detected_aromas: tuple[
        CatDetectedAroma, ...
    ] = ()

    ambient_aroma: (
        CatAmbientAroma | None
    ) = None

    ozone_detected: bool = False
    sniffed: bool = False

    def __post_init__(self):
        if (
            not isinstance(self.detected_aromas, tuple)
            or any(
                not isinstance(item, CatDetectedAroma)
                for item in self.detected_aromas
            )
        ):
            raise TypeError(
                "Cat olfaction detected aromas must "
                "be a tuple of CatDetectedAroma objects."
            )

        if (
            self.ambient_aroma is not None
            and not isinstance(
                self.ambient_aroma,
                CatAmbientAroma,
            )
        ):
            raise TypeError(
                "Cat olfaction ambient aroma must "
                "be CatAmbientAroma or None."
            )

    @property
    def detected_count(self):
        return len(
            self.detected_aromas
        )
