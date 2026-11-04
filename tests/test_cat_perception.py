import unittest
from core.entity.components import SpatialVector3
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_quantum_box_memory_details import (
    CatQuantumBoxObservedMemoryDetails,
)

class CatPerceptionTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='observer', color='black', fur_length='short')
        self.cat.position = SpatialVector3(x=1.0, y=0.0, z=0.0)

    def create_other_cat(self, name, position):
        cat = self.cats.create_cat(name=name, color='gray', fur_length='short')
        cat.position = position
        return cat

    def create_cronenberg(self, size, position):
        cronenberg = self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('Perception test.'), source_component='test', source_operation='cat_perception')
        cronenberg.size = float(size)
        cronenberg.position = position
        return cronenberg

    def test_cat_sees_nearby_cat_only(self):
        near = self.create_other_cat('near', SpatialVector3(x=2.0, y=0.0, z=0.0))
        self.create_other_cat('far', SpatialVector3(x=20.0, y=0.0, z=0.0))
        result = self.cats.observe_cat(self.cat)
        self.assertIn(near.name, result.nearby_cats)
        self.assertNotIn('far', result.nearby_cats)

    def test_cat_distinguishes_huntable_cronenberg(self):
        small = self.create_cronenberg(size=0.8, position=SpatialVector3(x=2.0, y=0.0, z=0.0))
        large = self.create_cronenberg(size=2.0, position=SpatialVector3(x=3.0, y=0.0, z=0.0))
        result = self.cats.observe_cat(self.cat)
        self.assertIn(small.id, result.huntable_cronenbergs)
        self.assertNotIn(large.id, result.huntable_cronenbergs)
        self.assertIn(large.id, result.visible_cronenbergs)

    def test_quantum_box_is_unexplored_until_remembered(self):
        box = self.universe.create_quantum_box()
        box.position = SpatialVector3(x=2.0, y=0.0, z=0.0)
        first = self.cats.observe_cat(self.cat)
        self.assertIn(box.id, first.unexplored_boxes)
        self.cat.memory.remember(
            event_type='box_explored',
            participants=[box.id],
            details=CatQuantumBoxObservedMemoryDetails(
                box_id=box.id,
            ),
        )
        second = self.cats.observe_cat(self.cat)
        self.assertNotIn(box.id, second.unexplored_boxes)

    def test_canonical_box_details_without_participants(self):
        box = self.universe.create_quantum_box()
        box.position = SpatialVector3(x=2.0, y=0.0, z=0.0)

        self.cat.memory.remember(
            event_type='quantum_box_observed',
            participants=[],
            details=CatQuantumBoxObservedMemoryDetails(
                box_id=box.id,
            ),
        )

        result = self.cats.observe_cat(self.cat)
        self.assertNotIn(box.id, result.unexplored_boxes)

    def test_legacy_dict_details_do_not_mark_box_explored(self):
        box = self.universe.create_quantum_box()
        box.position = SpatialVector3(x=2.0, y=0.0, z=0.0)

        self.cat.memory.remember(
            event_type='quantum_box_observed',
            participants=[],
            details={'box_id': box.id},
        )

        result = self.cats.observe_cat(self.cat)
        self.assertIn(box.id, result.unexplored_boxes)

    def test_box_participant_marks_explored_without_details(self):
        box = self.universe.create_quantum_box()
        box.position = SpatialVector3(x=2.0, y=0.0, z=0.0)

        self.cat.memory.remember(
            event_type='box_entered',
            participants=[box.id],
        )

        result = self.cats.observe_cat(self.cat)
        self.assertNotIn(box.id, result.unexplored_boxes)

    def test_bar_is_visible_near_door(self):
        result = self.cats.observe_cat(self.cat)
        self.assertTrue(result.bar_visible)
        self.assertTrue(result.bar_known)

    def test_observation_is_stored_in_mind(self):
        result = self.cats.observe_cat(self.cat)
        self.assertEqual(self.cat.mind.last_observations.position, result.position)
        self.assertEqual(len(self.cat.mind.observation_history), 1)
if __name__ == '__main__':
    unittest.main()
