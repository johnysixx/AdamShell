import unittest

from meeting_place.dice_box import DiceBox


class FixedPercentileRng:

    def choice(self, items):
        return "d10_percentile"

    def randint(self, minimum, maximum):
        return 7


class FixedZeroPercentileRng:

    def choice(self, items):
        return "d10_percentile"

    def randint(self, minimum, maximum):
        return 10


class BarDiceSetTests(unittest.TestCase):

    def test_bar_dice_set_is_standard_without_d20(self):
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

    def test_percentile_die_rotates_in_tens(self):
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

    def test_percentile_ten_represents_zero(self):
        box = DiceBox()

        result = box.rotate_random_die(
            rng=FixedZeroPercentileRng()
        )

        self.assertEqual(
            result["raw_value"],
            10
        )

        self.assertEqual(
            result["value"],
            0
        )


if __name__ == "__main__":
    unittest.main()