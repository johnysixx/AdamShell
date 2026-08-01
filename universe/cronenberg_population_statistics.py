class CronenbergPopulationStatistics:

    def __init__(self, universe):
        self.name = "cronenberg_population_statistics"
        self.type = "population_statistics"
        self.universe = universe
        self.history = []

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

        return record

    @property
    def last_record(self):
        if not self.history:
            return None

        return self.history[-1]

    @property
    def public_state(self):
        return self.snapshot()