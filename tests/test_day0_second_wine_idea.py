import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0SecondWineIdeaTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_bartender_asks_god_what_he_wants(self):
        result = self.scene.advance_to_second_wine_idea()
        self.assertEqual(result['bartender']['question'], 'what_will_you_have')

    def test_god_is_still_choosing_and_orders_nothing(self):
        result = self.scene.advance_to_second_wine_idea()
        self.assertFalse(result['god']['ordered'])
        self.assertEqual(self.scene.god.bar_state['activity'], 'still_choosing')

    def test_lilith_tastes_mead(self):
        result = self.scene.advance_to_second_wine_idea()
        self.assertEqual(result['wine_idea']['tasting']['drink'], 'mead')

    def test_lilith_adds_sweetness_as_wine_property(self):
        result = self.scene.advance_to_second_wine_idea()
        idea = result['wine_idea']['idea']
        self.assertEqual(idea.subject, 'wine')
        self.assertTrue(idea.desired_property['sweetness'])

    def test_wine_discussion_now_has_two_ideas(self):
        self.scene.advance_to_second_wine_idea()
        ideas = self.scene.serpent_lilith_good_drink_discussion.ideas
        self.assertEqual(len(ideas), 2)
        self.assertEqual(ideas[0].serpent['proposal'], 'flavor_should_be_fuller')
        self.assertTrue(ideas[1].desired_property['sweetness'])

    def test_discussion_is_still_unresolved(self):
        self.scene.advance_to_second_wine_idea()
        self.assertFalse(self.scene.serpent_lilith_good_drink_discussion.resolved)
if __name__ == '__main__':
    unittest.main()
