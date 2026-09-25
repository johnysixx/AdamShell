import uuid
from copy import deepcopy
from dataclasses import dataclass, field

from core.entity.serpent_d20 import (
    SerpentResolvedConsequence,
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
            hidden.get(
                "possible_consequences",
                []
            )
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

        return event.to_dict()

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

        return {
            "box_id": box.id,
            "position": box.position.to_dict(),
            "state": box.state
        }

    def _execute_quantum_error(self):
        result = self.universe.trigger_quantum_error(
            error=RuntimeError(
                "Serpent D20 hidden quantum fluctuation."
            ),
            source_component="serpent_d20",
            source_operation="hidden_roll"
        )

        cronenberg = result.get(
            "cronenberg"
        )

        return {
            "error_type": result.get(
                "error_type"
            ),
            "error_message": result.get(
                "error_message"
            ),
            "cronenberg_id": (
                cronenberg.id
                if cronenberg is not None
                else None
            )
        }

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

        return {
            "cat_name": manifestation[
                "cat"
            ]["name"],
            "entity_name": manifestation[
                "entity"
            ].name,
            "origin": manifestation[
                "cat"
            ]["origin"]
        }

    def _execute_quantum_geometry_shift(self):
        if not hasattr(
            self.universe,
            "quantum_space"
        ):
            self.universe.enable_quantum_layer()

        space = self.universe.quantum_space

        before = {
            "configuration_id": (
                space.configuration_id
            ),
            "configuration_seed": (
                space.configuration_seed
            ),
            "reconfiguration_count": (
                space.reconfiguration_count
            )
        }

        space.reconfigure(
            cause="serpent_d20_hidden_roll"
        )

        after = {
            "configuration_id": (
                space.configuration_id
            ),
            "configuration_seed": (
                space.configuration_seed
            ),
            "reconfiguration_count": (
                space.reconfiguration_count
            )
        }

        return {
            "before": before,
            "after": after,
            "cause": "serpent_d20_hidden_roll"
        }

    def _execute_cronenberg_quantum_counterpart(self):
        candidates = [
            cronenberg
            for cronenberg in self.universe.cronenbergs
            if cronenberg.is_alive
            and cronenberg.quantum_state
            .counterpart_id is None
        ]

        if not candidates:
            return {
                "result": "no_eligible_cronenberg",
                "counterpart_created": False
            }

        original = candidates[0]

        result = (
            self.universe
            .create_cronenberg_quantum_counterpart(
                original=original,
                source="serpent_d20_hidden_roll"
            )
        )

        counterpart = result["counterpart"]

        return {
            "result": result["result"],
            "counterpart_created": True,
            "original_id": original.id,
            "counterpart_id": counterpart.id,
            "pair_id": result["pair_id"],
            "original_spin": (
                original.quantum_state.spin
            ),
            "counterpart_spin": (
                counterpart.quantum_state.spin
            ),
            "counterpart_location": (
                counterpart.location
            )
        }

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
