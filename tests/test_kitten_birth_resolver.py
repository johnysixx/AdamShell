import unittest

from universe.universe import Universe
from cats import Cats
from cats.mating_resolver import (
    CatMatingResolver
)
from cats.kitten_birth_resolver import (
    KittenBirthResolver
)


class AlternatingFatherRng:

    def __init__(self):
        self.index = 0

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
        values = list(values)

        if (
            values
            and isinstance(
                values[0],
                dict
            )
            and values[0].get(
                "type"
            ) == "cat"
        ):
            value = values[
                self.index
                % len(values)
            ]

            self.index += 1
            return value

        return values[0]


class KittenBirthResolverTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(
            self.universe
        )

        self.mother = self.cats.create_cat(
            name="mother",
            color="black",
            fur_length="short",
            sex="female"
        )

        self.father_one = (
            self.cats.create_cat(
                name="father_one",
                color="black",
                fur_length="short",
                sex="male"
            )
        )

        self.father_two = (
            self.cats.create_cat(
                name="father_two",
                color="orange",
                fur_length="long",
                sex="male"
            )
        )

        self.mating = (
            CatMatingResolver(
                self.universe
            )
        )

        self.birth = (
            KittenBirthResolver(
                self.universe
            )
        )

    def _start_pregnancy(
        self,
        embryo_count=4
    ):
        rng = AlternatingFatherRng()

        self.mating.mate(
            self.mother,
            self.father_one
        )

        self.mating.mate(
            self.mother,
            self.father_two
        )

        return (
            self.mating
            .close_mating_window(
                self.mother,
                current_day=10,
                embryo_count=(
                    embryo_count
                ),
                rng=rng
            )
        )

    def test_premature_birth_is_denied(self):
        self._start_pregnancy(
            embryo_count=2
        )

        self.mating.advance_pregnancy(
            self.mother,
            days=64
        )

        result = self.birth.give_birth(
            self.mother,
            current_day=74
        )

        self.assertFalse(
            result["born"]
        )

        self.assertEqual(
            result["reason"],
            "gestation_not_complete"
        )

        self.assertTrue(
            self.mother[
                "reproduction"
            ]["pregnant"]
        )

    def test_completed_pregnancy_creates_kittens(self):
        self._start_pregnancy(
            embryo_count=3
        )

        self.mating.advance_pregnancy(
            self.mother,
            days=65
        )

        result = self.birth.give_birth(
            self.mother,
            current_day=75
        )

        kittens = result["kittens"]

        self.assertTrue(
            result["born"]
        )

        self.assertEqual(
            result["kittens_born"],
            3
        )

        self.assertEqual(
            [
                kitten["name"]
                for kitten in kittens
            ],
            [
                "kitten_0001",
                "kitten_0002",
                "kitten_0003"
            ]
        )

        self.assertTrue(
            all(
                kitten["state"]
                == "newborn"
                for kitten in kittens
            )
        )

        self.assertTrue(
            all(
                kitten["mother_name"]
                == "mother"
                for kitten in kittens
            )
        )

        self.assertTrue(
            all(
                "genotype" in kitten
                for kitten in kittens
            )
        )

        self.assertTrue(
            all(
                "phenotype" in kitten
                for kitten in kittens
            )
        )

        self.assertTrue(
            all(
                kitten[
                    "reproduction"
                ][
                    "reproductive_maturity"
                ] is False
                for kitten in kittens
            )
        )

    def test_newborn_kittens_enter_development_system(self):
        self._start_pregnancy(
            embryo_count=1
        )

        self.mating.advance_pregnancy(
            self.mother,
            days=65
        )

        result = self.birth.give_birth(
            self.mother,
            current_day=75
        )

        kitten = result["kittens"][0]
        reproduction = kitten[
            "reproduction"
        ]

        self.assertEqual(
            kitten["age_days"],
            0
        )

        self.assertEqual(
            kitten["birth_day"],
            75
        )

        self.assertEqual(
            kitten[
                "developmental_stage"
            ],
            "newborn"
        )

        self.assertFalse(
            reproduction["fertile"]
        )

        self.assertFalse(
            reproduction[
                "reproductive_maturity"
            ]
        )

    def test_multiple_fathers_are_preserved(self):
        self._start_pregnancy(
            embryo_count=4
        )

        self.mating.advance_pregnancy(
            self.mother,
            days=65
        )

        result = self.birth.give_birth(
            self.mother
        )

        fathers = {
            kitten["father_name"]
            for kitten in result[
                "kittens"
            ]
        }

        self.assertEqual(
            fathers,
            {
                "father_one",
                "father_two"
            }
        )

        self.assertTrue(
            result["multiple_sires"]
        )

    def test_rare_traits_are_copied_from_embryo(self):
        self._start_pregnancy(
            embryo_count=1
        )

        embryo = self.mother[
            "reproduction"
        ]["embryos"][0]

        embryo[
            "genetic_status"
        ] = "rare_valid"
        embryo["rare"] = True
        embryo[
            "special_traits"
        ] = [
            "xxy_male",
            "rare_valid_genotype"
        ]

        self.mating.advance_pregnancy(
            self.mother,
            days=65
        )

        result = self.birth.give_birth(
            self.mother
        )

        kitten = result[
            "kittens"
        ][0]

        self.assertEqual(
            kitten["genetic_status"],
            "rare_valid"
        )

        self.assertTrue(
            kitten["rare"]
        )

        self.assertIn(
            "xxy_male",
            kitten["special_traits"]
        )

    def test_pregnancy_is_closed_after_birth(self):
        self._start_pregnancy(
            embryo_count=2
        )

        self.mating.advance_pregnancy(
            self.mother,
            days=65
        )

        result = self.birth.give_birth(
            self.mother
        )

        reproduction = self.mother[
            "reproduction"
        ]

        self.assertFalse(
            reproduction["pregnant"]
        )

        self.assertIsNone(
            reproduction["pregnancy_day"]
        )

        self.assertEqual(
            reproduction["embryos"],
            []
        )

        self.assertEqual(
            reproduction["litters_born"],
            1
        )

        self.assertEqual(
            reproduction["last_litter"][
                "kitten_names"
            ],
            result["kitten_names"]
        )

        self.assertEqual(
            len(
                reproduction["litters"]
            ),
            1
        )


if __name__ == "__main__":
    unittest.main()