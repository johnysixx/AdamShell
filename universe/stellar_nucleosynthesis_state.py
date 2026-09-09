from dataclasses import dataclass


@dataclass(slots=True)
class StellarNucleosynthesisState:

    stellar_fusion_active: bool = False
    elements_up_to_iron_forged: bool = False
    iron_limit_reached: bool = False
    failed: bool = False
    element_count: int = 0

    def to_dict(self):
        return {
            "stellar_fusion_active": self.stellar_fusion_active,
            "elements_up_to_iron_forged": (
                self.elements_up_to_iron_forged
            ),
            "iron_limit_reached": self.iron_limit_reached,
            "failed": self.failed,
            "element_count": self.element_count,
        }
