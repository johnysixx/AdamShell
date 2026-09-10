from dataclasses import dataclass


@dataclass(slots=True)
class SupernovaEnrichmentState:

    stars_available: bool = False
    iron_available: bool = False
    supernova_exploded: bool = False
    elements_released: bool = False
    enriched_clouds_formed: bool = False

    def to_dict(self):
        return {
            "stars_available": self.stars_available,
            "iron_available": self.iron_available,
            "supernova_exploded": self.supernova_exploded,
            "elements_released": self.elements_released,
            "enriched_clouds_formed": self.enriched_clouds_formed,
        }
