import unittest

from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.stellar_objects import PrimordialStar
from universe.supernova_enrichment import SupernovaEnrichment
from universe.supernova_enrichment_process_state import (
    SupernovaEnrichmentProcessState,
)
from universe.universe import Universe


class SupernovaEnrichmentProcessStateObjectStateTests(
    unittest.TestCase
):

    def _star(self):
        cloud = StellarMaterialCloud(
            name="source_cloud",
            type="germinal_cloud",
            state="condensing",
            composition={},
            can_form_stars=True,
        )

        return PrimordialStar(
            name="first_star",
            type="primordial_star",
            generation=1,
            state="ignited",
            source_cloud=cloud,
            composition={
                "hydrogen": "dominant",
                "helium": "secondary",
            },
            can_fuse_elements=True,
            can_create_heavy_elements=True,
        )

    def _iron(self):
        return ChemicalElement(
            name="iron",
            symbol="Fe",
            atomic_number=26,
            official=True,
            discovered=True,
            state="forged",
            origin="stellar_nucleosynthesis",
        )

    def test_process_starts_ready_as_enum(self):
        process = SupernovaEnrichment(Universe())

        self.assertIs(
            process.state,
            SupernovaEnrichmentProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_stars_sets_failed_enum(self):
        process = SupernovaEnrichment(Universe())

        result = process.enrich_space()

        self.assertIs(
            process.state,
            SupernovaEnrichmentProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_missing_iron_sets_failed_enum(self):
        universe = Universe()
        universe.world["first_stars"] = [
            self._star()
        ]
        process = SupernovaEnrichment(universe)

        result = process.enrich_space()

        self.assertIs(
            process.state,
            SupernovaEnrichmentProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_enrichment_sets_enriched_enum(self):
        universe = Universe()
        universe.world["first_stars"] = [
            self._star()
        ]
        universe.world["elements_up_to_iron"] = {
            "iron": self._iron(),
        }
        process = SupernovaEnrichment(universe)

        result = process.enrich_space()

        self.assertIs(
            process.state,
            SupernovaEnrichmentProcessState.ENRICHED,
        )
        self.assertEqual(
            result["state"],
            "enriched",
        )

    def test_string_state_is_rejected(self):
        process = SupernovaEnrichment(Universe())

        with self.assertRaises(TypeError):
            process.state = "enriched"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in SupernovaEnrichmentProcessState
            },
            {
                "ready",
                "failed",
                "enriched",
            },
        )


if __name__ == "__main__":
    unittest.main()
