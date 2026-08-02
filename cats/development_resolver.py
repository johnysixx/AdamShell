class CatDevelopmentResolver:

    SEXUAL_MATURITY_DAY = 180
    ADULTHOOD_DAY = 365

    STAGES = (
        (0, "newborn"),
        (14, "socializing_kitten"),
        (49, "playful_kitten"),
        (98, "juvenile"),
        (180, "adolescent"),
        (365, "adult")
    )

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def initialize_newborn(
        self,
        cat,
        birth_day=None
    ):
        reproduction = cat[
            "reproduction"
        ]

        cat["age_days"] = 0
        cat["birth_day"] = birth_day
        cat["developmental_stage"] = (
            "newborn"
        )

        reproduction[
            "developmental_stage"
        ] = "newborn"

        reproduction[
            "reproductive_maturity"
        ] = False

        reproduction["fertile"] = False

        event = {
            "name": (
                "newborn_cat_development_initialized"
            ),
            "cat": cat["name"],
            "age_days": 0,
            "stage": "newborn",
            "fertile": False,
            "birth_day": birth_day
        }

        self.history.append(
            event
        )

        return event

    def advance_age(
        self,
        cat,
        days=1
    ):
        days = int(days)

        if days < 1:
            raise ValueError(
                "Cat age must advance by at "
                "least one day."
            )

        previous_age = int(
            cat.get(
                "age_days",
                0
            )
        )

        previous_stage = cat.get(
            "developmental_stage",
            self.stage_for_age(
                previous_age
            )
        )

        new_age = previous_age + days
        new_stage = self.stage_for_age(
            new_age
        )

        cat["age_days"] = new_age
        cat["developmental_stage"] = (
            new_stage
        )

        reproduction = cat[
            "reproduction"
        ]

        reproduction[
            "developmental_stage"
        ] = new_stage

        sexually_mature = (
            new_age
            >= self.SEXUAL_MATURITY_DAY
        )

        reproduction[
            "reproductive_maturity"
        ] = sexually_mature

        if reproduction.get(
            "neutered",
            False
        ):
            reproduction["fertile"] = False

        else:
            reproduction["fertile"] = (
                sexually_mature
            )

        transitions = self._collect_transitions(
            previous_age=previous_age,
            new_age=new_age
        )

        event = {
            "name": "cat_age_advanced",
            "cat": cat["name"],
            "days_advanced": days,
            "previous_age_days": (
                previous_age
            ),
            "age_days": new_age,
            "previous_stage": (
                previous_stage
            ),
            "stage": new_stage,
            "stage_changed": (
                previous_stage != new_stage
            ),
            "transitions": transitions,
            "reproductive_maturity": (
                sexually_mature
            ),
            "fertile": reproduction[
                "fertile"
            ]
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

    @classmethod
    def stage_for_age(
        cls,
        age_days
    ):
        age_days = int(age_days)

        if age_days < 0:
            raise ValueError(
                "Cat age cannot be negative."
            )

        stage = "newborn"

        for minimum_age, candidate in (
            cls.STAGES
        ):
            if age_days >= minimum_age:
                stage = candidate
            else:
                break

        return stage

    @classmethod
    def _collect_transitions(
        cls,
        previous_age,
        new_age
    ):
        return [
            {
                "day": minimum_age,
                "stage": stage
            }
            for minimum_age, stage
            in cls.STAGES
            if (
                previous_age
                < minimum_age
                <= new_age
            )
        ]