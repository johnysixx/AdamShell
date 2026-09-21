import unittest

from universe.big_bang import BigBang
from universe.cosmic_clouds import CosmicClouds
from universe.cosmic_objects import StellarMaterialCloud
from universe.primordial_objects import PrimordialCosmicComponent
from universe.stellar_nucleosynthesis import StellarNucleosynthesis
from universe.stellar_objects import PrimordialStar
from universe.universe import Universe


class PrimordialComponentDomainObjectStateTests(
    unittest.TestCase
):

    def test_component_to_dict_is_detached_boundary(self):
        component = PrimordialCosmicComponent(
            name="hydrogen",
            type="element",
            state="formed",
            origin="big_bang_nucleosynthesis",
        )

        snapshot = component.to_dict()
        snapshot["state"] = "changed"

        self.assertEqual(
            component.state,
            "formed",
        )

    def test_cosmic_clouds_reject_legacy_primordial_dict(self):
        universe = Universe()

        universe.world["primordial_elements"] = {
            "hydrogen": {
                "name": "hydrogen",
            },
            "helium": PrimordialCosmicComponent(
                name="helium",
                type="element",
                state="formed",
            ),
        }

        result = CosmicClouds(
            universe
        ).form_germinal_clouds()

        self.assertEqual(
            result["type"],
            "quantum_error",
        )
        self.assertIn(
            "PrimordialCosmicComponent",
            result[
                "cronenberg"
            ].origin.error_message,
        )

    def test_stellar_nucleosynthesis_keeps_primordial_element_object(
        self
    ):
        universe = Universe()

        BigBang(
            universe
        ).run_process()

        cloud = StellarMaterialCloud(
            name="cloud",
            type="germinal_cloud",
            state="condensing",
            composition={},
            can_form_stars=True,
        )

        universe.world["first_stars"] = [
            PrimordialStar(
                name="first_star",
                type="primordial_star",
                generation=1,
                state="burning",
                source_cloud=cloud,
                composition={},
                can_fuse_elements=True,
                can_create_heavy_elements=True,
            )
        ]

        from universe.stellar_state import (
            StellarFormationState,
        )

        stellar_state = StellarFormationState()
        stellar_state.stellar_fusion_possible = True

        universe.world[
            "stellar_state"
        ] = stellar_state

        hydrogen = universe.world[
            "primordial_elements"
        ]["hydrogen"]

        process = StellarNucleosynthesis(
            universe
        )
        process.forge_elements_up_to_iron()

        self.assertIs(
            process.elements_up_to_iron[
                "hydrogen"
            ],
            hydrogen,
        )
        self.assertEqual(
            process.elements_up_to_iron[
                "hydrogen"
            ].state,
            "formed",
        )

    def test_stellar_nucleosynthesis_rejects_legacy_primordial_dict(
        self
    ):
        universe = Universe()

        cloud = StellarMaterialCloud(
            name="cloud",
            type="germinal_cloud",
            state="condensing",
            composition={},
            can_form_stars=True,
        )

        universe.world["first_stars"] = [
            PrimordialStar(
                name="first_star",
                type="primordial_star",
                generation=1,
                state="burning",
                source_cloud=cloud,
                composition={},
                can_fuse_elements=True,
                can_create_heavy_elements=True,
            )
        ]

        from universe.stellar_state import (
            StellarFormationState,
        )

        stellar_state = StellarFormationState()
        stellar_state.stellar_fusion_possible = True

        universe.world[
            "stellar_state"
        ] = stellar_state

        universe.world[
            "primordial_elements"
        ] = {
            "hydrogen": {
                "name": "hydrogen",
                "type": "element",
            },
        }

        with self.assertRaises(
            TypeError
        ):
            StellarNucleosynthesis(
                universe
            ).forge_elements_up_to_iron()


if __name__ == "__main__":
    unittest.main()
