import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0LilithFinalServiceAndTableTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_serpent_is_already_at_table_when_bartender_returns(self):
        self.scene.advance_to_good_drink_discussion()
        names = [event['name'] for event in self.scene.history]
        serpent_move = names.index('serpent_moves_to_existing_table')
        bartender_return = names.index('bartender_returned_with_lemon')
        self.assertLess(serpent_move, bartender_return)

    def test_lilith_gets_drink_and_receipt(self):
        result = self.scene.advance_to_good_drink_discussion()
        self.assertEqual(result['served']['drink'].name, 'lilith')
        self.assertFalse(result['served']['receipt']['paid'])
        self.assertEqual(result['served']['receipt']['status'], 'open_unpaid')

    def test_first_served_lilith_has_one_sugar_cube(self):
        result = self.scene.advance_to_good_drink_discussion()
        names = [event['name'] for event in self.scene.history]
        self.assertIn('bartender_mixes_final_lilith', names)

    def test_lilith_requests_one_more_sugar_cube(self):
        result = self.scene.advance_to_good_drink_discussion()
        self.assertEqual(result['tasted']['request'], {'ingredient': 'sugar', 'amount': 1, 'unit': 'cube'})

    def test_final_recipe_has_two_sugar_cubes(self):
        result = self.scene.advance_to_good_drink_discussion()
        recipe = result['revised']['recipe']
        self.assertEqual(recipe.ingredients['sugar'].shots, 2)
        self.assertEqual(recipe.revision, 2)

    def test_price_stays_same_as_vodka(self):
        result = self.scene.advance_to_good_drink_discussion()
        self.assertEqual(result['revised']['recipe'].price_basis, 'vodka')

    def test_effects_remain_only_energy_and_creative_will(self):
        result = self.scene.advance_to_good_drink_discussion()
        self.assertEqual(set(result['revised']['recipe'].effects.keys()), {'energy_j', 'creative_will'})

    def test_lilith_then_joins_serpent(self):
        result = self.scene.advance_to_good_drink_discussion()
        self.assertEqual(result['moved']['with'], 'serpent')
        self.assertEqual(self.scene.lilith.bar_state['location'], 'table')

    def test_discussion_starts_without_answer_yet(self):
        result = self.scene.advance_to_good_drink_discussion()
        discussion = result['discussion']
        self.assertEqual(discussion['subjects'], ['wine', 'mead', 'beer'])
        self.assertEqual(discussion['ideas'], [])
        self.assertFalse(discussion['resolved'])
if __name__ == '__main__':
    unittest.main()
