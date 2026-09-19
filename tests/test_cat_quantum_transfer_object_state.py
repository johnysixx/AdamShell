import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_quantum_transfer_state import (
    CatQuantumTransferState,
)


class CatQuantumTransferObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='transfer_state_cat',
            color='black',
            fur_length='short',
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatQuantumTransferState(
            active=True,
            state='cat_transfer_superposition',
            cat_name='transfer_state_cat',
            source_box_id='source',
            target_box_id='target',
            source_layer='meeting_place',
            target_layer='quantum_layer',
            started_tick=7,
            cat_is_here=True,
            cat_is_not_here=True,
        )

        self.assertTrue(
            state.active
        )

        self.assertTrue(
            state.cat_is_here
        )

        self.assertTrue(
            state.cat_is_not_here
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

    def test_collapse_mutates_same_object(
        self
    ):
        state = CatQuantumTransferState(
            active=True,
            state='cat_transfer_superposition',
            cat_is_here=True,
            cat_is_not_here=True,
        )

        returned = state.collapse(
            resolved_layer='quantum_layer',
            resolved_position={
                'x': 1.0,
                'y': 2.0,
                'z': 3.0,
            },
            target_box_consumed=True,
        )

        self.assertIs(
            returned,
            state,
        )

        self.assertFalse(
            state.active
        )

        self.assertEqual(
            state.state,
            'collapsed',
        )

        self.assertTrue(
            state.cat_is_here
        )

        self.assertFalse(
            state.cat_is_not_here
        )

        self.assertEqual(
            state.resolved_layer,
            'quantum_layer',
        )

        self.assertTrue(
            state.target_box_consumed
        )

    def test_legacy_mapping_state_is_rejected(
        self
    ):
        self.cat.quantum_transfer = {
            'active': True,
            'state':
                'cat_transfer_superposition',
        }

        with self.assertRaises(
            TypeError
        ):
            (
                self.universe
                .cat_box_transfer
                .transfer_cat(
                    cat=self.cat,
                    source_box_id=(
                        'missing_source'
                    ),
                    target_box_id=(
                        'missing_target'
                    ),
                )
            )


if __name__ == '__main__':
    unittest.main()
