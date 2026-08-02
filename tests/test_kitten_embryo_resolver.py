import unittest

from universe.universe import Universe
from cats import Cats
from cats.genotype import CatGenotype
from cats.kitten_embryo_resolver import (
    KittenEmbryoResolver
)


class FirstChoiceRng:

    def choice(self, values):
        return list(values)[0]

    def randint(self, minimum, maximum):
        return minimum


class KittenEmbryoResolverTests(
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

        self.father = self.cats.create_cat(
            name="father",
            color="black",
            fur_length="short",
            sex="male"
        )

        self.resolver = (
            KittenEmbryoResolver(
                self.universe
            )
        )

    def test_standard_embryo_is_preserved(self):
        result = (
            self.resolver.create_embryo(
                mother=self.mother,
                father=self.father,
                rng=FirstChoiceRng()
            )
        )

        embryo = result["embryo"]

        self.assertTrue(
            result["viable"]
        )

        self.assertIsNotNone(
            embryo
        )

        self.assertEqual(
            embryo["state"],
            "gestating"
        )

        self.assertEqual(
            embryo["genetic_status"],
            "standard"
        )

        self.assertFalse(
            embryo["rare"]
        )

        self.assertIsNone(
            result["cronenberg"]
        )

    def test_rare_xxy_male_embryo_is_preserved(self):
        genotype = (
            CatGenotype.create_founder(
                sex="male",
                sex_chromosomes=(
                    "X",
                    "X",
                    "Y"
                ),
                orange_locus=(
                    "O",
                    "o"
                )
            )
        )

        result = (
            self.resolver.create_embryo(
                mother=self.mother,
                father=self.father,
                rng=FirstChoiceRng(),
                genotype_override=genotype
            )
        )

        embryo = result["embryo"]

        self.assertTrue(
            result["viable"]
        )

        self.assertEqual(
            embryo["genetic_status"],
            "rare_valid"
        )

        self.assertTrue(
            embryo["rare"]
        )

        self.assertEqual(
            embryo["profile"]["sex"],
            "male"
        )

        self.assertEqual(
            embryo["profile"]["color"],
            "tortoiseshell"
        )

        self.assertIsNone(
            result["cronenberg"]
        )

    def test_nonviable_embryo_becomes_cronenberg(self):
        genotype = (
            CatGenotype.create_founder(
                sex="female",
                lethal_mutations=[
                    "embryonic_lethal"
                ]
            )
        )

        cronenberg_count_before = (
            self.universe.cronenberg_count
        )

        result = (
            self.resolver.create_embryo(
                mother=self.mother,
                father=self.father,
                rng=FirstChoiceRng(),
                genotype_override=genotype
            )
        )

        self.assertFalse(
            result["viable"]
        )

        self.assertIsNone(
            result["embryo"]
        )

        self.assertIsNotNone(
            result["cronenberg"]
        )

        self.assertEqual(
            self.universe.cronenberg_count,
            cronenberg_count_before + 1
        )

        self.assertTrue(
            result["event"][
                "cronenberg_created"
            ]
        )

        self.assertFalse(
            result["event"][
                "kitten_created"
            ]
        )


if __name__ == "__main__":
    unittest.main()