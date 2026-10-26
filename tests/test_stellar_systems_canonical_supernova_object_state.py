import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.heavy_element_nucleosynthesis import (
    HeavyElementNucleosynthesis,
)
from universe.heavy_element_nucleosynthesis_process_state import (
    HeavyElementNucleosynthesisProcessState,
)
from universe.planets import Planets
from universe.planets_process_state import (
    PlanetsProcessState,
)
from universe.primordial_objects import (
    PrimordialCosmicComponent,
)
from universe.stars import Stars
from universe.stellar_nucleosynthesis import (
    StellarNucleosynthesis,
)
from universe.supernova_enrichment import (
    SupernovaEnrichment,
)
from universe.supernova_enrichment_process_state import (
    SupernovaEnrichmentProcessState,
)
from universe.stellar_system_objects import StellarSystem
from universe.stellar_systems import StellarSystems
from universe.stellar_systems_process_state import (
    StellarSystemsProcessState,
)
from universe.universe import Universe
from universe.big_bang import BigBang


class StellarSystemsCanonicalSupernovaTests(
    unittest.TestCase
):

    def _primordial_element(self, name):
        return PrimordialCosmicComponent(
            name=name,
            type="element",
            state="formed",
            origin="big_bang_nucleosynthesis",
        )

    def _cloud(self, name="test_cloud", eligible=True):
        return StellarMaterialCloud(
            name=name,
            type="enriched_stellar_cloud",
            state="expanding",
            composition={
                "hydrogen": "dominant",
                "oxygen": "present",
                "silicon": "present",
                "iron": "present",
            },
            can_form_stellar_systems=eligible,
        )

    def _prepared_chain(self):
        universe = Universe()

        primordial_elements = {
            "hydrogen": self._primordial_element(
                "hydrogen"
            ),
            "helium": self._primordial_element(
                "helium"
            ),
        }

        big_bang = BigBang(universe)
        big_bang.primordial_elements = primordial_elements
        universe.big_bang = big_bang

        source_cloud = StellarMaterialCloud(
            name="primordial_cloud",
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
            source_clouds=[source_cloud],
        )

        stars.form_first_stars()

        nucleosynthesis = StellarNucleosynthesis(
            universe
        )

        nucleosynthesis.forge_elements_up_to_iron()

        supernova = SupernovaEnrichment(universe)

        supernova_result = supernova.enrich_space()

        self.assertIs(
            supernova_result.state,
            SupernovaEnrichmentProcessState.ENRICHED,
        )

        heavy = HeavyElementNucleosynthesis(universe)

        heavy_result = heavy.forge_heavy_elements()

        self.assertIs(
            heavy_result.state,
            HeavyElementNucleosynthesisProcessState.FORGED,
        )

        return universe, supernova, heavy

    def test_canonical_formation_preserves_cloud_identity(
        self
    ):
        universe, supernova, heavy = (
            self._prepared_chain()
        )

        process = StellarSystems(universe)
        result = process.form_stellar_systems()

        self.assertIs(
            result.state,
            StellarSystemsProcessState.FORMED,
        )

        self.assertEqual(len(process.systems), 2)

        self.assertIs(
            universe.stellar_systems_layer,
            process,
        )

        self.assertIs(
            universe.supernova_enrichment_layer,
            supernova,
        )

        cloud = supernova.enriched_clouds[0]

        self.assertIsInstance(
            process.systems[0],
            StellarSystem,
        )

        self.assertIs(
            process.systems[0].source_cloud,
            cloud,
        )

        self.assertIs(
            process.systems[1].source_cloud,
            cloud,
        )

        self.assertIs(
            universe.world["solar_system"],
            process.systems[0],
        )

        self.assertIs(
            universe.world["systems"],
            process.systems,
        )

        self.assertIs(
            universe.world["stellar_system_state"],
            process.system_state,
        )

        self.assertIs(
            cloud.composition["gold"],
            heavy.heavy_elements["gold"],
        )

    def test_heavy_elements_reach_protoplanetary_disk(
        self
    ):
        universe, supernova, heavy = (
            self._prepared_chain()
        )

        process = StellarSystems(universe)
        process.form_stellar_systems()

        disk = (
            process.systems[0]
            .protoplanetary_disk
        )

        for element in (
            "hydrogen",
            "oxygen",
            "silicon",
            "iron",
            "gold",
            "platinum",
            "uranium",
        ):
            with self.subTest(element=element):
                self.assertIn(
                    element,
                    disk.available_elements,
                )

        self.assertTrue(disk.can_form_planets)
        self.assertTrue(disk.can_form_water)
        self.assertTrue(disk.can_form_iron_cores)
        self.assertTrue(disk.can_form_rocky_worlds)

        cloud = supernova.enriched_clouds[0]

        self.assertIs(
            cloud.composition["platinum"],
            heavy.heavy_elements["platinum"],
        )

    def test_public_decoy_cannot_override_canonical_clouds(
        self
    ):
        universe, supernova, _ = (
            self._prepared_chain()
        )

        universe.world["enriched_clouds"] = [
            {"name": "legacy_cloud"},
        ]

        process = StellarSystems(universe)
        result = process.form_stellar_systems()

        self.assertIs(
            result.state,
            StellarSystemsProcessState.FORMED,
        )

        self.assertIs(
            process.systems[0].source_cloud,
            supernova.enriched_clouds[0],
        )

    def test_missing_public_cloud_alias_does_not_block(
        self
    ):
        universe, supernova, _ = (
            self._prepared_chain()
        )

        universe.world.pop(
            "enriched_clouds",
            None,
        )

        process = StellarSystems(universe)
        result = process.form_stellar_systems()

        self.assertIs(
            result.state,
            StellarSystemsProcessState.FORMED,
        )

        self.assertIs(
            process.systems[0].source_cloud,
            supernova.enriched_clouds[0],
        )

    def test_world_only_clouds_do_not_form_systems(
        self
    ):
        universe = Universe()

        universe.world["enriched_clouds"] = [
            self._cloud(),
        ]

        process = StellarSystems(universe)
        result = process.form_stellar_systems()

        self.assertIs(
            result.state,
            StellarSystemsProcessState.FAILED,
        )

        self.assertEqual(process.systems, [])

        self.assertFalse(
            process.system_state.stellar_systems_formed
        )

    def test_canonical_cloud_eligibility_is_respected(
        self
    ):
        universe = Universe()
        supernova = SupernovaEnrichment(universe)

        supernova.enriched_clouds.append(
            self._cloud(
                name="ineligible_cloud",
                eligible=False,
            )
        )

        universe.world["enriched_clouds"] = [
            self._cloud("public_decoy"),
        ]

        process = StellarSystems(universe)
        result = process.form_stellar_systems()

        self.assertIs(
            result.state,
            StellarSystemsProcessState.FAILED,
        )

        self.assertEqual(process.systems, [])

    def test_invalid_canonical_cloud_creates_cronenberg(
        self
    ):
        universe = Universe()
        supernova = SupernovaEnrichment(universe)

        supernova.enriched_clouds.append(
            {
                "name": "legacy_cloud",
                "can_form_stellar_systems": True,
            }
        )

        process = StellarSystems(universe)
        result = process.form_stellar_systems()

        self.assertEqual(
            result.type,
            "quantum_error",
        )

        self.assertIn(
            "StellarMaterialCloud",
            result.cronenberg.origin.error_message,
        )

        self.assertEqual(
            result.cronenberg.origin.source_component,
            "stellar_systems",
        )

        self.assertEqual(
            result.cronenberg.origin.source_operation,
            "form_stellar_systems",
        )

    def test_no_world_read_and_planet_formation(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key == "enriched_clouds":
                    raise AssertionError(
                        "StellarSystems read public clouds"
                    )

                return super().get(key, default)

            def __getitem__(self, key):
                if key == "enriched_clouds":
                    raise AssertionError(
                        "StellarSystems indexed public clouds"
                    )

                return super().__getitem__(key)

        universe, supernova, _ = (
            self._prepared_chain()
        )

        universe.world = GuardedWorld(
            universe.world
        )

        process = StellarSystems(universe)
        result = process.form_stellar_systems()

        self.assertIs(
            result.state,
            StellarSystemsProcessState.FORMED,
        )

        self.assertIs(
            process.systems[0].source_cloud,
            supernova.enriched_clouds[0],
        )

        planet_result = (
            Planets(universe).form_planets()
        )

        self.assertIs(
            planet_result.state,
            PlanetsProcessState.FORMED,
        )

        earth = universe.world["earth"]

        self.assertEqual(earth.name, "earth")
        self.assertTrue(earth.water_possible)
        self.assertTrue(earth.has_iron_core)
        self.assertTrue(earth.has_rocky_crust)


if __name__ == "__main__":
    unittest.main()
