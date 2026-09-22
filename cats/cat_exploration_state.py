from dataclasses import dataclass, field
from core.entity.components import SpatialVector3, require_optional_spatial_vector, require_spatial_vector


@dataclass(slots=True)
class CatContinuationCandidate:
    layer: str
    position: SpatialVector3
    score: float
    direction_index: int
    revisit_penalty: float

    def __post_init__(self):
        self.position = require_spatial_vector(self.position, field_name="CatContinuationCandidate position")


@dataclass(slots=True)
class CatContinuationPlan:
    selected: bool = False

    layer: str | None = None
    position: SpatialVector3 | None = None
    score: float | None = None
    reason: str | None = None

    candidates: list = field(
        default_factory=list
    )

    def __post_init__(self):
        self.position = require_optional_spatial_vector(self.position, field_name="CatContinuationPlan position")


@dataclass(slots=True)
class CatAfterArrivalCandidate:
    action: str
    score: float
    reasons: list = field(
        default_factory=list
    )


@dataclass(slots=True)
class CatAfterArrivalDecision:
    selected: bool = False

    action: str | None = None
    score: float | None = None

    reasons: list = field(
        default_factory=list
    )

    finalists: list = field(
        default_factory=list
    )

    quantum_roll: int | None = None


@dataclass(slots=True)
class CatScentDestinationCandidate:
    identity: str | None
    layer: str | None
    position: SpatialVector3
    source_id: object

    confidence: float
    last_intensity: float
    score: float

    def __post_init__(self):
        self.position = require_spatial_vector(self.position, field_name="CatScentDestinationCandidate position")


@dataclass(slots=True)
class CatScentDestinationPlan:
    selected: bool = False

    reason: str | None = None

    identity: str | None = None
    layer: str | None = None
    position: SpatialVector3 | None = None
    source_id: object = None
    score: float | None = None

    candidates: list = field(
        default_factory=list
    )

    def __post_init__(self):
        self.position = require_optional_spatial_vector(self.position, field_name="CatScentDestinationPlan position")


@dataclass(slots=True)
class CatExplorationCandidate:
    layer: str
    position: SpatialVector3
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

    def __post_init__(self):
        self.position = require_spatial_vector(self.position, field_name="CatExplorationCandidate position")


@dataclass(slots=True)
class CatExplorationPlan:
    selected: bool = False

    reason: str | None = None
    current_layer: str | None = None

    layer: str | None = None
    position: SpatialVector3 | None = None
    score: float | None = None

    reasons: list = field(
        default_factory=list
    )

    candidate_count: int = 0

    candidates: list = field(
        default_factory=list
    )

    def __post_init__(self):
        self.position = require_optional_spatial_vector(self.position, field_name="CatExplorationPlan position")
