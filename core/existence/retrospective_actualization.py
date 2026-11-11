from core.actualization import (
    DirectedActualizer,
)

from .history_replay import HistoryReplay


class RetrospectiveActualization:

    def __init__(
        self,
        history
    ):
        self.history = history
        self.replay = HistoryReplay(
            history=history
        )

    def create_branch(
        self,
        cycle_id,
        source_branch_id,
        new_branch_id,
        selected_names,
        created_by=None
    ):
        if (
            source_branch_id
            == new_branch_id
        ):
            raise ValueError(
                "A new history branch must "
                "have a different identifier."
            )

        # Reject an existing target branch before replaying
        # any potential actions.
        if self.history.find_record(
            cycle_id=cycle_id,
            branch_id=new_branch_id,
        ) is not None:
            raise ValueError(
                "Cycle is already recorded "
                "in this history branch."
            )

        cycle = self.replay.reopen_cycle(
            cycle_id=cycle_id,
            source_branch_id=source_branch_id
        )

        actualizer = DirectedActualizer(
            selected_names=selected_names
        )

        # The target branch must be reserved before
        # any replayed action can execute.
        attempt = self.history.begin_attempt(
            cycle_id=cycle_id,
            branch_id=new_branch_id,
        )

        try:
            events = cycle.resolve(
                actualizer=actualizer
            )

            record = self.history.record_cycle(
                cycle=cycle,
                events=events,
                branch_id=new_branch_id,
                parent_branch_id=source_branch_id,
                created_by=created_by
            )

        except BaseException:
            self.history.mark_attempt_in_doubt(attempt)
            raise

        self.history.complete_attempt(attempt)
        return record
