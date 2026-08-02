import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from cats.cat_birth_effect_resolver import (
    CatBirthEffectResolver
)


class FirstChoiceRng:

    def choice(
        self,
        values
    ):
        return list(values)[0]

    def randint(
        self,
        minimum,
        maximum
    ):
        return minimum

    def random(self):
        return 0.5


class CatBirthQueenAndGarfieldEffectsTests(
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

        self.effects = (
            CatBirthEffectResolver(
                self.universe,
                self.bar
            )
        )

    def test_queen_rotates_all_dice_and_one_other_effect(self):
        result = self.effects.execute(
            identity="queen_elisabeth",
            cat_name="queen_elisabeth",
            rng=FirstChoiceRng(),
            special_birth_event=(
                "queen_elisabeth_birth_effects"
            )
        )

        rotation = result[
            "dice_rotation"
        ]

        self.assertEqual(
            result["name"],
            "queen_elisabeth_birth_effects"
        )

        self.assertEqual(
            rotation["bar_dice_count"],
            6
        )

        self.assertEqual(
            rotation[
                "registered_d20_count"
            ],
            len(
                self.universe
                .d20_registry
                .artifacts
            )
        )

        self.assertEqual(
            result[
                "selected_non_dice_effect"
            ],
            "woodoo_birth_chaos"
        )

        self.assertEqual(
            result[
                "non_dice_result"
            ]["effect_type"],
            "non_dice"
        )

    def test_garfield_selects_one_valid_effect_combination(
        self
    ):
        result = self.effects.execute(
            identity="garfield",
            cat_name="garfield",
            rng=FirstChoiceRng(),
            special_birth_event=(
                "garfield_birth_effect_"
                "combination"
            )
        )

        self.assertEqual(
            result["name"],
            "garfield_birth_effect_combination"
        )

        self.assertEqual(
            result["effect_mask"],
            1
        )

        self.assertEqual(
            result["effect_names"],
            [
                "force_next_woodoo"
            ]
        )

        self.assertEqual(
            result["effect_count"],
            1
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

        self.assertTrue(
            result["triggered"]
        )


if __name__ == "__main__":
    unittest.main()