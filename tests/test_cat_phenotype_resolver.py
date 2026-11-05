import unittest
from dataclasses import FrozenInstanceError

from cats.genotype import (
    CatAutosomalGenotype,
    CatGenotype,
)
from cats.cat_birth_objects import (
    CatBirthProfile,
    CatPhenotypeResult,
)
from cats.phenotype_resolver import (
    CatDilutionRule,
    CatPhenotypeResolver,
)


class CatPhenotypeResolverTests(
    unittest.TestCase
):

    @staticmethod
    def _genotype(
        sex="female",
        orange_locus=None,
        black=("B", "B"),
        dilution=("D", "D"),
        agouti=("a", "a"),
        white_spotting=("s", "s"),
        colorpoint=("C", "C"),
        longhair=("L", "L")
    ):
        return CatGenotype.create_founder(
            sex=sex,
            orange_locus=orange_locus,
            autosomal_loci=(
                CatAutosomalGenotype(
                    black=black,
                    dilution=dilution,
                    agouti=agouti,
                    white_spotting=(
                        white_spotting
                    ),
                    colorpoint=colorpoint,
                    longhair=longhair,
                )
            )
        )

    def test_black_shorthaired_female(self):
        genotype = self._genotype(
            sex="female",
            orange_locus=("o", "o")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertIsInstance(
            result,
            CatPhenotypeResult,
        )

        self.assertIsInstance(
            result.profile,
            CatBirthProfile,
        )

        self.assertEqual(
            result.profile.color,
            "black",
        )

        self.assertEqual(
            result.profile.fur_length,
            "short",
        )

        self.assertEqual(
            result.profile.pattern,
            "solid",
        )

        self.assertEqual(
            result.profile.eye_color,
            "green",
        )

        self.assertEqual(
            result.profile.sex,
            "female",
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
                "profile"
            ]

    def test_dilution_rules_are_immutable_objects(self):
        rules = CatPhenotypeResolver.DILUTION_RULES

        self.assertIsInstance(rules, tuple)

        self.assertEqual(
            tuple(
                (rule.base_color, rule.diluted_color)
                for rule in rules
            ),
            (
                ("black", "blue"),
                ("chocolate", "lilac"),
                ("cinnamon", "fawn"),
                ("orange", "cream"),
                (
                    "tortoiseshell",
                    "blue_tortoiseshell",
                ),
            ),
        )

        for rule in rules:
            self.assertIsInstance(
                rule,
                CatDilutionRule,
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
                _ = rule["base_color"]

        with self.assertRaises(FrozenInstanceError):
            rules[0].diluted_color = "changed"

    def test_dilution_rule_validation(self):
        with self.assertRaises(TypeError):
            CatDilutionRule(
                "",
                "blue",
            )

        with self.assertRaises(TypeError):
            CatDilutionRule(
                "black",
                "",
            )

        with self.assertRaises(TypeError):
            CatDilutionRule(
                "black",
                None,
            )

        with self.assertRaises(TypeError):
            CatDilutionRule(
                123,
                "blue",
            )

    def test_typed_dilution_preserves_phenotypes(self):
        resolver = CatPhenotypeResolver

        for rule in resolver.DILUTION_RULES:
            with self.subTest(color=rule.base_color):
                self.assertEqual(
                    resolver._diluted_color(
                        rule.base_color
                    ),
                    rule.diluted_color,
                )

        self.assertEqual(
            resolver._diluted_color("unknown"),
            "unknown",
        )

        orange = self._genotype(
            sex="male",
            orange_locus=("O",),
        )

        diluted_orange = self._genotype(
            sex="male",
            orange_locus=("O",),
            dilution=("d", "d"),
        )

        self.assertEqual(
            resolver.resolve(orange).profile.color,
            "orange",
        )

        self.assertEqual(
            resolver.resolve(
                diluted_orange
            ).profile.color,
            "cream",
        )

        diluted_tortoiseshell = self._genotype(
            sex="female",
            orange_locus=("O", "o"),
            dilution=("d", "d"),
        )

        self.assertEqual(
            resolver.resolve(
                diluted_tortoiseshell
            ).profile.color,
            "blue_tortoiseshell",
        )

    def test_dilute_black_cat_is_blue(self):
        genotype = self._genotype(
            sex="male",
            orange_locus=("o",),
            dilution=("d", "d")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            result.profile.color,
            "blue"
        )

        self.assertTrue(
            result.diluted
        )

    def test_chocolate_and_cinnamon_are_resolved(self):
        chocolate = (
            CatPhenotypeResolver.resolve(
                self._genotype(
                    black=("b", "bl")
                )
            )
        )

        cinnamon = (
            CatPhenotypeResolver.resolve(
                self._genotype(
                    black=("bl", "bl")
                )
            )
        )

        self.assertEqual(
            chocolate.profile.color,
            "chocolate"
        )

        self.assertEqual(
            cinnamon.profile.color,
            "cinnamon"
        )

    def test_dilution_creates_lilac_and_fawn(self):
        lilac = (
            CatPhenotypeResolver.resolve(
                self._genotype(
                    black=("b", "b"),
                    dilution=("d", "d")
                )
            )
        )

        fawn = (
            CatPhenotypeResolver.resolve(
                self._genotype(
                    black=("bl", "bl"),
                    dilution=("d", "d")
                )
            )
        )

        self.assertEqual(
            lilac.profile.color,
            "lilac"
        )

        self.assertEqual(
            fawn.profile.color,
            "fawn"
        )

    def test_orange_male_is_tabby(self):
        genotype = self._genotype(
            sex="male",
            orange_locus=("O",),
            agouti=("a", "a")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            result.profile.color,
            "orange"
        )

        self.assertEqual(
            result.profile.pattern,
            "tabby"
        )

    def test_tortoiseshell_female(self):
        genotype = self._genotype(
            sex="female",
            orange_locus=("O", "o")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            result.profile.color,
            "tortoiseshell"
        )

    def test_dilute_tortoiseshell_female(self):
        genotype = self._genotype(
            sex="female",
            orange_locus=("O", "o"),
            dilution=("d", "d")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            result.profile.color,
            "blue_tortoiseshell"
        )

    def test_tortoiseshell_with_white_is_calico(self):
        genotype = self._genotype(
            sex="female",
            orange_locus=("O", "o"),
            white_spotting=("S", "s")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            result.profile.color,
            "calico"
        )

        self.assertEqual(
            result.profile.pattern,
            "tricolor"
        )

    def test_agouti_cat_is_tabby(self):
        genotype = self._genotype(
            agouti=("A", "a")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            result.profile.pattern,
            "tabby"
        )

    def test_recessive_longhair_is_long(self):
        genotype = self._genotype(
            longhair=("l", "l")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertEqual(
            result.profile.fur_length,
            "long"
        )

    def test_colorpoint_profile(self):
        genotype = self._genotype(
            colorpoint=("cs", "cs")
        )

        result = (
            CatPhenotypeResolver.resolve(
                genotype
            )
        )

        self.assertTrue(
            result.colorpoint
        )

        self.assertEqual(
            result.profile.pattern,
            "pointed"
        )

        self.assertEqual(
            result.profile.eye_color,
            "blue"
        )


if __name__ == "__main__":
    unittest.main()