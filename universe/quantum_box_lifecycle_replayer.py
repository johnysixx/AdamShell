from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.quantum_box_disappearance_state import (
    QuantumBoxDisappearedEvent,
)
from universe.quantum_box_lifecycle_operations import (
    QuantumBoxLifecycleOperations,
    QuantumBoxReplayStage,
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

        supported_types = (
            QuantumBoxCreatedEvent,
            QuantumBoxCollapsedEvent,
            QuantumBoxDisappearedEvent,
        )

        previous_tick = -1
        collapse_causes = {}

        for index, event in enumerate(events):
            if not isinstance(event, supported_types):
                raise TypeError(
                    "Unsupported quantum box history event "
                    f"at index {index}: "
                    f"{type(event).__name__}"
                )

            tick = event.tick

            if type(tick) is not int or tick < 0:
                raise ValueError(
                    f"Invalid quantum history tick at index {index}."
                )

            if tick < previous_tick:
                raise ValueError(
                    "Quantum box history is not chronological."
                )

            previous_tick = tick

            if isinstance(event, QuantumBoxCreatedEvent):
                collapse_causes.pop(event.box_id, None)

            elif isinstance(event, QuantumBoxCollapsedEvent):
                if (
                    not isinstance(event.quantum_box_id, str)
                    or not event.quantum_box_id
                ):
                    raise ValueError(
                        "Quantum collapse requires a valid box ID."
                    )

                if (
                    not isinstance(event.cause, str)
                    or not event.cause
                ):
                    raise ValueError(
                        "Quantum collapse requires a valid cause."
                    )

                collapse_causes[
                    event.quantum_box_id
                ] = event.cause

            else:
                previous_cause = collapse_causes.get(
                    event.box_id
                )

                if (
                    previous_cause is not None
                    and previous_cause != event.cause
                ):
                    raise ValueError(
                        "Quantum box disappearance cause "
                        "does not match its collapse."
                    )

                collapse_causes.pop(event.box_id, None)

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
