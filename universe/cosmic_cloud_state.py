from dataclasses import dataclass


@dataclass(slots=True)
class CosmicCloudFormationState:

    hydrogen_available: bool = False
    helium_available: bool = False
    germinal_clouds_formed: bool = False
    star_formation_possible: bool = False

    def to_dict(self):
        return {
            "hydrogen_available": (
                self.hydrogen_available
            ),
            "helium_available": self.helium_available,
            "germinal_clouds_formed": (
                self.germinal_clouds_formed
            ),
            "star_formation_possible": (
                self.star_formation_possible
            ),
        }
