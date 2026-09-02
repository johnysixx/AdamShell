from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CronenbergConsumptionRecord:

    name: str
    mass: float
    energy: float
    digestion_days: int

    def __post_init__(self):
        object.__setattr__(
            self,
            "name",
            str(self.name),
        )
        object.__setattr__(
            self,
            "mass",
            float(self.mass),
        )
        object.__setattr__(
            self,
            "energy",
            float(self.energy),
        )
        object.__setattr__(
            self,
            "digestion_days",
            int(self.digestion_days),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "mass": self.mass,
            "energy": self.energy,
            "digestion_days": (
                self.digestion_days
            ),
        }
