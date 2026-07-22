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

        return record
