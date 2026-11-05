from dataclasses import dataclass

from cats.genotype import CatGenotype
from cats.cat_birth_objects import (
    CatBirthProfile,
    CatPhenotypeResult,
)


@dataclass(frozen=True, slots=True)
class CatDilutionRule:
    base_color: str
    diluted_color: str

    def __post_init__(self):
        for field_name in (
            "base_color",
            "diluted_color",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise TypeError(
                    "Cat dilution rule requires "
                    "nonempty color names."
                )


class CatPhenotypeResolver:

    DILUTION_RULES = (
        CatDilutionRule("black", "blue"),
        CatDilutionRule("chocolate", "lilac"),
        CatDilutionRule("cinnamon", "fawn"),
        CatDilutionRule("orange", "cream"),
        CatDilutionRule(
            "tortoiseshell",
            "blue_tortoiseshell",
        ),
    )

    @classmethod
    def resolve(
        cls,
        genotype
    ):
        CatGenotype.validate(
            genotype
        )

        sex = genotype.sex

        orange_alleles = tuple(
            genotype.orange_locus
        )

        loci = genotype.autosomal_loci

        base_color = (
            cls._resolve_base_color(
                sex=sex,
                orange_alleles=(
                    orange_alleles
                ),
                black_alleles=tuple(
                    loci.black
                )
            )
        )

        diluted = cls._is_homozygous(
            loci.dilution,
            "d"
        )

        color = (
            cls._diluted_color(base_color)
            if diluted
            else base_color
        )

        white_spotted = (
            "S"
            in loci.white_spotting
        )

        pattern = (
            cls._resolve_pattern(
                color=color,
                agouti_alleles=tuple(
                    loci.agouti
                ),
                colorpoint_alleles=tuple(
                    loci.colorpoint
                ),
                white_spotted=(
                    white_spotted
                )
            )
        )

        if (
            color
            in {
                "tortoiseshell",
                "blue_tortoiseshell"
            }
            and white_spotted
        ):
            color = "calico"
            pattern = "tricolor"

        elif white_spotted:
            pattern = "bicolor"

        fur_length = (
            "long"
            if cls._is_homozygous(
                loci.longhair,
                "l"
            )
            else "short"
        )

        colorpoint = (
            cls._is_colorpoint(
                loci.colorpoint
            )
        )

        eye_color = (
            "blue"
            if colorpoint
            else "green"
        )

        profile = CatBirthProfile(
            color=color,
            fur_length=fur_length,
            pattern=pattern,
            eye_color=eye_color,
            sex=sex,
        )

        return CatPhenotypeResult(
            profile=profile,
            base_color=base_color,
            diluted=diluted,
            white_spotted=(
                white_spotted
            ),
            colorpoint=colorpoint,
            genotype=genotype,
        )

    @classmethod
    def _diluted_color(
        cls,
        base_color,
    ):
        for rule in cls.DILUTION_RULES:
            if rule.base_color == base_color:
                return rule.diluted_color

        return base_color

    @classmethod
    def _resolve_base_color(
        cls,
        sex,
        orange_alleles,
        black_alleles
    ):
        if sex == "female":
            orange_count = (
                orange_alleles.count("O")
            )

            if orange_count == 2:
                return "orange"

            if orange_count == 1:
                return "tortoiseshell"

        elif sex == "male":
            orange_count = (
                orange_alleles.count("O")
            )

            if len(
                orange_alleles
            ) == 2:
                if orange_count == 2:
                    return "orange"

                if orange_count == 1:
                    return "tortoiseshell"

            elif orange_alleles == (
                "O",
            ):
                return "orange"

        return cls._resolve_eumelanin(
            black_alleles
        )

    @staticmethod
    def _resolve_eumelanin(
        alleles
    ):
        alleles = tuple(
            alleles
        )

        if "B" in alleles:
            return "black"

        if "b" in alleles:
            return "chocolate"

        return "cinnamon"

    @classmethod
    def _resolve_pattern(
        cls,
        color,
        agouti_alleles,
        colorpoint_alleles,
        white_spotted
    ):
        if cls._is_colorpoint(
            colorpoint_alleles
        ):
            return "pointed"

        if color in {
            "orange",
            "cream"
        }:
            return "tabby"

        if "A" in agouti_alleles:
            return "tabby"

        return "solid"

    @staticmethod
    def _is_homozygous(
        alleles,
        allele
    ):
        return tuple(
            alleles
        ) == (
            allele,
            allele
        )

    @staticmethod
    def _is_colorpoint(
        alleles
    ):
        alleles = tuple(
            alleles
        )

        return (
            "C" not in alleles
            and alleles
            in {
                ("cs", "cs"),
                ("cs", "c"),
                ("c", "cs")
            }
        )