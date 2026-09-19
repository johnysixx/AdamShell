from copy import deepcopy
from dataclasses import dataclass, field


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
    details: dict = field(
        default_factory=dict
    )

    def to_dict(self):
        return {
            "memory_id":
                self.memory_id,
            "sequence":
                self.sequence,
            "event_type":
                self.event_type,
            "universe_tick":
                self.universe_tick,
            "location":
                deepcopy(
                    self.location
                ),
            "participants":
                deepcopy(
                    self.participants
                ),
            "details":
                deepcopy(
                    self.details
                ),
        }
