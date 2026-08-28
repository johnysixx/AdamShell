import unittest
from universe.universe import Universe
from cats.cats import Cats
from universe.aroma_profile import AromaProfile
from universe.aroma_residue import AromaResidue
from cats.cat_olfaction import CatOlfaction

class AromaResidueTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.pazuzu = self.cats.create_cat(name='pazuzu', color='black', fur_length='short')
        self.observer = self.cats.create_cat(name='observer', color='gray', fur_length='short')
        self.pazuzu.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.observer['position'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}

    def test_aroma_can_transfer_to_object(self):
        box = self.universe.create_quantum_box()
        result = AromaResidue.transfer(source_profile=self.pazuzu.aroma, target=box, source_identity='pazuzu', fraction=0.2)
        self.assertTrue(result['transferred'])
        aroma = AromaProfile.current(box.aroma)
        self.assertGreater(aroma['cat'], 0.0)

    def test_residue_fades(self):
        box = self.universe.create_quantum_box()
        AromaResidue.transfer(self.pazuzu.aroma, box, 'pazuzu', fraction=0.2)
        before = AromaProfile.current(box.aroma)['cat']
        AromaResidue.decay(box, ticks=20)
        after = AromaProfile.current(box.aroma)['cat']
        self.assertLess(after, before)

    def test_other_cat_can_smell_residue_on_box(self):
        box = self.universe.create_quantum_box()
        box.position = {'x': 1.0, 'y': 0.0, 'z': 0.0}
        self.cats.learn_cat_aroma(observer=self.observer, observed_cat=self.pazuzu)
        AromaResidue.transfer(self.pazuzu.aroma, box, 'pazuzu', fraction=0.3)
        result = CatOlfaction.sniff(self.observer, self.universe)
        box_smell = next((item for item in result['detected_aromas'] if item['entity_id'] == box.id))
        self.assertTrue(box_smell['recognition']['recognized'])
        self.assertEqual(box_smell['recognition']['identity'], 'cat:pazuzu')
if __name__ == '__main__':
    unittest.main()
