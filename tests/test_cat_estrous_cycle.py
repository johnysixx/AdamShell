import unittest

from universe.universe import Universe
from cats import Cats
from cats.estrous_cycle_resolver import (
    CatEstrousCycleResolver
)
from cats.mating_resolver import (
    CatMatingResolver
)
from cats.reproduction import (
    CatReproduction
)


class CatEstrousCycleTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()

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

        self.cycle = (
            CatEstrousCycleResolver(
                self.universe
            )
        )

    def test_first_cycle_day_starts_estrus(self):
        result = self.cycle.tick_day(
            self.female,
            day=1
        )

        reproduction = self.female.reproduction

        self.assertEqual(
            result["name"],
            "cat_estrus_started"
        )

        self.assertEqual(
            reproduction[
                "estrous_phase"
            ],
            "estrus"
        )

        self.assertTrue(
            reproduction[
                "estrus_active"
            ]
        )

    def test_estrus_changes_to_interestrus(self):
        self.cycle.activate_estrus(
            self.female
        )

        for day in range(
            1,
            8
        ):
            result = self.cycle.tick_day(
                self.female,
                day=day
            )

        self.assertEqual(
            result["name"],
            "cat_interestrus_started"
        )

        self.assertFalse(
            self.female.reproduction[
                "estrus_active"
            ]
        )

    def test_interestrus_returns_to_estrus(self):
        reproduction = self.female.reproduction

        reproduction[
            "estrous_phase"
        ] = "interestrus"
        reproduction[
            "estrus_active"
        ] = False
        reproduction[
            "estrous_cycle_day"
        ] = 0

        for day in range(
            1,
            9
        ):
            result = self.cycle.tick_day(
                self.female,
                day=day
            )

        self.assertEqual(
            result["name"],
            "cat_estrus_started"
        )

        self.assertTrue(
            reproduction["estrus_active"]
        )

    def test_mating_is_denied_outside_estrus(self):
        reproduction = self.female.reproduction

        reproduction[
            "estrus_active"
        ] = False

        reproduction[
            "estrous_phase"
        ] = "interestrus"

        mating = CatMatingResolver(
            self.universe
        )

        result = mating.mate(
            self.female,
            self.male
        )

        self.assertEqual(
            result["reason"],
            "female_not_in_estrus"
        )

        self.assertFalse(
            result["mating_recorded"]
        )

    def test_mating_is_allowed_during_estrus(self):
        self.cycle.activate_estrus(
            self.female
        )

        mating = CatMatingResolver(
            self.universe
        )

        result = mating.mate(
            self.female,
            self.male
        )

        self.assertEqual(
            result["name"],
            "cat_mating_contact_recorded"
        )

    def test_neutered_female_never_cycles(self):
        self.female.reproduction = (
            CatReproduction.create_state(
                sex="female",
                neutered=True
            )
        )

        result = self.cycle.tick_day(
            self.female
        )

        self.assertEqual(
            result["reason"],
            "neutered"
        )

        self.assertFalse(
            self.female.reproduction[
                "estrus_active"
            ]
        )

    def test_pregnant_female_does_not_cycle(self):
        reproduction = self.female.reproduction

        reproduction["pregnant"] = True
        reproduction[
            "estrous_phase"
        ] = "diestrus"
        reproduction[
            "estrus_active"
        ] = False

        result = self.cycle.tick_day(
            self.female
        )

        self.assertEqual(
            result["reason"],
            "pregnant"
        )

        self.assertFalse(
            reproduction["estrus_active"]
        )


if __name__ == "__main__":
    unittest.main()