import unittest
from unittest.mock import patch

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatShareLegendTarget,
)


class CatShareLegendListenerLookupObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.storyteller = (
            self.cats.create_cat(
                name='storyteller',
                color='black',
                fur_length='short',
            )
        )

    def share_intention(
        self,
        listener_name,
    ):
        return CatIntentionCandidate(
            type='share_legend',
            target=CatShareLegendTarget(
                listener_name=listener_name,
            ),
            score=1.0,
            reasons=['test'],
        )

    def test_executor_resolves_listener_cat_object(
        self
    ):
        listener = self.cats.create_cat(
            name='listener_cat',
            color='gray',
            fur_length='short',
        )

        self.storyteller.mind.current_intention = (
            self.share_intention(
                listener.name
            )
        )

        share_result = {
            'name': 'cat_shared_legend',
            'storyteller': (
                self.storyteller.name
            ),
            'listener': listener.name,
            'shared': True,
        }

        with patch.object(
            CatKnowledge,
            'share_legend',
            return_value=share_result,
        ) as share_legend:
            result = (
                self.cats
                .execute_cat_intention(
                    self.storyteller
                )
            )

        self.assertTrue(
            result['executed']
        )

        self.assertEqual(
            result['name'],
            'cat_shared_legend',
        )

        share_legend.assert_called_once_with(
            storyteller=self.storyteller,
            listener=listener,
            universe=self.universe,
        )

    def test_universe_mapping_is_not_listener(
        self
    ):
        self.universe.entities.append({
            'name': 'listener_cat',
            'type': 'cat',
        })

        self.storyteller.mind.current_intention = (
            self.share_intention(
                'listener_cat'
            )
        )

        with patch.object(
            CatKnowledge,
            'share_legend',
        ) as share_legend:
            result = (
                self.cats
                .execute_cat_intention(
                    self.storyteller
                )
            )

        self.assertFalse(
            result['executed']
        )

        self.assertEqual(
            result['reason'],
            'listener_not_found',
        )

        share_legend.assert_not_called()


if __name__ == '__main__':
    unittest.main()
