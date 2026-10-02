from dataclasses import dataclass, field

@dataclass(slots=True, frozen=True)
class PhysicalBiologyGateBlockedEvent:
    operation: str
    cat: str | None
    cronenberg_id: str
    name: str = field(
        default=(
            "premature_cat_biology_"
            "replaced_by_cronenberg"
        ),
        init=False,
    )
    physical_universe_started: bool = field(
        default=False,
        init=False,
    )
    allowed: bool = field(
        default=False,
        init=False,
    )
    cronenberg_created: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "operation",
            str(self.operation),
        )

        if self.cat is not None:
            object.__setattr__(
                self,
                "cat",
                str(self.cat),
            )

        object.__setattr__(
            self,
            "cronenberg_id",
            str(self.cronenberg_id),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "operation": self.operation,
            "cat": self.cat,
            "physical_universe_started": (
                self.physical_universe_started
            ),
            "allowed": self.allowed,
            "cronenberg_created": (
                self.cronenberg_created
            ),
            "cronenberg_id": self.cronenberg_id,
        }


@dataclass(slots=True, frozen=True)
class PhysicalBiologyGateResult:

    operation: str
    allowed: bool

    event: (
        PhysicalBiologyGateBlockedEvent
        | None
    ) = None

    cronenberg: object | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "operation",
            str(
                self.operation
            ),
        )

        object.__setattr__(
            self,
            "allowed",
            bool(
                self.allowed
            ),
        )

        if self.allowed:
            if self.event is not None:
                raise ValueError(
                    "Allowed biology gate result "
                    "cannot contain a blocked event."
                )

            if self.cronenberg is not None:
                raise ValueError(
                    "Allowed biology gate result "
                    "cannot contain a Cronenberg."
                )

            return

        if not isinstance(
            self.event,
            PhysicalBiologyGateBlockedEvent,
        ):
            raise TypeError(
                "Blocked biology gate result "
                "requires a blocked event."
            )

        if self.cronenberg is None:
            raise ValueError(
                "Blocked biology gate result "
                "requires a Cronenberg."
            )

        if (
            self.event.operation
            != self.operation
        ):
            raise ValueError(
                "Biology gate result operation "
                "must match blocked event."
            )

        cronenberg_id = getattr(
            self.cronenberg,
            "id",
            None,
        )

        if (
            cronenberg_id is None
            or str(cronenberg_id)
            != self.event.cronenberg_id
        ):
            raise ValueError(
                "Biology gate result Cronenberg "
                "must match blocked event."
            )

    def to_dict(self):
        if self.allowed:
            return {
                "allowed": True,
                "operation": self.operation,
                "cronenberg": None,
            }

        snapshot = (
            self.event.to_dict()
        )

        snapshot[
            "cronenberg"
        ] = self.cronenberg

        return snapshot


class PhysicalBiologyGate:

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def require_physical_world(
        self,
        operation,
        cat=None
    ):
        if getattr(
            self.universe,
            "physical_universe_started",
            False
        ):
            return PhysicalBiologyGateResult(
                operation=operation,
                allowed=True,
            )

        cat_name = getattr(
            cat,
            "name",
            None
        )

        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Biological cat process attempted "
                    "before the physical universe existed."
                ),
                source_component=(
                    "physical_biology_gate"
                ),
                source_operation=operation
            )
        )

        event = PhysicalBiologyGateBlockedEvent(
            operation=operation,
            cat=cat_name,
            cronenberg_id=cronenberg.id,
        )

        self.record_event(
            event
        )

        self.universe.quantum_events.append(
            event.to_dict()
        )

        return PhysicalBiologyGateResult(
            operation=operation,
            allowed=False,
            event=event,
            cronenberg=cronenberg,
        )

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            PhysicalBiologyGateBlockedEvent,
        ):
            raise TypeError(
                "Physical biology gate history "
                "requires a "
                "PhysicalBiologyGateBlockedEvent "
                "object."
            )

        self.history.append(
            event
        )

        return event
