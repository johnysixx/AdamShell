from universe.logger import UniverseLogger


class CatEstrousCycleResolver:

    DEFAULT_ESTRUS_DAYS = 7
    DEFAULT_INTERESTRUS_DAYS = 8

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def tick_day(
        self,
        cat,
        day=None
    ):
        reproduction = cat.get(
            "reproduction",
            {}
        )

        if not self._can_cycle(
            cat
        ):
            return self._set_inactive(
                cat=cat,
                reason=self._inactive_reason(
                    cat
                ),
                day=day
            )

        phase = reproduction.get(
            "estrous_phase",
            "inactive"
        )

        if phase == "inactive":
            return self._start_estrus(
                cat=cat,
                day=day
            )

        reproduction[
            "estrous_cycle_day"
        ] = int(
            reproduction.get(
                "estrous_cycle_day",
                0
            )
        ) + 1

        if phase == "estrus":
            duration = int(
                reproduction.get(
                    "estrus_duration_days",
                    self.DEFAULT_ESTRUS_DAYS
                )
            )

            if (
                reproduction[
                    "estrous_cycle_day"
                ]
                >= duration
            ):
                return self._start_interestrus(
                    cat=cat,
                    day=day
                )

        elif phase == "interestrus":
            duration = int(
                reproduction.get(
                    "interestrus_duration_days",
                    self.DEFAULT_INTERESTRUS_DAYS
                )
            )

            if (
                reproduction[
                    "estrous_cycle_day"
                ]
                >= duration
            ):
                return self._start_estrus(
                    cat=cat,
                    day=day
                )

        event = {
            "name": (
                "cat_estrous_cycle_advanced"
            ),
            "cat": cat["name"],
            "day": day,
            "phase": phase,
            "cycle_day": reproduction[
                "estrous_cycle_day"
            ],
            "estrus_active": reproduction[
                "estrus_active"
            ],
            "phase_changed": False
        }

        self.history.append(
            event
        )

        return event

    def activate_estrus(
        self,
        cat,
        day=None
    ):
        if not self._can_cycle(
            cat
        ):
            return self._set_inactive(
                cat=cat,
                reason=self._inactive_reason(
                    cat
                ),
                day=day
            )

        return self._start_estrus(
            cat=cat,
            day=day
        )

    def end_estrus_after_ovulation(
        self,
        cat,
        day=None
    ):
        reproduction = cat[
            "reproduction"
        ]

        reproduction[
            "estrous_phase"
        ] = "diestrus"

        reproduction[
            "estrus_active"
        ] = False

        reproduction[
            "estrous_cycle_day"
        ] = 0

        event = {
            "name": (
                "cat_estrus_ended_after_ovulation"
            ),
            "cat": cat["name"],
            "day": day,
            "phase": "diestrus",
            "estrus_active": False,
            "phase_changed": True
        }

        self.history.append(
            event
        )

        return event

    def _start_estrus(
        self,
        cat,
        day=None
    ):
        reproduction = cat[
            "reproduction"
        ]

        reproduction[
            "estrous_phase"
        ] = "estrus"

        reproduction[
            "estrus_active"
        ] = True

        reproduction[
            "estrous_cycle_day"
        ] = 0

        event = {
            "name": "cat_estrus_started",
            "cat": cat["name"],
            "day": day,
            "phase": "estrus",
            "cycle_day": 0,
            "estrus_active": True,
            "phase_changed": True
        }

        self.history.append(
            event
        )

        UniverseLogger.event(
            f"CAT ESTRUS STARTED: {cat['name']}"
        )

        return event

    def _start_interestrus(
        self,
        cat,
        day=None
    ):
        reproduction = cat[
            "reproduction"
        ]

        reproduction[
            "estrous_phase"
        ] = "interestrus"

        reproduction[
            "estrus_active"
        ] = False

        reproduction[
            "estrous_cycle_day"
        ] = 0

        reproduction[
            "mating_window_open"
        ] = False

        reproduction[
            "mating_contacts"
        ] = []

        reproduction[
            "potential_fathers"
        ] = []

        reproduction[
            "estrous_cycles_completed"
        ] = int(
            reproduction.get(
                "estrous_cycles_completed",
                0
            )
        ) + 1

        event = {
            "name": (
                "cat_interestrus_started"
            ),
            "cat": cat["name"],
            "day": day,
            "phase": "interestrus",
            "cycle_day": 0,
            "estrus_active": False,
            "phase_changed": True
        }

        self.history.append(
            event
        )

        return event

    def _set_inactive(
        self,
        cat,
        reason,
        day=None
    ):
        reproduction = cat.get(
            "reproduction",
            {}
        )

        reproduction[
            "estrous_phase"
        ] = "inactive"

        reproduction[
            "estrus_active"
        ] = False

        reproduction[
            "estrous_cycle_day"
        ] = 0

        event = {
            "name": (
                "cat_estrous_cycle_inactive"
            ),
            "cat": cat.get("name"),
            "day": day,
            "phase": "inactive",
            "estrus_active": False,
            "reason": reason,
            "phase_changed": False
        }

        self.history.append(
            event
        )

        return event

    @staticmethod
    def _can_cycle(
        cat
    ):
        reproduction = cat.get(
            "reproduction",
            {}
        )

        return (
            cat.get("sex") == "female"
            and not reproduction.get(
                "neutered",
                True
            )
            and reproduction.get(
                "fertile",
                False
            )
            and not reproduction.get(
                "pregnant",
                False
            )
        )

    @staticmethod
    def _inactive_reason(
        cat
    ):
        reproduction = cat.get(
            "reproduction",
            {}
        )

        if cat.get("sex") != "female":
            return "not_female"

        if reproduction.get(
            "neutered",
            True
        ):
            return "neutered"

        if reproduction.get(
            "pregnant",
            False
        ):
            return "pregnant"

        if not reproduction.get(
            "fertile",
            False
        ):
            return "not_reproductively_mature"

        return "cycle_unavailable"