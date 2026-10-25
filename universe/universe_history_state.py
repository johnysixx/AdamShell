from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UniverseHistorySnapshot:
    tick: int
    energy: float
    gain: float
    cost: float
    delta: float
    classical_entropy_delta: float
    classical_entropy_total: float
    entropy: float
    pressure: float
    curvature: float
    physics_model: str
    quantum_enabled: bool
    quantum_fluctuation: float
    quantum_uncertainty: float
    quantum_entropy_delta: float
    quantum_entropy_total: float

    def __deepcopy__(self, memo):
        return self

    def to_dict(self):
        return {
            "tick": self.tick,
            "energy": self.energy,
            "gain": self.gain,
            "cost": self.cost,
            "delta": self.delta,
            "classical_entropy_delta": (
                self.classical_entropy_delta
            ),
            "classical_entropy_total": (
                self.classical_entropy_total
            ),
            "entropy": self.entropy,
            "pressure": self.pressure,
            "curvature": self.curvature,
            "physics_model": self.physics_model,
            "quantum_enabled": self.quantum_enabled,
            "quantum_fluctuation": (
                self.quantum_fluctuation
            ),
            "quantum_uncertainty": (
                self.quantum_uncertainty
            ),
            "quantum_entropy_delta": (
                self.quantum_entropy_delta
            ),
            "quantum_entropy_total": (
                self.quantum_entropy_total
            ),
        }
