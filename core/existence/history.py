from core.actualization import PotentialBlueprint


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

        self.actualized = [
            potential.public_state
            for potential in potentials
            if potential.state == "actualized"
        ]

        self.unrealized = [
            potential.public_state
            for potential in potentials
            if potential.state == "unrealized"
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
            "events": list(self.events),
            "actualized": list(
                self.actualized
            ),
            "unrealized": list(
                self.unrealized
            ),
            "potential_blueprints": [
                blueprint.public_state
                for blueprint
                in self.potential_blueprints
            ]
        }


class History:

    def __init__(self):
        self.records = []

    def record_cycle(
        self,
        cycle,
        events,
        branch_id="root",
        parent_branch_id=None,
        created_by=None
    ):
        if cycle.state != "resolved":
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
