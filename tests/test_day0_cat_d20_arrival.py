import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0CatD20ArrivalTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_cat_d20_was_not_in_day0_scene_before_this_point(self):
        self.assertIsNone(self.scene.cat_d20)

    def test_cat_d20_arrives_now(self):
        result = self.scene.advance_to_cat_d20_arrival()
        cat = result['cat_d20']['cat']
        self.assertEqual(cat.name, 'cat_d20')
        self.assertIs(self.scene.cat_d20, cat)

    def test_cat_d20_is_in_meeting_place(self):
        result = self.scene.advance_to_cat_d20_arrival()
        cat = result['cat_d20']['cat']
        self.assertEqual(cat.current_layer, 'meeting_place')
        self.assertIn(cat, self.bar.entities)

    def test_cat_d20_keeps_canonical_d20_trait(self):
        result = self.scene.advance_to_cat_d20_arrival()
        cat = result['cat_d20']['cat']
        self.assertIn('d20_cat', getattr(cat, 'special_traits', []))
        self.assertTrue(cat.cat_d20["is_cat"])
        self.assertFalse(cat.cat_d20["is_die"])

    def test_existing_welcome_lifecycle_is_used(self):
        result = self.scene.advance_to_cat_d20_arrival()
        arrival = result['cat_d20']['arrival']
        self.assertEqual(arrival['name'], 'cat_d20_arrival_completed')

    def test_cat_d20_arrives_after_bouncer_panel_is_proposed(self):
        self.scene.advance_to_cat_d20_arrival()
        names = [event['name'] for event in self.scene.history]
        panel = names.index('bartender_proposes_bouncer_as_second_taster')
        cat = names.index('cat_d20_arrives_during_judge_discussion')
        self.assertLess(panel, cat)

    def test_second_arrival_does_not_create_duplicate_cat(self):
        first = self.scene.advance_to_cat_d20_arrival()
        cat = first['cat_d20']['cat']
        count_before = sum((1 for entity in self.bar.entities if isinstance(entity, dict) and getattr(entity, 'name', None) == 'cat_d20'))
        second = self.scene.cat_d20_arrives_during_judge_discussion()
        count_after = sum((1 for entity in self.bar.entities if isinstance(entity, dict) and getattr(entity, 'name', None) == 'cat_d20'))
        self.assertIs(second['cat'], cat)
        self.assertEqual(count_before, count_after)
if __name__ == '__main__':
    unittest.main()
