import unittest

from universe.universe import Universe
from cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.mating_resolver import (
    CatMatingResolver
)


class FirstChoiceRng:

    def randint(
        self,
        minimum,
        maximum
    ):
        return minimum

    def choice(
        self,
        values
    ):
        return list(values)[0]


class LifeCycleSystemTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

    def test_life_cycle_does_not_advance_before_big_bang(self):
        kitten = self.cats.create_cat(
            name="kitten",
            color="black",
            fur_length="short",
            sex="female"
        )

        development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        development.initialize_newborn(
            kitten
        )

        result = (
            self.universe
            .life_cycle_system
            .tick_day()
        )

        self.assertFalse(
            result["advanced"]
        )

        self.assertEqual(
            result["reason"],
            "physical_universe_not_started"
        )

        self.assertEqual(
            kitten["age_days"],
            0
        )

        self.assertEqual(
            self.universe.cronenberg_count,
            0
        )

    def test_universe_tick_advances_newborn_age(self):
        self.universe.start_big_bang()

        kitten = self.cats.create_cat(
            name="kitten",
            color="black",
            fur_length="short",
            sex="female"
        )

        development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        development.initialize_newborn(
            kitten,
            birth_day=0
        )

        self.universe.tick_universe()

        self.assertEqual(
            kitten["age_days"],
            1
        )

        self.assertEqual(
            self.universe
            .life_cycle_system
            .day,
            1
        )

    def test_quantum_cat_without_biological_age_is_not_reset(self):
        self.universe.start_big_bang()

        cat = self.cats.create_cat(
            name="quantum_cat",
            color="black",
            fur_length="short",
            sex="female",
            origin="quantum_manifestation"
        )

        self.universe.tick_universe()

        self.assertNotIn(
            "age_days",
            cat
        )

        self.assertTrue(
            cat.reproduction["fertile"]
        )

    def test_universe_tick_advances_pregnancy(self):
        self.universe.start_big_bang()

        mother = self.cats.create_cat(
            name="mother",
            color="black",
            fur_length="short",
            sex="female"
        )

        father = self.cats.create_cat(
            name="father",
            color="black",
            fur_length="short",
            sex="male"
        )

        mating = CatMatingResolver(
            self.universe
        )

        mother[
            "reproduction"
        ]["ovulation_threshold"] = 1

        mother[
            "reproduction"
        ]["estrus_active"] = True

        mother[
            "reproduction"
        ]["estrous_phase"] = "estrus"

        mating.mate(
            mother,
            father
        )

        mating.close_mating_window(
            mother,
            embryo_count=1,
            rng=FirstChoiceRng()
        )

        self.universe.tick_universe()

        self.assertEqual(
            mother[
                "reproduction"
            ][
                "pregnancy_day"
            ],
            1
        )

    def test_due_pregnancy_gives_birth_automatically(self):
        self.universe.start_big_bang()

        mother = self.cats.create_cat(
            name="mother",
            color="black",
            fur_length="short",
            sex="female"
        )

        father = self.cats.create_cat(
            name="father",
            color="black",
            fur_length="short",
            sex="male"
        )

        mating = CatMatingResolver(
            self.universe
        )

        mother[
            "reproduction"
        ]["ovulation_threshold"] = 1

        mother[
            "reproduction"
        ]["estrus_active"] = True

        mother[
            "reproduction"
        ]["estrous_phase"] = "estrus"

        mating.mate(
            mother,
            father
        )

        mating.close_mating_window(
            mother,
            embryo_count=2,
            rng=FirstChoiceRng()
        )

        mother[
            "reproduction"
        ][
            "pregnancy_day"
        ] = 64

        self.universe.tick_universe()

        kittens = [
            cat
            for cat in self.cats.cats
            if cat.name.startswith(
                "kitten_"
            )
        ]

        self.assertFalse(
            mother[
                "reproduction"
            ]["pregnant"]
        )

        self.assertEqual(
            len(kittens),
            2
        )

        self.assertEqual(
            {
                kitten["mother_name"]
                for kitten in kittens
            },
            {
                "mother"
            }
        )

        self.assertEqual(
            mother[
                "reproduction"
            ]["litters_born"],
            1
        )


if __name__ == "__main__":
    unittest.main()