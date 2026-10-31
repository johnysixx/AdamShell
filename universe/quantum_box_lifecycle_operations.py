from dataclasses import dataclass, field

from core.entity.quantum_box import QuantumBox
from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.quantum_box_disappearance_state import (
    QuantumBoxDisappearedEvent,
)
from universe.universe_statistics import UniverseStatistics


@dataclass(slots=True)
class QuantumBoxReplayStage:
    """Explicit isolated state for lifecycle replay."""

    quantum_boxes: list[QuantumBox] = field(
        default_factory=list,
    )
    statistics: UniverseStatistics = field(
        default_factory=UniverseStatistics,
    )


class QuantumBoxLifecycleOperations:
    """Replay individual immutable lifecycle events."""

    @staticmethod
    def replay_created(state, event):
        if not isinstance(event, QuantumBoxCreatedEvent):
            raise TypeError(
                "Quantum box replay requires "
                "a QuantumBoxCreatedEvent object."
            )

        if any(
            box.id == event.box_id
            for box in state.quantum_boxes
        ):
            raise ValueError(
                "Quantum box ID already exists."
            )

        box = QuantumBox(
            box_id=event.box_id,
            position=event.position,
        )
        box.current_layer = event.layer

        state.quantum_boxes.append(box)
        state.statistics.record_quantum_box_created()

        return box

    @staticmethod
    def replay_collapsed(state, event):
        if not isinstance(event, QuantumBoxCollapsedEvent):
            raise TypeError(
                "Quantum box collapse replay requires "
                "a QuantumBoxCollapsedEvent object."
            )

        box = next(
            (
                box
                for box in state.quantum_boxes
                if box.id == event.quantum_box_id
            ),
            None,
        )

        if box is None:
            raise ValueError(
                "Quantum box not found for collapse replay."
            )

        if box.collapse.collapsed:
            raise ValueError(
                "Quantum box is already collapsed."
            )

        result = box.resolve_state(
            result=event.result,
            cause=event.cause,
            observer=event.observer,
            tick=event.tick,
        )

        state.statistics.record_quantum_collapse()
        return result

    @staticmethod
    def replay_disappeared(state, event):
        if not isinstance(event, QuantumBoxDisappearedEvent):
            raise TypeError(
                "Quantum box disappearance replay requires "
                "a QuantumBoxDisappearedEvent object."
            )

        box = next(
            (
                box for box in state.quantum_boxes
                if box.id == event.box_id
            ),
            None,
        )

        if box is None:
            raise ValueError(
                "Quantum box not found for disappearance replay."
            )

        if not box.collapse.collapsed:
            raise ValueError(
                "Quantum box must collapse before disappearance."
            )

        state.quantum_boxes.remove(box)
        state.statistics.record_quantum_box_disappeared()

        return box
