from dataclasses import dataclass, replace

from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.quantum_box_disappearance_state import (
    QuantumBoxDisappearedEvent,
)


@dataclass(slots=True, frozen=True)
class _ActiveQuantumBox:
    box_id: str
    created_tick: int
    collapse_tick: int | None = None
    collapse_cause: str | None = None


class QuantumBoxLifecycleValidator:
    """Validate lifecycle chronology without changing runtime state."""

    @staticmethod
    def validate(events):
        supported_types = (
            QuantumBoxCreatedEvent,
            QuantumBoxCollapsedEvent,
            QuantumBoxDisappearedEvent,
        )

        active = []
        previous_tick = -1

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
                if any(
                    item.box_id == event.box_id
                    for item in active
                ):
                    raise ValueError(
                        "Quantum box ID already exists."
                    )

                active.append(
                    _ActiveQuantumBox(
                        box_id=event.box_id,
                        created_tick=tick,
                    )
                )
                continue

            if isinstance(event, QuantumBoxCollapsedEvent):
                box_id = event.quantum_box_id

                if not isinstance(box_id, str) or not box_id:
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

            else:
                box_id = event.box_id

            position = next(
                (
                    item_index
                    for item_index, item in enumerate(active)
                    if item.box_id == box_id
                ),
                None,
            )

            if position is None:
                raise ValueError(
                    "Quantum history references an inactive box."
                )

            current = active[position]

            if isinstance(event, QuantumBoxCollapsedEvent):
                if current.collapse_tick is not None:
                    raise ValueError(
                        "Quantum box is already collapsed."
                    )

                active[position] = replace(
                    current,
                    collapse_tick=tick,
                    collapse_cause=event.cause,
                )
                continue

            if current.collapse_tick is None:
                raise ValueError(
                    "Quantum box must collapse before disappearance."
                )

            if current.collapse_cause != event.cause:
                raise ValueError(
                    "Quantum box disappearance cause "
                    "does not match its collapse."
                )

            active.pop(position)

        return tuple(active)
