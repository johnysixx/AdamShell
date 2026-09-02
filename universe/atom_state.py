from dataclasses import dataclass


@dataclass(slots=True)
class AtomFormationState:

    periodic_table_available: bool = False
    neutral_atoms_available: bool = False
    atom_count: int = 0

    def to_dict(self):
        return {
            "periodic_table_available": (
                self.periodic_table_available
            ),
            "neutral_atoms_available": (
                self.neutral_atoms_available
            ),
            "atom_count": self.atom_count,
        }
