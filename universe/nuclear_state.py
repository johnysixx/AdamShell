from dataclasses import dataclass


@dataclass(slots=True)
class NuclearFormationState:

    nucleons_available: bool = False
    hydrogen_nucleus_formed: bool = False
    helium_nucleus_formed: bool = False
    light_nuclei_formed: bool = False
    nuclear_composition_recorded: bool = False

    def to_dict(self):
        return {
            "nucleons_available": self.nucleons_available,
            "hydrogen_nucleus_formed": (
                self.hydrogen_nucleus_formed
            ),
            "helium_nucleus_formed": (
                self.helium_nucleus_formed
            ),
            "light_nuclei_formed": (
                self.light_nuclei_formed
            ),
            "nuclear_composition_recorded": (
                self.nuclear_composition_recorded
            ),
        }
