import unittest

from universe.universe import Universe
from cats import Cats
from cats.reproduction import (
    CatReproduction
)


class CatReproductionStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(
            self.universe
        )

    def test_female_cat_can_become_pregnant(self):
        cat = self.cats.create_cat(
            name="female_cat",
            color="black",
            fur_length="short",
            sex="female"
        )

        reproduction = cat[
            "reproduction"
        ]

        self.assertFalse(
            reproduction["neutered"]
        )

        self.assertTrue(
            reproduction["fertile"]
        )

        self.assertFalse(
            reproduction["pregnant"]
        )

        self.assertTrue(
            CatReproduction
            .can_become_pregnant(cat)
        )

    def test_male_cat_can_father_kittens(self):
        cat = self.cats.create_cat(
            name="male_cat",
            color="black",
            fur_length="short",
            sex="male"
        )

        self.assertTrue(
            CatReproduction
            .can_father_kittens(cat)
        )

        self.assertFalse(
            CatReproduction
            .can_become_pregnant(cat)
        )

    def test_neutered_cat_is_not_fertile(self):
        cat = self.cats.create_cat(
            name="neutered_cat",
            color="black",
            fur_length="short",
            sex="female"
        )

        cat["reproduction"] = (
            CatReproduction.create_state(
                sex="female",
                neutered=True
            )
        )

        self.assertFalse(
            CatReproduction.can_mate(cat)
        )

        self.assertFalse(
            CatReproduction
            .can_become_pregnant(cat)
        )

    def test_default_gestation_is_sixty_five_days(self):
        self.assertEqual(
            CatReproduction
            .GESTATION_DAYS_DEFAULT,
            65
        )

        self.assertEqual(
            CatReproduction
            .GESTATION_DAYS_MIN,
            63
        )

        self.assertEqual(
            CatReproduction
            .GESTATION_DAYS_MAX,
            66
        )


if __name__ == "__main__":
    unittest.main()