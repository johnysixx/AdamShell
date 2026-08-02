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
        if sex not in {
            "female",
            "male"
        }:
            raise ValueError(
                "Cat reproductive sex must be "
                "female or male."
            )

        neutered = bool(
            neutered
        )

        return {
            "sex": sex,
            "neutered": neutered,
            "fertile": not neutered,
            "estrus_active": False,
            "mating_window_open": False,
            "mating_window_started_day": None,
            "mating_contacts": [],
            "potential_fathers": [],
            "pregnant": False,
            "pregnancy_day": None,
            "gestation_days": None,
            "expected_birth_day": None,
            "mother_name": None,
            "father_name": None,
            "mating_contact": None,
            "embryos": [],
            "litters_born": 0
        }

    @classmethod
    def can_mate(
        cls,
        cat
    ):
        reproduction = cat.get(
            "reproduction",
            {}
        )

        return (
            reproduction.get(
                "fertile",
                False
            )
            and not reproduction.get(
                "neutered",
                True
            )
        )

    @classmethod
    def can_become_pregnant(
        cls,
        cat
    ):
        reproduction = cat.get(
            "reproduction",
            {}
        )

        return (
            cat.get("sex") == "female"
            and cls.can_mate(cat)
            and not reproduction.get(
                "pregnant",
                False
            )
        )

    @classmethod
    def can_father_kittens(
        cls,
        cat
    ):
        return (
            cat.get("sex") == "male"
            and cls.can_mate(cat)
        )