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
