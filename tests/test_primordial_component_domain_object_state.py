import unittest

from universe.big_bang import BigBang
from universe.cosmic_clouds import CosmicClouds
from universe.cosmic_objects import StellarMaterialCloud
from universe.primordial_objects import PrimordialElement
from universe.stellar_nucleosynthesis import StellarNucleosynthesis
from universe.stellar_objects import PrimordialStar
from universe.stars import Stars
from universe.universe import Universe


class PrimordialComponentDomainObjectStateTests(
    unittest.TestCase
):

    def _wire_canonical_big_bang(self, universe, elements):
        big_bang = BigBang(universe)
        big_bang.primordial_elements = elements
        universe.big_bang = big_bang

    def test_component_to_dict_is_detached_boundary(self):
        component = PrimordialElement(
            name="hydrogen",
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

        primordial_elements = {
            "hydrogen": {
                "name": "hydrogen",
            },
            "helium": PrimordialElement(
                name="helium",
                state="formed",
            ),
        }

        self._wire_canonical_big_bang(universe, primordial_elements)

        result = CosmicClouds(
            universe
        ).form_germinal_clouds()

        self.assertEqual(
            result.type,
            "quantum_error",
        )
        self.assertIn(
            "PrimordialElement",
            result.cronenberg.origin.error_message,
        )

    def test_stellar_nucleosynthesis_keeps_primordial_element_object(
        self
    ):
        universe = Universe()

        universe.start_big_bang()

        cloud = StellarMaterialCloud(
            name="cloud",
            type="germinal_cloud",
            state="condensing",
            composition={},
            can_form_stars=True,
        )

        stars_layer = Stars(universe)

        stars_layer.stars.extend([
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
        ])

        stars_layer.stellar_state.stellar_fusion_possible = True
        stars_layer.write_to_world()

        hydrogen = universe.big_bang.primordial_elements["hydrogen"]

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

        stars_layer = Stars(universe)

        stars_layer.stars.extend([
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
        ])

        stars_layer.stellar_state.stellar_fusion_possible = True
        stars_layer.write_to_world()

        primordial_elements = {
            "hydrogen": {
                "name": "hydrogen",
                "type": "element",
            },
        }

        self._wire_canonical_big_bang(universe, primordial_elements)

        with self.assertRaises(
            TypeError
        ):
            StellarNucleosynthesis(
                universe
            ).forge_elements_up_to_iron()


if __name__ == "__main__":
    unittest.main()
