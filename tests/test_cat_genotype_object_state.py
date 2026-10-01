import unittest

from cats.genotype import (
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
