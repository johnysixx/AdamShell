import unittest
from dataclasses import FrozenInstanceError, replace
from universe.aroma_composition import AromaComposition

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
                AromaComposition.from_pairs(
                    ("ozone", 1.0),
                ),
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
            (),
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
            components=(
                AromaComposition.from_pairs(
                    ("ozone", 1.0),
                )
            ),
            source="test",
        )

        recognition = (
            CatKnowledge.recognize_aroma(
                self.cat,
                AromaComposition.from_pairs(
                    ("ozone", 1.0),
                ),
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
            components=(
                AromaComposition.from_pairs(
                    ("cat", 1.0),
                    ("fur", 0.8),
                )
            ),
            source="test",
        )

        recognition = (
            CatKnowledge.recognize_aroma(
                self.cat,
                AromaComposition.from_pairs(
                    ("cat", 1.0),
                    ("fur", 0.8),
                ),
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



    def test_aroma_match_is_immutable(self):
        match = CatAromaMatch(
            identity="cat:pazuzu",
            similarity=0.9,
            confidence=0.8,
            encounters=3,
        )

        for name, value in (
            ("identity", "other"),
            ("similarity", 0.1),
            ("confidence", 0.2),
            ("encounters", 9),
        ):
            with self.subTest(field=name):
                with self.assertRaises(FrozenInstanceError):
                    setattr(match, name, value)

    def test_aroma_match_replacement_preserves_original(self):
        original = CatAromaMatch(
            identity="cat:pazuzu",
            similarity=0.9,
            confidence=0.8,
            encounters=3,
        )

        updated = replace(
            original,
            confidence=0.95,
            encounters=4,
        )

        self.assertIsNot(updated, original)
        self.assertEqual(original.confidence, 0.8)
        self.assertEqual(original.encounters, 3)
        self.assertEqual(updated.confidence, 0.95)
        self.assertEqual(updated.encounters, 4)

    def test_recognition_produces_immutable_match(self):
        components = AromaComposition.from_pairs(
            ("cat", 1.0),
            ("fur", 0.8),
        )

        CatKnowledge.learn_aroma(
            cat=self.cat,
            identity="cat:pazuzu",
            components=components,
            source="test",
        )

        recognition = CatKnowledge.recognize_aroma(
            self.cat,
            components,
        )

        self.assertTrue(recognition.recognized)
        self.assertTrue(recognition.matches)

        match = recognition.matches[0]

        self.assertIsInstance(match, CatAromaMatch)
        self.assertEqual(match.identity, "cat:pazuzu")

        with self.assertRaises(FrozenInstanceError):
            match.similarity = 0.0

        self.assertEqual(
            recognition.similarity,
            match.similarity,
        )

    def test_aroma_match_has_value_equality(self):
        first = CatAromaMatch(
            identity="cat:pazuzu",
            similarity=0.9,
            confidence=0.8,
            encounters=3,
        )

        second = CatAromaMatch(
            identity="cat:pazuzu",
            similarity=0.9,
            confidence=0.8,
            encounters=3,
        )

        self.assertIsNot(first, second)
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        self.assertEqual(len({first, second}), 1)



    def test_recognition_is_deeply_immutable(self):
        match = CatAromaMatch(
            identity="cat:pazuzu",
            similarity=0.9,
            confidence=0.8,
            encounters=3,
        )

        recognition = CatAromaRecognition(
            recognized=True,
            identity=match.identity,
            similarity=match.similarity,
            matches=(match,),
        )

        for name, value in (
            ("recognized", False),
            ("identity", "other"),
            ("similarity", 0.0),
            ("matches", ()),
        ):
            with self.subTest(field=name):
                with self.assertRaises(FrozenInstanceError):
                    setattr(recognition, name, value)

        with self.assertRaises(TypeError):
            recognition.matches[0] = match

        with self.assertRaises(FrozenInstanceError):
            recognition.matches[0].confidence = 0.1

    def test_recognition_rejects_mutable_and_invalid_matches(self):
        match = CatAromaMatch(
            identity="cat:pazuzu",
            similarity=0.9,
            confidence=0.8,
            encounters=3,
        )

        for invalid in (
            [],
            [match],
            ({"identity": "cat:pazuzu"},),
            ("cat:pazuzu",),
        ):
            with self.subTest(invalid=repr(invalid)):
                with self.assertRaises(TypeError):
                    CatAromaRecognition(
                        matches=invalid,
                    )

    def test_recognition_replacement_preserves_original(self):
        match = CatAromaMatch(
            identity="cat:pazuzu",
            similarity=0.9,
            confidence=0.8,
            encounters=3,
        )

        original = CatAromaRecognition(
            recognized=True,
            identity=match.identity,
            similarity=0.9,
            matches=(match,),
        )

        updated = replace(
            original,
            similarity=0.95,
        )

        self.assertIsNot(updated, original)
        self.assertEqual(original.similarity, 0.9)
        self.assertEqual(updated.similarity, 0.95)
        self.assertIs(updated.matches, original.matches)

    def test_recognition_producer_returns_immutable_tuple(self):
        components = AromaComposition.from_pairs(
            ("cat", 1.0),
            ("fur", 0.8),
        )

        CatKnowledge.learn_aroma(
            cat=self.cat,
            identity="cat:pazuzu",
            components=components,
            source="test",
        )

        recognition = CatKnowledge.recognize_aroma(
            self.cat,
            components,
        )

        self.assertTrue(recognition.recognized)
        self.assertIsInstance(recognition.matches, tuple)
        self.assertTrue(recognition.matches)
        self.assertTrue(
            all(
                isinstance(match, CatAromaMatch)
                for match in recognition.matches
            )
        )
        self.assertEqual(
            recognition.identity,
            recognition.matches[0].identity,
        )
        self.assertEqual(
            recognition.similarity,
            recognition.matches[0].similarity,
        )


if __name__ == "__main__":
    unittest.main()
