import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_perception import CatPerception
from cats.cat_olfaction import CatOlfaction
from universe.aroma_residue import AromaResidue

class CatQuantumBoxLayerVisibilityTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.pazuzu = self.cats.create_cat(name='pazuzu', color='black', fur_length='short')
        self.observer = self.cats.create_cat(name='observer', color='gray', fur_length='short')
        self.observer.current_layer = 'meeting_place'
        self.observer.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.source = self.universe.create_quantum_box(layer='meeting_place')
        self.target = self.universe.create_quantum_box(layer='quantum_layer')
        self.source.position = {'x': 1.0, 'y': 0.0, 'z': 0.0}
        self.target.position = {'x': 1.0, 'y': 0.0, 'z': 0.0}
        self.universe.cat_box_transfer.pair_boxes(self.source, self.target)
        self.cats.learn_cat_aroma(observer=self.observer, observed_cat=self.pazuzu)
        AromaResidue.transfer(source_profile=self.pazuzu.aroma, target=self.source, source_identity='pazuzu', fraction=0.3)
        AromaResidue.transfer(source_profile=self.pazuzu.aroma, target=self.target, source_identity='pazuzu', fraction=0.3)

    def test_cat_only_sees_box_in_current_layer(self):
        perception = CatPerception(self.cats)
        observations = perception.observe(self.observer)
        self.assertIn(self.source.id, observations['visible_boxes'])
        self.assertNotIn(self.target.id, observations['visible_boxes'])

    def test_cat_only_smells_box_in_current_layer(self):
        result = CatOlfaction.sniff(self.observer, self.universe)
        smelled_ids = {item['entity_id'] for item in result['detected_aromas']}
        self.assertIn(self.source.id, smelled_ids)
        self.assertNotIn(self.target.id, smelled_ids)

    def test_local_box_still_knows_counterpart(self):
        counterpart = self.source.quantum_counterpart
        self.assertTrue(counterpart.paired)
        self.assertEqual(counterpart.box_id, self.target.id)
        self.assertEqual(counterpart.layer, 'quantum_layer')
if __name__ == '__main__':
    unittest.main()
