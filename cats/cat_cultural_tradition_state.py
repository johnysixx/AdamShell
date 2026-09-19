from dataclasses import dataclass


@dataclass(slots=True)
class CatCulturalTraditionState:
    name: str | None = None
    category: str | None = None
    occurrences: int = 0
    strength: float = 0.0
    inherited_from: str | None = None
