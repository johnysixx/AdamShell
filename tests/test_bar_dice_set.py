import unittest

from meeting_place.dice_box import DiceBox


class FixedPercentileRng:

    def choice(
        self,
        items
    ):
        return "d10_percentile"

    def randint(
        self,
        minimum,
        maximum
    ):
        return 7


class FixedZeroPercentileRng:

    def choice(
        self,
        items
    ):
        return "d10_percentile"

    def randint(
        self,
        minimum,
        maximum
    ):
        return 10


class FixedPercentilePairRng:

    def __init__(
        self,
        values
    ):
        self.values = iter(
            values
        )

    def randint(
        self,
        minimum,
        maximum
    ):
        return next(
            self.values
        )


class BarDiceSetTests(
    unittest.TestCase
):

    def test_bar_dice_set_is_standard_without_d20(
        self
    ):
        box = DiceBox()

        self.assertEqual(
            box.contents,
            [
                "d4",
                "d6",
                "d8",
                "d10",
                "d10_percentile",
                "d12"
            ]
        )

        self.assertNotIn(
            "d100",
            box.contents
        )

        self.assertNotIn(
            "d20",
            box.contents
        )

        self.assertEqual(
            box.public_state["missing"],
            ["d20"]
        )

    def test_percentile_die_rotates_in_tens(
        self
    ):
        box = DiceBox()

        before = list(
            box.contents
        )

        result = box.rotate_random_die(
            rng=FixedPercentileRng()
        )

        self.assertEqual(
            result["die"],
            "d10_percentile"
        )

        self.assertEqual(
            result["sides"],
            10
        )

        self.assertEqual(
            result["face_value"],
            7
        )

        self.assertEqual(
            result["percentile_tens"],
            70
        )

        # Zpětná kompatibilita.
        self.assertEqual(
            result["raw_value"],
            7
        )

        self.assertEqual(
            result["value"],
            70
        )

        self.assertTrue(
            result["is_percentile"]
        )

        self.assertFalse(
            result["removed_from_box"]
        )

        self.assertEqual(
            box.contents,
            before
        )

    def test_percentile_ten_represents_zero(
        self
    ):
        box = DiceBox()

        result = box.rotate_random_die(
            rng=FixedZeroPercentileRng()
        )

        self.assertEqual(
            result["face_value"],
            10
        )

        self.assertEqual(
            result["percentile_tens"],
            0
        )

        self.assertEqual(
            result["raw_value"],
            10
        )

        self.assertEqual(
            result["value"],
            0
        )

    def test_percentile_pair_rolls_seventy_four(
        self
    ):
        box = DiceBox()

        result = box.rotate_percentile_pair(
            rng=FixedPercentilePairRng(
                [7, 4]
            )
        )

        self.assertEqual(
            result["tens"][
                "percentile_tens"
            ],
            70
        )

        self.assertEqual(
            result["units"][
                "percentile_units"
            ],
            4
        )

        self.assertEqual(
            result["value"],
            74
        )

    def test_double_zero_represents_one_hundred(
        self
    ):
        box = DiceBox()

        result = box.rotate_percentile_pair(
            rng=FixedPercentilePairRng(
                [10, 10]
            )
        )

        self.assertEqual(
            result["tens"][
                "percentile_tens"
            ],
            0
        )

        self.assertEqual(
            result["units"][
                "percentile_units"
            ],
            0
        )

        self.assertEqual(
            result["value"],
            100
        )

    def test_zero_tens_and_five_units_is_five(
        self
    ):
        box = DiceBox()

        result = box.rotate_percentile_pair(
            rng=FixedPercentilePairRng(
                [10, 5]
            )
        )

        self.assertEqual(
            result["value"],
            5
        )


if __name__ == "__main__":
    unittest.main()