from .cat_birth_objects import (
    CatBirthProfile,
    CatGeneticsValidation,
)
from .cat_genetics_validation_status import (
    CatGeneticsValidationStatus,
)


class CatGeneticsValidator:

    TORTOISESHELL_COLORS = {
        "tortoiseshell",
        "blue_tortoiseshell",
        "calico"
    }

    MULTICOLOR_PATTERNS = {
        "tricolor"
    }

    def validate(
        self,
        profile,
        karyotype=None
    ):
        if not isinstance(profile, CatBirthProfile):
            raise TypeError(
                "profile must be a CatBirthProfile object."
            )

        sex = profile.sex

        if karyotype is None:
            karyotype = (
                "XX"
                if sex == "female"
                else "XY"
            )

        if not isinstance(karyotype, str):
            raise TypeError(
                "karyotype must be a string."
            )

        color_requires_mosaic = (
            profile.color
            in self.TORTOISESHELL_COLORS
        )

        pattern_requires_mosaic = (
            profile.pattern
            in self.MULTICOLOR_PATTERNS
        )

        requires_two_x_color_mosaic = (
            color_requires_mosaic
            or pattern_requires_mosaic
        )

        if color_requires_mosaic:
            conflicting_trait = "color"
            reroll_die = "d12"

        elif pattern_requires_mosaic:
            conflicting_trait = "pattern"
            reroll_die = "d8"

        else:
            conflicting_trait = None
            reroll_die = None

        if not requires_two_x_color_mosaic:
            return CatGeneticsValidation(
                valid=True,
                status=(
                    CatGeneticsValidationStatus
                    .STANDARD_GENETICS
                ),
                reason=None,
                karyotype=karyotype,
            )

        if karyotype in {
            "XX",
            "XXY"
        }:
            return CatGeneticsValidation(
                valid=True,
                status=(
                    CatGeneticsValidationStatus
                    .RARE_GENETIC_EXCEPTION
                    if sex == "male"
                    else (
                        CatGeneticsValidationStatus
                        .STANDARD_GENETICS
                    )
                ),
                reason=(
                    "male_multicolor_requires_extra_x"
                    if sex == "male"
                    else None
                ),
                karyotype=karyotype,
            )

        if (
            sex == "male"
            and karyotype == "XY"
        ):
            return CatGeneticsValidation(
                valid=False,
                status=(
                    CatGeneticsValidationStatus
                    .IMPOSSIBLE_FOR_DECLARED_GENOTYPE
                ),
                reason=(
                    "xy_male_cannot_form_standard_"
                    "orange_nonorange_x_mosaic"
                ),
                karyotype=karyotype,
                conflicting_trait=conflicting_trait,
                reroll_die=reroll_die,
            )

        return CatGeneticsValidation(
            valid=False,
            status=(
                CatGeneticsValidationStatus
                .UNSUPPORTED_GENETIC_MODEL
            ),
            reason=(
                "multicolor_profile_requires_"
                "compatible_x_chromosome_model"
            ),
            karyotype=karyotype,
            conflicting_trait=conflicting_trait,
            reroll_die=reroll_die,
        )
