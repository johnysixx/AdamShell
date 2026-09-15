from cats.cat import Cat
from cats.cat_reproduction_state import CatReproductionState


class CatReproduction:

    GESTATION_DAYS_DEFAULT = 65
    GESTATION_DAYS_MIN = 63
    GESTATION_DAYS_MAX = 66

    @classmethod
    def create_state(
        cls,
        sex,
        neutered=False
    ):
        return CatReproductionState(
            sex=sex,
            neutered=neutered,
        )

    @classmethod
    def can_mate(
        cls,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatReproduction requires Cat."
            )

        reproduction = cat.reproduction

        return (
            reproduction.fertile
            and not reproduction.neutered
        )

    @classmethod
    def can_become_pregnant(
        cls,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatReproduction requires Cat."
            )

        return (
            cat.sex == "female"
            and cls.can_mate(cat)
            and not cat.reproduction.pregnant
        )

    @classmethod
    def can_father_kittens(
        cls,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatReproduction requires Cat."
            )

        return (
            cat.sex == "male"
            and cls.can_mate(cat)
        )
