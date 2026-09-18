import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_perception_state import (
    CatPerceptionState,
)
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatShareLegendTarget,
)


class CatShareLegendTargetObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='storyteller',
            color='black',
            fur_length='short',
        )

    def test_mind_creates_object_target(
        self
    ):
        observations = CatPerceptionState(
            nearby_cats=[
                'listener_cat',
            ],
            shareable_legend_count=1,
        )

        candidates = CatMind.consider(
            cat=self.cat,
            observations=observations,
        )

        candidate = next(
            item
            for item in candidates
            if item.type
            == 'share_legend'
        )

        self.assertIsInstance(
            candidate.target,
            CatShareLegendTarget,
        )

        self.assertEqual(
            candidate.target.listener_name,
            'listener_cat',
        )

        self.assertFalse(
            hasattr(
                candidate.target,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                candidate.target,
                '__getitem__',
            )
        )

    def test_executor_rejects_legacy_targets(
        self
    ):
        legacy_targets = [
            'listener_cat',
            {
                'name': 'listener_cat',
            },
            {
                'id': 'listener_cat',
            },
        ]

        for legacy_target in legacy_targets:
            self.cat.mind.current_intention = (
                CatIntentionCandidate(
                    type='share_legend',
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
                    'invalid_share_legend_target'
                ),
            )


if __name__ == '__main__':
    unittest.main()
