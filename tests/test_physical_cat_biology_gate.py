import unittest

from universe.universe import Universe
from cats import Cats
from cats.mating_resolver import (
    CatMatingResolver
)


class PhysicalCatBiologyGateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(
            self.universe
        )

        self.female = self.cats.create_cat(
            name="female",
            color="black",
            fur_length="short",
            sex="female"
        )

        self.male = self.cats.create_cat(
            name="male",
            color="black",
            fur_length="short",
            sex="male"
        )

        self.resolver = CatMatingResolver(
            self.universe
        )

    def test_mating_before_physical_world_creates_cronenberg(self):
        before = (
            self.universe.cronenberg_count
        )

        result = self.resolver.mate(
            self.female,
            self.male
        )

        self.assertFalse(
            result["allowed"]
        )

        self.assertTrue(
            result["cronenberg_created"]
        )

        self.assertEqual(
            result["operation"],
            "cat_mating"
        )

        self.assertEqual(
            self.universe.cronenberg_count,
            before + 1
        )

        self.assertFalse(
            self.female[
                "reproduction"
            ]["mating_window_open"]
        )

        self.assertFalse(
            self.female[
                "reproduction"
            ]["pregnant"]
        )

    def test_mating_after_physical_world_is_allowed(self):
        self.universe.start_big_bang()

        result = self.resolver.mate(
            self.female,
            self.male
        )

        self.assertEqual(
            result["name"],
            "cat_mating_contact_recorded"
        )

        self.assertTrue(
            self.female[
                "reproduction"
            ]["mating_window_open"]
        )

        self.assertEqual(
            self.universe.cronenberg_count,
            0
        )


if __name__ == "__main__":
    unittest.main()