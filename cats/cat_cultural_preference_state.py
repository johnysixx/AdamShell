from dataclasses import dataclass


@dataclass(slots=True)
class CatCulturalPreferenceState:
    value: object = None
    strength: float = 0.0
    expressions: int = 0
    inherited_from: str | None = None
