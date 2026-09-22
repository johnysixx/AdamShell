from core.entity.components import SpatialVector3
import unittest

from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatKnownScentTarget,
)
from cats.cat_mind import CatMind
from cats.cat_perception_state import (
    CatPerceptionState,
)
from cats.cat_scent_navigation_state import (
    CatKnownScentFollowState,
)


class CatKnownScentFollowStateObjectTests(
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

        self.cat.position = SpatialVector3(x=0.0, y=0.0, z=0.0)

    def test_state_has_no_mapping_api(self):
        state = CatKnownScentFollowState(
            active=True,
            identity='cat:pazuzu',
        )

        self.assertFalse(
            hasattr(state, 'get')
        )

        self.assertFalse(
            hasattr(
                state,
                '__getitem__',
            )
        )

        self.assertTrue(
            state.active
        )

        self.assertEqual(
            state.identity,
            'cat:pazuzu',
        )

    def test_mind_rejects_mapping_state(self):
        self.cat.known_scent_follow = {
            'arrived': True,
        }

        with self.assertRaises(TypeError):
            CatMind.consider(
                self.cat,
                CatPerceptionState(),
            )

    def test_executor_creates_object_state(self):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type='follow_known_scent',
                target=CatKnownScentTarget(
                    identity='cat:pazuzu',
                    layer='quantum_layer',
                    position=SpatialVector3(x=3.0, y=0.0, z=0.0),
                    source_id='trace_latest',
                    trail_direction=CatScentTrailDirection(
                        inferred=True,
                    ),
                ),
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
            result['name'],
            'cat_following_known_scent',
        )

        self.assertIsInstance(
            self.cat.known_scent_follow,
            CatKnownScentFollowState,
        )

    def test_finished_follow_remains_object_state(
        self
    ):
        self.cat.position = SpatialVector3(x=3.0, y=0.0, z=0.0)

        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type='follow_known_scent',
                target=CatKnownScentTarget(
                    identity='cat:pazuzu',
                    layer='quantum_layer',
                    position=self.cat.position,
                    source_id='trace_latest',
                    trail_direction=CatScentTrailDirection(
                        inferred=True,
                    ),
                ),
                score=1.0,
                reasons=['test'],
            )
        )

        self.cats.execute_cat_intention(
            self.cat
        )

        state = (
            self.cat.known_scent_follow
        )

        self.assertIsInstance(
            state,
            CatKnownScentFollowState,
        )

        self.assertTrue(
            state.arrived
        )

        self.assertFalse(
            state.active
        )


if __name__ == '__main__':
    unittest.main()
