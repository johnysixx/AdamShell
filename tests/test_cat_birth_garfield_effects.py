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


class GarfieldMaskRng:

    def __init__(
        self,
        effect_mask
    ):
        self.effect_mask = effect_mask
        self.mask_used = False

    def randint(
        self,
        minimum,
        maximum
    ):
        if (
            not self.mask_used
            and minimum == 1
            and maximum == 7
        ):
            self.mask_used = True
            return self.effect_mask

        return minimum

    def random(self):
        return 0.0

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


class CatBirthGarfieldEffectsTests(
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

    def execute_mask(
        self,
        mask
    ):
        return self.effects.execute(
            identity="garfield",
            cat_name="garfield",
            rng=GarfieldMaskRng(mask),
            special_birth_event=(
                "garfield_birth_effect_"
                "combination"
            )
        )

    def test_mask_one_forces_next_woodoo(self):
        result = self.execute_mask(1)

        self.assertEqual(
            result["effect_names"],
            [
                "force_next_woodoo"
            ]
        )

        self.assertTrue(
            result["force_next_woodoo"]
        )

        self.assertFalse(
            result["cat_d20_rotated"]
        )

        self.assertFalse(
            result["quantum_d20_rotated"]
        )

        self.assertTrue(
            self.universe
            .force_next_woodoo_birth
        )

    def test_mask_two_rotates_only_cat_d20(self):
        before = len(
            self.bar
            .cat_d20_secret_history
        )

        result = self.execute_mask(2)

        self.assertEqual(
            result["effect_names"],
            [
                "rotate_cat_d20"
            ]
        )

        self.assertFalse(
            result["force_next_woodoo"]
        )

        self.assertTrue(
            result["cat_d20_rotated"]
        )

        self.assertFalse(
            result["quantum_d20_rotated"]
        )

        self.assertEqual(
            len(
                self.bar
                .cat_d20_secret_history
            ),
            before + 1
        )

    def test_mask_four_rotates_only_quantum_d20(self):
        before = (
            self.universe
            .quantum_die
            .roll_count
        )

        result = self.execute_mask(4)

        self.assertEqual(
            result["effect_names"],
            [
                "rotate_quantum_d20"
            ]
        )

        self.assertFalse(
            result["force_next_woodoo"]
        )

        self.assertFalse(
            result["cat_d20_rotated"]
        )

        self.assertTrue(
            result["quantum_d20_rotated"]
        )

        self.assertEqual(
            self.universe
            .quantum_die
            .roll_count,
            before + 1
        )

    def test_mask_seven_runs_all_three_effects(self):
        result = self.execute_mask(7)

        self.assertEqual(
            result["effect_names"],
            [
                "force_next_woodoo",
                "rotate_cat_d20",
                "rotate_quantum_d20"
            ]
        )

        self.assertEqual(
            result["effect_count"],
            3
        )

        self.assertTrue(
            result["force_next_woodoo"]
        )

        self.assertTrue(
            result["cat_d20_rotated"]
        )

        self.assertTrue(
            result["quantum_d20_rotated"]
        )

    def test_all_seven_masks_are_nonempty(self):
        for mask in range(1, 8):
            with self.subTest(
                effect_mask=mask
            ):
                result = self.execute_mask(
                    mask
                )

                self.assertEqual(
                    result["effect_mask"],
                    mask
                )

                self.assertGreaterEqual(
                    result["effect_count"],
                    1
                )

                self.assertEqual(
                    result["effect_count"],
                    len(
                        result["effect_names"]
                    )
                )

    def test_forced_effect_makes_next_cat_woodoo(self):
        resolver = CatBirthResolver(
            self.universe,
            self.bar
        )

        self.universe.force_next_woodoo_birth = True

        result = resolver.resolve_profile(
            rng=GarfieldMaskRng(1)
        )

        canonical = result[
            "canonical"
        ]

        self.assertEqual(
            canonical["identity"],
            "woodoo"
        )

        self.assertTrue(
            canonical["forced_birth"]
        )

        self.assertEqual(
            canonical["forced_by"],
            "garfield"
        )

        self.assertEqual(
            canonical[
                "special_birth_event"
            ],
            "woodoo_rebirth_chaos"
        )

        self.assertFalse(
            self.universe
            .force_next_woodoo_birth
        )


if __name__ == "__main__":
    unittest.main()