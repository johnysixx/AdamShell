class CronenbergPopulationStatistics:

    def __init__(self, universe):
        self.name = "cronenberg_population_statistics"
        self.type = "population_statistics"
        self.universe = universe
        self.history = []
        self.pressure_transition_history = []

    def snapshot(self):
        cronenbergs = list(
            self.universe.cronenbergs
        )

        active = [
            cronenberg
            for cronenberg in cronenbergs
            if getattr(
                cronenberg,
                "active",
                True
            )
        ]

        inactive = [
            cronenberg
            for cronenberg in cronenbergs
            if not getattr(
                cronenberg,
                "active",
                True
            )
        ]

        active_pair_ids = {
            cronenberg.quantum_state.get(
                "pair_id"
            )
            for cronenberg in active
            if cronenberg.quantum_state.get(
                "pair_id"
            ) is not None
        }

        standalone = [
            cronenberg
            for cronenberg in active
            if cronenberg.quantum_state.get(
                "pair_id"
            ) is None
        ]

        merged = [
            cronenberg
            for cronenberg in cronenbergs
            if cronenberg.state
            == "born_from_quantum_merge"
        ]

        recombined = [
            cronenberg
            for cronenberg in cronenbergs
            if cronenberg.state
            == "born_from_quantum_pair_consumption"
        ]

        total_active_size = sum(
            float(cronenberg.size)
            for cronenberg in active
        )

        total_active_energy = sum(
            float(cronenberg.energy)
            for cronenberg in active
        )

        population_pressure = (
            len(active)
            + len(active_pair_ids)
            + total_active_energy
        )

        return {
            "name": self.name,
            "type": self.type,
            "total_count": len(
                cronenbergs
            ),
            "active_count": len(
                active
            ),
            "inactive_count": len(
                inactive
            ),
            "standalone_active_count": len(
                standalone
            ),
            "active_quantum_pair_count": len(
                active_pair_ids
            ),
            "merged_count": len(
                merged
            ),
            "recombined_count": len(
                recombined
            ),
            "total_active_size": (
                total_active_size
            ),
            "total_active_energy": (
                total_active_energy
            ),
            "population_pressure": (
                population_pressure
            ),
            "population_pressure_level": (
                self.classify_pressure(
                    population_pressure
                )
            )
        }

    def classify_pressure(
        self,
        pressure=None
    ):
        if pressure is None:
            pressure = self.snapshot()[
                "population_pressure"
            ]

        pressure = float(pressure)

        if pressure < 5.0:
            return "low"

        if pressure < 10.0:
            return "elevated"

        if pressure < 20.0:
            return "high"

        return "critical"

    def record_snapshot(self):
        current = self.snapshot()

        previous_snapshot = None

        if self.history:
            previous_snapshot = self.history[-1][
                "snapshot"
            ]

        delta_fields = (
            "total_count",
            "active_count",
            "inactive_count",
            "merged_count",
            "recombined_count",
            "total_active_size",
            "total_active_energy",
            "population_pressure"
        )

        delta = {}

        for field in delta_fields:
            delta_name = f"{field}_delta"

            if previous_snapshot is None:
                delta[delta_name] = (
                    0.0
                    if field.startswith("total_active_")
                    else 0
                )
            else:
                delta[delta_name] = (
                    current[field]
                    - previous_snapshot[field]
                )

        record = {
            "tick": getattr(
                self.universe,
                "universe_tick",
                0
            ),
            "snapshot": current,
            "delta": delta
        }

        self.history.append(
            record
        )

        if previous_snapshot is not None:
            previous_level = previous_snapshot[
                "population_pressure_level"
            ]

            current_level = current[
                "population_pressure_level"
            ]

            if previous_level != current_level:
                transition_event = {
                    "name": (
                        "cronenberg_population_"
                        "pressure_level_changed"
                    ),
                    "tick": record["tick"],
                    "previous_level": previous_level,
                    "current_level": current_level,
                    "previous_pressure": (
                        previous_snapshot[
                            "population_pressure"
                        ]
                    ),
                    "current_pressure": (
                        current[
                            "population_pressure"
                        ]
                    )
                }

                self.pressure_transition_history.append(
                    transition_event
                )

                record["pressure_transition"] = (
                    transition_event
                )
            else:
                record["pressure_transition"] = None
        else:
            record["pressure_transition"] = None

        return record

    @property
    def last_pressure_transition(self):
        if not self.pressure_transition_history:
            return None

        return self.pressure_transition_history[-1]

    @property
    def last_record(self):
        if not self.history:
            return None

        return self.history[-1]

    @property
    def public_state(self):
        return self.snapshot()