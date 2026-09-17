from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True)
class CatKnownPlace:

    place_id: str
    layer: str
    position: dict
    discovered_by: str
    first_source: str
    last_source: str

    visit_count: int = 1
    confidence: float = 0.55

    safe_observations: int = 0
    danger_observations: int = 0

    first_seen_tick: int | None = None
    last_seen_tick: int | None = None

    details: dict = field(
        default_factory=dict
    )

    safety: float | None = None

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

        if details:
            self.details.update(
                deepcopy(details)
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
    position: dict
    source_id: str
    identity: str

    observations: int = 1
    confidence: float = 0.3

    last_intensity: float = 0.0
    strongest_intensity: float = 0.0

    components: dict = field(
        default_factory=dict
    )

    first_seen_tick: int | None = None
    last_seen_tick: int | None = None

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
            float(self.confidence)
            + (
                0.1
                if recognized_identity
                else 0.03
            ),
        )

        if components:
            self.components = deepcopy(
                components
            )



@dataclass(slots=True)
class CatHeardLegend:

    legend_id: str | None
    claim_type: str | None
    place_id: str | None
    layer: str | None
    position: dict | None

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
    trust_change: dict



@dataclass(slots=True)
class CatKnownAroma:

    identity: str
    components: dict
    source: str

    encounters: int = 1
    confidence: float = 0.55

    @staticmethod
    def normalize_components(
        components
    ):
        return {
            str(key): float(value)
            for key, value
            in dict(components).items()
            if float(value) > 0.0
        }

    @classmethod
    def create(
        cls,
        identity,
        components,
        source='direct_experience',
    ):
        return cls(
            identity=identity,
            components=(
                cls.normalize_components(
                    components
                )
            ),
            source=source,
        )

    def record_encounter(
        self,
        components,
        source,
    ):
        normalized = (
            self.normalize_components(
                components
            )
        )

        self.encounters += 1
        self.source = source

        all_keys = (
            set(self.components)
            | set(normalized)
        )

        self.components = {
            key: (
                float(
                    self.components.get(
                        key,
                        0.0,
                    )
                )
                + float(
                    normalized.get(
                        key,
                        0.0,
                    )
                )
            )
            / 2.0
            for key in all_keys
        }

        self.confidence = min(
            1.0,
            float(self.confidence)
            + 0.1,
        )

    def similarity_to(
        self,
        components,
    ):
        observed = (
            self.normalize_components(
                components
            )
        )

        keys = (
            set(observed)
            | set(self.components)
        )

        if not keys:
            return 0.0

        dot = sum(
            float(
                observed.get(
                    key,
                    0.0,
                )
            )
            * float(
                self.components.get(
                    key,
                    0.0,
                )
            )
            for key in keys
        )

        observed_length = sum(
            float(
                observed.get(
                    key,
                    0.0,
                )
            ) ** 2
            for key in keys
        ) ** 0.5

        known_length = sum(
            float(
                self.components.get(
                    key,
                    0.0,
                )
            ) ** 2
            for key in keys
        ) ** 0.5

        if (
            observed_length == 0.0
            or known_length == 0.0
        ):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                dot
                / (
                    observed_length
                    * known_length
                ),
            ),
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

    heard_group_myths: dict = field(
        default_factory=dict
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
            + len(self.heard_group_myths)
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
