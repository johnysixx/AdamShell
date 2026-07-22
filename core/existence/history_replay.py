from core.actualization import (
    ActualizationCycle,
)


class HistoryReplay:

    def __init__(
        self,
        history
    ):
        self.history = history

    def reopen_cycle(
        self,
        cycle_id,
        source_branch_id="root"
    ):
        record = self.history.find_record(
            cycle_id=cycle_id,
            branch_id=source_branch_id
        )

        if record is None:
            raise ValueError(
                "Historical cycle was not found."
            )

        cycle = ActualizationCycle(
            cycle_id=record.cycle_id
        )

        potentials = [
            blueprint.create_potential(
                cycle_id=record.cycle_id
            )
            for blueprint
            in record.potential_blueprints
        ]

        cycle.add_potentials(
            potentials
        )

        return cycle
