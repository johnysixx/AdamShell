from dataclasses import dataclass


@dataclass(slots=True)
class IsotopeFormationState:

    periodic_table_available: bool = False
    reference_isotopes_available: bool = False
    radioactive_isotopes_available: bool = False
    atomic_time_isotope_available: bool = False
    isotope_count: int = 0

    def to_dict(self):
        return {
            "periodic_table_available": (
                self.periodic_table_available
            ),
            "reference_isotopes_available": (
                self.reference_isotopes_available
            ),
            "radioactive_isotopes_available": (
                self.radioactive_isotopes_available
            ),
            "atomic_time_isotope_available": (
                self.atomic_time_isotope_available
            ),
            "isotope_count": self.isotope_count,
        }
