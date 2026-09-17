from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True)
class CatPersonalityTraits:

    curiosity: float = 0.5
    courage: float = 0.5
    aggression: float = 0.5
    empathy: float = 0.5
    patience: float = 0.5
    sociability: float = 0.5

    def to_dict(self):
        return {
            "curiosity": self.curiosity,
            "courage": self.courage,
            "aggression": self.aggression,
            "empathy": self.empathy,
            "patience": self.patience,
            "sociability": self.sociability,
        }


@dataclass(slots=True)
class CatPersonalityState:

    traits: CatPersonalityTraits = field(
        default_factory=CatPersonalityTraits
    )
    experiences_processed: int = 0
    history: list = field(default_factory=list)

    def to_dict(self):
        return {
            "traits": self.traits.to_dict(),
            "experiences_processed": self.experiences_processed,
            "history": deepcopy(self.history),
        }
