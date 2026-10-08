import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap,
)
from cats.cat_birth_objects import (
    CatBirthProfile,
    CatCanonicalBirthResolution,
)
from cats.cat_birth_resolver import CatBirthResolver


class CatBirthProfileObjectStateTests(unittest.TestCase):

    def setUp(self):
        registry = UniverseRegistry()
        self.universe = Universe()
        _, layers, _ = UniverseBootstrap(
            registry,
            self.universe,
        ).run()
        self.bar = layers.get("meeting")
        self.bar.welcome_cat_d20()
        self.resolver = CatBirthResolver(
            self.universe,
            self.bar,
        )

    def test_canonical_profiles_are_objects(self):
        self.assertIsInstance(
            self.resolver.canonical_profile,
            CatBirthProfile,
        )
        self.assertIsInstance(
            self.resolver.queen_elisabeth_profile,
            CatBirthProfile,
        )
        self.assertIsInstance(
            self.resolver.garfield_profile,
            CatBirthProfile,
        )

    def test_canonical_resolution_is_object(self):
        result = (
            self.resolver
            ._resolve_canonical_profile(
                self.resolver.canonical_profile
            )
        )

        self.assertIsInstance(
            result,
            CatCanonicalBirthResolution,
        )
        self.assertEqual(result.identity, "pazuzu")
        self.assertIs(
            result.profile,
            self.resolver.canonical_profile,
        )

    def test_mapping_profile_is_rejected(self):
        with self.assertRaises(TypeError):
            self.resolver._resolve_canonical_profile({
                "color": "black",
                "fur_length": "short",
                "pattern": "solid",
                "eye_color": "green",
                "sex": "female",
            })

    def test_profile_trait_change_returns_new_object(self):
        original = self.resolver.canonical_profile
        changed = original.with_trait(
            "eye_color",
            "gold",
        )

        self.assertIsNot(original, changed)
        self.assertEqual(original.eye_color, "green")
        self.assertEqual(changed.eye_color, "gold")

    def test_profile_snapshot_is_detached_and_canonical_is_object_only(
        self
    ):
        profile = self.resolver.canonical_profile
        resolution = CatCanonicalBirthResolution(
            matched=True,
            occurrence=1,
            identity="pazuzu",
            profile=profile,
            special_birth_event=(
                "pazuzu_birth_dice_resonance"
            ),
        )

        profile_snapshot = profile.to_dict()
        profile_snapshot["color"] = "white"

        self.assertEqual(
            profile.color,
            "black",
        )

        self.assertIs(
            resolution.profile,
            profile,
        )

        self.assertEqual(
            resolution.identity,
            "pazuzu",
        )

        self.assertFalse(
            hasattr(
                resolution,
                "to_dict",
            )
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    resolution,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = resolution[
                "identity"
            ]


if __name__ == "__main__":
    unittest.main()
