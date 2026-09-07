from dataclasses import dataclass


@dataclass(slots=True)
class RadioactiveDecayState:

    isotopes_available: bool = False
    radioactive_decay_available: bool = False
    radiocarbon_time_available: bool = False
    geological_time_available: bool = False
    decay_pattern_count: int = 0

    def to_dict(self):
        return {
            "isotopes_available": self.isotopes_available,
            "radioactive_decay_available": (
                self.radioactive_decay_available
            ),
            "radiocarbon_time_available": (
                self.radiocarbon_time_available
            ),
            "geological_time_available": (
                self.geological_time_available
            ),
            "decay_pattern_count": self.decay_pattern_count,
        }
