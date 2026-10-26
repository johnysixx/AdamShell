import unittest

from universe.big_bang import BigBang
from universe.chemical_objects import ChemicalElement
from universe.cosmic_clouds import CosmicClouds
from universe.cosmic_clouds_process_state import (
    CosmicCloudsProcessState,
)
from universe.cosmic_objects import StellarMaterialCloud
from universe.primordial_objects import PrimordialElement
from universe.stars import Stars
from universe.stars_process_state import StarsProcessState
from universe.stellar_nucleosynthesis import (
    StellarNucleosynthesis,
    STELLAR_ELEMENT_SPECS,
)
from universe.stellar_nucleosynthesis_process_state import (
    StellarNucleosynthesisProcessState,
)
from universe.supernova_enrichment import SupernovaEnrichment
from universe.supernova_enrichment_process_state import (
    SupernovaEnrichmentProcessState,
)
from universe.universe import Universe


class StellarNucleosynthesisCanonicalBigBangTests(
    unittest.TestCase
):

    def _component(self, name):
        return PrimordialElement(
            name=name,
            state="formed",
            origin="big_bang_nucleosynthesis",
        )

    def _ready_stars(self, *, with_big_bang=True):
        universe = Universe()

        if with_big_bang:
            universe.start_big_bang()

            clouds = CosmicClouds(universe)

            cloud_result = clouds.form_germinal_clouds()

            self.assertIs(
                cloud_result.state,
                CosmicCloudsProcessState.FORMED,
            )

            stars = Stars(universe)
        else:
            cloud = StellarMaterialCloud(
                name="isolated_stellar_source",
                type="germinal_cloud",
                state="condensing",
                composition={
                    "hydrogen": "dominant",
                    "helium": "secondary",
                },
                can_form_stars=True,
            )

            stars = Stars(
                universe,
                source_clouds=[cloud],
            )

        result = stars.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )

        self.assertEqual(len(stars.stars), 2)

        return universe, stars

    def test_full_canonical_big_bang_to_iron(self):
        universe, stars = self._ready_stars()

        process = StellarNucleosynthesis(universe)
        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            universe.stars_layer,
            stars,
        )

        self.assertEqual(
            len(STELLAR_ELEMENT_SPECS),
            23,
        )

        self.assertEqual(
            len(process.elements_up_to_iron),
            26,
        )

        big_bang = universe.big_bang

        for name in (
            "hydrogen",
            "helium",
            "trace_lithium",
        ):
            with self.subTest(element=name):
                self.assertIs(
                    process.elements_up_to_iron[name],
                    big_bang.primordial_elements[name],
                )

                self.assertIs(
                    result.elements_up_to_iron[name],
                    big_bang.primordial_elements[name],
                )

        self.assertIsInstance(
            process.elements_up_to_iron["iron"],
            ChemicalElement,
        )

        self.assertEqual(
            process.elements_up_to_iron["iron"].atomic_number,
            26,
        )

        self.assertEqual(
            process.stellar_nucleosynthesis_state.element_count,
            26,
        )

    def test_public_decoy_cannot_override_big_bang(
        self
    ):
        universe, _ = self._ready_stars()

        universe.world["primordial_elements"] = {
            "hydrogen": {
                "name": "legacy_hydrogen",
            },
        }

        process = StellarNucleosynthesis(universe)
        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            process.elements_up_to_iron["hydrogen"],
            universe.big_bang.primordial_elements[
                "hydrogen"
            ],
        )

        self.assertEqual(
            len(process.elements_up_to_iron),
            26,
        )

    def test_missing_public_alias_does_not_block(
        self
    ):
        universe, _ = self._ready_stars()

        self.assertNotIn("primordial_elements", universe.world)

        process = StellarNucleosynthesis(universe)
        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            process.elements_up_to_iron["helium"],
            universe.big_bang.primordial_elements[
                "helium"
            ],
        )

    def test_world_only_primordial_elements_are_ignored(
        self
    ):
        universe, _ = self._ready_stars(
            with_big_bang=False,
        )

        universe.world["primordial_elements"] = {
            "hydrogen": self._component("hydrogen"),
            "helium": self._component("helium"),
        }

        process = StellarNucleosynthesis(universe)
        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertEqual(
            len(process.elements_up_to_iron),
            23,
        )

        self.assertNotIn(
            "hydrogen",
            process.elements_up_to_iron,
        )

        self.assertNotIn(
            "helium",
            process.elements_up_to_iron,
        )

        self.assertIn(
            "iron",
            process.elements_up_to_iron,
        )

    def test_canonical_partial_primordial_registry(
        self
    ):
        universe, _ = self._ready_stars(
            with_big_bang=False,
        )

        big_bang = BigBang(universe)

        hydrogen = self._component("hydrogen")

        big_bang.primordial_elements = {
            "hydrogen": hydrogen,
        }

        universe.big_bang = big_bang

        process = StellarNucleosynthesis(universe)
        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            process.elements_up_to_iron["hydrogen"],
            hydrogen,
        )

        self.assertNotIn(
            "helium",
            process.elements_up_to_iron,
        )

        self.assertEqual(
            len(process.elements_up_to_iron),
            24,
        )

    def test_non_element_components_are_not_forged(
        self
    ):
        universe, _ = self._ready_stars()

        process = StellarNucleosynthesis(universe)
        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIn(
            "energy",
            universe.big_bang.primordial_components,
        )

        self.assertIn(
            "matter",
            universe.big_bang.primordial_components,
        )

        self.assertNotIn(
            "energy",
            universe.big_bang.primordial_elements,
        )

        self.assertNotIn(
            "matter",
            universe.big_bang.primordial_elements,
        )

        self.assertNotIn(
            "energy",
            process.elements_up_to_iron,
        )

        self.assertNotIn(
            "matter",
            process.elements_up_to_iron,
        )

    def test_non_element_in_element_registry_is_rejected(self):
        universe, _ = self._ready_stars()

        universe.big_bang.primordial_elements["energy"] = (
            universe.big_bang.primordial_components["energy"]
        )

        process = StellarNucleosynthesis(universe)

        with self.assertRaisesRegex(
            TypeError,
            "PrimordialElement",
        ):
            process.forge_elements_up_to_iron()

    def test_invalid_canonical_component_is_rejected(
        self
    ):
        universe, _ = self._ready_stars(
            with_big_bang=False,
        )

        big_bang = BigBang(universe)

        big_bang.primordial_elements = {
            "hydrogen": {
                "name": "legacy_hydrogen",
            },
        }

        universe.big_bang = big_bang

        process = StellarNucleosynthesis(universe)

        with self.assertRaisesRegex(
            TypeError,
            "PrimordialElement",
        ):
            process.forge_elements_up_to_iron()

    def test_forging_does_not_read_public_primordial_registry(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key == "primordial_elements":
                    raise AssertionError(
                        "Read public primordial registry"
                    )

                return super().get(key, default)

            def __getitem__(self, key):
                if key == "primordial_elements":
                    raise AssertionError(
                        "Indexed public primordial registry"
                    )

                return super().__getitem__(key)

            def __contains__(self, key):
                if key == "primordial_elements":
                    raise AssertionError(
                        "Checked public primordial registry"
                    )

                return super().__contains__(key)

        universe, _ = self._ready_stars()

        universe.world = GuardedWorld(
            universe.world
        )

        process = StellarNucleosynthesis(universe)
        result = process.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            result.elements_up_to_iron["hydrogen"],
            universe.big_bang.primordial_elements[
                "hydrogen"
            ],
        )

        self.assertEqual(
            len(result.elements_up_to_iron),
            26,
        )

    def test_downstream_supernova_keeps_iron_identity(
        self
    ):
        universe, _ = self._ready_stars()

        nucleosynthesis = StellarNucleosynthesis(
            universe
        )

        forged = nucleosynthesis.forge_elements_up_to_iron()

        self.assertIs(
            forged.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        supernova = SupernovaEnrichment(universe)

        result = supernova.enrich_space()

        self.assertIs(
            result.state,
            SupernovaEnrichmentProcessState.ENRICHED,
        )

        self.assertIs(
            result.enriched_clouds[0]
            .composition["iron"],
            nucleosynthesis.elements_up_to_iron[
                "iron"
            ],
        )


if __name__ == "__main__":
    unittest.main()
