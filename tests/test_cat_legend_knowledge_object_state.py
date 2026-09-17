import unittest

from cats.cat_knowledge import CatKnowledge
from cats.cat_knowledge_objects import (
    CatHeardLegend,
    CatVerifiedLegendRecord,
)
from cats.cats import Cats
from universe.universe import Universe


class CatLegendKnowledgeObjectStateTests(
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

        self.listener = (
            self.cats.create_cat(
                name='listener',
                color='gray',
                fur_length='short',
            )
        )

        place = (
            CatKnowledge.remember_place(
                self.storyteller,
                'quantum_layer',
                {
                    'x': 3.0,
                    'y': 4.0,
                    'z': 0.0,
                },
            )
        )

        self.legend = (
            CatKnowledge.publish_legend(
                self.universe,
                self.storyteller,
                place,
            )
        )

    def test_heard_legend_is_object_state(
        self
    ):
        heard = (
            CatKnowledge.hear_legend(
                self.listener,
                self.storyteller,
                self.legend,
            )
        )

        self.assertIsInstance(
            heard,
            CatHeardLegend,
        )

        stored = (
            self.listener.knowledge.heard_legends[0]
        )

        self.assertIsInstance(
            stored,
            CatHeardLegend,
        )

        self.assertFalse(
            hasattr(
                stored,
                'get',
            )
        )

    def test_verified_legend_is_object_state(
        self
    ):
        CatKnowledge.hear_legend(
            self.listener,
            self.storyteller,
            self.legend,
        )

        place = (
            CatKnowledge.remember_place(
                self.listener,
                'quantum_layer',
                {
                    'x': 3.0,
                    'y': 4.0,
                    'z': 0.0,
                },
            )
        )

        verified = (
            CatKnowledge
            .verify_heard_legend(
                self.listener,
                place,
            )
        )

        self.assertIsInstance(
            verified[0],
            CatVerifiedLegendRecord,
        )

        stored = (
            self.listener.knowledge.verified_legends[0]
        )

        self.assertIsInstance(
            stored,
            CatVerifiedLegendRecord,
        )

        self.assertFalse(
            hasattr(
                stored,
                'get',
            )
        )


if __name__ == '__main__':
    unittest.main()
