import unittest

from cats.genotype import CatGenotype
from cats.phenotype_resolver import (
    CatPhenotypeResolver
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
            autosomal_loci={
                "black": black,
                "dilution": dilution,
                "agouti": agouti,
                "white_spotting": (
                    white_spotting
                ),
                "colorpoint": colorpoint,
                "longhair": longhair
            }
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

        self.assertEqual(
            result["profile"],
            {
                "color": "black",
                "fur_length": "short",
                "pattern": "solid",
                "eye_color": "green",
                "sex": "female"
            }
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
            result["profile"]["color"],
            "blue"
        )

        self.assertTrue(
            result["diluted"]
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
            chocolate["profile"]["color"],
            "chocolate"
        )

        self.assertEqual(
            cinnamon["profile"]["color"],
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
            lilac["profile"]["color"],
            "lilac"
        )

        self.assertEqual(
            fawn["profile"]["color"],
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
            result["profile"]["color"],
            "orange"
        )

        self.assertEqual(
            result["profile"]["pattern"],
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
            result["profile"]["color"],
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
            result["profile"]["color"],
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
            result["profile"]["color"],
            "calico"
        )

        self.assertEqual(
            result["profile"]["pattern"],
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
            result["profile"]["pattern"],
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
            result["profile"]["fur_length"],
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
            result["colorpoint"]
        )

        self.assertEqual(
            result["profile"]["pattern"],
            "pointed"
        )

        self.assertEqual(
            result["profile"]["eye_color"],
            "blue"
        )


if __name__ == "__main__":
    unittest.main()