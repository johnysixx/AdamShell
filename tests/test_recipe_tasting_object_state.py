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
from meeting_place.drink_recipe_status import (
    DrinkRecipeStatus,
)


class MutableSerializedRecipeTasting(
    RecipeTasting
):

    def __init__(self):
        super().__init__(
            guest="newton",
            liked=True,
            comment="bright",
        )

        self.metadata = {
            "history": {
                "notes": ["original"],
            },
        }

    def to_dict(self):
        snapshot = super().to_dict()
        snapshot["metadata"] = self.metadata
        return snapshot


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

    def test_nested_tasting_snapshot_is_detached(self):
        tasting = MutableSerializedRecipeTasting()

        recipe = DrinkRecipe(
            name="singularity",
            origin="test_recipe",
            ingredients=[],
            tastings=[tasting],
        )

        first = recipe.to_dict()
        second = recipe.to_dict()

        first["tastings"][0]["metadata"][
            "history"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            tasting.metadata["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["tastings"][0]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        self.assertEqual(
            recipe.to_dict()["tastings"][0][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        self.assertIs(
            recipe.tastings[0],
            tasting,
        )

        self.assertIsNot(
            first["tastings"][0]["metadata"],
            tasting.metadata,
        )

        self.assertEqual(
            first["tastings"][0]["guest"],
            "newton",
        )

        self.assertTrue(
            first["tastings"][0]["liked"],
        )

    def test_tasting_snapshot_ignores_later_live_changes(self):
        tasting = MutableSerializedRecipeTasting()

        recipe = DrinkRecipe(
            name="singularity",
            origin="test_recipe",
            ingredients=[],
            tastings=[tasting],
        )

        history = recipe.tastings
        snapshot = recipe.to_dict()

        tasting.metadata["history"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["tastings"][0]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        current = recipe.to_dict()

        self.assertEqual(
            current["tastings"][0]["metadata"][
                "history"
            ]["notes"],
            ["original", "live_change"],
        )

        snapshot["tastings"][0]["metadata"][
            "history"
        ]["notes"].append("snapshot_only")

        snapshot["tastings"].clear()

        self.assertEqual(
            tasting.metadata["history"]["notes"],
            ["original", "live_change"],
        )

        self.assertIs(
            recipe.tastings,
            history,
        )

        self.assertIs(
            recipe.tastings[0],
            tasting,
        )

        self.assertEqual(
            len(recipe.tastings),
            1,
        )

    def test_recipe_book_preserves_tasting_identity_and_votes(self):
        book = HowToMixDrinks()

        recipe = book.add_created_recipe(
            name="singularity",
            ingredients=["lemonade"],
        )

        original = book.record_tasting(
            drink="singularity",
            guest="curie",
            liked=False,
            comment="too sour",
        )

        tasting = MutableSerializedRecipeTasting()

        recipe.tastings.append(tasting)

        history = recipe.tastings

        first = recipe.to_dict()
        second = recipe.to_dict()

        self.assertIs(
            book.recipes["singularity"],
            recipe,
        )

        self.assertIs(
            recipe.tastings,
            history,
        )

        self.assertIs(
            recipe.tastings[0],
            original,
        )

        self.assertIs(
            recipe.tastings[1],
            tasting,
        )

        self.assertIs(
            recipe.status,
            DrinkRecipeStatus.TESTING,
        )

        self.assertEqual(
            recipe.votes_against,
            1,
        )

        self.assertEqual(
            recipe.votes_for,
            0,
        )

        self.assertFalse(
            recipe.approved,
        )

        first["tastings"][1]["metadata"][
            "history"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            tasting.metadata["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["tastings"][1]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        tasting.metadata["history"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            second["tastings"][1]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        current = recipe.to_dict()

        self.assertEqual(
            current["tastings"][1]["metadata"][
                "history"
            ]["notes"],
            ["original", "live_change"],
        )

        self.assertEqual(
            current["tastings"][0]["guest"],
            "curie",
        )

        self.assertEqual(
            current["votes_against"],
            1,
        )

        self.assertEqual(
            current["status"],
            "testing",
        )

        self.assertIs(
            book.recipes["singularity"],
            recipe,
        )

        self.assertIs(
            recipe.tastings[0],
            original,
        )

        self.assertIs(
            recipe.tastings[1],
            tasting,
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
