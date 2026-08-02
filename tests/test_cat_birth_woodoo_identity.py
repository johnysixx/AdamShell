import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from cats.cat_birth_resolver import (
    CatBirthResolver
)


class RareHitRng:

    def random(self):
        return 0.0005


class RareMissRng:

    def random(self):
        return 0.5


class CatBirthWoodooIdentityTests(
    unittest.TestCase
):

    def setUp(self):
        registry = UniverseRegistry()
        self.universe = Universe()

        root, layers, idea = UniverseBootstrap(
            registry,
            self.universe
        ).run()

        bar = layers.get("meeting")
        bar.welcome_cat_d20()

        self.resolver = CatBirthResolver(
            self.universe,
            bar
        )

        self.canonical = {
            "color": "black",
            "fur_length": "short",
            "pattern": "solid",
            "eye_color": "green",
            "sex": "female"
        }

        self.ordinary = {
            "color": "white",
            "fur_length": "long",
            "pattern": "tabby",
            "eye_color": "blue",
            "sex": "male"
        }

    def _create_first_woodoo(self):
        first = (
            self.resolver
            ._resolve_canonical_profile(
                self.canonical,
                rng=RareMissRng()
            )
        )

        second = (
            self.resolver
            ._resolve_canonical_profile(
                self.canonical,
                rng=RareMissRng()
            )
        )

        third = (
            self.resolver
            ._resolve_canonical_profile(
                self.canonical,
                rng=RareMissRng()
            )
        )

        return first, second, third

    def test_third_canonical_profile_is_first_woodoo(self):
        first, second, third = (
            self._create_first_woodoo()
        )

        self.assertEqual(
            first["identity"],
            "pazuzu"
        )

        self.assertEqual(
            second["identity"],
            "gib"
        )

        self.assertEqual(
            third["identity"],
            "woodoo"
        )

        self.assertEqual(
            third["profile"],
            {
                "color": "black",
                "fur_length": "short",
                "pattern": "solid",
                "eye_color": "gold",
                "sex": "female"
            }
        )

        self.assertEqual(
            self.resolver.woodoo_birth_count,
            1
        )

    def test_later_canonical_profile_can_rarely_create_woodoo(self):
        self._create_first_woodoo()

        result = (
            self.resolver
            ._resolve_canonical_profile(
                self.canonical,
                rng=RareHitRng()
            )
        )

        self.assertTrue(
            result["matched"]
        )

        self.assertEqual(
            result["occurrence"],
            4
        )

        self.assertEqual(
            result["identity"],
            "woodoo"
        )

        self.assertTrue(
            result["woodoo_rebirth"]
        )

        self.assertEqual(
            result["woodoo_birth_number"],
            2
        )

        self.assertEqual(
            result["profile"],
            {
                "color": "black",
                "fur_length": "short",
                "pattern": "solid",
                "eye_color": "gold",
                "sex": "female"
            }
        )

    def test_later_canonical_profile_normally_creates_ordinary_black_cat(self):
        self._create_first_woodoo()

        result = (
            self.resolver
            ._resolve_canonical_profile(
                self.canonical,
                rng=RareMissRng()
            )
        )

        self.assertTrue(
            result["matched"]
        )

        self.assertEqual(
            result["occurrence"],
            4
        )

        self.assertIsNone(
            result["identity"]
        )

        self.assertFalse(
            result["woodoo_rebirth"]
        )

        self.assertEqual(
            result["profile"],
            self.canonical
        )

        self.assertEqual(
            result["profile"]["eye_color"],
            "green"
        )

    def test_noncanonical_profile_never_creates_woodoo(self):
        self._create_first_woodoo()

        result = (
            self.resolver
            ._resolve_canonical_profile(
                self.ordinary,
                rng=RareHitRng()
            )
        )

        self.assertFalse(
            result["matched"]
        )

        self.assertIsNone(
            result["identity"]
        )

        self.assertFalse(
            result["woodoo_rebirth"]
        )

        self.assertEqual(
            result["profile"],
            self.ordinary
        )


if __name__ == "__main__":
    unittest.main()