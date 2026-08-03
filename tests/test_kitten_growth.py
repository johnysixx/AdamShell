import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.kitten_upbringing_resolver import (
    KittenUpbringingResolver
)


class KittenGrowthTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        self.upbringing = (
            KittenUpbringingResolver(
                self.universe
            )
        )

        self.mother = self.cats.create_cat(
            name="mother",
            color="black",
            fur_length="short",
            origin="natural_birth"
        )

        self.father = self.cats.create_cat(
            name="father",
            color="gray",
            fur_length="short",
            sex="male",
            origin="natural_birth"
        )

        self.kitten = self.cats.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        self.kitten["parents"] = {
            "mother": "mother",
            "father": "father"
        }

        self.kitten["mother_name"] = "mother"
        self.kitten["father_name"] = "father"

        self.development.initialize_newborn(
            self.kitten,
            birth_day=0
        )

        self.initial_size = self.kitten[
            "size"
        ]

        self.initial_strength = self.kitten[
            "strength"
        ]

    def run_day(
        self,
        day
    ):
        self.kitten[
            "age_days"
        ] = day

        return self.upbringing.tick_day(
            kitten=self.kitten,
            cats=self.cats.cats,
            current_day=day
        )

    def test_cat_milk_causes_growth(self):
        self.run_day(1)

        self.assertGreater(
            self.kitten["size"],
            self.initial_size
        )

        self.assertGreater(
            self.kitten["strength"],
            self.initial_strength
        )

        growth = self.kitten[
            "growth"
        ]

        self.assertEqual(
            growth["milk_feedings"],
            1
        )

    def test_same_milk_day_is_not_counted_twice(self):
        self.run_day(1)

        size_after_first = (
            self.kitten["size"]
        )

        result = self.upbringing.growth.feed_cat_milk(
            kitten=self.kitten,
            day=1,
            amount=1.0,
            source="mother"
        )

        self.assertFalse(
            result["grew"]
        )

        self.assertEqual(
            self.kitten["size"],
            size_after_first
        )

    def test_dead_cronenberg_delivery_causes_growth(self):
        self.run_day(14)

        growth = self.kitten[
            "growth"
        ]

        self.assertGreater(
            growth[
                "cronenberg_mass_consumed"
            ],
            0.0
        )

    def test_first_kill_causes_growth(self):
        size_before = self.kitten[
            "size"
        ]

        self.run_day(35)

        self.assertGreater(
            self.kitten["size"],
            size_before
        )

        self.assertGreater(
            self.kitten[
                "cronenberg_mass_eaten"
            ],
            0.0
        )

    def test_family_hunt_causes_growth(self):
        self.run_day(35)

        size_before = self.kitten[
            "size"
        ]

        result = self.run_day(36)

        hunt = next(
            event
            for event in result["events"]
            if event.get("name")
            == "kitten_joined_family_cronenberg_hunt"
        )

        self.assertTrue(
            hunt["growth"]["grew"]
        )

        self.assertGreater(
            self.kitten["size"],
            size_before
        )

    def test_father_delivery_causes_growth(self):
        self.kitten["upbringing"] = (
            self.upbringing
            ._create_upbringing_state()
        )

        size_before = self.kitten[
            "size"
        ]

        event = (
            self.upbringing
            ._father_food_delivery(
                kitten=self.kitten,
                father=self.father,
                age_days=5,
                current_day=5
            )
        )

        self.assertIsNotNone(
            event
        )

        self.assertTrue(
            event["growth"]["grew"]
        )

        self.assertGreater(
            self.kitten["size"],
            size_before
        )

    def test_growth_updates_existing_food_statistics(self):
        self.run_day(35)
        self.run_day(36)

        self.assertGreaterEqual(
            self.kitten[
                "cronenbergs_eaten"
            ],
            2
        )

        self.assertGreater(
            self.kitten[
                "cronenberg_mass_eaten"
            ],
            0.0
        )


if __name__ == "__main__":
    unittest.main()