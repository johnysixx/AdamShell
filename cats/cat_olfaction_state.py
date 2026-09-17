from dataclasses import dataclass, field


@dataclass(slots=True)
class CatAromaMatch:
    identity: str
    similarity: float
    confidence: float
    encounters: int


@dataclass(slots=True)
class CatAromaRecognition:
    recognized: bool = False
    identity: str | None = None
    similarity: float = 0.0

    matches: list = field(
        default_factory=list
    )

@dataclass(slots=True)
class CatDetectedAroma:
    entity_id: object
    actual_identity: str | None
    position: object
    distance: float

    components: dict
    raw_components: dict

    perceived_intensity: float
    recognition: CatAromaRecognition`n