import uuid
from dataclasses import dataclass, field

from core.entity.components.spatial import (
    SpatialVector3,
)
from core.entity.serpent_d20 import (
    SerpentResolvedConsequence,
)
from quantum.error_boundary import (
    QuantumErrorResult,
)
from universe.logger import UniverseLogger


@dataclass(slots=True, frozen=True)
class SerpentUnresolvedConsequence:

    consequence: str
    reason: str = "handler_not_implemented"

    def __post_init__(self):
        object.__setattr__(
            self,
            "consequence",
            str(self.consequence),
        )

        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

    def to_dict(self):
        return {
            "consequence": self.consequence,
            "reason": self.reason,
        }


@dataclass(slots=True, frozen=True)
class SerpentQuantumBoxResult:

    box_id: str
    position: SpatialVector3
    state: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "box_id",
            str(self.box_id),
        )

        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Serpent quantum-box result requires "
                "a SpatialVector3 position."
            )

        object.__setattr__(
            self,
            "state",
            str(self.state),
        )

    def to_dict(self):
        return {
            "box_id": self.box_id,
            "position": self.position.to_dict(),
            "state": self.state,
        }


@dataclass(slots=True, frozen=True)
class SerpentQuantumErrorResult:

    error_type: str
    error_message: str
    cronenberg_id: str | None

    def __post_init__(self):
        object.__setattr__(
            self,
            "error_type",
            str(self.error_type),
        )

        object.__setattr__(
            self,
            "error_message",
            str(self.error_message),
        )

        if self.cronenberg_id is not None:
            object.__setattr__(
                self,
                "cronenberg_id",
                str(self.cronenberg_id),
            )

    def to_dict(self):
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "cronenberg_id": self.cronenberg_id,
        }


@dataclass(slots=True, frozen=True)
class SerpentCatManifestationResult:

    cat_name: str
    entity_name: str
    origin: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat_name",
            str(self.cat_name),
        )
        object.__setattr__(
            self,
            "entity_name",
            str(self.entity_name),
        )
        object.__setattr__(
            self,
            "origin",
            str(self.origin),
        )

    def to_dict(self):
        return {
            "cat_name": self.cat_name,
            "entity_name": self.entity_name,
            "origin": self.origin,
        }


@dataclass(slots=True, frozen=True)
class SerpentQuantumGeometryState:

    configuration_id: str | None
    configuration_seed: int | None
    reconfiguration_count: int

    def __post_init__(self):
        if self.configuration_id is not None:
            object.__setattr__(
                self,
                "configuration_id",
                str(self.configuration_id),
            )

        if self.configuration_seed is not None:
            object.__setattr__(
                self,
                "configuration_seed",
                int(self.configuration_seed),
            )

        object.__setattr__(
            self,
            "reconfiguration_count",
            int(self.reconfiguration_count),
        )

    def to_dict(self):
        return {
            "configuration_id": (
                self.configuration_id
            ),
            "configuration_seed": (
                self.configuration_seed
            ),
            "reconfiguration_count": (
                self.reconfiguration_count
            ),
        }


@dataclass(slots=True, frozen=True)
class SerpentQuantumGeometryShiftResult:

    before: SerpentQuantumGeometryState
    after: SerpentQuantumGeometryState
    cause: str

    def __post_init__(self):
        for field_name in (
            "before",
            "after",
        ):
            if not isinstance(
                getattr(self, field_name),
                SerpentQuantumGeometryState,
            ):
                raise TypeError(
                    "Serpent quantum geometry result "
                    "requires geometry state objects."
                )

        object.__setattr__(
            self,
            "cause",
            str(self.cause),
        )

    def to_dict(self):
        return {
            "before": self.before.to_dict(),
            "after": self.after.to_dict(),
            "cause": self.cause,
        }


