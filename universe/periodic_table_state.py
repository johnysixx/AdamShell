from dataclasses import dataclass


@dataclass(slots=True)
class PeriodicTableRegistryState:

    known_elements_registered: bool = False
    known_element_count: int = 0
    future_element_generation_available: bool = True
    future_element_count: int = 0

    def to_dict(self):
        return {
            "known_elements_registered": (
                self.known_elements_registered
            ),
            "known_element_count": self.known_element_count,
            "future_element_generation_available": (
                self.future_element_generation_available
            ),
            "future_element_count": self.future_element_count,
        }
