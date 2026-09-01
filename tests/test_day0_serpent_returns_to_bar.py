import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0SerpentReturnsToBarTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_serpent_leaves_table_for_bar(self):
        result = self.scene.advance_to_serpent_at_bar_lilith_with_god()
        self.assertEqual(result['serpent']['from'], 'table')
        self.assertEqual(result['serpent']['to'], 'bar_counter')
        self.assertEqual(self.scene.serpent.bar_state.location, 'bar_counter')

    def test_serpent_leaves_because_only_bad_beer_remains(self):
        result = self.scene.advance_to_serpent_at_bar_lilith_with_god()
        self.assertEqual(result['serpent']['remaining_drink'], 'bad_beer')
        self.assertEqual(result['serpent']['reason'], 'nothing_good_left_to_drink')

    def test_lilith_and_god_remain_at_table(self):
        self.scene.advance_to_serpent_at_bar_lilith_with_god()
        self.assertEqual(self.scene.lilith.bar_state.location, 'table')
        self.assertEqual(self.scene.god.bar_state.location, 'table')

    def test_lilith_and_god_continue_talking(self):
        result = self.scene.advance_to_serpent_at_bar_lilith_with_god()
        conversation = result['conversation']
        self.assertEqual(conversation['participants'], ['lilith', 'god'])
        self.assertFalse(conversation['serpent_present'])
        self.assertIsNone(conversation['new_conclusion'])

    def test_serpent_move_happens_before_private_table_talk(self):
        self.scene.advance_to_serpent_at_bar_lilith_with_god()
        names = [event['name'] for event in self.scene.history]
        move = names.index('serpent_leaves_table_for_bar')
        talk = names.index('lilith_and_god_continue_talking_at_table')
        self.assertLess(move, talk)
if __name__ == '__main__':
    unittest.main()
