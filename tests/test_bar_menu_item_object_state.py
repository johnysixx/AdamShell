import unittest

from meeting_place.bar_menu_sign import BarMenuSign
from meeting_place.bar_objects import BarDrink, BarMenuItem, DrinkRecipe
from meeting_place.meeting_place import MeetingPlace
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarMenuItemObjectStateTests(unittest.TestCase):

    def _meeting_place(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        return MeetingPlace(universe)

    def test_menu_item_has_no_mapping_api(self):
        bar = self._meeting_place()
        item = bar.drink_menu["rum"]

        self.assertIsInstance(item, BarMenuItem)
        self.assertEqual(item.name, "rum")
        self.assertEqual(item.menu_source, "direct_stock")

        for name in ("get", "keys", "items", "values", "__getitem__"):
            self.assertFalse(hasattr(item, name), name)

        with self.assertRaises(TypeError):
            _ = item["name"]

    def test_add_drink_rejects_mapping_without_changing_state(self):
        bar = self._meeting_place()
        original_menu = dict(bar.drink_menu)
        original_memory = list(bar.bartender.chronicle_memory)

        with self.assertRaisesRegex(TypeError, "BarDrink"):
            bar.add_drink({"name": "absinthe", "type": "bar_drink"})

        self.assertEqual(bar.drink_menu, original_menu)
        self.assertEqual(bar.bartender.chronicle_memory, original_memory)

    def test_add_drink_stores_menu_item_referencing_drink_object(self):
        bar = self._meeting_place()
        drink = BarDrink(name="absinthe", type="bar_drink")

        item = bar.add_drink(drink, source="new_bottle")

        self.assertIsInstance(item, BarMenuItem)
        self.assertIs(bar.drink_menu["absinthe"], item)
        self.assertIs(item.drink, drink)
        self.assertEqual(item.menu_source, "new_bottle")

    def test_promoted_recipe_stays_object_backed(self):
        bar = self._meeting_place()
        recipe = DrinkRecipe(
            name="singularity",
            origin="test_recipe",
            ingredients=["raspberry_rum", "lemonade"],
            status="approved",
            approved=True,
        )
        bar.add_approved_cocktail(recipe)

        promoted = bar.promote_new_drink("singularity")
        item = bar.drink_menu["singularity"]

        self.assertIs(promoted, recipe)
        self.assertIsInstance(item, BarMenuItem)
        self.assertIs(item.recipe, recipe)
        self.assertEqual(item.menu_source, "promoted_recipe")

    def test_menu_sign_rejects_mapping_menu_value(self):
        sign = BarMenuSign(
            drink_menu={"rum": {"name": "rum"}},
            new_drinks={},
        )

        with self.assertRaisesRegex(TypeError, "BarMenuItem"):
            sign.open_drink("rum")

    def test_menu_sign_rejects_mapping_new_drink_value(self):
        sign = BarMenuSign(
            drink_menu={},
            new_drinks={"singularity": {"name": "singularity"}},
        )

        with self.assertRaisesRegex(TypeError, "DrinkRecipe"):
            sign.open_drink("singularity")


if __name__ == "__main__":
    unittest.main()
