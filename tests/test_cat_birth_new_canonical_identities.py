import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from cats.cat_birth_resolver import (
    CatBirthResolver
)


class CatBirthNewCanonicalIdentitiesTests(
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

    def test_first_queen_profile_is_queen_elisabeth(self):
        result = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver
                .queen_elisabeth_profile
            )
        )

        self.assertTrue(
            result["matched"]
        )

        self.assertEqual(
            result["occurrence"],
            1
        )

        self.assertEqual(
            result["identity"],
            "queen_elisabeth"
        )

        self.assertIsNone(
            result["special_birth_event"]
        )

    def test_second_queen_profile_is_mia(self):
        first = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver
                .queen_elisabeth_profile
            )
        )

        second = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver
                .queen_elisabeth_profile
            )
        )

        self.assertEqual(
            first["identity"],
            "queen_elisabeth"
        )

        self.assertEqual(
            second["occurrence"],
            2
        )

        self.assertEqual(
            second["identity"],
            "mia"
        )

        self.assertEqual(
            second["special_birth_event"],
            "mia_birth_global_rotation"
        )

    def test_later_queen_profile_is_ordinary_cat(self):
        for _ in range(2):
            self.resolver._resolve_canonical_profile(
                self.resolver
                .queen_elisabeth_profile
            )

        third = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver
                .queen_elisabeth_profile
            )
        )

        self.assertTrue(
            third["matched"]
        )

        self.assertEqual(
            third["occurrence"],
            3
        )

        self.assertIsNone(
            third["identity"]
        )

    def test_first_garfield_profile_is_garfield(self):
        result = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver.garfield_profile
            )
        )

        self.assertTrue(
            result["matched"]
        )

        self.assertEqual(
            result["occurrence"],
            1
        )

        self.assertEqual(
            result["identity"],
            "garfield"
        )

        self.assertIsNone(
            result["special_birth_event"]
        )

    def test_later_garfield_profile_is_ordinary_cat(self):
        first = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver.garfield_profile
            )
        )

        second = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver.garfield_profile
            )
        )

        self.assertEqual(
            first["identity"],
            "garfield"
        )

        self.assertEqual(
            second["occurrence"],
            2
        )

        self.assertIsNone(
            second["identity"]
        )

    def test_sequences_have_independent_counters(self):
        queen = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver
                .queen_elisabeth_profile
            )
        )

        garfield = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver.garfield_profile
            )
        )

        pazuzu = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver.canonical_profile
            )
        )

        self.assertEqual(
            queen["occurrence"],
            1
        )

        self.assertEqual(
            queen["identity"],
            "queen_elisabeth"
        )

        self.assertEqual(
            garfield["occurrence"],
            1
        )

        self.assertEqual(
            garfield["identity"],
            "garfield"
        )

        self.assertEqual(
            pazuzu["occurrence"],
            1
        )

        self.assertEqual(
            pazuzu["identity"],
            "pazuzu"
        )


if __name__ == "__main__":
    unittest.main()