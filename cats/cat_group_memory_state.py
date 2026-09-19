from dataclasses import dataclass, field


@dataclass(slots=True)
class CatGroupMemoryState:
    encounters: int = 0
    peaceful_encounters: int = 0
    conflicts: int = 0
    victories: int = 0
    defeats: int = 0
    standoffs: int = 0
    cooperations: int = 0
    betrayals: int = 0
    last_outcome: str | None = None
    recent_events: list = field(
        default_factory=list
    )

    def to_dict(self):
        return {
            "encounters": self.encounters,
            "peaceful_encounters": (
                self.peaceful_encounters
            ),
            "conflicts": self.conflicts,
            "victories": self.victories,
            "defeats": self.defeats,
            "standoffs": self.standoffs,
            "cooperations": self.cooperations,
            "betrayals": self.betrayals,
            "last_outcome": self.last_outcome,
            "recent_events": list(
                self.recent_events
            ),
        }
