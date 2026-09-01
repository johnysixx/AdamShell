import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0GodBrowsesDrinkMenuTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_god_looks_around_after_entering(self):
        result = self.scene.advance_to_god_browsing_menu()
        self.assertEqual(result['looked']['activity'], 'looking_around')

    def test_god_moves_to_menu_and_browses_drinks(self):
        result = self.scene.advance_to_god_browsing_menu()
        self.assertEqual(self.scene.god.bar_state.location, 'drink_menu')
        self.assertEqual(self.scene.god.bar_state.activity, 'browsing_drinks')
        self.assertTrue(isinstance(result['browsed']['available_drinks'], list))

    def test_lilith_and_serpent_continue_talking_while_god_browses(self):
        result = self.scene.advance_to_god_browsing_menu()
        self.assertEqual(result['continued']['subject'], 'wine')
        self.assertEqual(result['continued']['previous_idea'], 'flavor_should_be_fuller')
        self.assertIsNone(result['continued']['new_idea'])

    def test_discussion_remains_unresolved(self):
        self.scene.advance_to_god_browsing_menu()
        self.assertFalse(self.scene.serpent_lilith_good_drink_discussion.resolved)

    def test_order_of_events(self):
        self.scene.advance_to_god_browsing_menu()
        names = [event['name'] for event in self.scene.history]
        arrival = names.index('god_arrives_during_wine_discussion')
        look = names.index('god_looks_around_bar')
        continue_talk = names.index('serpent_and_lilith_continue_wine_discussion')
        menu = names.index('god_browses_drink_menu')
        self.assertLess(arrival, look)
        self.assertLess(look, menu)
        self.assertLess(arrival, continue_talk)
if __name__ == '__main__':
    unittest.main()