@dataclass(slots=True, frozen=True)
class SerpentCronenbergCounterpartResult:

    result: str
    counterpart_created: bool
    original_id: str | None = None
    counterpart_id: str | None = None
    pair_id: str | None = None
    original_spin: float | None = None
    counterpart_spin: float | None = None
    counterpart_location: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "result",
            str(self.result),
        )
        object.__setattr__(
            self,
            "counterpart_created",
            bool(self.counterpart_created),
        )

        for field_name in (
            "original_id",
            "counterpart_id",
            "pair_id",
            "counterpart_location",
        ):
            value = getattr(
                self,
                field_name,
            )
            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    str(value),
                )

        for field_name in (
            "original_spin",
            "counterpart_spin",
        ):
            value = getattr(
                self,
                field_name,
            )
            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    float(value),
                )

    def to_dict(self):
        return {
            "result": self.result,
            "counterpart_created": (
                self.counterpart_created
            ),
            "original_id": self.original_id,
            "counterpart_id": self.counterpart_id,
            "pair_id": self.pair_id,
            "original_spin": self.original_spin,
            "counterpart_spin": (
                self.counterpart_spin
            ),
            "counterpart_location": (
                self.counterpart_location
            ),
        }


@dataclass(slots=True, frozen=True)
class SerpentConsequencesExecutedEvent:

    roll_id: str
    planned_consequences: tuple[str, ...]
    resolved_consequences: tuple[
        SerpentResolvedConsequence,
        ...,
    ]
    unresolved_consequences: tuple[
        SerpentUnresolvedConsequence,
        ...,
    ]

    name: str = field(
        default="serpent_consequences_executed",
        init=False,
    )

    visibility: str = field(
        default="universe_only",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "roll_id",
            str(self.roll_id),
        )

        object.__setattr__(
            self,
            "planned_consequences",
            tuple(
                str(consequence)
                for consequence
                in self.planned_consequences
            ),
        )

        resolved = tuple(
            self.resolved_consequences
        )

        if not all(
            isinstance(
                consequence,
                SerpentResolvedConsequence,
            )
            for consequence
            in resolved
        ):
            raise TypeError(
                "Resolved serpent consequences "
                "require "
                "SerpentResolvedConsequence objects."
            )

        object.__setattr__(
            self,
            "resolved_consequences",
            resolved,
        )

        unresolved = tuple(
            self.unresolved_consequences
        )

        if not all(
            isinstance(
                consequence,
                SerpentUnresolvedConsequence,
            )
            for consequence
            in unresolved
        ):
            raise TypeError(
                "Unresolved serpent consequences "
                "require "
                "SerpentUnresolvedConsequence objects."
            )

        object.__setattr__(
            self,
            "unresolved_consequences",
            unresolved,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "roll_id": self.roll_id,
            "planned_consequences": list(
                self.planned_consequences
            ),
            "resolved_consequences": [
                consequence.to_dict()
                for consequence
                in self.resolved_consequences
            ],
            "unresolved_consequences": [
                consequence.to_dict()
                for consequence
                in self.unresolved_consequences
            ],
            "visibility": self.visibility,
        }


