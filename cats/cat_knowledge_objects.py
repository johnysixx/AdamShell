from copy import deepcopy
from dataclasses import dataclass, field
from universe.aroma_composition import (
    AromaComposition,
    require_aroma_composition,
)
from core.entity.components import SpatialVector3, require_optional_spatial_vector, require_spatial_vector
from cats.cat_social_objects import (
    CatRelationshipTrustEvent,
)
from cats.cat_heard_group_myth_registry import (
    CatHeardGroupMythRegistry,
)


@dataclass(slots=True, frozen=True)
class CatKnownPlaceDetails:

    pair_id: str | None = None
    exploration_stage: int | None = None

    def __post_init__(
        self,
    ):
        if self.pair_id is not None:
            object.__setattr__(
                self,
                "pair_id",
                str(
                    self.pair_id
                ),
            )

        if self.exploration_stage is not None:
            object.__setattr__(
                self,
                "exploration_stage",
                int(
                    self.exploration_stage
                ),
            )

    def merged_with(
        self,
        other,
    ):
        if not isinstance(
            other,
            CatKnownPlaceDetails,
        ):
            raise TypeError(
                "Cat known place details merge "
                "requires CatKnownPlaceDetails."
            )

        return CatKnownPlaceDetails(
            pair_id=(
                other.pair_id
                if other.pair_id is not None
                else self.pair_id
            ),
            exploration_stage=(
                other.exploration_stage
                if other.exploration_stage
                is not None
                else self.exploration_stage
            ),
        )


@dataclass(slots=True, frozen=True)
class CatKnownPlaceDetails:

    pair_id: str | None = None
    exploration_stage: int | None = None

    def __post_init__(
        self,
    ):
        if self.pair_id is not None:
            object.__setattr__(
                self,
                "pair_id",
                str(
                    self.pair_id
                ),
            )

        if self.exploration_stage is not None:
            object.__setattr__(
                self,
                "exploration_stage",
                int(
                    self.exploration_stage
                ),
            )

    def merged_with(
        self,
        other,
    ):
        if not isinstance(
            other,
            CatKnownPlaceDetails,
        ):
            raise TypeError(
                "Cat known place details merge "
                "requires CatKnownPlaceDetails."
            )

        return CatKnownPlaceDetails(
            pair_id=(
                other.pair_id
                if other.pair_id is not None
                else self.pair_id
            ),
            exploration_stage=(
                other.exploration_stage
                if other.exploration_stage
                is not None
                else self.exploration_stage
            ),
        )


@dataclass(slots=True)
class CatKnownPlace:

    place_id: str
    layer: str
    position: SpatialVector3
    discovered_by: str
    first_source: str
    last_source: str

    visit_count: int = 1
    confidence: float = 0.55

    safe_observations: int = 0
    danger_observations: int = 0

    first_seen_tick: int | None = None
    last_seen_tick: int | None = None

    details: CatKnownPlaceDetails = field(
        default_factory=CatKnownPlaceDetails
    )

    safety: float | None = None

    def __post_init__(self):
        self.position = require_spatial_vector(
            self.position,
            field_name=(
                "cat known place position"
            ),
        )

        if not isinstance(
            self.details,
            CatKnownPlaceDetails,
        ):
            raise TypeError(
                "Cat known place details must use "
                "CatKnownPlaceDetails."
            )

        self.details = deepcopy(
            self.details
        )

    def record_visit(
        self,
        source,
        universe_tick=None,
        details=None,
    ):
        self.visit_count += 1
        self.last_source = source
        self.last_seen_tick = universe_tick

        self.confidence = min(
            1.0,
            float(self.confidence)
            + 0.1,
        )

        if details is not None:
            if not isinstance(
                details,
                CatKnownPlaceDetails,
            ):
                raise TypeError(
                    "Cat known place visit details "
                    "must use CatKnownPlaceDetails."
                )

            self.details = (
                self.details
                .merged_with(
                    deepcopy(
                        details
                    )
                )
            )

    def record_safety(
        self,
        safe=None,
        danger=None,
    ):
        if safe is True:
            self.safe_observations += 1

        if danger is True:
            self.danger_observations += 1

        observations = (
            self.safe_observations
            + self.danger_observations
        )

        self.safety = (
            self.safe_observations
            / observations
            if observations
            else None
        )


@dataclass(slots=True)
class CatScentPlaceMemory:

    place_id: str
    layer: str
    position: SpatialVector3
    source_id: str
    identity: str

    observations: int = 1
    confidence: float = 0.3

    last_intensity: float = 0.0
    strongest_intensity: float = 0.0

    components: AromaComposition = field(
        default_factory=AromaComposition.empty
    )

    first_seen_tick: int | None = None
    last_seen_tick: int | None = None

    def __post_init__(self):
        self.position = require_spatial_vector(
            self.position,
            field_name=(
                "cat scent memory position"
            ),
        )

        self.components = (
            require_aroma_composition(
                self.components,
                field_name=(
                    "cat scent memory components"
                ),
            )
        )

    def record_observation(
        self,
        recognized_identity=None,
        components=None,
        perceived_intensity=0.0,
        universe_tick=None,
    ):
        intensity = float(
            perceived_intensity
        )

        self.observations += 1
        self.last_intensity = intensity

        self.strongest_intensity = max(
            float(
                self.strongest_intensity
            ),
            intensity,
        )

        self.last_seen_tick = (
            universe_tick
        )

        self.confidence = min(
            1.0,
            float(
                self.confidence
            )
            + (
                0.1
                if recognized_identity
                else 0.03
            ),
        )

        if components is not None:
            components = (
                require_aroma_composition(
                    components,
                    field_name=(
                        "cat scent observation components"
                    ),
                )
            )

            if not components.is_empty:
                self.components = components



