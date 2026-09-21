import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.stars import Stars
from universe.stellar_nucleosynthesis import StellarNucleosynthesis
from universe.stellar_objects import PrimordialStar
from universe.stellar_state import StellarFormationState
from universe.supernova_enrichment import SupernovaEnrichment
from universe.universe import Universe


class StellarDomainObjectStateTests(unittest.TestCase):

    def _cloud(self, name="source_cloud"):
        return StellarMaterialCloud(
            name=name,
            type="germinal_cloud",
            state="condensing",
            composition={
                "hydrogen": "dominant",
                "helium": "secondary",
            },
            can_form_stars=True,
        )

    def _star(self):
        return PrimordialStar(
            name="test_star",
            type="primordial_star",
            generation=1,
            state="ignited",
            source_cloud=self._cloud(),
            composition={
                "hydrogen": "dominant",
                "helium": "secondary",
            },
            can_fuse_elements=True,
            can_create_heavy_elements=True,
        )

    def test_primordial_star_is_object_only(self):
        star = self._star()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(hasattr(star, mapping_method))

        with self.assertRaises(TypeError):
            _ = star["name"]

    def test_star_keeps_source_cloud_object(self):
        cloud = self._cloud("birth_cloud")
        star = PrimordialStar(
            name="test_star",
            type="primordial_star",
            generation=1,
            state="ignited",
            source_cloud=cloud,
            composition={},
            can_fuse_elements=True,
            can_create_heavy_elements=True,
        )

        self.assertIs(star.source_cloud, cloud)
        self.assertEqual(star.formed_from, "birth_cloud")

    def test_star_rejects_legacy_source_cloud_dict(self):
        with self.assertRaises(TypeError):
            PrimordialStar(
                name="legacy_star",
                type="primordial_star",
                generation=1,
                state="ignited",
                source_cloud={"name": "legacy_cloud"},
                composition={},
                can_fuse_elements=True,
                can_create_heavy_elements=True,
            )

    def test_composition_is_read_only(self):
        star = self._star()

        with self.assertRaises(TypeError):
            star.composition["hydrogen"] = "missing"

    def test_to_dict_is_detached_boundary(self):
        star = self._star()

        snapshot = star.to_dict()
        snapshot["composition"]["hydrogen"] = "missing"
        snapshot["formed_from"] = "other_cloud"

        self.assertEqual(
            star.composition["hydrogen"],
            "dominant",
        )
        self.assertEqual(star.formed_from, "source_cloud")

    def test_star_formation_preserves_cloud_identity(self):
        universe = Universe()
        cloud = self._cloud("formation_cloud")
        universe.world["germinal_clouds"] = [cloud]

        process = Stars(universe)
        process.form_first_stars()

        self.assertIsInstance(process.stars[0], PrimordialStar)
        self.assertIs(process.stars[0].source_cloud, cloud)

    def test_stellar_nucleosynthesis_rejects_legacy_star_dict(self):
        universe = Universe()
        universe.world["first_stars"] = [
            {"name": "legacy_star"}
        ]
        state = StellarFormationState()
        state.stellar_fusion_possible = True
        universe.world["stellar_state"] = state

        process = StellarNucleosynthesis(universe)

        with self.assertRaises(TypeError):
            process.forge_elements_up_to_iron()

    def test_supernova_boundary_rejects_legacy_star_dict(self):
        universe = Universe()
        universe.world["first_stars"] = [
            {"name": "legacy_star"}
        ]
        universe.world["elements_up_to_iron"] = {
            "iron": {"atomic_number": 26},
        }

        result = SupernovaEnrichment(universe).enrich_space()

        self.assertEqual(result["type"], "quantum_error")
        self.assertIn(
            "PrimordialStar",
            result["cronenberg"].origin.error_message,
        )


if __name__ == "__main__":
    unittest.main()
