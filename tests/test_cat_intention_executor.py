from core.entity.social_entity import SocialEntity
import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind

class CatIntentionExecutorTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='autonomous_cat', color='black', fur_length='short')
        self.cat.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}

    def set_intention(self, intention_type, target=None):
        self.cat.mind.current_intention = {'type': intention_type, 'target': target, 'score': 0.8, 'reasons': ['test']}

    def create_cronenberg(self):
        cronenberg = self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('Executor test.'), source_component='test', source_operation='cat_intention_executor')
        cronenberg.position = {'x': 3.0, 'y': 0.0, 'z': 0.0}
        cronenberg.size = 0.5
        return cronenberg

    def test_visit_bar_starts_existing_navigation(self):
        self.set_intention('visit_bar')
        result = self.cats.execute_cat_intention(self.cat)
        self.assertTrue(result['executed'])
        self.assertEqual(result['intention'], 'visit_bar')
        self.assertEqual(result['body_intent'], 'return_to_bar')
        self.assertEqual(self.cat.intent, 'return_to_bar')
        self.assertTrue(hasattr(self.cat, 'active_route_id'))

    def test_hunt_uses_existing_hunt_navigation(self):
        cronenberg = self.create_cronenberg()
        self.set_intention('hunt_cronenberg', target=cronenberg.id)
        result = self.cats.execute_cat_intention(self.cat, cronenbergs=[cronenberg])
        self.assertTrue(result['executed'])
        self.assertEqual(result['body_intent'], 'hunt_nearest_cronenberg')
        self.assertEqual(self.cat.intent, 'hunt_nearest_cronenberg')

    def test_rest_is_executed_without_route(self):
        self.set_intention('rest')
        result = self.cats.execute_cat_intention(self.cat)
        self.assertTrue(result['executed'])
        self.assertEqual(self.cat.state, 'resting_by_own_choice')
        self.assertFalse(hasattr(self.cat, 'active_route_id'))

    def test_unimplemented_body_action_is_deferred(self):
        self.set_intention('observe', target='unknown_target')
        result = self.cats.execute_cat_intention(self.cat)
        self.assertFalse(result['executed'])
        self.assertTrue(result['deferred'])
        self.assertTrue(result['decision_preserved'])
        self.assertEqual(self.cat.mind.current_intention['type'], 'observe')

    def test_executor_does_not_make_new_decision(self):
        decision = CatMind.decide(cat=self.cat, observations={'bar_known': True, 'bar_visible': True})
        decision_count = self.cat.mind.decision_count
        result = self.cats.execute_cat_intention(self.cat)
        self.assertTrue(result['executed'])
        self.assertEqual(self.cat.mind.decision_count, decision_count)
        self.assertEqual(decision['intention'], result['intention'])

    def test_no_intention_does_nothing(self):
        result = self.cats.execute_cat_intention(self.cat)
        self.assertFalse(result['executed'])
        self.assertEqual(result['reason'], 'no_current_intention')

    def test_visit_recipient_requests_follow_entity_navigation(self):
        self.set_intention('visit_recipient', target={'recipient': 'wizard'})
        original_navigation = self.cats.offer_navigation_for_suggested_intent
        original_acceptance = self.cats.accept_navigation_offer
        captured = {}

        def fake_navigation(cat, cronenbergs=None, step_size=None):
            captured['suggested_intent'] = getattr(cat, 'suggested_intent', None)
            captured['navigation_target'] = getattr(cat, 'navigation_target', None)
            return {'name': 'cat_navigation_offered', 'offered': True, 'accepted': False, 'route_id': 'test_route', 'destination': 'wizard', 'route_step_count': 1}

        def fake_acceptance(cat):
            return {'name': 'cat_navigation_offer_accepted', 'accepted': True, 'route_id': 'test_route', 'destination': 'wizard'}
        self.cats.offer_navigation_for_suggested_intent = fake_navigation
        self.cats.accept_navigation_offer = fake_acceptance
        try:
            result = self.cats.execute_cat_intention(self.cat)
        finally:
            self.cats.offer_navigation_for_suggested_intent = original_navigation
            self.cats.accept_navigation_offer = original_acceptance
        self.assertTrue(result['executed'])
        self.assertEqual(result['intention'], 'visit_recipient')
        self.assertEqual(result['body_intent'], 'follow_entity')
        self.assertEqual(captured['suggested_intent'], 'follow_entity')
        self.assertEqual(captured['navigation_target'], 'wizard')

    def test_visit_recipient_starts_direct_route_in_same_layer(self):
        recipient = SocialEntity.from_mapping({'id': 'wizard', 'type': 'idea_entity', 'needs_cat': False, 'current_layer': 'idea_universe', 'position': {'x': 4.0, 'y': 3.0, 'z': 0.0}})
        self.universe.cat_recipient_registry.register(recipient)
        self.cat.current_layer = 'idea_universe'
        self.set_intention('visit_recipient', target={'recipient': 'wizard'})
        result = self.cats.execute_cat_intention(self.cat)
        self.assertTrue(result['executed'])
        self.assertEqual(result['body_intent'], 'follow_entity')
        self.assertEqual(result['destination'], 'recipient:wizard')
        self.assertEqual(self.cat.navigation_target, 'wizard')
        self.assertTrue(hasattr(self.cat, 'active_route_id'))

    def test_approach_cat_starts_direct_route(self):
        target_cat = self.cats.create_cat(name='target_cat', color='white', fur_length='short')
        target_cat.position = {'x': 4.0, 'y': 0.0, 'z': 0.0}
        target_cat.current_layer = self.cat.current_layer
        self.set_intention('approach_cat', target='target_cat')
        result = self.cats.execute_cat_intention(self.cat)
        self.assertTrue(result['executed'])
        self.assertEqual(result['name'], 'cat_approach_started')
        self.assertEqual(result['target'], 'target_cat')
        self.assertEqual(self.cat.state, 'approaching_cat')
        self.assertEqual(self.cat.navigation_target, 'target_cat')
        self.assertTrue(hasattr(self.cat, 'active_route_id'))

    def test_approach_cat_completes_when_already_near(self):
        target_cat = self.cats.create_cat(name='target_cat', color='white', fur_length='short')
        target_cat.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        target_cat.current_layer = self.cat.current_layer
        self.set_intention('approach_cat', target='target_cat')
        result = self.cats.execute_cat_intention(self.cat)
        self.assertTrue(result['executed'])
        self.assertTrue(result['arrived'])
        self.assertEqual(result['name'], 'cat_approach_completed')
        self.assertEqual(self.cat.state, 'near_target_cat')
if __name__ == '__main__':
    unittest.main()
