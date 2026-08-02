import random

from cats.kitten_embryo_resolver import KittenEmbryoResolver
from cats.reproduction import CatReproduction


class CatMatingResolver:

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

        self.embryo_resolver = (
            KittenEmbryoResolver(
                universe
            )
        )

    def mate(
        self,
        female,
        male,
        current_day=0,
        gestation_days=None,
        embryo_count=None,
        rng=None
    ):
        self._validate_pair(
            female,
            male
        )

        reproduction = female[
            "reproduction"
        ]

        rng = rng or random

        embryo_count = (
            int(
                rng.randint(
                    1,
                    6
                )
            )
            if embryo_count is None
            else int(embryo_count)
        )

        if embryo_count < 1:
            raise ValueError(
                "Embryo count must be "
                "at least one."
            )

        gestation_days = (
            CatReproduction
            .GESTATION_DAYS_DEFAULT
            if gestation_days is None
            else int(gestation_days)
        )

        if not (
            CatReproduction.GESTATION_DAYS_MIN
            <= gestation_days
            <= CatReproduction.GESTATION_DAYS_MAX
        ):
            raise ValueError(
                "Gestation days must be between "
                f"{CatReproduction.GESTATION_DAYS_MIN} "
                "and "
                f"{CatReproduction.GESTATION_DAYS_MAX}."
            )

        current_day = int(
            current_day
        )

        embryo_results = [
            self.embryo_resolver
            .create_embryo(
                mother=female,
                father=male,
                rng=rng
            )
            for _ in range(
                embryo_count
            )
        ]

        viable_embryos = [
            result["embryo"]
            for result in embryo_results
            if result["viable"]
        ]

        nonviable_results = [
            result
            for result in embryo_results
            if not result["viable"]
        ]

        contact = {
            "name": "cat_mating_contact",
            "female": female["name"],
            "male": male["name"],
            "successful": True,
            "day": current_day
        }

        reproduction.update({
            "pregnant": True,
            "pregnancy_day": 0,
            "gestation_days": gestation_days,
            "expected_birth_day": (
                current_day
                + gestation_days
            ),
            "mother_name": female[
                "name"
            ],
            "father_name": male[
                "name"
            ],
            "mating_contact": contact,
            "embryos": viable_embryos
        })

        event = {
            "name": "cat_pregnancy_started",
            "mother": female["name"],
            "father": male["name"],
            "contact": contact,
            "gestation_days": gestation_days,
            "pregnancy_day": 0,
            "started_on_day": current_day,
            "expected_birth_day": (
                current_day
                + gestation_days
            ),
            "embryos_attempted": (
                embryo_count
            ),
            "viable_embryo_count": len(
                viable_embryos
            ),
            "nonviable_embryo_count": len(
                nonviable_results
            ),
            "embryo_results": (
                embryo_results
            ),
            "started": True
        }

        self.history.append(
            event
        )

        if hasattr(
            self.universe,
            "quantum_events"
        ):
            self.universe.quantum_events.append(
                event
            )

        return event

    def advance_pregnancy(
        self,
        female,
        days=1
    ):
        reproduction = female.get(
            "reproduction",
            {}
        )

        if not reproduction.get(
            "pregnant",
            False
        ):
            return {
                "name": (
                    "cat_pregnancy_advance_failed"
                ),
                "reason": "cat_is_not_pregnant",
                "advanced": False
            }

        days = int(
            days
        )

        if days < 1:
            raise ValueError(
                "Pregnancy advance must be "
                "at least one day."
            )

        reproduction[
            "pregnancy_day"
        ] += days

        ready_for_birth = (
            reproduction[
                "pregnancy_day"
            ]
            >= reproduction[
                "gestation_days"
            ]
        )

        event = {
            "name": "cat_pregnancy_advanced",
            "mother": female["name"],
            "days_advanced": days,
            "pregnancy_day": reproduction[
                "pregnancy_day"
            ],
            "gestation_days": reproduction[
                "gestation_days"
            ],
            "ready_for_birth": (
                ready_for_birth
            ),
            "advanced": True
        }

        self.history.append(
            event
        )

        return event

    @staticmethod
    def _validate_pair(
        female,
        male
    ):
        if female is male:
            raise ValueError(
                "A cat cannot mate with itself."
            )

        if not (
            CatReproduction
            .can_become_pregnant(
                female
            )
        ):
            raise ValueError(
                "Female cat cannot become pregnant."
            )

        if not (
            CatReproduction
            .can_father_kittens(
                male
            )
        ):
            raise ValueError(
                "Male cat cannot father kittens."
            )