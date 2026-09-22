from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class EnergyGateCollectionEvent:

    source: str
    amount_j: float
    total_idea_energy_j: float
    name: str = "idea_energy_collected"

    def __post_init__(self):
        object.__setattr__(
            self,
            "source",
            str(self.source),
        )
        object.__setattr__(
            self,
            "amount_j",
            float(self.amount_j),
        )
        object.__setattr__(
            self,
            "total_idea_energy_j",
            float(self.total_idea_energy_j),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "source": self.source,
            "amount_j": self.amount_j,
            "total_idea_energy_j": (
                self.total_idea_energy_j
            ),
        }


@dataclass(slots=True)
class EnergyGateState:

    threshold_j: float
    idea_energy_j: float = 0.0
    energy_ratio: float = 0.0
    threshold_reached: bool = False
    physical_seed_created: bool = False
    big_bang_allowed: bool = False
    big_bang_started: bool = False

    def to_dict(self):
        return {
            "threshold_j": self.threshold_j,
            "idea_energy_j": self.idea_energy_j,
            "energy_ratio": self.energy_ratio,
            "threshold_reached": self.threshold_reached,
            "physical_seed_created": (
                self.physical_seed_created
            ),
            "big_bang_allowed": self.big_bang_allowed,
            "big_bang_started": self.big_bang_started,
        }
