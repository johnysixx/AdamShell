import unittest

from cats.cat_scent_navigation_state import (
    CatScentBoxFollowState,
)


class CatScentBoxFollowStateObjectTests(
    unittest.TestCase
):

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatScentBoxFollowState(
            active=True,
            source_box_id='source',
            target_box_id='target',
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

        self.assertTrue(
            state.active
        )

        self.assertEqual(
            state.source_box_id,
            'source',
        )


if __name__ == '__main__':
    unittest.main()
