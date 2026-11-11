from copy import deepcopy
from dataclasses import replace

from .history_attempt_state import (
    HistoryAttempt,
    HistoryAttemptStatus,
)
from .history_attempt_journal import (
    SQLiteHistoryAttemptJournal,
)

from core.actualization import PotentialBlueprint
from core.actualization.cycle_state import (
    ActualizationCycleState,
)
from core.actualization.potential_state import (
    PotentialState,
)


class HistoryRecord:

    def __init__(
        self,
        cycle_id,
        events,
        potentials,
        branch_id="root",
        parent_branch_id=None,
        created_by=None
    ):
        self.cycle_id = cycle_id
        self.branch_id = branch_id
        self.parent_branch_id = parent_branch_id
        self.created_by = created_by
        self.events = list(events)
        self._recorded_events = deepcopy(
            self.events
        )

        self.actualized = [
            potential.public_state
            for potential in potentials
            if potential.state is PotentialState.ACTUALIZED
        ]

        self.unrealized = [
            potential.public_state
            for potential in potentials
            if potential.state is PotentialState.UNREALIZED
        ]

        self.potential_blueprints = [
            PotentialBlueprint.from_potential(
                potential
            )
            for potential in potentials
        ]

    @property
    def public_state(self):
        return {
            "cycle_id": self.cycle_id,
            "branch_id": self.branch_id,
            "parent_branch_id": self.parent_branch_id,
            "created_by": self.created_by,
            "events": deepcopy(self._recorded_events),
            "actualized": deepcopy(
                self.actualized
            ),
            "unrealized": deepcopy(
                self.unrealized
            ),
            "potential_blueprints": [
                blueprint.public_state
                for blueprint
                in self.potential_blueprints
            ]
        }


class History:

    def __init__(self, journal_path=None):
        self.records = []
        self._cycle_attempts = []
        self._journal = (
            SQLiteHistoryAttemptJournal(journal_path)
            if journal_path is not None
            else None
        )

    @property
    def unresolved_attempts(self):
        if self._journal is not None:
            return self._journal.unresolved_attempts()

        return tuple(self._cycle_attempts)

    def find_attempt(self, cycle_id, branch_id="root"):
        if self._journal is not None:
            return self._journal.find_attempt(
                cycle_id=cycle_id,
                branch_id=branch_id,
            )

        for attempt in self._cycle_attempts:
            if (
                attempt.cycle_id == cycle_id
                and attempt.branch_id == branch_id
            ):
                return attempt

        return None

    def begin_attempt(self, cycle_id, branch_id="root"):
        if self.find_record(
            cycle_id=cycle_id,
            branch_id=branch_id,
        ) is not None:
            raise ValueError(
                "Cycle is already recorded "
                "in this history branch."
            )

        if self._journal is not None:
            return self._journal.begin_attempt(
                cycle_id=cycle_id,
                branch_id=branch_id,
            )

        if self.find_attempt(
            cycle_id=cycle_id,
            branch_id=branch_id,
        ) is not None:
            raise RuntimeError(
                "Cycle attempt is in doubt or still running; "
                "manual reconciliation required."
            )

        attempt = HistoryAttempt(
            cycle_id=cycle_id,
            branch_id=branch_id,
            status=HistoryAttemptStatus.RUNNING,
        )

        self._cycle_attempts.append(attempt)

        return attempt

    def mark_attempt_in_doubt(self, attempt):
        if self._journal is not None:
            return self._journal.mark_attempt_in_doubt(
                attempt
            )

        for index, current in enumerate(
            self._cycle_attempts
        ):
            if current is attempt:
                updated = replace(
                    current,
                    status=HistoryAttemptStatus.IN_DOUBT,
                )
                self._cycle_attempts[index] = updated
                return updated

        raise RuntimeError(
            "Unknown history attempt."
        )

    def complete_attempt(self, attempt):
        if self.find_record(
            cycle_id=attempt.cycle_id,
            branch_id=attempt.branch_id,
        ) is None:
            raise RuntimeError(
                "Cannot complete an unrecorded attempt."
            )

        if self._journal is not None:
            return self._journal.complete_attempt(
                attempt
            )

        for index, current in enumerate(
            self._cycle_attempts
        ):
            if current is attempt:
                self._cycle_attempts.pop(index)
                return

        raise RuntimeError(
            "Unknown history attempt."
        )

    def record_cycle(
        self,
        cycle,
        events,
        branch_id="root",
        parent_branch_id=None,
        created_by=None
    ):
        if (
            cycle.state
            is not ActualizationCycleState.RESOLVED
        ):
            raise ValueError(
                "Only a resolved cycle "
                "can become history."
            )

        if any(
            record.cycle_id == cycle.cycle_id
            and record.branch_id == branch_id
            for record in self.records
        ):
            raise ValueError(
                "Cycle is already recorded "
                "in this history branch."
            )

        record = HistoryRecord(
            cycle_id=cycle.cycle_id,
            events=events,
            potentials=cycle.potentials,
            branch_id=branch_id,
            parent_branch_id=parent_branch_id,
            created_by=created_by
        )

        self.records.append(
            record
        )

        return record

    def find_record(
        self,
        cycle_id,
        branch_id="root"
    ):
        for record in self.records:
            if (
                record.cycle_id == cycle_id
                and record.branch_id == branch_id
            ):
                return record

        return None

    @property
    def latest(self):
        if not self.records:
            return None

        return self.records[-1]

    @property
    def public_state(self):
        return {
            "record_count": len(
                self.records
            ),
            "records": [
                record.public_state
                for record in self.records
            ]
        }