@dataclass(slots=True)
class CatHeardLegend:

    legend_id: str | None
    claim_type: str | None
    place_id: str | None
    layer: str | None
    position: SpatialVector3 | None

    storyteller: str

    trust_in_storyteller: float
    source_confidence: float
    credibility: float

    heard_count: int = 1

    verified: bool = False
    contradicted: bool = False

    trust_after_verification: (
        float | None
    ) = None

    trust_after_contradiction: (
        float | None
    ) = None

    def __post_init__(self):
        self.position = require_optional_spatial_vector(self.position, field_name="heard legend position")

    def record_hearing(
        self,
        trust_in_storyteller,
        source_confidence,
        credibility,
    ):
        self.heard_count += 1

        self.trust_in_storyteller = (
            float(
                trust_in_storyteller
            )
        )

        self.source_confidence = float(
            source_confidence
        )

        self.credibility = min(
            1.0,
            (
                float(
                    self.credibility
                )
                + float(
                    credibility
                )
            )
            / 2.0
            + 0.03,
        )

    def verify(
        self,
        trust_after,
    ):
        self.verified = True
        self.contradicted = False

        self.trust_after_verification = (
            float(
                trust_after
            )
        )

    def contradict(
        self,
        trust_after,
    ):
        self.contradicted = True
        self.verified = False

        self.trust_after_contradiction = (
            float(
                trust_after
            )
        )


@dataclass(slots=True)
class CatVerifiedLegendRecord:

    legend_id: str | None
    place_id: str | None

    storyteller: str
    verified_by: str

    credibility_before: float
    trust_change: CatRelationshipTrustEvent

    def __post_init__(self):
        if not isinstance(
            self.trust_change,
            CatRelationshipTrustEvent,
        ):
            raise TypeError(
                "Verified legend trust change must be "
                "CatRelationshipTrustEvent."
            )



@dataclass(slots=True)
class CatKnownAroma:

    identity: str
    components: AromaComposition
    source: str

    encounters: int = 1
    confidence: float = 0.55

    def __post_init__(self):
        self.components = (
            require_aroma_composition(
                self.components,
                field_name=(
                    "known aroma components"
                ),
            )
        )

    @classmethod
    def create(
        cls,
        identity,
        components,
        source="direct_experience",
    ):
        return cls(
            identity=identity,
            components=(
                require_aroma_composition(
                    components,
                    field_name=(
                        "learned aroma components"
                    ),
                )
            ),
            source=source,
        )

    def record_encounter(
        self,
        components,
        source,
    ):
        components = (
            require_aroma_composition(
                components,
                field_name=(
                    "repeated aroma encounter components"
                ),
            )
        )

        self.encounters += 1
        self.source = source

        self.components = (
            self.components.average_with(
                components
            )
        )

        self.confidence = min(
            1.0,
            float(
                self.confidence
            )
            + 0.1,
        )

    def similarity_to(
        self,
        components,
    ):
        components = (
            require_aroma_composition(
                components,
                field_name=(
                    "observed aroma components"
                ),
            )
        )

        return (
            self.components
            .similarity_to(
                components
            )
        )



@dataclass(slots=True)
class CatKnownPrinciples:

    quantum_boxes_are_paired: bool = True



@dataclass(slots=True)
class CatKnowledgeState:

    known_places: list = field(
        default_factory=list
    )

    heard_legends: list = field(
        default_factory=list
    )

    verified_legends: list = field(
        default_factory=list
    )

    known_aromas: list = field(
        default_factory=list
    )

    known_scent_places: list = field(
        default_factory=list
    )

    known_principles: CatKnownPrinciples = field(
        default_factory=CatKnownPrinciples
    )

    current_quantum_layer_map: object | None = None

    scent_clock_tick: int | None = None

    heard_group_myths: CatHeardGroupMythRegistry = field(
        default_factory=(
            CatHeardGroupMythRegistry
        )
    )

    group_received_knowledge: dict = field(
        default_factory=dict
    )

    def role_knowledge_score(self):
        evidence_count = (
            len(self.known_places)
            + len(self.heard_legends)
            + len(self.verified_legends)
            + len(self.known_aromas)
            + len(self.known_scent_places)
            + self.heard_group_myths.count
            + len(
                self.group_received_knowledge
            )
        )

        principle_count = int(
            self.known_principles
            .quantum_boxes_are_paired
        )

        return min(
            1.0,
            (
                evidence_count
                + principle_count
            )
            / 10.0,
        )
