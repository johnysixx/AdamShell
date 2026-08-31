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
    DrinkRecipe,
    RecipeIngredientRequirement,
)


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

    def test_menu_is_still_boundary_dict(
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
            dict
        )

        self.assertEqual(
            item[
                "menu_source"
            ],
            "direct_stock"
        )


if __name__ == "__main__":
    unittest.main()
