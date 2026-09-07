from dataclasses import dataclass


@dataclass(slots=True)
class AtomicTimeState:

    isotopes_available: bool = False
    caesium_133_available: bool = False
    si_second_defined: bool = False
    precision_time_available: bool = False

    def to_dict(self):
        return {
            "isotopes_available": self.isotopes_available,
            "caesium_133_available": (
                self.caesium_133_available
            ),
            "si_second_defined": self.si_second_defined,
            "precision_time_available": (
                self.precision_time_available
            ),
        }
