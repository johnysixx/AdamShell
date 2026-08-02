class CatOvulationResolver:

    DEFAULT_THRESHOLD = 4

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def record_stimulation(
        self,
        female,
        male=None,
        amount=1,
        day=None
    ):
        reproduction = female[
            "reproduction"
        ]

        amount = int(amount)

        if amount < 1:
            raise ValueError(
                "Ovulation stimulation must "
                "increase by at least one."
            )

        current = int(
            reproduction.get(
                "ovulation_stimulation",
                0
            )
        )

        threshold = int(
            reproduction.get(
                "ovulation_threshold",
                self.DEFAULT_THRESHOLD
            )
        )

        new_value = current + amount

        reproduction[
            "ovulation_stimulation"
        ] = new_value

        event = {
            "name": (
                "cat_ovulation_stimulation_recorded"
            ),
            "female": female["name"],
            "male": (
                male.get("name")
                if isinstance(male, dict)
                else None
            ),
            "day": day,
            "amount": amount,
            "stimulation": new_value,
            "threshold": threshold,
            "threshold_reached": (
                new_value >= threshold
            )
        }

        self.history.append(
            event
        )

        return event

    def resolve(
        self,
        female,
        day=None
    ):
        reproduction = female[
            "reproduction"
        ]

        stimulation = int(
            reproduction.get(
                "ovulation_stimulation",
                0
            )
        )

        threshold = int(
            reproduction.get(
                "ovulation_threshold",
                self.DEFAULT_THRESHOLD
            )
        )

        induced = (
            stimulation >= threshold
        )

        reproduction[
            "ovulation_induced"
        ] = induced

        if induced:
            reproduction[
                "last_ovulation_day"
            ] = day

        event = {
            "name": (
                "cat_induced_ovulation_resolved"
            ),
            "female": female["name"],
            "day": day,
            "stimulation": stimulation,
            "threshold": threshold,
            "ovulation_induced": induced,
            "reason": (
                None
                if induced
                else "insufficient_stimulation"
            )
        }

        self.history.append(
            event
        )

        return event

    def reset(
        self,
        female
    ):
        reproduction = female[
            "reproduction"
        ]

        reproduction[
            "ovulation_stimulation"
        ] = 0

        reproduction[
            "ovulation_induced"
        ] = False