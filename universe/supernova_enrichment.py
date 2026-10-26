from universe.physical_record_state import CosmicHistoryEvent
from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.primordial_objects import PrimordialElement
from universe.stellar_objects import PrimordialStar, Supernova
from universe.supernova_enrichment_state import (
    SupernovaEnrichmentState,
)
from universe.supernova_enrichment_process_state import (
    SupernovaEnrichmentProcessState,
)
from universe.supernova_enrichment_result_state import (
    SupernovaEnrichmentResult,
)


class SupernovaEnrichment:

    def __init__(self, universe):
        self.universe = universe
        self.name = "supernova_enrichment"
        self.type = "stellar_enrichment_process"
        self.state = SupernovaEnrichmentProcessState.READY

        self.supernovae = []
        self.enriched_clouds = []

        self.supernova_enrichment_state = (
            SupernovaEnrichmentState()
        )
        self.result = None

        self.public_state = self._build_public_state()

        self.universe.supernova_enrichment_layer = self

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if not isinstance(
            state,
            SupernovaEnrichmentProcessState,
        ):
            raise TypeError(
                "Supernova enrichment process state must use "
                "SupernovaEnrichmentProcessState."
            )

        self._state = state

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "supernovae": [
                supernova.to_dict()
                for supernova in self.supernovae
            ],
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
        stars_layer = getattr(
            self.universe,
            "stars_layer",
            None,
        )
        nucleosynthesis_layer = getattr(
            self.universe,
            "stellar_nucleosynthesis_layer",
            None,
        )

        first_stars = (
            stars_layer.stars
            if stars_layer is not None
            else ()
        )
        elements = (
            nucleosynthesis_layer.elements_up_to_iron
            if nucleosynthesis_layer is not None
            else {}
        )

        if not first_stars:
            self.state = (
                SupernovaEnrichmentProcessState.FAILED
            )

            print(
                "SUPERNOVA ENRICHMENT FAILED: "
                "no stars available"
            )
            self.write_to_world()

            self.result = SupernovaEnrichmentResult(
                state=self.state,
                supernovae=tuple(
                    self.supernovae
                ),
                enriched_clouds=tuple(
                    self.enriched_clouds
                ),
                supernova_enrichment_state=(
                    self.supernova_enrichment_state
                ),
            )

            return self.result

        for star in first_stars:
            if not isinstance(star, PrimordialStar):
                raise TypeError(
                    "first_stars must contain PrimordialStar objects"
                )

        self.supernova_enrichment_state.stars_available = (
            True
        )

        if "iron" not in elements:
            self.state = (
                SupernovaEnrichmentProcessState.FAILED
            )

            print(
                "SUPERNOVA ENRICHMENT FAILED: "
                "iron has not been forged yet"
            )
            self.write_to_world()

            self.result = SupernovaEnrichmentResult(
                state=self.state,
                supernovae=tuple(
                    self.supernovae
                ),
                enriched_clouds=tuple(
                    self.enriched_clouds
                ),
                supernova_enrichment_state=(
                    self.supernova_enrichment_state
                ),
            )

            return self.result

        for element in elements.values():
            if not isinstance(
                element,
                (
                    PrimordialElement,
                    ChemicalElement,
                ),
            ):
                raise TypeError(
                    "elements_up_to_iron must contain "
                    "primordial or ChemicalElement objects"
                )

        if not isinstance(
            elements["iron"],
            ChemicalElement,
        ):
            raise TypeError(
                "iron must be a ChemicalElement object"
            )

        self.supernova_enrichment_state.iron_available = (
            True
        )
        self.state = (
            SupernovaEnrichmentProcessState.ENRICHED
        )

        first_supernova = Supernova(
            name="first_supernova",
            type="supernova",
            state="exploded",
            source_star=first_stars[0],
            released_elements=tuple(elements.keys()),
        )
        self.supernovae.append(first_supernova)

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
                origin=first_supernova.name,
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

        self.result = SupernovaEnrichmentResult(
            state=self.state,
            supernovae=tuple(
                self.supernovae
            ),
            enriched_clouds=tuple(
                self.enriched_clouds
            ),
            supernova_enrichment_state=(
                self.supernova_enrichment_state
            ),
        )

        return self.result

    def record_history(self):
        history = self.universe.world.setdefault(
            "cosmic_history",
            [],
        )

        history.append(
            CosmicHistoryEvent(
                name="supernova_enrichment",
                description=(
                    "The first supernova releases elements up to "
                    "iron into space, forming enriched clouds for "
                    "future stellar systems."
                ),
            )
        )

    def write_to_world(self):
        self._refresh_public_state()

        self.universe.world["supernova_enrichment"] = (
            self.public_state
        )
        self.universe.world["supernovae"] = self.supernovae
        self.universe.world["enriched_clouds"] = (
            self.enriched_clouds
        )
