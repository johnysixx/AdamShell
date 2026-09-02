from dataclasses import dataclass


@dataclass(slots=True)
class UniversePhysicsLayers:

    classical: bool = True
    quantum: bool = False

    def enable_quantum(self):
        self.quantum = True

    def to_dict(self):
        return {
            "classical": self.classical,
            "quantum": self.quantum,
        }
