import unittest

from universe.universe import Universe
from cats import Cats
from cats.mating_resolver import (
    CatMatingResolver
)
from cats.reproduction import (
    CatReproduction
)


class CatMatingResolverTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(
            self.universe
        )

        self.female = self.cats.create_cat(
            name="mother",
            color="black",
            fur_length="short",
            sex="female"
        )

        self.male = self.cats.create_cat(
            name="father",
            color="orange",
            fur_length="long",
            sex="male"
        )

        self.resolver = (
            CatMatingResolver(
                self.universe
            )
        )

    def test_fertile_pair_starts_pregnancy(self):
        event = self.resolver.mate(
            self.female,
            self.male,
            current_day=10
        )

        reproduction = self.female[
            "reproduction"
        ]

        self.assertTrue(
            event["started"]
        )

        self.assertTrue(
            reproduction["pregnant"]
        )

        self.assertEqual(
            reproduction["pregnancy_day"],
            0
        )

        self.assertEqual(
            reproduction["gestation_days"],
            65
        )

        self.assertEqual(
            reproduction[
                "expected_birth_day"
            ],
            75
        )

        self.assertEqual(
            reproduction["father_name"],
            "father"
        )

        self.assertTrue(
            reproduction[
                "mating_contact"
            ]["successful"]
        )

    def test_pregnancy_advances_to_birth_day(self):
        self.resolver.mate(
            self.female,
            self.male
        )

        before = (
            self.resolver
            .advance_pregnancy(
                self.female,
                days=64
            )
        )

        self.assertFalse(
            before["ready_for_birth"]
        )

        final = (
            self.resolver
            .advance_pregnancy(
                self.female,
                days=1
            )
        )

        self.assertTrue(
            final["ready_for_birth"]
        )

        self.assertEqual(
            final["pregnancy_day"],
            65
        )

    def test_neutered_female_cannot_become_pregnant(self):
        self.female[
            "reproduction"
        ] = (
            CatReproduction.create_state(
                sex="female",
                neutered=True
            )
        )

        with self.assertRaises(
            ValueError
        ):
            self.resolver.mate(
                self.female,
                self.male
            )

    def test_neutered_male_cannot_father_kittens(self):
        self.male[
            "reproduction"
        ] = (
            CatReproduction.create_state(
                sex="male",
                neutered=True
            )
        )

        with self.assertRaises(
            ValueError
        ):
            self.resolver.mate(
                self.female,
                self.male
            )

    def test_male_cannot_become_pregnant(self):
        with self.assertRaises(
            ValueError
        ):
            self.resolver.mate(
                self.male,
                self.female
            )

    def test_pregnant_cat_cannot_start_second_pregnancy(self):
        self.resolver.mate(
            self.female,
            self.male
        )

        with self.assertRaises(
            ValueError
        ):
            self.resolver.mate(
                self.female,
                self.male
            )

    def test_mating_creates_requested_embryos(self):
        event = self.resolver.mate(
            self.female,
            self.male,
            embryo_count=4
        )

        embryos = self.female[
            "reproduction"
        ]["embryos"]

        self.assertEqual(
            event["embryos_attempted"],
            4
        )

        self.assertEqual(
            event["viable_embryo_count"],
            4
        )

        self.assertEqual(
            event["nonviable_embryo_count"],
            0
        )

        self.assertEqual(
            len(embryos),
            4
        )

        self.assertTrue(
            all(
                embryo["state"]
                == "gestating"
                for embryo in embryos
            )
        )

    def test_custom_gestation_must_stay_in_range(self):
        with self.assertRaises(
            ValueError
        ):
            self.resolver.mate(
                self.female,
                self.male,
                gestation_days=62
            )

        with self.assertRaises(
            ValueError
        ):
            self.resolver.mate(
                self.female,
                self.male,
                gestation_days=67
            )


if __name__ == "__main__":
    unittest.main()