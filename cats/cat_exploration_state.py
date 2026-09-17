from dataclasses import dataclass, field


@dataclass(slots=True)
class CatExplorationCandidate:
    layer: str
    position: object
    source: str

    known_visits: int = 0
    positive_memories: int = 0
    negative_memories: int = 0

    box_id: str | None = None
    memory_type: str | None = None
    legend_id: str | None = None
    storyteller: str | None = None
    legend_credibility: float | None = None

    score: float | None = None
    reasons: list = field(
        default_factory=list
    )


@dataclass(slots=True)
class CatExplorationPlan:
    selected: bool = False

    reason: str | None = None
    current_layer: str | None = None

    layer: str | None = None
    position: object = None
    score: float | None = None

    reasons: list = field(
        default_factory=list
    )

    candidate_count: int = 0

    candidates: list = field(
        default_factory=list
    )
