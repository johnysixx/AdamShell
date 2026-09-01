import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0GodReceivesWineTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_serpent_grimaces_and_turns_to_god(self):
        result = self.scene.advance_to_god_receives_wine()
        reaction = result['reaction']
        self.assertEqual(reaction['reaction'], 'grimace')
        self.assertEqual(reaction['drink'], 'lilith')
        self.assertEqual(reaction['turns_to'], 'god')

    def test_god_orders_wine_for_comparison(self):
        result = self.scene.advance_to_god_receives_wine()
        order = result['order']
        self.assertEqual(order['drink'], 'wine')
        self.assertEqual(order['purpose'], 'judge_wine_discussion')

    def test_bartender_serves_god_wine(self):
        result = self.scene.advance_to_god_receives_wine()
        self.assertEqual(result['service']['drink'].name, 'wine')
        self.assertTrue(self.scene.god.bar_state['wine_order']['served'])

    def test_god_has_not_tasted_wine_yet(self):
        result = self.scene.advance_to_god_receives_wine()
        self.assertFalse(self.scene.god.bar_state['wine_order']['tasted'])
        self.assertFalse(result['service']['event']['tasted'])

    def test_wine_is_added_to_existing_open_tab(self):
        result = self.scene.advance_to_god_receives_wine()
        receipt = result['service']['receipt']
        self.assertFalse(receipt['paid'])
        self.assertEqual(receipt['status'], 'open_unpaid')

    def test_event_order(self):
        self.scene.advance_to_god_receives_wine()
        names = [event['name'] for event in self.scene.history]
        taste = names.index('lilith_gives_serpent_taste_of_lilith')
        reaction = names.index('serpent_grimaces_at_lilith_and_turns_to_god')
        order = names.index('god_orders_wine_to_judge_discussion')
        service = names.index('bartender_serves_god_wine_and_receipt')
        self.assertLess(taste, reaction)
        self.assertLess(reaction, order)
        self.assertLess(order, service)

    def test_wine_hypothesis_does_not_change_yet(self):
        self.scene.advance_to_god_receives_wine()
        hypothesis = self.scene.serpent_lilith_good_drink_discussion.current_hypothesis
        self.assertEqual(hypothesis.to_dict(), {'fuller_flavor': True, 'sweetness': True, 'bitterness': False, 'acidity': True})
        self.assertFalse(self.scene.serpent_lilith_good_drink_discussion.resolved)
if __name__ == '__main__':
    unittest.main()
