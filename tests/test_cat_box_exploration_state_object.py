import unittest

from cats.cat_box_exploration_state import (
    CatBoxExplorationState,
)


class CatBoxExplorationStateObjectTests(
    unittest.TestCase
):

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatBoxExplorationState(
            active=True,
            arrived=False,
            box_id='box_alpha',
            route_id='route_alpha',
            destination={
                'x': 1.0,
                'y': 2.0,
                'z': 0.0,
            },
            observed=False,
        )

        self.assertTrue(
            state.active
        )

        self.assertEqual(
            state.box_id,
            'box_alpha',
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
                'update',
            )
        )


if __name__ == '__main__':
    unittest.main()
