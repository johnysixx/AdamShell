import unittest

from meeting_place.bar_counter import BarCounter
from meeting_place.bar_objects import (
    DrinkRecipe,
    RecipeTasting,
)
from meeting_place.bartender import Bartender
from meeting_place.how_to_mix_drinks import (
    HowToMixDrinks,
)


class RecipeTastingObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "guest"
            ]

    def test_tasting_is_same_object_stored_on_recipe(
        self
    ):
        book = HowToMixDrinks()

        recipe = book.add_created_recipe(
            name="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade",
            ],
        )

        tasting = book.record_tasting(
            drink="singularity",
            guest="newton",
            liked=True,
            comment="needs more lemon",
        )

        self.assertIsInstance(
            tasting,
            RecipeTasting
        )

        self.assertIs(
            recipe.tastings[0],
            tasting
        )

        self._assert_object_only(
            tasting
        )

    def test_recipe_snapshot_keeps_tasting_boundary_dict(
        self
    ):
        book = HowToMixDrinks()

        recipe = book.add_created_recipe(
            name="singularity",
            ingredients=[],
        )

        tasting = recipe.record_tasting(
            guest="newton",
            liked=True,
            comment=None,
        )

        snapshot = recipe.to_dict()

        self.assertEqual(
            snapshot[
                "tastings"
            ],
            [
                {
                    "guest": "newton",
                    "liked": True,
                    "comment": None,
                }
            ]
        )

        snapshot[
            "tastings"
        ][0][
            "liked"
        ] = False

        self.assertTrue(
            tasting.liked
        )

    def test_bartender_fallback_recipe_is_object_only(
        self
    ):
        bartender = Bartender(
            BarCounter()
            .hidden_story_book
        )

        recipe = bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade",
            ],
        )

        self.assertIsInstance(
            recipe,
            DrinkRecipe
        )

        self.assertEqual(
            recipe.ingredients,
            [
                "raspberry_rum",
                "lemonade",
            ]
        )

        self.assertFalse(
            hasattr(
                recipe,
                "get"
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = recipe[
                "name"
            ]


if __name__ == "__main__":
    unittest.main()
