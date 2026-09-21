import unittest

from cats.genotype import (
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
            kitten.inheritance_record.autosomal_loci[
                "black"
            ],
            CatParentalContribution,
        )

    def test_legacy_mapping_genotype_is_rejected(self):
        legacy = self.mother.to_dict()

        with self.assertRaises(TypeError):
            CatGenotype.validate(legacy)

        with self.assertRaises(TypeError):
            CatPhenotypeResolver.resolve(legacy)

        result = KittenGeneticViabilityResolver.resolve(
            legacy
        )
        self.assertFalse(result["viable"])
        self.assertEqual(
            result["reason"],
            "invalid_genotype",
        )

    def test_to_dict_is_detached_snapshot(self):
        snapshot = self.mother.to_dict()
        snapshot["sex"] = "male"
        snapshot["autosomal_loci"]["black"] = (
            "b",
            "b",
        )
        snapshot["lethal_mutations"].append(
            "test_mutation"
        )

        self.assertEqual(
            self.mother.sex,
            "female",
        )
        self.assertEqual(
            self.mother.autosomal_loci["black"],
            ("B", "B"),
        )
        self.assertEqual(
            self.mother.lethal_mutations,
            (),
        )


if __name__ == "__main__":
    unittest.main()
