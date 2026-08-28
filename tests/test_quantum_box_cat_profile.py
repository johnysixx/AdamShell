import unittest
from universe.universe import Universe

class QuantumBoxCatProfileTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

    def test_quantum_box_cat_is_juvenile_and_knows_meow(self):
        result = self.universe.manifest_cat(name='box_kitten', source='quantum_box_spontaneous_collapse', position={'x': 5.0, 'y': 2.0, 'z': -1.0})
        cat = result['cat']
        self.assertEqual(cat.age_days, 98)
        self.assertEqual(cat.developmental_stage, 'juvenile')
        self.assertTrue(cat.quantum_box_origin['manifested_from_box'])
        self.assertTrue(cat.learning['meow_knowledge']['learned'])
        self.assertTrue(cat.learning['meow_knowledge']['can_speak'])
        self.assertIn('sees_direct_path_to_bar', cat.special_traits)

    def test_quantum_box_cat_cannot_teach_yet(self):
        result = self.universe.manifest_cat(name='box_kitten', source='quantum_box_opened')
        cat = result['cat']
        abilities = cat.feline_wisdom['abilities']
        self.assertNotIn('teach_other_cats', abilities)
        self.assertNotIn('teach_teaching', abilities)

    def test_ordinary_manifested_cat_is_not_changed(self):
        result = self.universe.manifest_cat(name='ordinary_cat', source='test')
        cat = result['cat']
        self.assertNotIn('quantum_box_origin', cat)
        self.assertNotIn('juvenile_quantum_cat', cat.special_traits)
if __name__ == '__main__':
    unittest.main()
