import unittest

from cats.cat_knowledge import CatKnowledge
from cats.cat_knowledge_objects import (
    CatKnownAroma,
)
from cats.cats import Cats
from universe.universe import Universe


class CatAromaKnowledgeObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = (
            self.cats.create_cat(
                name='nose',
                color='black',
                fur_length='short',
            )
        )

    def test_known_aroma_is_object_state(
        self
    ):
        aroma = (
            CatKnowledge.learn_aroma(
                cat=self.cat,
                identity='raspberry_rum',
                components={
                    'berry': 1.0,
                    'ethanol': 0.7,
                },
            )
        )

        self.assertIsInstance(
            aroma,
            CatKnownAroma,
        )

        stored = (
            self.cat.knowledge[
                'known_aromas'
            ][0]
        )

        self.assertIsInstance(
            stored,
            CatKnownAroma,
        )

        self.assertFalse(
            hasattr(
                stored,
                'get',
            )
        )

    def test_repeated_learning_updates_object(
        self
    ):
        CatKnowledge.learn_aroma(
            cat=self.cat,
            identity='raspberry_rum',
            components={
                'berry': 1.0,
            },
            source='first_contact',
        )

        CatKnowledge.learn_aroma(
            cat=self.cat,
            identity='raspberry_rum',
            components={
                'berry': 0.8,
                'ethanol': 0.6,
            },
            source='second_contact',
        )

        aromas = (
            self.cat.knowledge[
                'known_aromas'
            ]
        )

        self.assertEqual(
            len(aromas),
            1,
        )

        stored = aromas[0]

        self.assertIsInstance(
            stored,
            CatKnownAroma,
        )

        self.assertEqual(
            stored.encounters,
            2,
        )

        self.assertEqual(
            stored.source,
            'second_contact',
        )

        self.assertGreater(
            stored.confidence,
            0.55,
        )


if __name__ == '__main__':
    unittest.main()
