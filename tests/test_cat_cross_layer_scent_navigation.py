import unittest
from core.entity.components import SpatialVector3
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_perception import CatPerception
from cats.cat_mind import CatMind
from universe.aroma_residue import AromaResidue

from cats.cat_perception_state import CatScentTransferCandidate

class CatCrossLayerScentNavigationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.pazuzu = self.cats.create_cat(name='pazuzu', color='black', fur_length='short')
        self.tracker = self.cats.create_cat(name='tracker', color='gray', fur_length='short')
        self.tracker.current_layer = 'meeting_place'
        self.tracker.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.source = self.universe.create_quantum_box(layer='meeting_place')
        self.target = self.universe.create_quantum_box(layer='quantum_layer')
        self.source.position = SpatialVector3(x=1.0, y=0.0, z=0.0)
        self.target.position = SpatialVector3(x=1.0, y=0.0, z=0.0)
        self.universe.cat_box_transfer.pair_boxes(self.source, self.target)
        self.cats.learn_cat_aroma(observer=self.tracker, observed_cat=self.pazuzu)
        AromaResidue.transfer(source_profile=self.pazuzu.aroma, target=self.source, source_identity='pazuzu', fraction=0.35)

    def test_perception_detects_cross_layer_scent(self):
        perception = CatPerception(self.cats)
        result = perception.observe(self.tracker)
        candidates = result.scent_transfer_candidates
        self.assertEqual(len(candidates), 1)
        self.assertIsInstance(
            candidates[0],
            CatScentTransferCandidate,
        )
        self.assertEqual(candidates[0].identity, 'cat:pazuzu')
        self.assertEqual(candidates[0].counterpart_box_id, self.target.id)

    def test_mind_can_choose_to_follow_scent_through_box(self):
        perception = CatPerception(self.cats)
        observations = perception.observe(self.tracker)
        traits = self.tracker.personality.traits
        traits.curiosity = 1.0
        traits.courage = 1.0
        candidates = CatMind.consider(cat=self.tracker, observations=observations)
        scent_candidates = [candidate for candidate in candidates if candidate.type == 'follow_scent_through_box']
        self.assertEqual(len(scent_candidates), 1)
        self.assertEqual(scent_candidates[0].target.identity, 'cat:pazuzu')

    def test_mind_rejects_mapping_scent_transfer_candidate(
        self
    ):
        perception = CatPerception(
            self.cats
        )

        observations = perception.observe(
            self.tracker
        )

        observations.scent_transfer_candidates = [
            {
                'box_id': self.source.id,
                'counterpart_box_id': (
                    self.target.id
                ),
                'identity': 'cat:pazuzu',
                'similarity': 1.0,
                'source_layer': (
                    'meeting_place'
                ),
                'target_layer': (
                    'quantum_layer'
                ),
                'box_position': self.source.position.to_dict(),
                'counterpart_position': self.target.position.to_dict(),
            }
        ]

        with self.assertRaises(
            TypeError
        ):
            CatMind.consider(
                cat=self.tracker,
                observations=observations,
            )

if __name__ == '__main__':
    unittest.main()
