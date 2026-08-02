import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from cats.cat_birth_effect_resolver import (
    CatBirthEffectResolver
)
from cats.cat_birth_resolver import (
    CatBirthResolver
)


class FullFixedRng:

    def random(self):
        return 0.0

    def randint(
        self,
        minimum,
        maximum
    ):
        return minimum

    def uniform(
        self,
        minimum,
        maximum
    ):
        return minimum

    def choice(
        self,
        values
    ):
        return list(values)[0]

    def sample(
        self,
        values,
        count
    ):
        return list(values)[:count]

    def shuffle(
        self,
        values
    ):
        return None


class WoodooBirthEffectsTests(
    unittest.TestCase
):

    def setUp(self):
        registry = UniverseRegistry()
        self.universe = Universe()

        root, layers, idea = UniverseBootstrap(
            registry,
            self.universe
        ).run()

        self.bar = layers.get(
            "meeting"
        )

        self.bar.welcome_cat_d20()

        self.effects = CatBirthEffectResolver(
            self.universe,
            self.bar
        )

    def test_first_woodoo_rotates_only_d20(self):
        result = self.effects.execute(
            identity="woodoo",
            cat_name="woodoo",
            rng=FullFixedRng(),
            special_birth_event=(
                "woodoo_birth_chaos"
            )
        )

        self.assertEqual(
            result["name"],
            "woodoo_birth_d20_rotation"
        )

        self.assertEqual(
            result[
                "registered_d20_count"
            ],
            len(
                self.universe
                .d20_registry
                .artifacts
            )
        )

        self.assertFalse(
            result["bar_dice_rotated"]
        )

    def test_later_woodoo_reconfigures_space_and_marks_next_cat(self):
        quantum_space = (
            self.universe
            .quantum_space
        )

        before_count = (
            quantum_space
            .reconfiguration_count
        )

        result = self.effects.execute(
            identity="woodoo",
            cat_name="woodoo",
            rng=FullFixedRng(),
            special_birth_event=(
                "woodoo_rebirth_chaos"
            )
        )

        self.assertEqual(
            result["name"],
            (
                "woodoo_rebirth_quantum_"
                "reconfiguration"
            )
        )

        self.assertEqual(
            quantum_space
            .reconfiguration_count,
            before_count + 1
        )

        self.assertTrue(
            self.universe
            .next_cat_birth_white
        )

    def test_white_trace_is_used_only_by_next_cat(self):
        resolver = CatBirthResolver(
            self.universe,
            self.bar
        )

        self.universe.next_cat_birth_white = True

        original_resolve_canonical = (
            resolver
            ._resolve_canonical_profile
        )

        captured_profiles = []

        def capture_profile(
            profile,
            rng=None
        ):
            captured_profiles.append(
                dict(profile)
            )

            return {
                "matched": False,
                "occurrence": 0,
                "identity": None,
                "profile": dict(profile),
                "special_birth_event": None,
                "woodoo_rebirth": False
            }

        resolver._resolve_canonical_profile = (
            capture_profile
        )

        try:
            resolver.resolve_profile(
                rng=FullFixedRng()
            )

            resolver.resolve_profile(
                rng=FullFixedRng()
            )

        finally:
            resolver._resolve_canonical_profile = (
                original_resolve_canonical
            )

        self.assertEqual(
            captured_profiles[0]["color"],
            "white"
        )

        self.assertFalse(
            self.universe
            .next_cat_birth_white
        )

        self.assertFalse(
            captured_profiles[1]["color"]
            == "white"
            and captured_profiles[0]
            != captured_profiles[1]
        )


if __name__ == "__main__":
    unittest.main()