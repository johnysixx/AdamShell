import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0SerpentMovesBeforeBartenderReturnsTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))
        self.scene.advance_to_lilith_entry()
        self.scene.lilith_orders_vodka_with_lemon()
        self.scene.serpent_and_lilith_begin_conversation()
        self.scene.play_serpent_lilith_first_conversation()

    def test_they_agree_on_table_before_bartender_returns(self):
        event = self.scene.serpent_and_lilith_agree_on_table()
        self.assertTrue(event['agreed'])
        self.assertEqual(self.bar.bartender.current_location, 'bar_yard')

    def test_serpent_moves_to_existing_table_first(self):
        self.scene.serpent_and_lilith_agree_on_table()
        event = self.scene.serpent_moves_from_bar_to_existing_table()
        self.assertEqual(event['from'], 'bar_counter')
        self.assertEqual(self.scene.serpent.bar_state['location'], 'table')
        self.assertEqual(self.scene.serpent.bar_state['activity'], 'waiting_for_lilith')

    def test_lilith_remains_at_bar_when_serpent_leaves(self):
        self.scene.serpent_and_lilith_agree_on_table()
        self.scene.serpent_moves_from_bar_to_existing_table()
        self.assertIn(self.scene.lilith, self.bar.entities)
        self.assertNotEqual(getattr(self.scene.lilith, 'bar_state', {}).get('location'), 'table')

    def test_bartender_returns_to_find_only_lilith_at_counter(self):
        self.scene.serpent_and_lilith_agree_on_table()
        self.scene.serpent_moves_from_bar_to_existing_table()
        result = self.scene.bartender_returns_with_lemon()
        self.assertEqual(self.bar.bartender.current_location, 'bar')
        self.assertEqual(self.scene.serpent.bar_state['location'], 'table')
        self.assertNotEqual(getattr(self.scene.lilith, 'bar_state', {}).get('location'), 'table')
        self.assertEqual(result['returned']['ingredient'], 'lemon')
if __name__ == '__main__':
    unittest.main()
