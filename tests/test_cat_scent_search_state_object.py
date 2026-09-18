import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatScentSearchTarget,
)
from cats.cat_mind import CatMind
from cats.cat_perception import CatPerception
from cats.cat_scent_navigation_state import (
    CatKnownScentFollowState,
    CatScentSearchState,
)


class CatScentSearchStateObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='tracker',
            color='black',
            fur_length='short',
        )

        self.cat.current_layer = (
            'quantum_layer'
        )

        self.cat.position = {
            'x': 3.0,
            'y': 0.0,
            'z': 0.0,
        }

        self.cat.known_scent_follow = (
            CatKnownScentFollowState(
                arrived=True,
                identity='cat:pazuzu',
                destination=dict(
                    self.cat.position
                ),
                trail_direction={
                    'inferred': True,
                    'unit_vector': {
                        'x': 1.0,
                        'y': 0.0,
                        'z': 0.0,
                    },
                    'confidence': 0.8,
                },
            )
        )

    def observations(self):
        return CatPerception(
            self.cats
        ).observe(
            self.cat
        )

    def search_intention(self):
        return CatIntentionCandidate(
            type='search_for_scent',
            target=CatScentSearchTarget(
                identity='cat:pazuzu',
                layer='quantum_layer',
                from_position=dict(
                    self.cat.position
                ),
                trail_direction={
                    'inferred': True,
                    'unit_vector': {
                        'x': 1.0,
                        'y': 0.0,
                        'z': 0.0,
                    },
                    'confidence': 0.8,
                },
                attempt=1,
                max_attempts=3,
                search_distance=1.0,
            ),
            score=1.0,
            reasons=['test'],
        )

    def test_state_has_no_mapping_api(self):
        state = CatScentSearchState(
            identity='cat:pazuzu',
        )

        self.assertFalse(
            hasattr(
                state,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__getitem__',
            )
        )

        self.assertEqual(
            state.identity,
            'cat:pazuzu',
        )

    def test_mind_rejects_mapping_state(self):
        self.cat.scent_search = {
            'identity': 'cat:pazuzu',
        }

        with self.assertRaises(
            TypeError
        ):
            CatMind.consider(
                cat=self.cat,
                observations=(
                    self.observations()
                ),
            )

    def test_executor_rejects_mapping_state(
        self
    ):
        self.cat.scent_search = {
            'active': True,
            'identity': 'cat:pazuzu',
        }

        self.cat.mind.current_intention = (
            self.search_intention()
        )

        with self.assertRaises(
            TypeError
        ):
            self.cats.execute_cat_intention(
                self.cat
            )

    def test_executor_creates_object_state(
        self
    ):
        self.cat.mind.current_intention = (
            self.search_intention()
        )

        result = (
            self.cats.execute_cat_intention(
                self.cat
            )
        )

        self.assertEqual(
            result['name'],
            'cat_searching_for_scent',
        )

        self.assertIsInstance(
            self.cat.scent_search,
            CatScentSearchState,
        )

        self.assertTrue(
            self.cat.scent_search.active
        )

        self.assertEqual(
            self.cat.scent_search.identity,
            'cat:pazuzu',
        )


if __name__ == '__main__':
    unittest.main()
