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

    def test_garfield_runs_all_non_dice_effects(self):
        dice_history_before = len(
            self.bar
            .dice_box
            .rotation_history
        ) if hasattr(
            self.bar.dice_box,
            "rotation_history"
        ) else 0

        result = self.effects.execute(
            identity="garfield",
            cat_name="garfield",
            rng=FirstChoiceRng(),
            special_birth_event=(
                "garfield_birth_all_"
                "non_dice_effects"
            )
        )

        dice_history_after = len(
            self.bar
            .dice_box
            .rotation_history
        ) if hasattr(
            self.bar.dice_box,
            "rotation_history"
        ) else 0

        self.assertEqual(
            result["name"],
            "garfield_birth_all_non_dice_effects"
        )

        self.assertFalse(
            result["dice_rotated"]
        )

        self.assertEqual(
            dice_history_before,
            dice_history_after
        )

        self.assertEqual(
            result["effect_names"],
            [
                "woodoo_birth_chaos",
                "woodoo_rebirth_chaos"
            ]
        )

        self.assertEqual(
            len(result["effects"]),
            2
        )

        self.assertTrue(
            all(
                effect["triggered"]
                for effect
                in result["effects"]
            )
        )


if __name__ == "__main__":
    unittest.main()