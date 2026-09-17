import unittest

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

    def test_ensure_state_preserves_object(
        self
    ):
        intellect = self.cat.intellect

        intellect.score = 140

        ensured = (
            CatIntellect.ensure_state(
                self.cat
            )
        )

        self.assertIs(
            ensured,
            intellect,
        )

        self.assertEqual(
            ensured.score,
            140,
        )

        self.assertEqual(
            ensured.normalized,
            CatIntellect.normalize(
                140
            ),
        )

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
