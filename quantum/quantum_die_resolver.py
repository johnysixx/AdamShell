from dataclasses import dataclass, field

from core.entity.quantum_die import QuantumDieRollEvent
from universe.logger import UniverseLogger


@dataclass(slots=True, frozen=True)
class QuantumDieResolution:
    result: str
    cronenberg_id: str | None = None
    original_id: str | None = None
    counterpart_id: str | None = None
    pair_id: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "result",
            str(self.result),
        )

    def to_dict(self):
        snapshot = {
            "result": self.result,
        }

        for field_name in (
            "cronenberg_id",
            "original_id",
            "counterpart_id",
            "pair_id",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                snapshot[field_name] = value

        return snapshot


@dataclass(slots=True, frozen=True)
class QuantumDieResolutionEvent:
    die: str
    value: int
    roll_number: int | None
    source: str
    resolution: QuantumDieResolution
    name: str = field(
        default="quantum_die_resolved",
        init=False,
    )
    visibility: str = field(
        default="universe_only",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.resolution,
            QuantumDieResolution,
        ):
            raise TypeError(
                "Quantum die resolution event requires "
                "a QuantumDieResolution object."
            )

        object.__setattr__(
            self,
            "die",
            str(self.die),
        )
        object.__setattr__(
            self,
            "value",
            int(self.value),
        )

        if self.roll_number is not None:
            object.__setattr__(
                self,
                "roll_number",
                int(self.roll_number),
            )

        object.__setattr__(
            self,
            "source",
            str(self.source),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "die": self.die,
            "value": self.value,
            "roll_number": self.roll_number,
            "source": self.source,
            "resolution": (
                self.resolution.to_dict()
            ),
            "visibility": self.visibility,
        }


class QuantumDieResolver:

    def __init__(self, universe):
        self.name = "quantum_die_resolver"
        self.universe = universe
        self.history = []

    def resolve(
        self,
        roll_event,
        source="quantum_die"
    ):
        if not isinstance(
            roll_event,
            QuantumDieRollEvent,
        ):
            raise TypeError(
                "Quantum die resolver requires a "
                "QuantumDieRollEvent object."
            )

        value = roll_event.value

        if value < 1 or value > 20:
            raise ValueError(
                "Quantum d20 result must be between 1 and 20."
            )

        if value == 20:
            resolution = self._resolve_twenty(
                source=source
            )
        else:
            resolution = self._resolve_standard(
                source=source
            )

        event = QuantumDieResolutionEvent(
            die=roll_event.die,
            value=value,
            roll_number=roll_event.roll_number,
            source=source,
            resolution=resolution,
        )

        self.history.append(
            event
        )

        UniverseLogger.event(
            "QUANTUM DIE RESOLVED "
            f"ROLL={value} "
            f"RESULT={resolution.result}"
        )

        return event

    def _resolve_standard(self, source):
        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Quantum d20 manifestation."
                ),
                source_component="quantum_die",
                source_operation=source
            )
        )

        return QuantumDieResolution(
            result="single_cronenberg_manifested",
            cronenberg_id=cronenberg.id,
        )

    def _resolve_twenty(self, source):
        candidate = self._find_counterpart_candidate()

        if candidate is not None:
            result = (
                self.universe
                .create_cronenberg_quantum_counterpart(
                    original=candidate,
                    source=source
                )
            )

            counterpart = result[
                "counterpart"
            ]

            return QuantumDieResolution(
                result=(
                    "existing_cronenberg_counterpart_manifested"
                ),
                original_id=candidate.id,
                counterpart_id=counterpart.id,
                pair_id=result["pair_id"],
            )

        original = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Quantum d20 critical pair manifestation."
                ),
                source_component="quantum_die",
                source_operation=source
            )
        )

        pair_result = (
            self.universe
            .create_cronenberg_quantum_counterpart(
                original=original,
                source=source
            )
        )

        counterpart = pair_result[
            "counterpart"
        ]

        return QuantumDieResolution(
            result="new_cronenberg_pair_manifested",
            original_id=original.id,
            counterpart_id=counterpart.id,
            pair_id=pair_result["pair_id"],
        )

    def _find_counterpart_candidate(self):
        return next(
            (
                cronenberg
                for cronenberg
                in self.universe.cronenbergs
                if getattr(
                    cronenberg,
                    "active",
                    True
                )
                and cronenberg.is_alive
                and cronenberg.quantum_state
                .counterpart_potential
                and not cronenberg.quantum_state
                .counterpart_manifested
                and cronenberg.quantum_state
                .counterpart_id is None
            ),
            None
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "resolution_count": len(
                self.history
            )
        }
