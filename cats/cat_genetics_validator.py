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
        genetics=None
    ):
        genetics = dict(
            genetics or {}
        )

        sex = profile.get("sex")

        karyotype = genetics.get(
            "karyotype"
        )

        if karyotype is None:
            karyotype = (
                "XX"
                if sex == "female"
                else "XY"
            )

        genetics["karyotype"] = (
            karyotype
        )

        color_requires_mosaic = (
            profile.get("color")
            in self.TORTOISESHELL_COLORS
        )

        pattern_requires_mosaic = (
            profile.get("pattern")
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
            return {
                "valid": True,
                "status": "standard_genetics",
                "reason": None,
                "genetics": genetics,
                "conflicting_trait": None,
                "reroll_die": None
            }

        if karyotype in {
            "XX",
            "XXY"
        }:
            return {
                "valid": True,
                "status": (
                    "rare_genetic_exception"
                    if sex == "male"
                    else "standard_genetics"
                ),
                "reason": (
                    "male_multicolor_requires_extra_x"
                    if sex == "male"
                    else None
                ),
                "genetics": genetics,
                "conflicting_trait": None,
                "reroll_die": None
            }

        if (
            sex == "male"
            and karyotype == "XY"
        ):
            return {
                "valid": False,
                "status": (
                    "impossible_for_declared_genotype"
                ),
                "reason": (
                    "xy_male_cannot_form_standard_"
                    "orange_nonorange_x_mosaic"
                ),
                "genetics": genetics,
                "conflicting_trait": (
                    conflicting_trait
                ),
                "reroll_die": reroll_die
            }

        return {
            "valid": False,
            "status": "unsupported_genetic_model",
            "reason": (
                "multicolor_profile_requires_"
                "compatible_x_chromosome_model"
            ),
            "genetics": genetics,
            "conflicting_trait": (
                conflicting_trait
            ),
            "reroll_die": reroll_die
        }