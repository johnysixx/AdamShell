import unittest

from cats.genotype import CatGenotype


class FirstChoiceRng:

    def choice(self, values):
        return list(values)[0]


class LastChoiceRng:

    def choice(self, values):
        return list(values)[-1]


class CatGenotypeInheritanceTests(
    unittest.TestCase
):

    def setUp(self):
        self.mother = (
            CatGenotype.create_founder(
                sex="female",
                orange_locus=(
                    "O",
                    "o"
                ),
                autosomal_loci={
                    "black": (
                        "B",
                        "b"
                    ),
                    "dilution": (
                        "D",
                        "d"
                    ),
                    "agouti": (
                        "A",
                        "a"
                    ),
                    "white_spotting": (
                        "S",
                        "s"
                    ),
                    "colorpoint": (
                        "C",
                        "cs"
                    ),
                    "longhair": (
                        "L",
                        "l"
                    )
                }
            )
        )

        self.father = (
            CatGenotype.create_founder(
                sex="male",
                orange_locus=(
                    "o",
                ),
                autosomal_loci={
                    "black": (
                        "b",
                        "bl"
                    ),
                    "dilution": (
                        "d",
                        "d"
                    ),
                    "agouti": (
                        "a",
                        "a"
                    ),
                    "white_spotting": (
                        "s",
                        "s"
                    ),
                    "colorpoint": (
                        "cs",
                        "c"
                    ),
                    "longhair": (
                        "l",
                        "l"
                    )
                }
            )
        )

    def test_daughter_inherits_x_from_both_parents(self):
        kitten = CatGenotype.inherit(
            self.mother,
            self.father,
            rng=FirstChoiceRng()
        )

        self.assertEqual(
            kitten["sex"],
            "female"
        )

        self.assertEqual(
            kitten[
                "sex_chromosomes"
            ],
            (
                "X",
                "X"
            )
        )

        self.assertEqual(
            kitten["orange_locus"],
            (
                "O",
                "o"
            )
        )

    def test_son_inherits_x_only_from_mother(self):
        kitten = CatGenotype.inherit(
            self.mother,
            self.father,
            rng=LastChoiceRng()
        )

        self.assertEqual(
            kitten["sex"],
            "male"
        )

        self.assertEqual(
            kitten[
                "sex_chromosomes"
            ],
            (
                "X",
                "Y"
            )
        )

        self.assertEqual(
            kitten["orange_locus"],
            (
                "o",
            )
        )

        self.assertIsNone(
            kitten[
                "inheritance_record"
            ][
                "orange_locus"
            ][
                "from_father"
            ]
        )

    def test_each_autosomal_locus_comes_from_both_parents(self):
        kitten = CatGenotype.inherit(
            self.mother,
            self.father,
            rng=FirstChoiceRng()
        )

        self.assertEqual(
            kitten[
                "autosomal_loci"
            ][
                "black"
            ],
            (
                "B",
                "b"
            )
        )

        self.assertEqual(
            kitten[
                "autosomal_loci"
            ][
                "dilution"
            ],
            (
                "D",
                "d"
            )
        )

        record = kitten[
            "inheritance_record"
        ][
            "autosomal_loci"
        ][
            "longhair"
        ]

        self.assertEqual(
            record["from_mother"],
            "L"
        )

        self.assertEqual(
            record["from_father"],
            "l"
        )

    def test_invalid_male_orange_locus_is_rejected(self):
        invalid = (
            CatGenotype.create_founder(
                sex="male"
            )
        )

        invalid[
            "orange_locus"
        ] = (
            "O",
            "o"
        )

        with self.assertRaises(
            ValueError
        ):
            CatGenotype.validate(
                invalid
            )

    def test_mother_and_father_roles_are_enforced(self):
        with self.assertRaises(
            ValueError
        ):
            CatGenotype.inherit(
                self.father,
                self.mother,
                rng=FirstChoiceRng()
            )


if __name__ == "__main__":
    unittest.main()