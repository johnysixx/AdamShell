import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intellect import (
    CatIntellect
)
from cats.cat_mind import CatMind


class FixedGaussianRng:

    def __init__(
        self,
        value
    ):
        self.value = float(
            value
        )

    def gauss(
        self,
        mean,
        deviation
    ):
        return self.value


class CatIntellectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="thinking_cat",
            color="black",
            fur_length="short"
        )

    def test_new_cat_has_intellect(
        self
    ):
        intellect = self.cat[
            "intellect"
        ]

        self.assertGreaterEqual(
            intellect["score"],
            40
        )

        self.assertLessEqual(
            intellect["score"],
            160
        )

        self.assertEqual(
            intellect["distribution"],
            "gaussian"
        )

    def test_mean_gaussian_value_is_preserved(
        self
    ):
        intellect = (
            CatIntellect.create_state(
                rng=FixedGaussianRng(
                    100
                )
            )
        )

        self.assertEqual(
            intellect["score"],
            100
        )

        self.assertEqual(
            intellect["normalized"],
            0.5
        )

    def test_extreme_values_are_clamped(
        self
    ):
        very_high = (
            CatIntellect.create_state(
                rng=FixedGaussianRng(
                    500
                )
            )
        )

        very_low = (
            CatIntellect.create_state(
                rng=FixedGaussianRng(
                    -500
                )
            )
        )

        self.assertEqual(
            very_high["score"],
            160
        )

        self.assertEqual(
            very_low["score"],
            40
        )

    def test_high_intellect_uses_fewer_finalists(
        self
    ):
        self.cat[
            "intellect"
        ][
            "score"
        ] = 140

        count = (
            CatIntellect
            .decision_finalist_count(
                cat=self.cat,
                candidate_count=6
            )
        )

        self.assertEqual(
            count,
            2
        )

    def test_low_intellect_considers_more_options(
        self
    ):
        self.cat[
            "intellect"
        ][
            "score"
        ] = 60

        count = (
            CatIntellect
            .decision_finalist_count(
                cat=self.cat,
                candidate_count=6
            )
        )

        self.assertEqual(
            count,
            5
        )

    def test_intellect_is_recorded_in_decision(
        self
    ):
        self.cat[
            "intellect"
        ][
            "score"
        ] = 135

        result = CatMind.decide(
            cat=self.cat,
            observations={
                "bar_known": True,
                "bar_visible": True,
                "unexplored_boxes": [
                    "box_alpha"
                ],
                "nearby_cats": [
                    "other_cat"
                ],
                "interesting_unknown": True
            },
            quantum_roll=20
        )

        self.assertEqual(
            result["intellect_score"],
            135
        )

        self.assertEqual(
            result["intellect_category"],
            "exceptional"
        )

        self.assertEqual(
            result["finalist_count"],
            2
        )


if __name__ == "__main__":
    unittest.main()