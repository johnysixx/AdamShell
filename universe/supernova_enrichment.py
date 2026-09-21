from copy import deepcopy

from universe.cosmic_objects import StellarMaterialCloud
from universe.supernova_enrichment_state import (
    SupernovaEnrichmentState,
)


class SupernovaEnrichment:

    def __init__(self, universe):
        self.universe = universe
        self.name = "supernova_enrichment"
        self.type = "stellar_enrichment_process"
        self.state = "ready"

        self.supernovae = []
        self.enriched_clouds = []

        self.supernova_enrichment_state = (
            SupernovaEnrichmentState()
        )

        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "supernovae": deepcopy(self.supernovae),
            "enriched_clouds": [
                cloud.to_dict()
                for cloud in self.enriched_clouds
            ],
            "supernova_enrichment_state": (
                self.supernova_enrichment_state.to_dict()
            ),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def enrich_space(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=self._enrich_space_unprotected,
                source_component="supernova_enrichment",
                source_operation="enrich_space",
            )
        )

    def _enrich_space_unprotected(self):
        first_stars = self.universe.world.get(
            "first_stars",
            [],
        )
        elements = self.universe.world.get(
            "elements_up_to_iron",
            {},
        )

        if not first_stars:
            self.state = "failed"

            print(
                "SUPERNOVA ENRICHMENT FAILED: "
                "no stars available"
            )
            self.write_to_world()
            return self.public_state

        self.supernova_enrichment_state.stars_available = (
            True
        )

        if "iron" not in elements:
            self.state = "failed"

            print(
                "SUPERNOVA ENRICHMENT FAILED: "
                "iron has not been forged yet"
            )
            self.write_to_world()
            return self.public_state

        self.supernova_enrichment_state.iron_available = (
            True
        )
        self.state = "enriched"

        self.supernovae.append({
            "name": "first_supernova",
            "type": "supernova",
            "state": "exploded",
            "source_star": first_stars[0]["name"],
            "released_elements": list(elements.keys()),
        })

        self.supernova_enrichment_state.supernova_exploded = (
            True
        )
        self.supernova_enrichment_state.elements_released = (
            True
        )

        self.enriched_clouds.append(
            StellarMaterialCloud(
                name="first_enriched_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                origin="first_supernova",
                composition=elements,
                contains_elements_up_to_iron=True,
                can_form_stellar_systems=True,
            )
        )

        self.supernova_enrichment_state.enriched_clouds_formed = (
            True
        )

        self.record_history()
        self.write_to_world()

        print("FIRST SUPERNOVA EXPLODED")
        print("ELEMENTS UP TO IRON RELEASED INTO SPACE")
        print("ENRICHED CLOUDS FORMED")
        print("STELLAR SYSTEM FORMATION BECOMES POSSIBLE")

        return self.public_state

    def record_history(self):
        history = self.universe.world.setdefault(
            "cosmic_history",
            [],
        )

        history.append({
            "name": "supernova_enrichment",
            "description": (
                "The first supernova releases elements up to "
                "iron into space, forming enriched clouds for "
                "future stellar systems."
            ),
        })

    def write_to_world(self):
        self._refresh_public_state()

        self.universe.world["supernova_enrichment"] = (
            self.public_state
        )
        self.universe.world["supernovae"] = self.supernovae
        self.universe.world["enriched_clouds"] = (
            self.enriched_clouds
        )
        self.universe.world["supernova_enrichment_state"] = (
            self.supernova_enrichment_state
        )
