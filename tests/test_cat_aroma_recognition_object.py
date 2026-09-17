import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge
from cats.cat_olfaction_state import (
    CatAromaMatch,
    CatAromaRecognition,
)


class CatAromaRecognitionObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="recognition_cat",
            color="black",
            fur_length="short",
        )

    def test_unknown_aroma_returns_object(
        self
    ):
        recognition = (
            CatKnowledge.recognize_aroma(
                self.cat,
                {
                    "ozone": 1.0,
                },
            )
        )

        self.assertIsInstance(
            recognition,
            CatAromaRecognition,
        )

        self.assertFalse(
            recognition.recognized
        )

        self.assertIsNone(
            recognition.identity
        )

        self.assertEqual(
            recognition.matches,
            [],
        )

        self.assertFalse(
            hasattr(
                recognition,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                recognition,
                "__getitem__",
            )
        )

    def test_known_aroma_match_is_object(
        self
    ):
        CatKnowledge.learn_aroma(
            cat=self.cat,
            identity="cronenberg",
            components={
                "ozone": 1.0,
            },
            source="test",
        )

        recognition = (
            CatKnowledge.recognize_aroma(
                self.cat,
                {
                    "ozone": 1.0,
                },
            )
        )

        self.assertTrue(
            recognition.recognized
        )

        self.assertEqual(
            recognition.identity,
            "cronenberg",
        )

        self.assertTrue(
            recognition.matches
        )

        self.assertIsInstance(
            recognition.matches[0],
            CatAromaMatch,
        )

        self.assertFalse(
            hasattr(
                recognition.matches[0],
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                recognition.matches[0],
                "__getitem__",
            )
        )

    def test_best_match_is_exposed_through_attributes(
        self
    ):
        CatKnowledge.learn_aroma(
            cat=self.cat,
            identity="known_cat",
            components={
                "cat": 1.0,
                "fur": 0.8,
            },
            source="test",
        )

        recognition = (
            CatKnowledge.recognize_aroma(
                self.cat,
                {
                    "cat": 1.0,
                    "fur": 0.8,
                },
            )
        )

        winner = recognition.matches[0]

        self.assertEqual(
            recognition.identity,
            winner.identity,
        )

        self.assertEqual(
            recognition.similarity,
            winner.similarity,
        )


if __name__ == "__main__":
    unittest.main()
