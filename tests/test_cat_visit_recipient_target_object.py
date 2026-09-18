import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatVisitRecipientTarget,
)


class CatVisitRecipientTargetObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='recipient_seeker',
            color='black',
            fur_length='short',
        )

    def test_target_has_no_mapping_api(
        self
    ):
        target = CatVisitRecipientTarget(
            recipient_id='wizard',
        )

        self.assertEqual(
            target.recipient_id,
            'wizard',
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
                type='visit_recipient',
                target={
                    'recipient': 'wizard',
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
                'invalid_visit_recipient_target'
            ),
        )


if __name__ == '__main__':
    unittest.main()
