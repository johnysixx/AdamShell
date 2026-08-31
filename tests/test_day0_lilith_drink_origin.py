import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0LilithDrinkOriginTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.library = Library(self.universe)
        self.gods = Gods(self.universe)
        self.idea_entities = IdeaEntities(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=self.library, gods=self.gods, idea_entities=self.idea_entities)
        self.scene.advance_to_lilith_entry()
        self.scene.lilith_orders_vodka_with_lemon()

    def test_sugar_exists_from_bar_start(self):
        sugar = self.bar.back_room.bar_ingredients['sugar']
        self.assertTrue(sugar.available)
        self.assertEqual(sugar.unit, 'cube')

    def test_bartender_brings_lemon_into_stock(self):
        self.scene.bartender_returns_with_lemon()
        lemon = self.bar.back_room.bar_ingredients['lemon']
        self.assertTrue(lemon.available)
        self.assertEqual(lemon.shots, 1)

    def test_vodka_with_lemon_is_basic_and_has_no_effects(self):
        self.scene.bartender_returns_with_lemon()
        drink = self.scene.bartender_makes_vodka_with_lemon()
        self.assertEqual(drink.name, 'vodka_with_lemon')
        self.assertEqual(drink.price_basis, 'vodka')
        self.assertEqual(drink.effects, {})

    def test_lilith_recipe_uses_whole_lemon_and_sugar_cube(self):
        self.scene.bartender_returns_with_lemon()
        self.scene.bartender_makes_vodka_with_lemon()
        self.scene.lilith_corrects_vodka_with_lemon()
        learned = self.scene.bartender_learns_lilith_drink()
        recipe = learned['recipe']
        self.assertEqual(recipe.ingredients['lemon'].use, 'whole')
        self.assertEqual(recipe.ingredients['sugar'].shots, 1)
        self.assertEqual(recipe.price_basis, 'vodka')

    def test_lilith_has_only_energy_and_creative_will_effects(self):
        self.scene.bartender_returns_with_lemon()
        self.scene.bartender_makes_vodka_with_lemon()
        self.scene.lilith_corrects_vodka_with_lemon()
        learned = self.scene.bartender_learns_lilith_drink()
        self.assertEqual(set(learned['recipe'].effects.keys()), {'energy_j', 'creative_will'})

    def test_lilith_effect_increases_energy_and_creative_will(self):
        self.scene.bartender_returns_with_lemon()
        self.scene.bartender_makes_vodka_with_lemon()
        self.scene.lilith_corrects_vodka_with_lemon()
        self.scene.bartender_learns_lilith_drink()
        before_energy = float(getattr(self.scene.lilith, 'energy_j', 0.0))
        before_will = float(getattr(self.scene.lilith, 'creative_will', 0.0))
        result = self.scene.apply_lilith_drink_effect(self.scene.lilith)
        self.assertGreater(self.scene.lilith.energy_j, before_energy)
        self.assertGreater(self.scene.lilith.creative_will, before_will)
        self.assertEqual(set(result.keys()), {'name', 'energy_j', 'creative_will'})
if __name__ == '__main__':
    unittest.main()
