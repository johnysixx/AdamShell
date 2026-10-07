from dataclasses import replace

from cats.cat_overpopulation_activation_state import (
    CatOverpopulationActivatedEvent,
    CatOverpopulationActivationDeniedResult,
)
from universe.cronenberg_population_statistics_state import (
    CronenbergPopulationCriticalResponse,
    CronenbergPopulationDelta,
    CronenbergPopulationPressureTransitionEvent,
    CronenbergPopulationPressureWarningEvent,
    CronenbergPopulationRecord,
    CronenbergPopulationSnapshot,
)


class CronenbergPopulationStatistics:

    def __init__(
        self,
        universe,
    ):
        self.name = (
            "cronenberg_population_statistics"
        )

        self.type = (
            "population_statistics"
        )

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
            for cronenberg
            in cronenbergs
            if getattr(
                cronenberg,
                "active",
                True,
            )
        ]

        inactive = [
            cronenberg
            for cronenberg
            in cronenbergs
            if not getattr(
                cronenberg,
                "active",
                True,
            )
        ]

        active_pair_ids = {
            cronenberg.quantum_state.pair_id
            for cronenberg
            in active
            if (
                cronenberg
                .quantum_state
                .pair_id
                is not None
            )
        }

        standalone = [
            cronenberg
            for cronenberg
            in active
            if (
                cronenberg
                .quantum_state
                .pair_id
                is None
            )
        ]

        merged = [
            cronenberg
            for cronenberg
            in cronenbergs
            if (
                cronenberg.state
                == "born_from_quantum_merge"
            )
        ]

        recombined = [
            cronenberg
            for cronenberg
            in cronenbergs
            if (
                cronenberg.state
                == (
                    "born_from_quantum_"
                    "pair_consumption"
                )
            )
        ]

        total_active_size = sum(
            float(
                cronenberg.size
            )
            for cronenberg
            in active
        )

        total_active_energy = sum(
            float(
                cronenberg.energy
            )
            for cronenberg
            in active
        )

        population_pressure = (
            len(active)
            + len(active_pair_ids)
            + total_active_energy
        )

        return (
            CronenbergPopulationSnapshot(
                total_count=len(
                    cronenbergs
                ),
                active_count=len(
                    active
                ),
                inactive_count=len(
                    inactive
                ),
                standalone_active_count=len(
                    standalone
                ),
                active_quantum_pair_count=len(
                    active_pair_ids
                ),
                merged_count=len(
                    merged
                ),
                recombined_count=len(
                    recombined
                ),
                total_active_size=
                    total_active_size,
                total_active_energy=
                    total_active_energy,
                population_pressure=
                    population_pressure,
                population_pressure_level=
                    self.classify_pressure(
                        population_pressure
                    ),
            )
        )

    def classify_pressure(
        self,
        pressure=None,
    ):
        if pressure is None:
            pressure = (
                self.snapshot()
                .population_pressure
            )

        pressure = float(
            pressure
        )

        if pressure < 5.0:
            return "low"

        if pressure < 10.0:
            return "elevated"

        if pressure < 20.0:
            return "high"

        return "critical"

    def record_snapshot(self):
        current = self.snapshot()

        previous_snapshot = (
            self.history[-1].snapshot
            if self.history
            else None
        )

        if previous_snapshot is None:
            delta = (
                CronenbergPopulationDelta(
                    total_count_delta=0,
                    active_count_delta=0,
                    inactive_count_delta=0,
                    merged_count_delta=0,
                    recombined_count_delta=0,
                    total_active_size_delta=0.0,
                    total_active_energy_delta=0.0,
                    population_pressure_delta=0.0,
                )
            )

        else:
            delta = (
                CronenbergPopulationDelta(
                    total_count_delta=(
                        current.total_count
                        - previous_snapshot.total_count
                    ),
                    active_count_delta=(
                        current.active_count
                        - previous_snapshot.active_count
                    ),
                    inactive_count_delta=(
                        current.inactive_count
                        - previous_snapshot.inactive_count
                    ),
                    merged_count_delta=(
                        current.merged_count
                        - previous_snapshot.merged_count
                    ),
                    recombined_count_delta=(
                        current.recombined_count
                        - previous_snapshot.recombined_count
                    ),
                    total_active_size_delta=(
                        current.total_active_size
                        - previous_snapshot.total_active_size
                    ),
                    total_active_energy_delta=(
                        current.total_active_energy
                        - previous_snapshot.total_active_energy
                    ),
                    population_pressure_delta=(
                        current.population_pressure
                        - previous_snapshot.population_pressure
                    ),
                )
            )

        current_level = (
            current.population_pressure_level
        )

        if current_level == "critical":
            self.critical_pressure_streak += 1

        else:
            self.critical_pressure_streak = 0

        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None,
        )

        existing_cat_count = (
            len(
                cats_layer.cats
            )
            if cats_layer is not None
            else 0
        )

        critical_response = (
            CronenbergPopulationCriticalResponse(
                active=(
                    current_level
                    == "critical"
                ),
                critical_pressure_streak=
                    self.critical_pressure_streak,
                existing_cat_count=
                    existing_cat_count,
                activate_existing_cats_first=(
                    current_level
                    == "critical"
                    and existing_cat_count > 0
                ),
                overpopulation_reinforcement_allowed=(
                    current_level
                    == "critical"
                    and self.critical_pressure_streak
                    >= 3
                    and existing_cat_count == 0
                ),
            )
        )

        tick = int(
            getattr(
                self.universe,
                "universe_tick",
                0,
            )
        )

        transition_event = None
        warning_event = None

        if previous_snapshot is not None:
            previous_level = (
                previous_snapshot
                .population_pressure_level
            )

            if previous_level != current_level:
                transition_event = (
                    CronenbergPopulationPressureTransitionEvent(
                        tick=tick,
                        previous_level=
                            previous_level,
                        current_level=
                            current_level,
                        previous_pressure=(
                            previous_snapshot
                            .population_pressure
                        ),
                        current_pressure=(
                            current
                            .population_pressure
                        ),
                    )
                )

                self.pressure_transition_history.append(
                    replace(
                        transition_event
                    )
                )

                if current_level in {
                    "high",
                    "critical",
                }:
                    activated_cats = []

                    if (
                        current_level
                        == "critical"
                        and cats_layer
                        is not None
                    ):
                        for cat in list(
                            cats_layer.cats
                        ):
                            activation = (
                                cats_layer
                                .activate_for_cronenberg_overpopulation(
                                    cat,
                                    hunt_quota=10,
                                )
                            )

                            if isinstance(
                                activation,
                                CatOverpopulationActivatedEvent,
                            ):
                                activated_cats.append(
                                    activation.cat
                                )

                            elif not isinstance(
                                activation,
                                CatOverpopulationActivationDeniedResult,
                            ):
                                raise TypeError(
                                    "Cat overpopulation activation "
                                    "must return an object."
                                )

                    warning_event = (
                        CronenbergPopulationPressureWarningEvent(
                            tick=tick,
                            pressure=(
                                current
                                .population_pressure
                            ),
                            pressure_level=
                                current_level,
                            active_count=(
                                current
                                .active_count
                            ),
                            active_quantum_pair_count=(
                                current
                                .active_quantum_pair_count
                            ),
                            existing_cats_activated=len(
                                activated_cats
                            ),
                            activated_cat_names=tuple(
                                activated_cats
                            ),
                            cat_reinforcements_suggested=(
                                current_level
                                == "critical"
                                and not activated_cats
                            ),
                            cat_reinforcement_allowed=(
                                current_level
                                == "critical"
                                and self
                                .critical_pressure_streak
                                >= 3
                            ),
                        )
                    )

                    self.universe.quantum_events.append(
                        replace(
                            warning_event
                        )
                    )

        record = (
            CronenbergPopulationRecord(
                tick=tick,
                critical_pressure_streak=
                    self.critical_pressure_streak,
                snapshot=current,
                delta=delta,
                critical_response=
                    critical_response,
                pressure_transition=
                    transition_event,
                pressure_warning=
                    warning_event,
            )
        )

        self.history.append(
            replace(
                record
            )
        )

        return record

    @property
    def last_pressure_transition(self):
        if not self.pressure_transition_history:
            return None

        return (
            self.pressure_transition_history[
                -1
            ]
        )

    @property
    def last_record(self):
        if not self.history:
            return None

        return self.history[
            -1
        ]

    @property
    def public_state(self):
        return self.snapshot()
