import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import UniverseBootstrap
from universe.bootstraps.entity_bootstrap import EntityBootstrap

class QuantumBoxCatBarMeowTests(unittest.TestCase):

    def setUp(self):
        registry = UniverseRegistry()
        self.universe = Universe()
        root_transition, self.layers, idea_universe = UniverseBootstrap(registry, self.universe).run()
        EntityBootstrap(self.universe, idea_universe, root_transition).run()
        self.bar = self.layers.get('meeting')
        manifestation = self.universe.manifest_cat(name='quantum_kitten', source='quantum_box_opened', position={'x': 10.0, 'y': 5.0, 'z': -2.0})
        self.cat = manifestation['cat']

    def test_cat_meows_at_bouncer_before_entry(self):
        self.bar.add_entity(self.cat)
        names = [event['name'] for event in self.bar.bouncer.cat_meow_history]
        self.assertIn('cat_meowed_at_bouncer', names)
        self.assertIn('bouncer_recognized_cat_meow', names)
        self.assertIn('bouncer_allowed_cat', names)
        recognition = next((event for event in self.bar.bouncer.cat_meow_history if event['name'] == 'bouncer_recognized_cat_meow'))
        self.assertTrue(recognition['recognized'])
        self.assertIn(self.cat, self.bar.entities)

    def test_bartender_replies_meow_and_serves_milk(self):
        self.bar.add_entity(self.cat)
        names = [event['name'] for event in self.bar.bartender.cat_meow_history]
        self.assertIn('cat_meowed_at_bartender', names)
        self.assertIn('bartender_replied_meow', names)
        self.assertEqual(self.bar.bar_counter.milk_bowl['contains'], 'milk')

    def test_bar_milk_makes_quantum_kitten_grow(self):
        size_before = self.cat.size
        strength_before = self.cat.strength
        self.bar.add_entity(self.cat)
        self.assertGreater(self.cat.size, size_before)
        self.assertGreater(self.cat.strength, strength_before)
        growth = self.cat.growth
        self.assertEqual(growth['milk_feedings'], 1)
        milk_event = next((event for event in self.bar.events if isinstance(event, dict) and event.get('name') == 'cat_drank_milk_at_bar'))
        self.assertTrue(milk_event['served'])
        self.assertTrue(milk_event['growth']['grew'])
if __name__ == '__main__':
    unittest.main()