class SerpentConsequenceExecutor:

    def __init__(self, universe):
        self.name = "serpent_consequence_executor"
        self.universe = universe
        self.execution_history = []

        self.handlers = {
            "quantum_tick": self._execute_quantum_tick,
            "quantum_box": self._execute_quantum_box,
            "quantum_error": self._execute_quantum_error,
            "cat_manifestation": self._execute_cat_manifestation,
            "quantum_geometry_shift": (
                self._execute_quantum_geometry_shift
            ),
            "cronenberg_quantum_counterpart": (
                self._execute_cronenberg_quantum_counterpart
            )
        }

    def execute_hidden_plan(
        self,
        serpent_d20,
        roll_id
    ):
        hidden = serpent_d20.hidden_resolution_for(
            roll_id
        )

        if hidden is None:
            raise ValueError(
                f"Unknown Serpent roll: {roll_id}"
            )

        planned = list(
            hidden.possible_consequences
        )

        resolved = []
        unresolved = []

        for consequence in planned:
            handler = self.handlers.get(
                consequence
            )

            if handler is None:
                unresolved.append(
                    SerpentUnresolvedConsequence(
                        consequence=consequence,
                    )
                )
                continue

            result = handler()

            resolved.append(
                SerpentResolvedConsequence(
                    consequence=consequence,
                    result=result,
                )
            )

        serpent_d20.record_resolved_consequences(
            roll_id=roll_id,
            resolved_consequences=resolved
        )

        event = SerpentConsequencesExecutedEvent(
            roll_id=roll_id,
            planned_consequences=tuple(
                planned
            ),
            resolved_consequences=tuple(
                resolved
            ),
            unresolved_consequences=tuple(
                unresolved
            ),
        )

        self.record_execution(
            event
        )

        UniverseLogger.event(
            "SERPENT CONSEQUENCES EXECUTED: "
            f"{roll_id}"
        )

        return event

    def record_execution(
        self,
        event,
    ):
        if not isinstance(
            event,
            SerpentConsequencesExecutedEvent,
        ):
            raise TypeError(
                "Serpent execution history requires "
                "a SerpentConsequencesExecutedEvent "
                "object."
            )

        self.execution_history.append(
            event
        )

        return event

    def _execute_quantum_tick(self):
        return self.universe.tick_quantum()

    def _execute_quantum_box(self):
        box = self.universe.create_quantum_box()

        return SerpentQuantumBoxResult(
            box_id=box.id,
            position=box.position,
            state=box.state,
        )

    def _execute_quantum_error(self):
        result = self.universe.trigger_quantum_error(
            error=RuntimeError(
                "Serpent D20 hidden quantum fluctuation."
            ),
            source_component="serpent_d20",
            source_operation="hidden_roll"
        )

        if not isinstance(
            result,
            QuantumErrorResult,
        ):
            raise TypeError(
                "Serpent quantum error consequence "
                "requires QuantumErrorResult."
            )

        cronenberg = result.cronenberg

        return SerpentQuantumErrorResult(
            error_type=result.error_type,
            error_message=result.error_message,
            cronenberg_id=(
                cronenberg.id
                if cronenberg is not None
                else None
            ),
        )

    def _execute_cat_manifestation(self):
        name = (
            f"serpent_cat_"
            f"{uuid.uuid4().hex[:8]}"
        )

        manifestation = (
            self.universe.manifest_cat(
                name=name,
                source="serpent_d20_hidden_roll"
            )
        )

        return SerpentCatManifestationResult(
            cat_name=manifestation.cat.name,
            entity_name=manifestation.entity.name,
            origin=manifestation.cat.origin,
        )

    def _execute_quantum_geometry_shift(self):
        if not hasattr(
            self.universe,
            "quantum_space"
        ):
            self.universe.enable_quantum_layer()

        space = self.universe.quantum_space

        before = SerpentQuantumGeometryState(
            configuration_id=(
                space.configuration_id
            ),
            configuration_seed=(
                space.configuration_seed
            ),
            reconfiguration_count=(
                space.reconfiguration_count
            ),
        )

        space.reconfigure(
            cause="serpent_d20_hidden_roll"
        )

        after = SerpentQuantumGeometryState(
            configuration_id=(
                space.configuration_id
            ),
            configuration_seed=(
                space.configuration_seed
            ),
            reconfiguration_count=(
                space.reconfiguration_count
            ),
        )

        return SerpentQuantumGeometryShiftResult(
            before=before,
            after=after,
            cause="serpent_d20_hidden_roll",
        )

    def _execute_cronenberg_quantum_counterpart(self):
        candidates = [
            cronenberg
            for cronenberg in self.universe.cronenbergs
            if cronenberg.is_alive
            and cronenberg.quantum_state
            .counterpart_id is None
        ]

        if not candidates:
            return SerpentCronenbergCounterpartResult(
                result="no_eligible_cronenberg",
                counterpart_created=False,
            )

        original = candidates[0]

        result = (
            self.universe
            .create_cronenberg_quantum_counterpart(
                original=original,
                source="serpent_d20_hidden_roll"
            )
        )

        counterpart = result.counterpart

        return SerpentCronenbergCounterpartResult(
            result=result.result,
            counterpart_created=True,
            original_id=original.id,
            counterpart_id=counterpart.id,
            pair_id=result.pair_id,
            original_spin=(
                original.quantum_state.spin
            ),
            counterpart_spin=(
                counterpart.quantum_state.spin
            ),
            counterpart_location=(
                counterpart.location
            ),
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "execution_count": len(
                self.execution_history
            ),
            "implemented_consequences": list(
                self.handlers.keys()
            )
        }
