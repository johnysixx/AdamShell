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
