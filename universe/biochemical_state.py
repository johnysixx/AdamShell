from dataclasses import dataclass


@dataclass(slots=True)
class BiochemicalFoundationState:

    water_based_chemistry_possible: bool = False
    carbon_chemistry_possible: bool = False
    sugars_possible: bool = False
    amino_acids_possible: bool = False
    lipids_possible: bool = False
    fermentation_substrate_possible: bool = False

    def to_dict(self):
        return {
            "water_based_chemistry_possible": (
                self.water_based_chemistry_possible
            ),
            "carbon_chemistry_possible": (
                self.carbon_chemistry_possible
            ),
            "sugars_possible": self.sugars_possible,
            "amino_acids_possible": self.amino_acids_possible,
            "lipids_possible": self.lipids_possible,
            "fermentation_substrate_possible": (
                self.fermentation_substrate_possible
            ),
        }
