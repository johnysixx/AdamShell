from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class DarkSectorEnergyReceivedEvent:
    box_id: str
    energy_j: float
    dark_energy_total_j: float
    threshold_progress: float
    name: str = field(
        default="empty_quantum_box_energy_received",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "box_id",
            str(self.box_id),
        )
        object.__setattr__(
            self,
            "energy_j",
            float(self.energy_j),
        )
        object.__setattr__(
            self,
            "dark_energy_total_j",
            float(self.dark_energy_total_j),
        )
        object.__setattr__(
            self,
            "threshold_progress",
            float(self.threshold_progress),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "box_id": self.box_id,
            "energy_j": self.energy_j,
            "dark_energy_total_j": (
                self.dark_energy_total_j
            ),
            "threshold_progress": (
                self.threshold_progress
            ),
        }


@dataclass(slots=True, frozen=True)
class DarkMatterCondensationEvent:
    consumed_energy_j: float
    produced_dark_matter_kg: float
    dark_energy_remaining_j: float
    dark_matter_total_kg: float
    name: str = field(
        default="dark_matter_naturally_condensed",
        init=False,
    )

    def __post_init__(self):
        for field_name in (
            "consumed_energy_j",
            "produced_dark_matter_kg",
            "dark_energy_remaining_j",
            "dark_matter_total_kg",
        ):
            object.__setattr__(
                self,
                field_name,
                float(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

    def to_dict(self):
        return {
            "name": self.name,
            "consumed_energy_j": (
                self.consumed_energy_j
            ),
            "produced_dark_matter_kg": (
                self.produced_dark_matter_kg
            ),
            "dark_energy_remaining_j": (
                self.dark_energy_remaining_j
            ),
            "dark_matter_total_kg": (
                self.dark_matter_total_kg
            ),
        }


@dataclass(slots=True)
class DarkSectorState:

    quantum_threshold_j: float
    dark_energy_j: float = 0.0
    dark_matter_kg: float = 0.0

    def to_dict(self):
        return {
            "quantum_threshold_j": self.quantum_threshold_j,
            "dark_energy_j": self.dark_energy_j,
            "dark_matter_kg": self.dark_matter_kg,
        }
