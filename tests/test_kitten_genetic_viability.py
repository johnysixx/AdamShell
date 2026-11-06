import unittest
from dataclasses import FrozenInstanceError

from cats.genotype import (
    CatAutosomalGenotype,
    CatGenotype,
)
from cats.phenotype_resolver import (
    CatPhenotypeResolver
)
from cats.kitten_viability_resolver import (
    KittenGeneticViabilityResolver,
    KittenGeneticViabilityResult,
    KittenViabilityDetailRule,
    KittenInvalidGenotypeDetails,
    KittenLethalMutationDetails,
    KittenXXYGenotypeDetails,
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
        return CatAutosomalGenotype(
            black=("B", "B"),
            dilution=("D", "D"),
            agouti=("a", "a"),
            white_spotting=(
                white_spotting
            ),
            colorpoint=("C", "C"),
            longhair=("L", "L"),
        )

    def test_detail_rules_are_immutable_objects(self):
        rules = KittenGeneticViabilityResult.DETAIL_RULES

        self.assertIsInstance(
            rules,
            tuple,
        )

        self.assertEqual(
            tuple(
                (rule.reason, rule.details_type)
                for rule in rules
            ),
            (
                (
                    "invalid_genotype",
                    KittenInvalidGenotypeDetails,
                ),
                (
                    "lethal_genetic_combination",
                    KittenLethalMutationDetails,
                ),
                (
                    "xxy_male",
                    KittenXXYGenotypeDetails,
                ),
            ),
        )

        for rule in rules:
            self.assertIsInstance(
                rule,
                KittenViabilityDetailRule,
            )

            for method in (
                "get",
                "keys",
                "items",
                "values",
                "to_dict",
            ):
                self.assertFalse(
                    hasattr(rule, method)
                )

            with self.assertRaises(TypeError):
                _ = rule["reason"]

            self.assertFalse(
                hasattr(rule, "__dict__")
            )

        with self.assertRaises(FrozenInstanceError):
            rules[0].reason = "changed"

    def test_detail_rule_rejects_invalid_values(self):
        with self.assertRaises(TypeError):
            KittenViabilityDetailRule(
                "",
                KittenInvalidGenotypeDetails,
            )

        with self.assertRaises(TypeError):
            KittenViabilityDetailRule(
                None,
                KittenInvalidGenotypeDetails,
            )

        with self.assertRaises(TypeError):
            KittenViabilityDetailRule(
                "invalid_genotype",
                dict,
            )

        with self.assertRaises(TypeError):
            KittenViabilityDetailRule(
                "invalid_genotype",
                None,
            )

        valid = KittenViabilityDetailRule(
            "invalid_genotype",
            KittenInvalidGenotypeDetails,
        )

        self.assertIs(
            valid.details_type,
            KittenInvalidGenotypeDetails,
        )

    def test_typed_rules_preserve_viability_validation(self):
        valid_genotype = CatGenotype.create_founder(
            sex="female",
        )

        detail_cases = (
            (
                "invalid_genotype",
                KittenInvalidGenotypeDetails(
                    error="invalid",
                ),
            ),
            (
                "lethal_genetic_combination",
                KittenLethalMutationDetails(
                    lethal_mutations=("lethal",),
                ),
            ),
            (
                "xxy_male",
                KittenXXYGenotypeDetails(
                    sex_chromosomes=("X", "X", "Y"),
                ),
            ),
        )

        for reason, details in detail_cases:
            result = KittenGeneticViabilityResult(
                status="nonviable",
                viable=False,
                rare=False,
                reason=reason,
                details=details,
                special_traits=(),
                genotype=valid_genotype,
            )

            self.assertEqual(
                result.reason,
                reason,
            )

            self.assertIs(
                result.details,
                details,
            )

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported kitten viability reason",
        ):
            KittenGeneticViabilityResult(
                status="nonviable",
                viable=False,
                rare=False,
                reason="unknown_reason",
                details=None,
                special_traits=(),
                genotype=valid_genotype,
            )

        with self.assertRaisesRegex(
            TypeError,
            "Viability details do not match",
        ):
            KittenGeneticViabilityResult(
                status="nonviable",
                viable=False,
                rare=False,
                reason="xxy_male",
                details=KittenInvalidGenotypeDetails(
                    error="wrong_type",
                ),
                special_traits=(),
                genotype=valid_genotype,
            )

        with self.assertRaisesRegex(
            TypeError,
            "Standard viability result",
        ):
            KittenGeneticViabilityResult(
                status="standard",
                viable=True,
                rare=False,
                reason=None,
                details=KittenInvalidGenotypeDetails(
                    error="unexpected",
                ),
                special_traits=(),
                genotype=valid_genotype,
            )

        standard = KittenGeneticViabilityResolver.resolve(
            valid_genotype,
        )

        self.assertIsNone(
            standard.reason,
        )

        self.assertIsNone(
            standard.details,
        )

        self.assertTrue(
            standard.viable,
        )

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
            result.status,
            "standard"
        )

        self.assertTrue(
            result.viable
        )

        self.assertFalse(
            result.rare
        )

        self.assertIsNone(
            result.details
        )

    def test_result_is_object_state(self):
        genotype = (
            CatGenotype.create_founder(
                sex="male",
                autosomal_loci=(
                    self._autosomal()
                ),
            )
        )

        result = (
            KittenGeneticViabilityResolver
            .resolve(genotype)
        )

        self.assertIsInstance(
            result,
            KittenGeneticViabilityResult,
        )

        self.assertIs(
            result.genotype,
            genotype,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = result[
                "status"
            ]

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
            viability.status,
            "rare_valid"
        )

        self.assertTrue(
            viability.viable
        )

        self.assertTrue(
            viability.rare
        )

        self.assertIsInstance(
            viability.details,
            KittenXXYGenotypeDetails,
        )

        self.assertEqual(
            viability.details.sex_chromosomes,
            (
                "X",
                "X",
                "Y",
            ),
        )

        self.assertIn(
            "xxy_male",
            viability.special_traits
        )

        self.assertEqual(
            phenotype.profile.color,
            "tortoiseshell"
        )

        self.assertEqual(
            phenotype.profile.sex,
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
            viability.status,
            "rare_valid"
        )

        self.assertEqual(
            phenotype.profile.color,
            "calico"
        )

        self.assertEqual(
            phenotype.profile.pattern,
            "tricolor"
        )

        self.assertEqual(
            phenotype.profile.sex,
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
            result.status,
            "nonviable"
        )

        self.assertFalse(
            result.viable
        )

        self.assertEqual(
            result.reason,
            "lethal_genetic_combination"
        )

        self.assertIsInstance(
            result.details,
            KittenLethalMutationDetails,
        )

        self.assertEqual(
            result.details.lethal_mutations,
            (
                "embryonic_lethal",
            ),
        )

        with self.assertRaises(TypeError):
            _ = result.details[
                "lethal_mutations"
            ]

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertEqual(
            result.details.lethal_mutations,
            (
                "embryonic_lethal",
            ),
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

        genotype.orange_locus = (
            "O",
            "o"
        )

        result = (
            KittenGeneticViabilityResolver
            .resolve(genotype)
        )

        self.assertEqual(
            result.status,
            "nonviable"
        )

        self.assertFalse(
            result.viable
        )

        self.assertEqual(
            result.reason,
            "invalid_genotype"
        )

        self.assertIsInstance(
            result.details,
            KittenInvalidGenotypeDetails,
        )

        self.assertTrue(
            result.details.error
        )


if __name__ == "__main__":
    unittest.main()