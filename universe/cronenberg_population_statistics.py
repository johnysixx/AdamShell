class CronenbergPopulationStatistics:

    def __init__(self, universe):
        self.name = "cronenberg_population_statistics"
        self.type = "population_statistics"
        self.universe = universe
        self.history = []
        self.pressure_transition_history = []
        self.critical_pressure_streak = 0

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

        current_level = current[
            "population_pressure_level"
        ]

        if current_level == "critical":
            self.critical_pressure_streak += 1
        else:
            self.critical_pressure_streak = 0

        record = {
            "tick": getattr(
                self.universe,
                "universe_tick",
                0
            ),
            "critical_pressure_streak": (
                self.critical_pressure_streak
            ),
            "snapshot": current,
            "delta": delta
        }

        self.history.append(
            record
        )

        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        existing_cat_count = (
            len(cats_layer.cats)
            if cats_layer is not None
            else 0
        )

        record["critical_response"] = {
            "active": (
                current_level == "critical"
            ),
            "critical_pressure_streak": (
                self.critical_pressure_streak
            ),
            "existing_cat_count": (
                existing_cat_count
            ),
            "activate_existing_cats_first": (
                current_level == "critical"
                and existing_cat_count > 0
            ),
            "overpopulation_reinforcement_allowed": (
                current_level == "critical"
                and self.critical_pressure_streak >= 3
                and existing_cat_count == 0
            ),
            "reinforcement_is_last_resort": True
        }

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

                if current_level in {
                    "high",
                    "critical"
                }:
                    activated_cats = []

                    if current_level == "critical":
                        cats_layer = getattr(
                            self.universe,
                            "cats_layer",
                            None
                        )

                        if cats_layer is not None:
                            for cat in list(
                                cats_layer.cats
                            ):
                                activation = (
                                    cats_layer
                                    .activate_for_cronenberg_overpopulation(
                                        cat,
                                        hunt_quota=10
                                    )
                                )

                                if activation.get(
                                    "activated",
                                    False
                                ):
                                    activated_cats.append(
                                        activation["cat"]
                                    )

                    warning_event = {
                        "name": (
                            "cronenberg_population_"
                            "pressure_warning"
                        ),
                        "tick": record["tick"],
                        "pressure": current[
                            "population_pressure"
                        ],
                        "pressure_level": (
                            current_level
                        ),
                        "active_count": current[
                            "active_count"
                        ],
                        "active_quantum_pair_count": (
                            current[
                                "active_quantum_pair_count"
                            ]
                        ),
                        "bar_assistance_requested": True,
                        "existing_cats_activated": (
                            len(activated_cats)
                        ),
                        "activated_cat_names": list(
                            activated_cats
                        ),
                        "cat_reinforcements_suggested": (
                            current_level == "critical"
                            and not activated_cats
                        ),
                        "cat_reinforcement_allowed": (
                            current_level == "critical"
                            and self.critical_pressure_streak >= 3
                        )
                    }

                    self.universe.quantum_events.append(
                        warning_event
                    )

                    record["pressure_warning"] = (
                        warning_event
                    )
                else:
                    record["pressure_warning"] = None
            else:
                record["pressure_transition"] = None
                record["pressure_warning"] = None
        else:
            record["pressure_transition"] = None
            record["pressure_warning"] = None

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