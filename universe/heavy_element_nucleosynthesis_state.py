from dataclasses import dataclass


@dataclass(slots=True)
class HeavyElementNucleosynthesisState:

    iron_seed_available: bool = False
    supernova_enrichment_available: bool = False
    neutron_capture_possible: bool = False
    heavy_elements_forged: bool = False
    enriched_clouds_updated: bool = False

    def to_dict(self):
        return {
            "iron_seed_available": self.iron_seed_available,
            "supernova_enrichment_available": (
                self.supernova_enrichment_available
            ),
            "neutron_capture_possible": self.neutron_capture_possible,
            "heavy_elements_forged": self.heavy_elements_forged,
            "enriched_clouds_updated": self.enriched_clouds_updated,
        }
