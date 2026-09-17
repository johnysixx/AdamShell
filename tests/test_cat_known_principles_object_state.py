import unittest

from cats.cat_knowledge import CatKnowledge
from cats.cat_knowledge_objects import (
    CatKnownPrinciples,
)
from cats.cats import Cats
from universe.universe import Universe


class CatKnownPrinciplesObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='principle_cat',
            color='black',
            fur_length='short',
        )

    def test_known_principles_are_object_state(
        self
    ):
        knowledge = (
            CatKnowledge.ensure_cat_knowledge(
                self.cat
            )
        )

        principles = knowledge.known_principles

        self.assertIsInstance(
            principles,
            CatKnownPrinciples,
        )

        self.assertTrue(
            principles.quantum_boxes_are_paired
        )

        self.assertFalse(
            hasattr(
                principles,
                'get',
            )
        )

    def test_principle_state_is_preserved(
        self
    ):
        knowledge = (
            CatKnowledge.ensure_cat_knowledge(
                self.cat
            )
        )

        principles = knowledge.known_principles

        principles.quantum_boxes_are_paired = (
            False
        )

        same_knowledge = (
            CatKnowledge.ensure_cat_knowledge(
                self.cat
            )
        )

        self.assertIs(
            same_knowledge.known_principles,
            principles,
        )

        self.assertFalse(
            principles.quantum_boxes_are_paired
        )


if __name__ == '__main__':
    unittest.main()
