import unittest
from core.entity.components import SpatialVector3
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_perception import CatPerception
from cats.cat_intention_state import CatIntentionCandidate

from cats.cat_intention_state import CatExploreBoxTarget

from cats.cat_box_exploration_state import CatBoxExplorationState

class CatBoxExplorationLifecycleTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='explorer', color='black', fur_length='short')
        self.cat.current_layer = 'quantum_layer'
        self.cat.position = SpatialVector3(x=0.0, y=0.0, z=0.0)
        self.box = self.universe.create_quantum_box()
        self.box.current_layer = 'quantum_layer'
        self.box.position = SpatialVector3(x=3.0, y=0.0, z=0.0)

    def test_cat_physically_explores_box(self):
        before = CatPerception(self.cats).observe(self.cat)
        self.assertIn(self.box.id, before.unexplored_boxes)
        self.cat.mind.current_intention = CatIntentionCandidate(

            type='explore_box',

            target=CatExploreBoxTarget(box_id=self.box.id),

            score=1.0,

            reasons=['test'],

        )
        first = self.cats.execute_cat_intention(self.cat)
        self.assertEqual(first['name'], 'cat_approaching_box_to_explore')
        self.assertEqual(
            self.cat.position,
            SpatialVector3(x=0.0, y=0.0, z=0.0)
        )
        result = first
        for _ in range(10):
            result = self.cats.execute_cat_intention(self.cat)
            if result['name'] == 'cat_explored_quantum_box':
                break
        self.assertEqual(result['name'], 'cat_explored_quantum_box')
        self.assertEqual(self.cat.position, self.box.position)
        self.assertIsInstance(
            self.cat.box_exploration,
            CatBoxExplorationState,
        )
        self.assertTrue(
            self.cat.box_exploration.arrived
        )
        self.assertTrue(self.cat.box_exploration.observed)
        self.assertIsNone(self.cat.mind.current_intention)
        after = CatPerception(self.cats).observe(self.cat)
        self.assertNotIn(self.box.id, after.unexplored_boxes)

    def test_mapping_runtime_state_is_rejected(
        self
    ):
        self.cat.box_exploration = {
            'active': True,
            'arrived': False,
            'box_id': self.box.id,
            'route_id': 'legacy_route',
            'destination': self.box.position.to_dict(),
            'observed': False,
        }

        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type='explore_box',
                target=CatExploreBoxTarget(
                    box_id=self.box.id
                ),
                score=1.0,
                reasons=['test'],
            )
        )

        with self.assertRaises(
            TypeError
        ):
            self.cats.execute_cat_intention(
                self.cat
            )

if __name__ == '__main__':
    unittest.main()
