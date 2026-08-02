import unittest

from cats.genotype import CatGenotype
from cats.phenotype_resolver import (
    CatPhenotypeResolver
)
from cats.kitten_viability_resolver import (
    KittenGeneticViabilityResolver
)


class KittenGeneticViabilityTests(
    unittest.TestCase
):

    @staticmethod
    def _autosomal(
        white_spotting=(
            "s",
            "s"
        )
    ):
        return {
            "black": (
                "B",
                "B"
            ),
            "dilution": (
                "D",
                "D"
            ),
            "agouti": (
                "a",
                "a"
            ),
            "white_spotting": (
                white_spotting
            ),
            "colorpoint": (
                "C",
                "C"
            ),
            "longhair": (
                "L",
                "L"
            )
        }

    def test_standard_xy_male_is_standard(self):
        genotype = (
            CatGenotype.create_founder(
                sex="male",
                orange_locus=(
                    "o",
                ),
                autosomal_loci=(
                    self._autosomal()
                )
            )
        )

        result = (
            KittenGeneticViabilityResolver
            .resolve(genotype)
        )

        self.assertEqual(
            result["status"],
            "standard"
        )

        self.assertTrue(
            result["viable"]
        )

        self.assertFalse(
            result["rare"]
        )

    def test_xxy_tortoiseshell_male_is_rare_valid(self):
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
                ),
                autosomal_loci=(
                    self._autosomal()
                )
            )
        )

        viability = (
            KittenGeneticViabilityResolver
            .resolve(genotype)
        )

        phenotype = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            viability["status"],
            "rare_valid"
        )

        self.assertTrue(
            viability["viable"]
        )

        self.assertTrue(
            viability["rare"]
        )

        self.assertIn(
            "xxy_male",
            viability[
                "special_traits"
            ]
        )

        self.assertEqual(
            phenotype["profile"]["color"],
            "tortoiseshell"
        )

        self.assertEqual(
            phenotype["profile"]["sex"],
            "male"
        )

    def test_xxy_calico_male_is_rare_valid(self):
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
                ),
                autosomal_loci=(
                    self._autosomal(
                        white_spotting=(
                            "S",
                            "s"
                        )
                    )
                )
            )
        )

        viability = (
            KittenGeneticViabilityResolver
            .resolve(genotype)
        )

        phenotype = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            viability["status"],
            "rare_valid"
        )

        self.assertEqual(
            phenotype["profile"]["color"],
            "calico"
        )

        self.assertEqual(
            phenotype["profile"]["pattern"],
            "tricolor"
        )

        self.assertEqual(
            phenotype["profile"]["sex"],
            "male"
        )

    def test_explicit_lethal_mutation_is_nonviable(self):
        genotype = (
            CatGenotype.create_founder(
                sex="female",
                autosomal_loci=(
                    self._autosomal()
                ),
                lethal_mutations=[
                    "embryonic_lethal"
                ]
            )
        )

        result = (
            KittenGeneticViabilityResolver
            .resolve(genotype)
        )

        self.assertEqual(
            result["status"],
            "nonviable"
        )

        self.assertFalse(
            result["viable"]
        )

        self.assertEqual(
            result["reason"],
            "lethal_genetic_combination"
        )

    def test_internally_invalid_genotype_is_nonviable(self):
        genotype = (
            CatGenotype.create_founder(
                sex="male",
                autosomal_loci=(
                    self._autosomal()
                )
            )
        )

        genotype[
            "orange_locus"
        ] = (
            "O",
            "o"
        )

        result = (
            KittenGeneticViabilityResolver
            .resolve(genotype)
        )

        self.assertEqual(
            result["status"],
            "nonviable"
        )

        self.assertFalse(
            result["viable"]
        )

        self.assertEqual(
            result["reason"],
            "invalid_genotype"
        )


if __name__ == "__main__":
    unittest.main()