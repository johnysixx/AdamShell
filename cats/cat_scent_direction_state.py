from dataclasses import dataclass


@dataclass(slots=True)
class CatScentTrailDirection:
    inferred: bool = False
    reason: str | None = None

    identity: str | None = None
    layer: str | None = None

    from_position: object = None
    to_position: object = None
    vector: object = None
    unit_vector: object = None

    distance: float | None = None
    tick_delta: int | None = None
    newest_age_ticks: int | None = None
    freshness: float | None = None
    confidence: float | None = None

    from_source_id: object = None
    to_source_id: object = None
