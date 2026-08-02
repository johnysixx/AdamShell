import unittest

from universe.universe import Universe
from cats import Cats
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


class CatInducedOvulationTests(
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

        self.female[
            "reproduction"
        ]["estrus_active"] = True

        self.female[
            "reproduction"
        ]["estrous_phase"] = "estrus"

        self.mating = CatMatingResolver(
            self.universe
        )

    def test_one_contact_does_not_induce_ovulation(self):
        result = self.mating.mate(
            self.female,
            self.male
        )

        self.assertEqual(
            result[
                "ovulation_stimulation"
            ],
            1
        )

        self.assertFalse(
            result[
                "ovulation_threshold_reached"
            ]
        )

    def test_four_contacts_reach_threshold(self):
        results = [
            self.mating.mate(
                self.female,
                self.male
            )
            for _ in range(4)
        ]

        self.assertEqual(
            results[-1][
                "ovulation_stimulation"
            ],
            4
        )

        self.assertTrue(
            results[-1][
                "ovulation_threshold_reached"
            ]
        )

    def test_insufficient_stimulation_closes_without_pregnancy(self):
        self.mating.mate(
            self.female,
            self.male
        )

        result = (
            self.mating
            .close_mating_window(
                self.female,
                embryo_count=2,
                rng=FirstChoiceRng()
            )
        )

        reproduction = self.female[
            "reproduction"
        ]

        self.assertFalse(
            result["started"]
        )

        self.assertFalse(
            result["ovulation_induced"]
        )

        self.assertEqual(
            result["ovulation"]["reason"],
            "insufficient_stimulation"
        )

        self.assertFalse(
            reproduction["pregnant"]
        )

        self.assertEqual(
            reproduction[
                "estrous_phase"
            ],
            "interestrus"
        )

        self.assertEqual(
            reproduction["embryos"],
            []
        )

    def test_threshold_stimulation_starts_pregnancy(self):
        for _ in range(4):
            self.mating.mate(
                self.female,
                self.male
            )

        result = (
            self.mating
            .close_mating_window(
                self.female,
                embryo_count=2,
                rng=FirstChoiceRng()
            )
        )

        self.assertTrue(
            result["started"]
        )

        self.assertTrue(
            result["ovulation_induced"]
        )

        self.assertTrue(
            self.female[
                "reproduction"
            ]["pregnant"]
        )

        self.assertEqual(
            len(
                self.female[
                    "reproduction"
                ]["embryos"]
            ),
            2
        )

    def test_multiple_males_jointly_contribute_to_ovulation(self):
        second_male = (
            self.cats.create_cat(
                name="second_male",
                color="orange",
                fur_length="short",
                sex="male"
            )
        )

        self.mating.mate(
            self.female,
            self.male
        )

        self.mating.mate(
            self.female,
            second_male
        )

        self.mating.mate(
            self.female,
            self.male
        )

        final_contact = (
            self.mating.mate(
                self.female,
                second_male
            )
        )

        self.assertEqual(
            final_contact[
                "ovulation_stimulation"
            ],
            4
        )

        self.assertEqual(
            self.female[
                "reproduction"
            ]["potential_fathers"],
            [
                "male",
                "second_male"
            ]
        )


if __name__ == "__main__":
    unittest.main()