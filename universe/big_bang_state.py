from dataclasses import dataclass


@dataclass(slots=True)
class BigBangCosmicState:

    spacetime_expanded: bool = False
    primordial_plasma_formed: bool = False
    light_nuclei_conditions_prepared: bool = False
    light_separated_from_darkness: bool = False
    darkness_present: bool = True

    def to_dict(self):
        return {
            "spacetime_expanded": (
                self.spacetime_expanded
            ),
            "primordial_plasma_formed": (
                self.primordial_plasma_formed
            ),
            "light_nuclei_conditions_prepared": (
                self.light_nuclei_conditions_prepared
            ),
            "light_separated_from_darkness": (
                self.light_separated_from_darkness
            ),
            "darkness_present": self.darkness_present,
        }
