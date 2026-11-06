import unittest
from dataclasses import FrozenInstanceError, replace

from cats.cat_intellect import (
    CatIntellect,
    CatIntellectState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatIntellectObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="intellect_object_cat",
            color="black",
            fur_length="short",
        )

    def test_cat_intellect_is_object_state(
        self
    ):
        self.assertIsInstance(
            self.cat.intellect,
            CatIntellectState,
        )

        self.assertFalse(
            hasattr(
                self.cat.intellect,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                self.cat.intellect,
                "__getitem__",
            )
        )

    def test_intellect_is_frozen(self):
        state = self.cat.intellect

        with self.assertRaises(FrozenInstanceError):
            state.score = 140

        with self.assertRaises(FrozenInstanceError):
            state.normalized = 0.8

    def test_with_score_preserves_original(self):
        original = self.cat.intellect
        old_score = original.score
        old_normalized = original.normalized

        updated = CatIntellect.with_score(original, 140)
        self.cat.intellect = updated

        self.assertIsNot(updated, original)
        self.assertEqual(original.score, old_score)
        self.assertEqual(original.normalized, old_normalized)
        self.assertEqual(updated.score, 140)
        self.assertEqual(updated.normalized, CatIntellect.normalize(140))
        self.assertIs(CatIntellect.ensure_state(self.cat), updated)

    def test_ensure_state_repairs_normalization(self):
        original = replace(
            self.cat.intellect, score=140, normalized=-1.0
        )
        self.cat.intellect = original

        corrected = CatIntellect.ensure_state(self.cat)

        self.assertIsNot(corrected, original)
        self.assertIs(corrected, self.cat.intellect)
        self.assertEqual(original.normalized, -1.0)
        self.assertEqual(corrected.score, 140)
        self.assertEqual(corrected.normalized, CatIntellect.normalize(140))

    def test_with_score_clamps_and_rejects_mapping(self):
        original = self.cat.intellect
        upper = CatIntellect.with_score(original, 500)
        lower = CatIntellect.with_score(original, -500)

        self.assertEqual((upper.score, upper.normalized), (160, 1.0))
        self.assertEqual((lower.score, lower.normalized), (40, 0.0))

        with self.assertRaises(TypeError):
            CatIntellect.with_score({"score": 100}, 140)

    def test_ensure_state_clamps_by_rebinding(self):
        original = replace(self.cat.intellect, score=500)
        self.cat.intellect = original

        corrected = CatIntellect.ensure_state(self.cat)

        self.assertIsNot(corrected, original)
        self.assertEqual(original.score, 500)
        self.assertIs(corrected, self.cat.intellect)
        self.assertEqual((corrected.score, corrected.normalized), (160, 1.0))

    def test_ensure_state_rejects_mapping_state(
        self
    ):
        self.cat.intellect = {
            "score": 100,
        }

        with self.assertRaises(
            TypeError
        ):
            CatIntellect.ensure_state(
                self.cat
            )


if __name__ == "__main__":
    unittest.main()
