from dataclasses import dataclass


@dataclass(slots=True)
class CatCulturalTraditionEvaluationState:
    group_id: str
    score: float
    category: str
