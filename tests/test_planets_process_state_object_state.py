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
from universe.universe import Universe


class PlanetsProcessStateObjectStateTests(
    unittest.TestCase
):

    def _solar_system(
        self,
        *,
        can_form_planets=True,
    ):
        elements = (
            "hydrogen",
            "carbon",
            "nitrogen",
            "oxygen",
            "magnesium",
            "silicon",
            "calcium",
            "iron",
        )

        source_cloud = StellarMaterialCloud(
            name="planet_process_test_cloud",
            type="enriched_stellar_cloud",
            state="expanding",
            composition={
                element: {}
                for element in elements
            },
            can_form_stellar_systems=True,
        )

        return StellarSystem(
            name="solar_system",
            type="stellar_system",
            state="forming",
            generation=2,
            source_cloud=source_cloud,
            star=SecondGenerationStar(
                name="sun",
                type="main_sequence_star",
                state="ignited",
                generation=2,
            ),
            protoplanetary_disk=ProtoplanetaryDisk(
                name="solar_protoplanetary_disk",
                type="protoplanetary_disk",
                state="rotating",
                available_elements=elements,
                can_form_planets=can_form_planets,
                can_form_water=True,
                can_form_iron_cores=True,
                can_form_rocky_worlds=True,
            ),
        )

    def test_process_starts_ready_as_enum(self):
        process = Planets(Universe())

        self.assertIs(
            process.state,
            PlanetsProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_solar_system_sets_failed_enum(self):
        process = Planets(Universe())

        result = process.form_planets()

        self.assertIs(
            process.state,
            PlanetsProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_inactive_disk_sets_failed_enum(self):
        universe = Universe()
        universe.world["solar_system"] = (
            self._solar_system(
                can_form_planets=False,
            )
        )
        process = Planets(universe)

        result = process.form_planets()

        self.assertIs(
            process.state,
            PlanetsProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_formation_sets_formed_enum(self):
        universe = Universe()
        universe.world["solar_system"] = (
            self._solar_system()
        )
        process = Planets(universe)

        result = process.form_planets()

        self.assertIs(
            process.state,
            PlanetsProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = Planets(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in PlanetsProcessState
            },
            {
                "ready",
                "failed",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
