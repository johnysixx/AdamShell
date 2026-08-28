import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_olfaction import CatOlfaction
from cats.cat_knowledge import CatKnowledge
from universe.aroma_profile import AromaProfile

class CatOlfactionTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.observer = self.cats.create_cat(name='observer', color='black', fur_length='short')
        self.other = self.cats.create_cat(name='pazuzu', color='black', fur_length='short')
        self.observer.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.other.position = {'x': 2.0, 'y': 0.0, 'z': 0.0}
        self.universe.entities.append(self.observer)
        self.universe.entities.append(self.other)

    def test_cat_can_smell_other_cat(self):
        result = CatOlfaction.sniff(self.observer, self.universe)
        detected = [item for item in result['detected_aromas'] if item['actual_identity'] == 'cat:pazuzu']
        self.assertEqual(len(detected), 1)
        self.assertGreater(detected[0]['components']['cat'], 0.0)

    def test_unknown_cat_smell_is_not_identified(self):
        result = CatOlfaction.sniff(self.observer, self.universe)
        pazuzu = next((item for item in result['detected_aromas'] if item['actual_identity'] == 'cat:pazuzu'))
        self.assertFalse(pazuzu["recognition"]['recognized'])

    def test_cat_learns_specific_cat_smell(self):
        self.cats.learn_cat_aroma(observer=self.observer, observed_cat=self.other)
        result = CatOlfaction.sniff(self.observer, self.universe)
        pazuzu = next((item for item in result['detected_aromas'] if item['actual_identity'] == 'cat:pazuzu'))
        self.assertTrue(pazuzu["recognition"]['recognized'])
        self.assertEqual(pazuzu["recognition"]['identity'], 'cat:pazuzu')

    def test_surface_smell_does_not_destroy_identity(self):
        self.cats.learn_cat_aroma(self.observer, self.other)
        self.cats.add_surface_aroma(cat=self.other, source='raspberry_rum', components={'berry': 1.0, 'ethanol': 0.7}, intensity=0.3)
        result = CatOlfaction.sniff(self.observer, self.universe)
        pazuzu = next((item for item in result['detected_aromas'] if item['actual_identity'] == 'cat:pazuzu'))
        self.assertTrue(pazuzu["recognition"]['recognized'])
        self.assertEqual(pazuzu["recognition"]['identity'], 'cat:pazuzu')

    def test_ozone_can_be_detected_without_understanding_it(self):
        fake_cronenberg = type('FakeCronenberg', (), {})()
        fake_cronenberg.id = 'cronenberg_test'
        fake_cronenberg.position = {'x': 3.0, 'y': 0.0, 'z': 0.0}
        fake_cronenberg.aroma = AromaProfile.create('cronenberg', {'ozone': 1.0, 'ionized_air': 0.85, 'electrical': 0.75})
        self.universe.cronenbergs.append(fake_cronenberg)
        result = CatOlfaction.sniff(self.observer, self.universe)
        self.assertTrue(result['ozone_detected'])
        detected = next((item for item in result['detected_aromas'] if item['actual_identity'] == 'cronenberg'))
        self.assertFalse(detected['recognition']['recognized'])

    def test_experienced_cat_recognizes_cronenberg_ozone(self):
        fake_cronenberg = type('FakeCronenberg', (), {})()
        fake_cronenberg.id = 'cronenberg_test'
        fake_cronenberg.position = {'x': 3.0, 'y': 0.0, 'z': 0.0}
        fake_cronenberg.aroma = AromaProfile.create('cronenberg', {'ozone': 1.0, 'ionized_air': 0.85, 'electrical': 0.75})
        self.universe.cronenbergs.append(fake_cronenberg)
        self.cats.learn_aroma(cat=self.observer, identity='cronenberg', components=AromaProfile.current(fake_cronenberg.aroma), source='direct_cronenberg_encounter')
        result = CatOlfaction.sniff(self.observer, self.universe)
        detected = next((item for item in result['detected_aromas'] if item['actual_identity'] == 'cronenberg'))
        self.assertTrue(detected['recognition']['recognized'])
        self.assertEqual(detected['recognition']['identity'], 'cronenberg')

    def test_known_cat_is_not_confused_with_other_cat(self):
        garfield = self.cats.create_cat(name='garfield', color='orange', fur_length='short')
        garfield.position = {'x': 3.0, 'y': 0.0, 'z': 0.0}
        self.universe.entities.append(garfield)
        self.cats.learn_cat_aroma(observer=self.observer, observed_cat=self.other)
        result = CatOlfaction.sniff(self.observer, self.universe)
        pazuzu = next((item for item in result['detected_aromas'] if item['actual_identity'] == 'cat:pazuzu'))
        garfield_smell = next((item for item in result['detected_aromas'] if item['actual_identity'] == 'cat:garfield'))
        self.assertTrue(pazuzu["recognition"]['recognized'])
        self.assertEqual(pazuzu["recognition"]['identity'], 'cat:pazuzu')
        self.assertFalse(garfield_smell['recognition']['recognized'])

    def test_surface_aroma_preserves_individual_cat_identity(self):
        self.cats.learn_cat_aroma(observer=self.observer, observed_cat=self.other)
        self.cats.add_surface_aroma(cat=self.other, source='raspberry_rum', components={'berry': 1.0, 'ethanol': 0.7}, intensity=0.3)
        result = CatOlfaction.sniff(self.observer, self.universe)
        pazuzu = next((item for item in result['detected_aromas'] if item['actual_identity'] == 'cat:pazuzu'))
        self.assertTrue(pazuzu["recognition"]['recognized'])
        self.assertEqual(pazuzu["recognition"]['identity'], 'cat:pazuzu')
if __name__ == '__main__':
    unittest.main()
