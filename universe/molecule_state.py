from dataclasses import dataclass


@dataclass(slots=True)
class MoleculeFormationState:

    periodic_table_available: bool = False
    simple_molecules_available: bool = False
    organic_molecules_available: bool = False
    alcohols_available: bool = False
    molecule_count: int = 0

    def to_dict(self):
        return {
            "periodic_table_available": (
                self.periodic_table_available
            ),
            "simple_molecules_available": (
                self.simple_molecules_available
            ),
            "organic_molecules_available": (
                self.organic_molecules_available
            ),
            "alcohols_available": self.alcohols_available,
            "molecule_count": self.molecule_count,
        }
