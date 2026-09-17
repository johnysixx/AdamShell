import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_olfaction import CatOlfaction
from cats.cat_olfaction_state import (
    CatOlfactionState,
)
from cats.cat_perception import CatPerception


class CatOlfactionStateObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="observer",
            color="black",
            fur_length="short",
        )

        self.cat.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

    def test_sniff_returns_clean_object_state(
        self
    ):
        result = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        self.assertIsInstance(
            result,
            CatOlfactionState,
        )

        self.assertFalse(
            hasattr(
                result,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                result,
                "__getitem__",
            )
        )

        self.assertTrue(
            result.sniffed
        )

        self.assertEqual(
            result.cat,
            self.cat.name,
        )

    def test_detected_count_is_derived_from_aromas(
        self
    ):
        result = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        self.assertEqual(
            result.detected_count,
            len(
                result.detected_aromas
            ),
        )

        result.detected_aromas.append(
            object()
        )

        self.assertEqual(
            result.detected_count,
            len(
                result.detected_aromas
            ),
        )

    def test_perception_keeps_olfaction_object(
        self
    ):
        observations = CatPerception(
            self.cats
        ).observe(
            self.cat
        )

        self.assertIsInstance(
            observations.olfaction,
            CatOlfactionState,
        )


if __name__ == "__main__":
    unittest.main()
