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

        # Canonical list state is required for in-place
        # rollback without replacing the registry object.
        boxes = universe.quantum_boxes

        if not isinstance(boxes, list):
            raise TypeError(
                "Quantum box registry must be a list."
            )

        boxes_before = tuple(boxes)

        statistic_names = (
            "total_quantum_boxes_created",
            "total_quantum_collapses",
            "total_quantum_boxes_disappeared",
        )

        statistics_before = tuple(
            (name, getattr(statistics, name))
            for name in statistic_names
        )

        try:
            boxes.extend(staged.quantum_boxes)

            for name in statistic_names:
                setattr(
                    statistics,
                    name,
                    getattr(staged.statistics, name),
                )

        except BaseException:
            # A list extension may append successfully
            # before raising. Restore its original contents
            # using the built-in list implementation.
            list.__setitem__(
                boxes,
                slice(None),
                boxes_before,
            )

            # Restore the original statistics without
            # invoking a potentially failing setter.
            for name, value in statistics_before:
                object.__setattr__(
                    statistics,
                    name,
                    value,
                )

            raise

        return tuple(boxes)
