import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe

from meeting_place.meeting_place import (
    MeetingPlace
)

from meeting_place.how_to_mix_drinks import (
    HowToMixDrinks
)

from meeting_place.bar_objects import (
    BarIngredientStock,
    BarMenuItem,
    DrinkRecipe,
    RecipeIngredientRequirement,
)


class MutableSerializedRecipeRequirement(
    RecipeIngredientRequirement
):

    def __init__(self):
        super().__init__(
            shots=1,
            consumed=False,
            use="drop",
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


class BarRecipeStockObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value
    ):
        self.assertFalse(
            hasattr(
                value,
                "get"
            )
        )

        self.assertFalse(
            hasattr(
                value,
                "keys"
            )
        )

        self.assertFalse(
            hasattr(
                value,
                "items"
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "name"
            ]

    def test_bar_stock_values_are_domain_objects(
        self
    ):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        bar = MeetingPlace(
            universe
        )

        rum = (
            bar
            .back_room
            .bar_ingredients[
                "rum"
            ]
        )

        self.assertIsInstance(
            rum,
            BarIngredientStock
        )

        self.assertTrue(
            rum.available
        )

        self._assert_object_only(
            rum
        )

    def test_recipe_registry_values_are_domain_objects(
        self
    ):
        book = (
            HowToMixDrinks()
        )

        recipe = (
            book.recipes[
                "vodka_with_lemon"
            ]
        )

        self.assertIsInstance(
            recipe,
            DrinkRecipe
        )

        self.assertEqual(
            recipe.name,
            "vodka_with_lemon"
        )

        self._assert_object_only(
            recipe
        )

    def test_recipe_requirements_are_domain_objects(
        self
    ):
        book = (
            HowToMixDrinks()
        )

        requirement = (
            book
            .recipes[
                "vodka_with_lemon"
            ]
            .ingredients[
                "lemon"
            ]
        )

        self.assertIsInstance(
            requirement,
            RecipeIngredientRequirement
        )

        self.assertEqual(
            requirement.use,
            "drop"
        )

        self.assertFalse(
            hasattr(
                requirement,
                "get"
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = requirement[
                "shots"
            ]

    def test_nested_ingredient_snapshot_is_detached(self):
        requirement = MutableSerializedRecipeRequirement()

        ingredients = {
            "lemon": requirement,
        }

        recipe = DrinkRecipe(
            name="singularity",
            origin="test_recipe",
            ingredients=ingredients,
        )

        first = recipe.to_dict()
        second = recipe.to_dict()

        first["ingredients"]["lemon"]["metadata"][
            "history"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            requirement.metadata["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["ingredients"]["lemon"]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        self.assertEqual(
            recipe.to_dict()["ingredients"]["lemon"][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        self.assertIs(
            recipe.ingredients,
            ingredients,
        )

        self.assertIs(
            recipe.ingredients["lemon"],
            requirement,
        )

        self.assertIsNot(
            first["ingredients"]["lemon"]["metadata"],
            requirement.metadata,
        )

        self.assertEqual(
            first["ingredients"]["lemon"]["use"],
            "drop",
        )

    def test_ingredient_snapshot_ignores_live_changes(self):
        requirement = MutableSerializedRecipeRequirement()

        recipe = DrinkRecipe(
            name="singularity",
            origin="test_recipe",
            ingredients={
                "lemon": requirement,
            },
        )

        snapshot = recipe.to_dict()

        requirement.metadata["history"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["ingredients"]["lemon"][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        current = recipe.to_dict()

        self.assertEqual(
            current["ingredients"]["lemon"][
                "metadata"
            ]["history"]["notes"],
            ["original", "live_change"],
        )

        snapshot["ingredients"]["lemon"][
            "metadata"
        ]["history"]["notes"].append(
            "snapshot_only"
        )

        snapshot["ingredients"].clear()

        self.assertEqual(
            requirement.metadata["history"]["notes"],
            ["original", "live_change"],
        )

        self.assertIs(
            recipe.ingredients["lemon"],
            requirement,
        )

        simple = DrinkRecipe(
            name="simple_drink",
            origin="test_recipe",
            ingredients=["lemonade"],
        )

        self.assertEqual(
            simple.to_dict()["ingredients"],
            ["lemonade"],
        )

    def test_recipe_registry_preserves_ingredient_identity(self):
        book = HowToMixDrinks()

        recipe = book.recipes[
            "vodka_with_lemon"
        ]

        ingredients = recipe.ingredients

        requirement = MutableSerializedRecipeRequirement()

        ingredients["lemon"] = requirement

        original_vodka = ingredients["vodka"]

        first = recipe.to_dict()
        second = recipe.to_dict()

        self.assertIs(
            book.recipes["vodka_with_lemon"],
            recipe,
        )

        self.assertIs(
            recipe.ingredients,
            ingredients,
        )

        self.assertIs(
            recipe.ingredients["lemon"],
            requirement,
        )

        self.assertIs(
            recipe.ingredients["vodka"],
            original_vodka,
        )

        first["ingredients"]["lemon"]["metadata"][
            "history"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            requirement.metadata["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["ingredients"]["lemon"]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        requirement.metadata["history"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            second["ingredients"]["lemon"]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        current = recipe.to_dict()

        self.assertEqual(
            current["ingredients"]["lemon"]["metadata"][
                "history"
            ]["notes"],
            ["original", "live_change"],
        )

        self.assertEqual(
            current["ingredients"]["vodka"]["shots"],
            1,
        )

        self.assertEqual(
            current["ingredients"]["lemon"]["use"],
            "drop",
        )

        self.assertIs(
            book.recipes["vodka_with_lemon"],
            recipe,
        )

        self.assertIs(
            recipe.ingredients["lemon"],
            requirement,
        )

    def test_hidden_recipe_reveals_same_object_without_mapping_bridge(
        self
    ):
        book = (
            HowToMixDrinks()
        )

        hidden = (
            book.hidden_recipes[
                "raspberry_rum"
            ]
        )

        revealed = (
            book
            .reveal_hidden_recipe(
                "raspberry_rum",
                "god"
            )
        )

        self.assertIs(
            revealed,
            hidden
        )

        self.assertFalse(
            revealed.hidden
        )

        self.assertTrue(
            revealed.learned
        )

        self.assertEqual(
            revealed.teacher,
            "god"
        )

        self._assert_object_only(
            revealed
        )

    def test_menu_values_are_domain_objects(
        self
    ):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        bar = MeetingPlace(
            universe
        )

        item = (
            bar.drink_menu[
                "rum"
            ]
        )

        self.assertIsInstance(
            item,
            BarMenuItem
        )

        self.assertEqual(
            item.menu_source,
            "direct_stock"
        )

        self.assertIs(
            item.stock,
            bar.back_room.bar_ingredients["rum"]
        )

        self._assert_object_only(
            item
        )


if __name__ == "__main__":
    unittest.main()
