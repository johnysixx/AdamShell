import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0SerpentCallsGodToTableTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_serpent_notices_god_and_calls_him(self):
        self.scene.advance_to_god_first_lilith_taste()
        event = self.scene.serpent_notices_god_and_calls_him_over()
        self.assertEqual(event['caller'], 'serpent')
        self.assertEqual(event['called'], 'god')
        self.assertEqual(self.scene.god.bar_state.called_to_table_by, 'serpent')

    def test_god_comes_to_existing_table(self):
        result = self.scene.advance_to_god_at_table()
        self.assertEqual(self.scene.god.bar_state.location, 'table')
        self.assertEqual(self.scene.god.bar_state.activity, 'at_table')
        self.assertEqual(result['joined']['with'], ['serpent', 'lilith'])

    def test_god_brings_lilith_to_table(self):
        result = self.scene.advance_to_god_at_table()
        self.assertEqual(result['joined']['drink_in_hand'], 'lilith')
        self.assertEqual(self.scene.god.bar_state.drink.name, 'lilith')

    def test_serpent_and_lilith_remain_at_table(self):
        self.scene.advance_to_god_at_table()
        self.assertEqual(self.scene.serpent.bar_state.location, 'table')
        self.assertEqual(self.scene.lilith.bar_state.location, 'table')

    def test_call_precedes_god_joining_table(self):
        self.scene.advance_to_god_at_table()
        names = [event['name'] for event in self.scene.history]
        call_index = names.index('serpent_notices_god_and_calls_him_over')
        join_index = names.index('god_joins_serpent_and_lilith_at_table')
        self.assertLess(call_index, join_index)

    def test_god_still_has_no_creator_mask(self):
        self.scene.advance_to_god_at_table()
        self.assertNotIn('creator', getattr(self.scene.god, 'masks', {}))
        self.assertNotEqual(getattr(self.scene.god, 'active_mask', None), 'creator')

    def test_wine_discussion_is_not_changed_by_arrival(self):
        self.scene.advance_to_god_at_table()
        discussion = self.scene.serpent_lilith_good_drink_discussion
        self.assertEqual(len(discussion.ideas), 3)
        self.assertFalse(discussion.resolved)
if __name__ == '__main__':
    unittest.main()
