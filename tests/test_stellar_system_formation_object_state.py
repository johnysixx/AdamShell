import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.planets import Planets
from universe.planets_process_state import (
    PlanetsProcessState,
)
from universe.stellar_system_objects import (
    ProtoplanetaryDisk,
    SecondGenerationStar,
    StellarSystem,
)
from universe.stellar_system_state import (
    StellarSystemFormationState,
)
from universe.stellar_system_formation_result_state import (
    StellarSystemFormationResult,
)
from universe.stellar_systems import StellarSystems
from universe.stellar_systems_process_state import (
    StellarSystemsProcessState,
)
from universe.universe import Universe
from universe.supernova_enrichment import SupernovaEnrichment


class StellarSystemFormationObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def _formed_process(self):
        universe = Universe()
        universe.world["enriched_clouds"] = [
            StellarMaterialCloud(
                name="first_enriched_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                composition={
                    "hydrogen": {},
                    "oxygen": {},
                    "silicon": {},
                    "iron": {},
                },
                can_form_stellar_systems=True,
            )
        ]

        supernova_layer = SupernovaEnrichment(universe)
        supernova_layer.enriched_clouds = (
            universe.world["enriched_clouds"]
        )

        process = StellarSystems(universe)
        result = process.form_stellar_systems()

        return universe, process, result

    def test_state_is_object_only(self):
        state = StellarSystemFormationState()

        self._assert_object_only(
            state,
            "stellar_systems_formed",
        )

    def test_initial_values_are_preserved(self):
        state = StellarSystemFormationState()

        self.assertFalse(
            state.stellar_systems_formed
        )
        self.assertFalse(state.solar_system_formed)
        self.assertFalse(
            state.planet_formation_possible
        )
        self.assertFalse(
            state.water_formation_possible
        )
        self.assertFalse(state.rocky_worlds_possible)

    def test_formation_mutates_same_state_object(
        self
    ):
        universe, process, _ = self._formed_process()
        state = process.system_state

        self.assertIs(process.system_state, state)
        self.assertIs(
            universe.world["stellar_system_state"],
            state,
        )
        self.assertTrue(state.stellar_systems_formed)
        self.assertTrue(state.solar_system_formed)
        self.assertTrue(
            state.planet_formation_possible
        )
        self.assertTrue(
            state.water_formation_possible
        )
        self.assertTrue(state.rocky_worlds_possible)

    def test_world_keeps_boundary_registries(
        self
    ):
        universe, process, _ = self._formed_process()

        self.assertIs(
            universe.world["systems"],
            process.systems,
        )
        self.assertIs(
            universe.world["solar_system"],
            process.systems[0],
        )
        self.assertIsInstance(
            universe.world["systems"],
            list,
        )
        self.assertIsInstance(
            universe.world["solar_system"],
            StellarSystem,
        )
        self.assertIsInstance(
            universe.world["solar_system"].star,
            SecondGenerationStar,
        )
        self.assertIsInstance(
            universe.world["solar_system"].protoplanetary_disk,
            ProtoplanetaryDisk,
        )

    def test_runtime_result_is_object_and_snapshot_is_dict(
        self
    ):
        _, process, result = self._formed_process()

        self.assertIsInstance(
            result,
            StellarSystemFormationResult,
        )
        self._assert_object_only(
            result,
            "state",
        )

        self.assertIs(
            result.system_state,
            process.system_state,
        )
        self.assertIsInstance(
            result.systems,
            tuple,
        )
        self.assertIs(
            result.systems[0],
            process.systems[0],
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["system_state"],
            dict,
        )
        self.assertIsInstance(
            snapshot["systems"],
            list,
        )
        self.assertTrue(
            snapshot["system_state"][
                "stellar_systems_formed"
            ]
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_process()

        snapshot = result.to_dict()

        snapshot["system_state"][
            "stellar_systems_formed"
        ] = False
        snapshot["systems"][0][
            "protoplanetary_disk"
        ]["available_elements"].append("fake")

        self.assertTrue(
            process.system_state.stellar_systems_formed
        )
        self.assertNotIn(
            "fake",
            process.systems[0]
            .protoplanetary_disk
            .available_elements,
        )

    def test_material_possibilities_follow_composition(
        self
    ):
        universe = Universe()
        universe.world["enriched_clouds"] = [
            StellarMaterialCloud(
                name="hydrogen_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                composition={"hydrogen": {}},
                can_form_stellar_systems=True,
            )
        ]
        supernova_layer = SupernovaEnrichment(universe)
        supernova_layer.enriched_clouds = (
            universe.world["enriched_clouds"]
        )

        process = StellarSystems(universe)

        process.form_stellar_systems()

        self.assertTrue(
            process.system_state.planet_formation_possible
        )
        self.assertFalse(
            process.system_state.water_formation_possible
        )
        self.assertFalse(
            process.system_state.rocky_worlds_possible
        )

    def test_missing_cloud_preserves_initial_state(
        self
    ):
        universe = Universe()
        process = StellarSystems(universe)

        result = process.form_stellar_systems()

        self.assertIs(
            process.state,
            StellarSystemsProcessState.FAILED,
        )
        self.assertFalse(
            process.system_state.stellar_systems_formed
        )
        self.assertFalse(
            result
            .system_state
            .stellar_systems_formed
        )

    def test_planet_process_uses_solar_system_boundary(
        self
    ):
        universe, _, _ = self._formed_process()
        process = Planets(universe)

        result = process.form_planets()

        self.assertIs(
            result.state,
            PlanetsProcessState.FORMED,
        )
        self.assertEqual(
            universe.world["earth"].name,
            "earth",
        )

    def test_formation_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        universe.world["enriched_clouds"] = [
            StellarMaterialCloud(
                name="broken_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                composition={"iron": {}},
                can_form_stellar_systems=True,
            )
        ]
        supernova_layer = SupernovaEnrichment(universe)
        supernova_layer.enriched_clouds = (
            universe.world["enriched_clouds"]
        )

        process = StellarSystems(universe)

        def broken_history():
            raise RuntimeError(
                "stellar system formation exploded"
            )

        process.record_history = broken_history

        result = process.form_stellar_systems()
        cronenberg = result.cronenberg

        self.assertEqual(
            result.type,
            "quantum_error",
        )
        self.assertIn(
            cronenberg,
            universe.cronenbergs,
        )
        self.assertEqual(
            cronenberg.origin.source_component,
            "stellar_systems",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_stellar_systems",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "stellar system formation exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = StellarSystemFormationState()
        state.solar_system_formed = True

        snapshot = state.to_dict()
        snapshot["solar_system_formed"] = False

        self.assertTrue(state.solar_system_formed)


if __name__ == "__main__":
    unittest.main()
