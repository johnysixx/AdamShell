import unittest

from meeting_place.bottle_shelf import BottleShelf


class BottleShelfTests(
    unittest.TestCase
):

    def test_bottle_shelf_exists_behind_bar(
        self
    ):
        shelf = BottleShelf()

        self.assertEqual(
            shelf.name,
            "bottle_shelf"
        )

        self.assertEqual(
            shelf.location,
            "behind_bar"
        )

        self.assertEqual(
            shelf.bottles,
            []
        )


    def test_first_dark_energy_creates_bottle(
        self
    ):
        shelf = BottleShelf()

        bottle = shelf.add_dark_energy(
            5.0
        )

        self.assertEqual(
            len(shelf.bottles),
            1
        )

        self.assertEqual(
            bottle["name"],
            "dark_energy_bottle"
        )

        self.assertEqual(
            bottle["type"],
            "dark_energy_bottle"
        )

        self.assertEqual(
            bottle["location"],
            "bottle_shelf"
        )

        self.assertEqual(
            bottle["dark_energy_j"],
            5.0
        )


    def test_additional_dark_energy_fills_existing_bottle(
        self
    ):
        shelf = BottleShelf()

        first = shelf.add_dark_energy(
            5.0
        )

        second = shelf.add_dark_energy(
            2.0
        )

        self.assertEqual(
            len(shelf.bottles),
            1
        )

        self.assertIs(
            first,
            second
        )

        self.assertEqual(
            first["dark_energy_j"],
            7.0
        )


if __name__ == "__main__":
    unittest.main()


