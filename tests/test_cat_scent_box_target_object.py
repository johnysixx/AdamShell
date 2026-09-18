import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatScentBoxTarget,
)


class CatScentBoxTargetObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='tracker',
            color='black',
            fur_length='short',
        )

    def test_target_has_no_mapping_api(
        self
    ):
        target = CatScentBoxTarget(
            identity='cat:pazuzu',
            box_id='source_box',
            counterpart_box_id='target_box',
            source_layer='meeting_place',
            target_layer='quantum_layer',
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
            target.counterpart_box_id,
            'target_box',
        )

    def test_executor_rejects_mapping_target(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type=(
                    'follow_scent_through_box'
                ),
                target={
                    'identity': 'cat:pazuzu',
                    'box_id': 'source_box',
                    'counterpart_box_id': (
                        'target_box'
                    ),
                    'source_layer': (
                        'meeting_place'
                    ),
                    'target_layer': (
                        'quantum_layer'
                    ),
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
            'invalid_scent_box_target',
        )

        self.assertFalse(
            result['executed']
        )


if __name__ == '__main__':
    unittest.main()
