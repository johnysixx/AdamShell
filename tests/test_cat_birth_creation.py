import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from cats.cat_birth_resolver import (
    CatBirthResolver
)


class CatBirthCreationTests(
    unittest.TestCase
):

    def setUp(self):
        self.registry = UniverseRegistry()
        self.universe = Universe()

        (
            self.root_transition,
            self.layers,
            self.idea_universe
        ) = UniverseBootstrap(
            self.registry,
            self.universe
        ).run()

        self.bar = self.layers.get(
            "meeting"
        )

        self.bar.welcome_cat_d20()

        self.resolver = CatBirthResolver(
            self.universe,
            self.bar
        )

    def _ordinary_birth(self):
        return {
            "profile": {
                "color": "white",
                "fur_length": "long",
                "pattern": "tabby",
                "eye_color": "blue",
                "sex": "female"
            },
            "rolled_profile": {
                "color": "white",
                "fur_length": "long",
                "pattern": "tabby",
                "eye_color": "blue",
                "sex": "female"
            },
            "canonical": {
                "matched": False,
                "occurrence": 0,
                "identity": None,
                "profile": {
                    "color": "white",
                    "fur_length": "long",
                    "pattern": "tabby",
                    "eye_color": "blue",
                    "sex": "female"
                },
                "special_birth_event": None
            },
            "genetics": {
                "valid": True,
                "conflict_count": 0,
                "conflict_history": [],
                "cronenberg_count": 0
            },
            "trait_dice_mapping": {
                "cat_d20_value": 8,
                "die_to_trait": {},
                "trait_to_die": {}
            },
            "percentile": {
                "die": "d10_percentile",
                "value": 70
            }
        }

    def test_create_cat_manifests_ordinary_cat(self):
        birth = self._ordinary_birth()

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        result = self.resolver.create_cat()

        cat = result["cat"]

        self.assertTrue(
            result["created"]
        )

        self.assertEqual(
            result["name"],
            "cat_born_from_dice"
        )

        self.assertEqual(
            cat["name"],
            "cat_0001"
        )

        self.assertEqual(
            cat["color"],
            "white"
        )

        self.assertEqual(
            cat["fur_length"],
            "long"
        )

        self.assertEqual(
            cat["pattern"],
            "tabby"
        )

        self.assertEqual(
            cat["eye_color"],
            "blue"
        )

        self.assertEqual(
            cat["sex"],
            "female"
        )

        self.assertIsNone(
            cat["canonical_identity"]
        )

        self.assertIn(
            cat,
            self.universe.cats_layer.cats
        )

        self.assertEqual(
            cat["birth_profile"],
            birth["profile"]
        )

        self.assertEqual(
            cat["rolled_birth_profile"],
            birth["rolled_profile"]
        )

    def test_generated_cat_names_increment(self):
        birth = self._ordinary_birth()

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        first = self.resolver.create_cat()
        second = self.resolver.create_cat()

        self.assertEqual(
            first["cat"]["name"],
            "cat_0001"
        )

        self.assertEqual(
            second["cat"]["name"],
            "cat_0002"
        )

    def test_explicit_name_is_preserved(self):
        birth = self._ordinary_birth()

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        result = self.resolver.create_cat(
            name="micka"
        )

        self.assertTrue(
            result["created"]
        )

        self.assertEqual(
            result["cat"]["name"],
            "micka"
        )


if __name__ == "__main__":
    unittest.main()