import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.kitten_upbringing_resolver import (
    KittenUpbringingResolver
)


class CatPersonalitySocializationTests(
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

        self.kitten = self.cats.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        self.kitten["parents"] = {
            "mother": "mother",
            "father": None
        }

        self.kitten["mother_name"] = (
            "mother"
        )

        self.development.initialize_newborn(
            self.kitten,
            birth_day=0
        )

    def run_day(
        self,
        day
    ):
        self.kitten["age_days"] = day

        return self.upbringing.tick_day(
            kitten=self.kitten,
            cats=self.cats.cats,
            current_day=day
        )

    def traits(self):
        return self.kitten[
            "personality"
        ][
            "traits"
        ]

    def test_first_socialization_lesson_builds_empathy(
        self
    ):
        result = self.run_day(14)

        lesson = next(
            event
            for event in result["events"]
            if event.get("name")
            == "kitten_socialization_lesson"
        )

        self.assertAlmostEqual(
            self.traits()["empathy"],
            0.51
        )

        self.assertAlmostEqual(
            self.traits()["patience"],
            0.505
        )

        self.assertTrue(
            lesson[
                "personality"
            ][
                "applied"
            ]
        )

    def test_socialization_changes_accumulate(
        self
    ):
        for day in range(14, 21):
            self.run_day(day)

        self.assertAlmostEqual(
            self.traits()["empathy"],
            0.57
        )

        self.assertAlmostEqual(
            self.traits()["patience"],
            0.535
        )

    def test_pre_socialization_care_does_not_change_traits(
        self
    ):
        self.run_day(10)

        self.assertEqual(
            self.traits()["empathy"],
            0.5
        )

        self.assertEqual(
            self.traits()["patience"],
            0.5
        )


if __name__ == "__main__":
    unittest.main()