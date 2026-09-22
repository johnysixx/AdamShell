from core.entity.components import SpatialVector3
import unittest

from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)

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
)


class CatScentSearchTargetObjectTests(
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

        self.cat.position = SpatialVector3(x=3.0, y=0.0, z=0.0)

        self.cat.known_scent_follow = (
            CatKnownScentFollowState(
                arrived=True,
                identity='cat:pazuzu',
                destination=self.cat.position,
                trail_direction=CatScentTrailDirection(
                    inferred=True,
                    unit_vector=SpatialVector3(x=1.0, y=0.0, z=0.0),
                    confidence=0.8,
                ),
            )
        )

    def observations(self):
        return CatPerception(
            self.cats
        ).observe(
            self.cat
        )

    def test_target_has_no_mapping_api(self):
        target = CatScentSearchTarget(
            identity='cat:pazuzu',
            layer='quantum_layer',
            attempt=2,
            max_attempts=3,
            search_distance=1.5,
        )

        self.assertFalse(
            hasattr(
                target,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                target,
                '__getitem__',
            )
        )

        self.assertEqual(
            target.identity,
            'cat:pazuzu',
        )

        self.assertEqual(
            target.attempt,
            2,
        )

    def test_mind_creates_object_target(self):
        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations(),
        )

        search = next(
            candidate
            for candidate in candidates
            if candidate.type
            == 'search_for_scent'
        )

        self.assertIsInstance(
            search.target,
            CatScentSearchTarget,
        )

        self.assertEqual(
            search.target.identity,
            'cat:pazuzu',
        )

        self.assertEqual(
            search.target.layer,
            'quantum_layer',
        )

    def test_executor_rejects_mapping_target(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type='search_for_scent',
                target={
                    'identity': 'cat:pazuzu',
                    'trail_direction': {
                        'inferred': True,
                        'unit_vector': {
                            'x': 1.0,
                            'y': 0.0,
                            'z': 0.0,
                        },
                    },
                },
                score=1.0,
                reasons=['test'],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertEqual(
            result['reason'],
            'invalid_search_target',
        )

        self.assertFalse(
            result['executed']
        )


if __name__ == '__main__':
    unittest.main()
