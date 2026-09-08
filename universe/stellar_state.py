from dataclasses import dataclass


@dataclass(slots=True)
class StellarFormationState:

    first_stars_formed: bool = False
    stellar_fusion_possible: bool = False
    heavy_elements_possible: bool = False

    def to_dict(self):
        return {
            "first_stars_formed": (
                self.first_stars_formed
            ),
            "stellar_fusion_possible": (
                self.stellar_fusion_possible
            ),
            "heavy_elements_possible": (
                self.heavy_elements_possible
            ),
        }
