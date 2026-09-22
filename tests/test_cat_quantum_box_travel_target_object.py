from core.entity.components import SpatialVector3
import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatQuantumBoxTravelTarget,
)


class CatQuantumBoxTravelTargetObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='traveller',
            color='black',
            fur_length='short',
        )

    def test_target_has_no_mapping_api(
        self
    ):
        target = CatQuantumBoxTravelTarget(
            source_box_id='source',
            counterpart_box_id='counterpart',
            source_layer='quantum_layer',
            target_layer='meeting_place',
            target_position=SpatialVector3(x=1.0, y=2.0, z=0.0),
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
            target.source_box_id,
            'source',
        )

        self.assertEqual(
            target.counterpart_box_id,
            'counterpart',
        )

    def test_executor_rejects_mapping_target(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type=(
                    'travel_through_known_quantum_box'
                ),
                target={
                    'source_box_id': 'source',
                    'counterpart_box_id': (
                        'counterpart'
                    ),
                    'source_layer': (
                        'quantum_layer'
                    ),
                    'target_layer': (
                        'meeting_place'
                    ),
                    'target_position': {
                        'x': 1.0,
                        'y': 2.0,
                        'z': 0.0,
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
            (
                'invalid_quantum_box_travel_target'
            ),
        )

        self.assertFalse(
            result['executed']
        )


if __name__ == '__main__':
    unittest.main()
