import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatExplorationPairTarget,
    CatIntentionCandidate,
)


class CatExplorationPairTargetObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='pair_builder',
            color='black',
            fur_length='short',
        )

    def test_target_has_no_mapping_api(
        self
    ):
        target = (
            CatExplorationPairTarget(
                layer='quantum_layer',
                position={
                    'x': 8.0,
                    'y': 2.0,
                    'z': 0.0,
                },
                energy_cost=200.0,
            )
        )

        self.assertEqual(
            target.layer,
            'quantum_layer',
        )

        self.assertEqual(
            target.position,
            {
                'x': 8.0,
                'y': 2.0,
                'z': 0.0,
            },
        )

        self.assertEqual(
            target.energy_cost,
            200.0,
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

    def test_executor_rejects_mapping_target(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type=(
                    'create_exploration_pair'
                ),
                target={
                    'layer': 'quantum_layer',
                    'position': {
                        'x': 8.0,
                        'y': 2.0,
                        'z': 0.0,
                    },
                    'energy_cost': 200.0,
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

        self.assertFalse(
            result['executed']
        )

        self.assertEqual(
            result['reason'],
            (
                'invalid_exploration_pair_target'
            ),
        )


if __name__ == '__main__':
    unittest.main()
