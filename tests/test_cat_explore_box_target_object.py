import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatExploreBoxTarget,
    CatIntentionCandidate,
)


class CatExploreBoxTargetObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='explorer',
            color='black',
            fur_length='short',
        )

    def test_target_has_no_mapping_api(
        self
    ):
        target = CatExploreBoxTarget(
            box_id='box_alpha'
        )

        self.assertEqual(
            target.box_id,
            'box_alpha',
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

    def test_executor_rejects_legacy_targets(
        self
    ):
        legacy_targets = (
            'box_alpha',
            {
                'box_id': 'box_alpha'
            },
            {
                'id': 'box_alpha'
            },
        )

        for legacy_target in legacy_targets:
            with self.subTest(
                target=legacy_target
            ):
                self.cat.mind.current_intention = (
                    CatIntentionCandidate(
                        type='explore_box',
                        target=legacy_target,
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
                        'invalid_explore_box_target'
                    ),
                )


if __name__ == '__main__':
    unittest.main()
