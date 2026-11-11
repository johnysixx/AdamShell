from core.actualization import (
    ActualizationCycle,
    Actualizer,
)


class ExistenceCycleRunner:

    def __init__(
        self,
        reality,
        history,
        actualizer=None
    ):
        self.reality = reality
        self.history = history
        self.actualizer = (
            actualizer
            if actualizer is not None
            else Actualizer()
        )

    def run(
        self,
        cycle_id
    ):
        # Reject duplicate cycles before generating potentials
        # or executing any actualization actions.
        if self.history.find_record(
            cycle_id=cycle_id,
        ) is not None:
            raise ValueError(
                "Cycle is already recorded "
                "in this history branch."
            )

        # Reserve before collecting or executing potentials.
        # An exception leaves the attempt in doubt.
        attempt = self.history.begin_attempt(
            cycle_id=cycle_id,
        )

        try:
            cycle = ActualizationCycle(
                cycle_id=cycle_id
            )

            potentials = (
                self.reality.collect_potentials(
                    cycle_id=cycle_id
                )
            )

            cycle.add_potentials(
                potentials
            )

            events = cycle.resolve(
                actualizer=self.actualizer
            )

            record = self.history.record_cycle(
                cycle=cycle,
                events=events
            )

        except BaseException:
            self.history.mark_attempt_in_doubt(attempt)
            raise

        self.history.complete_attempt(attempt)
        return record
