import unittest

from cats.cat_knowledge import CatKnowledge
from cats.cat_knowledge_objects import (
    CatKnowledgeState,
    CatKnownPrinciples,
)
from cats.cats import Cats
from universe.universe import Universe


class CatKnowledgeStateObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = (
            self.cats.create_cat(
                name='first_knowledge_cat',
                color='black',
                fur_length='short',
            )
        )

        self.second = (
            self.cats.create_cat(
                name='second_knowledge_cat',
                color='white',
                fur_length='short',
            )
        )

    def test_cat_owns_knowledge_state_object(
        self
    ):
        self.assertIsInstance(
            self.first.knowledge,
            CatKnowledgeState,
        )

        self.assertIsInstance(
            self.first
            .knowledge
            .known_principles,
            CatKnownPrinciples,
        )

        self.assertFalse(
            hasattr(
                self.first.knowledge,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                self.first.knowledge,
                'setdefault',
            )
        )

    def test_cats_own_separate_knowledge_state(
        self
    ):
        self.assertIsNot(
            self.first.knowledge,
            self.second.knowledge,
        )

        self.assertIsNot(
            self.first
            .knowledge
            .known_places,
            self.second
            .knowledge
            .known_places,
        )

        self.assertIsNot(
            self.first
            .knowledge
            .heard_group_myths,
            self.second
            .knowledge
            .heard_group_myths,
        )

    def test_ensure_returns_same_object(
        self
    ):
        state = (
            CatKnowledge
            .ensure_cat_knowledge(
                self.first
            )
        )

        self.assertIs(
            state,
            self.first.knowledge,
        )


if __name__ == '__main__':
    unittest.main()
