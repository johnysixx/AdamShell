from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.quantum_box_lifecycle_operations import (
    QuantumBoxLifecycleOperations,
    QuantumBoxReplayStage,
)
from universe.quantum_box_lifecycle_validator import (
    QuantumBoxLifecycleValidator,
)


class QuantumBoxLifecycleReplayer:
    """Atomic reconstruction of QuantumBox lifecycle state."""

    @staticmethod
    def replay(universe, events):
        try:
            events = tuple(events)
        except TypeError as error:
            raise TypeError(
                "Quantum box history must be iterable."
            ) from error

        statistics = universe.statistics

        if (
            universe.quantum_boxes
            or statistics.total_quantum_boxes_created
            or statistics.total_quantum_boxes_disappeared
            or statistics.total_quantum_collapses
        ):
            raise ValueError(
                "Quantum box history replay requires "
                "an empty target box lifecycle."
            )

        QuantumBoxLifecycleValidator.validate(events)

        # Stage on an explicit object-state container.
        # No Universe constructor, RNG or UUID is invoked.
        staged = QuantumBoxReplayStage()

        for event in events:
            if isinstance(event, QuantumBoxCreatedEvent):
                QuantumBoxLifecycleOperations.replay_created(staged, event)

            elif isinstance(event, QuantumBoxCollapsedEvent):
                QuantumBoxLifecycleOperations.replay_collapsed(staged, event)

            else:
                QuantumBoxLifecycleOperations.replay_disappeared(staged, event)

        # Commit only after all events replay successfully.
        universe.quantum_boxes.extend(staged.quantum_boxes)

        statistics.total_quantum_boxes_created = (
            staged.statistics.total_quantum_boxes_created
        )
        statistics.total_quantum_collapses = (
            staged.statistics.total_quantum_collapses
        )
        statistics.total_quantum_boxes_disappeared = (
            staged.statistics.total_quantum_boxes_disappeared
        )

        return tuple(universe.quantum_boxes)
