from dataclasses import dataclass


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
