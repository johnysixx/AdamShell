import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_quantum_exploration_state import (
    CatQuantumExplorationState,
)


class CatQuantumExplorationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='exploration_state_cat',
            color='black',
            fur_length='short',
        )

    @staticmethod
    def legacy_state():
        return {
            'active': True,
            'arrived': False,
            'pair_id': 'legacy_pair',
            'route_id': 'legacy_route',
            'destination': None,
            'stabilized_path': None,
            'stage': 1,
            'continuation': False,
        }

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatQuantumExplorationState(
            active=True,
            pair_id='pair_test',
            route_id='route_test',
            destination={
                'x': 1.0,
                'y': 2.0,
                'z': 3.0,
            },
        )

        self.assertTrue(
            state.active
        )

        self.assertFalse(
            state.arrived
        )

        self.assertEqual(
            state.stage,
            1,
        )

        self.assertFalse(
            state.continuation
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

        self.assertFalse(
            hasattr(
                state,
                '__setitem__',
            )
        )

    def test_inactive_object_is_not_advanced(
        self
    ):
        self.cat.quantum_exploration = (
            CatQuantumExplorationState(
                active=False,
            )
        )

        result = (
            self.cats
            .advance_cat_quantum_exploration(
                self.cat
            )
        )

        self.assertFalse(
            result['advanced']
        )

        self.assertEqual(
            result['reason'],
            'exploration_not_active',
        )

    def test_advance_rejects_mapping_state(
        self
    ):
        self.cat.quantum_exploration = (
            self.legacy_state()
        )

        with self.assertRaises(
            TypeError
        ):
            self.cats.advance_cat_quantum_exploration(
                self.cat
            )

    def test_finish_rejects_mapping_state(
        self
    ):
        self.cat.quantum_exploration = (
            self.legacy_state()
        )

        with self.assertRaises(
            TypeError
        ):
            self.universe.cat_box_transfer.finish_quantum_exploration(
                self.cat
            )

    def test_continue_rejects_mapping_state(
        self
    ):
        self.cat.quantum_exploration = (
            self.legacy_state()
        )

        with self.assertRaises(
            TypeError
        ):
            self.universe.cat_box_transfer.continue_quantum_exploration(
                self.cat
            )

    def test_start_rejects_mapping_state(
        self
    ):
        self.cat.quantum_exploration = (
            self.legacy_state()
        )

        with self.assertRaises(
            TypeError
        ):
            self.universe.cat_box_transfer.start_quantum_exploration_route(
                cat=self.cat,
                pair_id='missing_pair',
            )


if __name__ == '__main__':
    unittest.main()
