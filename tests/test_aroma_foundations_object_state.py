import unittest
from types import SimpleNamespace

from universe.aroma_foundations import (
    AromaDefinition,
    AromaFoundations,
    AromaMixture,
)
from cats.cats import Cats
from universe.universe import Universe


class AromaFoundationsObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.foundations = AromaFoundations(self.universe)

    def test_aroma_registry_contains_definition_objects(self):
        ozone = self.foundations.aromas["ozone"]

        self.assertIsInstance(ozone, AromaDefinition)
        self.assertEqual(ozone.name, "ozone")
        self.assertEqual(ozone.formula, "O3")
        self.assertGreater(ozone.components["ozone"], 0.9)

    def test_mixture_registry_contains_mixture_objects(self):
        rum = self.foundations.mixtures["raspberry_rum"]

        self.assertIsInstance(rum, AromaMixture)
        self.assertIn("ethanol", rum.chemical_base)
        self.assertGreater(rum.aroma_profile["berry"], 0.0)

    def test_getters_return_detached_objects(self):
        rum = self.foundations.get_mixture("raspberry_rum")
        rum.aroma_profile["berry"] = 0.0

        stored = self.foundations.mixtures["raspberry_rum"]
        self.assertEqual(stored.aroma_profile["berry"], 1.0)

    def test_to_dict_returns_detached_snapshot(self):
        ozone = self.foundations.get_aroma("ozone")
        snapshot = ozone.to_dict()
        snapshot["components"]["ozone"] = 0.0
        snapshot["natural_sources"].append("test")

        self.assertEqual(ozone.components["ozone"], 1.0)
        self.assertNotIn("test", ozone.natural_sources)

    def test_mixture_rejects_non_mapping_aroma_profile(self):
        with self.assertRaises(TypeError):
            AromaMixture(
                name="invalid",
                type="test",
                aroma_profile=[("berry", 1.0)],
            )

    def test_cat_learning_rejects_legacy_mixture_dict(self):
        cats = Cats(self.universe)
        cat = cats.create_cat(name="student", color="black", fur_length="short")
        meeting_place = SimpleNamespace(
            raspberry_rum={
                "aroma_profile": {"berry": 1.0},
            }
        )

        with self.assertRaises(TypeError):
            cats.learn_raspberry_rum_aroma(cat, meeting_place)


if __name__ == "__main__":
    unittest.main()
