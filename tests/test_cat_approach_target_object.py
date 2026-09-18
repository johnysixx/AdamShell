import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_perception_state import (
    CatPerceptionState,
)
from cats.cat_intention_state import (
    CatApproachCatTarget,
    CatIntentionCandidate,
)


class CatApproachTargetObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='approacher',
            color='black',
            fur_length='short',
        )

    def test_mind_creates_object_target(
        self
    ):
        target = CatApproachCatTarget(
            cat_name='target_cat',
        )

        self.assertEqual(
            target.cat_name,
            'target_cat',
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

        observations = CatPerceptionState(
            nearby_cats=[
                'target_cat'
            ],
        )

        candidates = CatMind.consider(
            cat=self.cat,
            observations=observations,
        )

        approach = next(
            candidate
            for candidate in candidates
            if candidate.type
            == 'approach_cat'
        )

        self.assertIsInstance(
            approach.target,
            CatApproachCatTarget,
        )

        self.assertEqual(
            approach.target.cat_name,
            'target_cat',
        )

    def test_executor_rejects_legacy_targets(
        self
    ):
        legacy_targets = [
            'target_cat',
            {
                'cat': 'target_cat',
            },
            {
                'name': 'target_cat',
            },
        ]

        for legacy_target in legacy_targets:
            self.cat.mind.current_intention = (
                CatIntentionCandidate(
                    type='approach_cat',
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
                    'invalid_approach_cat_target'
                ),
            )


if __name__ == '__main__':
    unittest.main()
