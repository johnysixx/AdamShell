from dataclasses import (
    dataclass,
    field,
)


@dataclass(slots=True)
class CatMemoryRecord:
    memory_id: str
    sequence: int
    event_type: str
    universe_tick: object = None
    location: object = None
    participants: list = field(
        default_factory=list
    )
    details: object = field(
        default_factory=dict
    )
