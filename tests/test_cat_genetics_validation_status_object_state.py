import unittest

from cats.cat_birth_objects import (
    CatBirthProfile,
    CatGeneticsValidation,
)
from cats.cat_genetics_validation_status import (
    CatGeneticsValidationStatus,
)
from cats.cat_genetics_validator import (
    CatGeneticsValidator,
)


class CatGeneticsValidationStatusObjectStateTests(
    unittest.TestCase
):

    @staticmethod
    def _profile(
        *,
        color="white",
        pattern="solid",
        sex="female",
    ):
        return CatBirthProfile(
            color=color,
            fur_length="short",
            pattern=pattern,
            eye_color="green",
            sex=sex,
        )

    def test_standard_genetics_uses_enum(self):
        result = CatGeneticsValidator().validate(
            self._profile()
        )

        self.assertIs(
            result.status,
            (
                CatGeneticsValidationStatus
                .STANDARD_GENETICS
            ),
        )

        self.assertEqual(
            result.status.value,
            "standard_genetics",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

    def test_rare_genetic_exception_uses_enum(self):
        result = CatGeneticsValidator().validate(
            self._profile(
                color="tortoiseshell",
                sex="male",
            ),
            karyotype="XXY",
        )

        self.assertIs(
            result.status,
            (
                CatGeneticsValidationStatus
                .RARE_GENETIC_EXCEPTION
            ),
        )

        self.assertTrue(
            result.valid
        )

    def test_impossible_genotype_uses_enum(self):
        result = CatGeneticsValidator().validate(
            self._profile(
                color="tortoiseshell",
                sex="male",
            ),
            karyotype="XY",
        )

        self.assertIs(
            result.status,
            (
                CatGeneticsValidationStatus
                .IMPOSSIBLE_FOR_DECLARED_GENOTYPE
            ),
        )

        self.assertFalse(
            result.valid
        )

    def test_unsupported_model_uses_enum(self):
        result = CatGeneticsValidator().validate(
            self._profile(
                color="tortoiseshell",
                sex="female",
            ),
            karyotype="XO",
        )

        self.assertIs(
            result.status,
            (
                CatGeneticsValidationStatus
                .UNSUPPORTED_GENETIC_MODEL
            ),
        )

        self.assertFalse(
            result.valid
        )

    def test_string_status_is_rejected(self):
        with self.assertRaises(TypeError):
            CatGeneticsValidation(
                valid=True,
                status="standard_genetics",
                reason=None,
                karyotype="XX",
            )

    def test_status_domain_is_finite(self):
        self.assertEqual(
            {
                status.value
                for status
                in CatGeneticsValidationStatus
            },
            {
                "standard_genetics",
                "rare_genetic_exception",
                "impossible_for_declared_genotype",
                "unsupported_genetic_model",
            },
        )


if __name__ == "__main__":
    unittest.main()
