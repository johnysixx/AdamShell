import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_quantum_return_state import (
    CatQuantumReturnState,
)


class CatQuantumReturnObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='return_state_cat',
            color='black',
            fur_length='short',
        )

    def test_return_state_has_no_mapping_api(
        self
    ):
        state = CatQuantumReturnState(
            active=True,
            pair_id='pair_test',
            route_id='route_test',
            remote_box_id='remote_box',
            anchor_box_id='anchor_box',
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
            state.arrived_at_box
        )

        self.assertEqual(
            state.pair_id,
            'pair_test',
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
        self.cat.quantum_return = (
            CatQuantumReturnState(
                active=False,
            )
        )

        result = (
            self.cats
            .advance_cat_quantum_return(
                self.cat
            )
        )

        self.assertFalse(
            result['advanced']
        )

        self.assertEqual(
            result['reason'],
            'no_active_quantum_return',
        )

    def test_legacy_mapping_state_is_rejected(
        self
    ):
        self.cat.quantum_return = {
            'active': True,
            'arrived_at_box': False,
            'pair_id': 'legacy_pair',
            'route_id': 'legacy_route',
            'remote_box_id': 'remote',
            'anchor_box_id': 'anchor',
            'destination': None,
            'stabilized_path': None,
        }

        with self.assertRaises(
            TypeError
        ):
            self.cats.advance_cat_quantum_return(
                self.cat
            )


if __name__ == '__main__':
    unittest.main()
