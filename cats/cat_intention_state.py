from dataclasses import dataclass, field
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)


@dataclass(slots=True)
class CatIntentionCandidate:
    type: str
    target: object = None
    score: float = 0.0
    reasons: list = field(
        default_factory=list
    )

    def __post_init__(self):
        self.score = min(
            1.0,
            max(
                0.0,
                float(self.score),
            ),
        )

        self.reasons = list(
            self.reasons
        )



@dataclass(slots=True)
class CatKnownScentTarget:
    identity: str | None = None
    layer: str | None = None
    position: object = None
    source_id: object = None

    age_ticks: int | None = None
    freshness: float | None = None

    trail_direction: (
        CatScentTrailDirection | None
    ) = None

    def __post_init__(self):
        if (
            self.trail_direction is not None
            and not isinstance(
                self.trail_direction,
                CatScentTrailDirection,
            )
        ):
            raise TypeError(
                'Known scent target trail direction must be CatScentTrailDirection.'
            )


@dataclass(slots=True)
class CatScentSearchTarget:
    identity: str | None = None
    layer: str | None = None
    from_position: object = None
    trail_direction: (
        CatScentTrailDirection | None
    ) = None
    attempt: int = 1
    max_attempts: int = 1
    search_distance: float = 1.0

    def __post_init__(self):
        if (
            self.trail_direction is not None
            and not isinstance(
                self.trail_direction,
                CatScentTrailDirection,
            )
        ):
            raise TypeError(
                'Scent search target trail direction must be CatScentTrailDirection.'
            )



@dataclass(slots=True)
class CatScentBoxTarget:
    identity: str | None = None
    box_id: object = None
    counterpart_box_id: object = None
    source_layer: str | None = None
    target_layer: str | None = None



@dataclass(slots=True)
class CatQuantumBoxTravelTarget:
    source_box_id: object = None
    counterpart_box_id: object = None

    source_layer: str | None = None
    target_layer: str | None = None

    target_position: object = None



@dataclass(slots=True)
class CatQuantumCounterpartSenseTarget:
    box_id: object = None



@dataclass(slots=True)
class CatExploreBoxTarget:
    box_id: object = None



@dataclass(slots=True)
class CatExplorationPairTarget:
    layer: str | None = None
    position: object = None
    energy_cost: float = 0.0



@dataclass(slots=True)
class CatVisitRecipientTarget:
    recipient_id: str | None = None
