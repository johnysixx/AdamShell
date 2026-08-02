import random

from cats.reproduction import CatReproduction
from cats.kitten_embryo_resolver import (
    KittenEmbryoResolver
)
from cats.paternity_resolver import (
    MultipleSirePaternityResolver
)


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

        self.paternity_resolver = (
            MultipleSirePaternityResolver()
        )

    def mate(
        self,
        female,
        male,
        current_day=0
    ):
        self._validate_pair(
            female,
            male
        )

        reproduction = female[
            "reproduction"
        ]

        current_day = int(
            current_day
        )

        if reproduction.get(
            "pregnant",
            False
        ):
            raise ValueError(
                "A pregnant cat cannot add "
                "another potential father."
            )

        if not reproduction.get(
            "mating_window_open",
            False
        ):
            reproduction.update({
                "estrus_active": True,
                "mating_window_open": True,
                "mating_window_started_day": (
                    current_day
                ),
                "mating_contacts": [],
                "potential_fathers": []
            })

        contact_number = (
            len(
                reproduction[
                    "mating_contacts"
                ]
            )
            + 1
        )

        contact = {
            "name": "cat_mating_contact",
            "contact_number": contact_number,
            "female": female["name"],
            "male": male["name"],
            "male_name": male["name"],
            "successful": True,
            "day": current_day,

            # Interní reference pro genetiku embryí.
            "_male_ref": male
        }

        reproduction[
            "mating_contacts"
        ].append(
            contact
        )

        if (
            male["name"]
            not in reproduction[
                "potential_fathers"
            ]
        ):
            reproduction[
                "potential_fathers"
            ].append(
                male["name"]
            )

        event = {
            "name": (
                "cat_mating_contact_recorded"
            ),
            "female": female["name"],
            "male": male["name"],
            "day": current_day,
            "contact_number": contact_number,
            "mating_window_open": True,
            "potential_fathers": list(
                reproduction[
                    "potential_fathers"
                ]
            ),
            "pregnancy_started": False
        }

        self.history.append(
            event
        )

        return event

    def close_mating_window(
        self,
        female,
        current_day=0,
        gestation_days=None,
        embryo_count=None,
        rng=None
    ):
        reproduction = female.get(
            "reproduction",
            {}
        )

        if reproduction.get(
            "pregnant",
            False
        ):
            raise ValueError(
                "Cat is already pregnant."
            )

        if not reproduction.get(
            "mating_window_open",
            False
        ):
            raise ValueError(
                "Cat has no open mating window."
            )

        contacts = reproduction.get(
            "mating_contacts",
            []
        )

        if not contacts:
            raise ValueError(
                "Ovulation requires at least "
                "one successful mating contact."
            )

        rng = rng or random

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

        embryo_results = []
        paternity_results = []

        for _ in range(
            embryo_count
        ):
            paternity = (
                self.paternity_resolver
                .select_father(
                    mating_contacts=contacts,
                    rng=rng
                )
            )

            father = paternity[
                "father"
            ]

            embryo_result = (
                self.embryo_resolver
                .create_embryo(
                    mother=female,
                    father=father,
                    rng=rng
                )
            )

            embryo_results.append(
                embryo_result
            )

            paternity_results.append({
                "embryo_id": (
                    embryo_result[
                        "embryo"
                    ]["id"]
                    if embryo_result[
                        "embryo"
                    ] is not None
                    else embryo_result[
                        "event"
                    ][
                        "embryo_id"
                    ]
                ),
                "father": father["name"],
                "selection": paternity[
                    "event"
                ]
            })

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

        current_day = int(
            current_day
        )

        father_names = []

        for result in paternity_results:
            father_name = result[
                "father"
            ]

            if father_name not in father_names:
                father_names.append(
                    father_name
                )

        reproduction.update({
            "estrus_active": False,
            "mating_window_open": False,
            "pregnant": True,
            "pregnancy_day": 0,
            "gestation_days": gestation_days,
            "expected_birth_day": (
                current_day
                + gestation_days
            ),
            "mother_name": female["name"],
            "father_name": (
                father_names[0]
                if len(father_names) == 1
                else None
            ),
            "father_names": father_names,
            "embryos": viable_embryos
        })

        event = {
            "name": "cat_pregnancy_started",
            "mother": female["name"],
            "father_names": father_names,
            "multiple_sires": (
                len(father_names) > 1
            ),
            "mating_contact_count": len(
                contacts
            ),
            "paternity_results": (
                paternity_results
            ),
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