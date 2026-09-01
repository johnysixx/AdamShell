import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0ThirdWineIdeaTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_god_finishes_browsing_and_orders_lilith(self):
        result = self.scene.advance_to_third_wine_idea()
        self.assertEqual(result['god_order']['drink'], 'lilith')
        self.assertEqual(self.scene.god.bar_state.activity, 'ordered_lilith')

    def test_serpent_tastes_mead_then_beer(self):
        result = self.scene.advance_to_third_wine_idea()
        names = [event['name'] for event in self.scene.history]
        mead_index = names.index('serpent_tastes_mead')
        beer_index = names.index('serpent_tastes_beer')
        self.assertLess(mead_index, beer_index)

    def test_serpent_says_sweetness_is_good_but_not_full_body(self):
        result = self.scene.advance_to_third_wine_idea()
        idea = result['wine_idea']
        self.assertEqual(idea.assessment['sweetness'], 'good')
        self.assertEqual(idea.assessment['full_body'], 'still_missing')

    def test_serpent_proposes_bitterness(self):
        result = self.scene.advance_to_third_wine_idea()
        self.assertTrue(result['wine_idea'].proposal['bitterness'])

    def test_wine_discussion_has_three_ideas(self):
        self.scene.advance_to_third_wine_idea()
        ideas = self.scene.serpent_lilith_good_drink_discussion.ideas
        self.assertEqual(len(ideas), 3)
        self.assertEqual(ideas[0].serpent['proposal'], 'flavor_should_be_fuller')
        self.assertTrue(ideas[1].desired_property['sweetness'])
        self.assertTrue(ideas[2].proposal['bitterness'])

    def test_discussion_is_still_unresolved(self):
        self.scene.advance_to_third_wine_idea()
        self.assertFalse(self.scene.serpent_lilith_good_drink_discussion.resolved)
if __name__ == '__main__':
    unittest.main()
