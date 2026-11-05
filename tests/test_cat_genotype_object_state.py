import unittest
from dataclasses import FrozenInstanceError, replace

from cats.genotype import (
    CatAutosomalAlleleRule,
    CatOrangeAlleleRule,
    CatAutosomalGenotype,
    CatAutosomalInheritanceRecord,
    CatGenotype,
    CatInheritanceRecord,
    CatParentalContribution,
)
from cats.phenotype_resolver import CatPhenotypeResolver
from cats.kitten_viability_resolver import (
    KittenGeneticViabilityResolver,
)


class FirstChoiceRng:

    def choice(self, values):
        return list(values)[0]


class CatGenotypeObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.mother = CatGenotype.create_founder(
            sex="female",
            orange_locus=("O", "o"),
        )
        self.father = CatGenotype.create_founder(
            sex="male",
            orange_locus=("o",),
        )

    def test_autosomal_rules_are_immutable_objects(self):
        rules = CatGenotype.AUTOSOMAL_RULES

        self.assertIsInstance(rules, tuple)
        self.assertEqual(len(rules), 6)

        self.assertEqual(
            tuple(rule.locus for rule in rules),
            (
                "black",
                "dilution",
                "agouti",
                "white_spotting",
                "colorpoint",
                "longhair",
            ),
        )

        expected = (
            frozenset({"B", "b", "bl"}),
            frozenset({"D", "d"}),
            frozenset({"A", "a"}),
            frozenset({"S", "s"}),
            frozenset({"C", "cb", "cs", "c"}),
            frozenset({"L", "l"}),
        )

        self.assertEqual(
            tuple(rule.allowed_alleles for rule in rules),
            expected,
        )

        for rule in rules:
            self.assertIsInstance(
                rule,
                CatAutosomalAlleleRule,
            )

            self.assertIsInstance(
                rule.allowed_alleles,
                frozenset,
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
                _ = rule["locus"]

        with self.assertRaises(FrozenInstanceError):
            rules[0].locus = "changed"

        self.assertFalse(
            hasattr(rules[0].allowed_alleles, "add")
        )

    def test_autosomal_rule_rejects_invalid_values(self):
        with self.assertRaises(TypeError):
            CatAutosomalAlleleRule(
                "",
                frozenset({"B"}),
            )

        with self.assertRaises(TypeError):
            CatAutosomalAlleleRule(
                "black",
                {"B"},
            )

        with self.assertRaises(ValueError):
            CatAutosomalAlleleRule(
                "black",
                frozenset(),
            )

        with self.assertRaises(TypeError):
            CatAutosomalAlleleRule(
                "black",
                frozenset({42}),
            )

        with self.assertRaises(TypeError):
            CatAutosomalAlleleRule(
                "black",
                frozenset({""}),
            )

    def test_autosomal_rules_preserve_genotype_validation(self):
        valid_loci = CatAutosomalGenotype(
            black=("bl", "b"),
            dilution=("d", "d"),
            agouti=("A", "a"),
            white_spotting=("S", "s"),
            colorpoint=("cb", "cs"),
            longhair=("l", "l"),
        )

        valid = CatGenotype.create_founder(
            sex="female",
            orange_locus=("O", "o"),
            autosomal_loci=valid_loci,
        )

        self.assertTrue(
            CatGenotype.validate(valid)
        )

        self.assertIs(
            valid.autosomal_loci,
            valid_loci,
        )

        for rule in CatGenotype.AUTOSOMAL_RULES:
            invalid_loci = replace(
                self.mother.autosomal_loci,
                **{
                    rule.locus: (
                        "INVALID",
                        "INVALID",
                    ),
                },
            )

            invalid = replace(
                self.mother,
                autosomal_loci=invalid_loci,
            )

            with self.assertRaisesRegex(
                ValueError,
                "Unsupported allele at " + rule.locus,
            ):
                CatGenotype.validate(invalid)

        self.assertTrue(
            CatGenotype.validate(self.mother)
        )

    def test_orange_allele_rule_is_immutable_object(self):
        rule = CatGenotype.ORANGE_RULE

        self.assertIsInstance(
            rule,
            CatOrangeAlleleRule,
        )

        self.assertEqual(
            rule.allowed_alleles,
            frozenset({"O", "o"}),
        )

        self.assertIsInstance(
            rule.allowed_alleles,
            frozenset,
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
            _ = rule["allowed_alleles"]

        with self.assertRaises(FrozenInstanceError):
            rule.allowed_alleles = frozenset({"X"})

        self.assertFalse(
            hasattr(rule.allowed_alleles, "add")
        )

    def test_orange_allele_rule_rejects_invalid_values(self):
        with self.assertRaises(TypeError):
            CatOrangeAlleleRule({"O", "o"})

        with self.assertRaises(ValueError):
            CatOrangeAlleleRule(frozenset())

        with self.assertRaises(TypeError):
            CatOrangeAlleleRule(frozenset({42}))

        with self.assertRaises(TypeError):
            CatOrangeAlleleRule(frozenset({""}))

    def test_orange_allele_rule_preserves_inheritance(self):
        self.assertTrue(
            CatGenotype.validate(self.mother)
        )

        self.assertTrue(
            CatGenotype.validate(self.father)
        )

        daughter = CatGenotype.inherit(
            self.mother,
            self.father,
            rng=FirstChoiceRng(),
        )

        self.assertEqual(
            daughter.sex,
            "female",
        )

        self.assertEqual(
            daughter.orange_locus,
            ("O", "o"),
        )

        self.assertTrue(
            CatGenotype.validate(daughter)
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported orange allele",
        ):
            CatGenotype.create_founder(
                sex="female",
                orange_locus=("O", "X"),
            )

        invalid_male = replace(
            self.father,
            orange_locus=("X",),
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported orange allele",
        ):
            CatGenotype.validate(invalid_male)

        self.assertTrue(
            CatGenotype.validate(self.father)
        )

    def test_founder_is_cat_genotype_object(self):
        self.assertIsInstance(
            self.mother,
            CatGenotype,
        )
        self.assertEqual(
            self.mother.sex,
            "female",
        )
        self.assertEqual(
            self.mother.origin,
            "founder",
        )
        self.assertIsInstance(
            self.mother.autosomal_loci,
            CatAutosomalGenotype,
        )

    def test_autosomal_genotype_has_no_mapping_api(self):
        autosomal = self.mother.autosomal_loci

        for name in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
        ):
            self.assertFalse(
                hasattr(
                    autosomal,
                    name,
                ),
                name,
            )

        self.assertEqual(
            autosomal.black,
            ("B", "B"),
        )

        with self.assertRaises(TypeError):
            _ = autosomal[
                "black"
            ]

    def test_mapping_autosomal_genotype_is_rejected(self):
        with self.assertRaises(TypeError):
            CatGenotype.create_founder(
                sex="female",
                autosomal_loci={
                    "black": ("B", "B"),
                },
            )

    def test_inheritance_record_is_object_state(self):
        kitten = CatGenotype.inherit(
            self.mother,
            self.father,
            rng=FirstChoiceRng(),
        )

        self.assertIsInstance(
            kitten.inheritance_record,
            CatInheritanceRecord,
        )
        self.assertIsInstance(
            kitten.inheritance_record.orange_locus,
            CatParentalContribution,
        )
        self.assertIsInstance(
            kitten.inheritance_record.autosomal_loci,
            CatAutosomalInheritanceRecord,
        )
        self.assertIsInstance(
            kitten.inheritance_record.autosomal_loci.black,
            CatParentalContribution,
        )

    def test_autosomal_inheritance_has_no_mapping_api(self):
        kitten = CatGenotype.inherit(
            self.mother,
            self.father,
            rng=FirstChoiceRng(),
        )

        autosomal = (
            kitten.inheritance_record
            .autosomal_loci
        )

        for name in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
        ):
            self.assertFalse(
                hasattr(
                    autosomal,
                    name,
                ),
                name,
            )

        with self.assertRaises(TypeError):
            _ = autosomal[
                "black"
            ]

    def test_legacy_mapping_genotype_is_rejected(self):
        legacy = {
            "sex": "female",
            "sex_chromosomes": (
                "X",
                "X",
            ),
            "orange_locus": (
                "O",
                "o",
            ),
            "autosomal_loci": {
                "black": (
                    "B",
                    "B",
                ),
            },
            "lethal_mutations": (),
            "origin": "founder",
        }

        with self.assertRaises(TypeError):
            CatGenotype.validate(legacy)

        with self.assertRaises(TypeError):
            CatPhenotypeResolver.resolve(legacy)

        result = KittenGeneticViabilityResolver.resolve(
            legacy
        )
        self.assertFalse(result.viable)
        self.assertEqual(
            result.reason,
            "invalid_genotype",
        )

    def test_genetics_domain_objects_have_no_serialization_api(self):
        kitten = CatGenotype.inherit(
            self.mother,
            self.father,
            rng=FirstChoiceRng(),
        )

        domain_objects = (
            self.mother,
            self.mother.autosomal_loci,
            kitten.inheritance_record,
            kitten.inheritance_record.sex_chromosomes,
            kitten.inheritance_record.orange_locus,
            kitten.inheritance_record.autosomal_loci,
            kitten.inheritance_record.autosomal_loci.black,
        )

        for domain_object in domain_objects:
            self.assertFalse(
                hasattr(
                    domain_object,
                    "to_dict",
                ),
                type(domain_object).__name__,
            )


if __name__ == "__main__":
    unittest.main()
