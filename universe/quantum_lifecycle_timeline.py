from dataclasses import dataclass

from universe.quantum_box_lifecycle_validator import (
    QuantumBoxLifecycleValidator,
)
from universe.quantum_tick_advanced_state import (
    UniverseQuantumTickAdvancedEvent,
)


@dataclass(slots=True, frozen=True)
class _ValidatedQuantumLifecycleHistory:
    events: tuple
    active_boxes: tuple


class UniverseQuantumLifecycleTimeline:
    """Read-only chronology of clock and box lifecycle events."""

    @staticmethod
    def merge(*, box_events, clock_events):
        return UniverseQuantumLifecycleTimeline.validate(
            box_events=box_events,
            clock_events=clock_events,
        ).events

    @staticmethod
    def validate(*, box_events, clock_events):
        try:
            box_events = tuple(box_events)
        except TypeError as error:
            raise TypeError(
                "Quantum box timeline must be iterable."
            ) from error

        try:
            clock_events = tuple(clock_events)
        except TypeError as error:
            raise TypeError(
                "Quantum clock timeline must be iterable."
            ) from error

        # Reuse the canonical lifecycle validator.
        active_boxes = QuantumBoxLifecycleValidator.validate(box_events)

        for expected_tick, event in enumerate(
            clock_events,
            start=1,
        ):
            if not isinstance(
                event,
                UniverseQuantumTickAdvancedEvent,
            ):
                raise TypeError(
                    "Unsupported quantum clock timeline event "
                    f"at tick {expected_tick}."
                )

            if event.tick != expected_tick:
                raise ValueError(
                    "Quantum timeline requires consecutive "
                    "clock ticks starting at 1."
                )

        last_tick = len(clock_events)

        if any(
            event.tick > last_tick
            for event in box_events
        ):
            raise ValueError(
                "Quantum timeline references "
                "an unrecorded clock tick."
            )

        ordered = []
        cursor = 0

        # Tick zero exists before the first clock event.
        while (
            cursor < len(box_events)
            and box_events[cursor].tick == 0
        ):
            ordered.append(box_events[cursor])
            cursor += 1

        # At tick N the clock advances first, followed
        # by box events already ordered in their stream.
        for clock_event in clock_events:
            ordered.append(clock_event)

            while (
                cursor < len(box_events)
                and box_events[cursor].tick == clock_event.tick
            ):
                ordered.append(box_events[cursor])
                cursor += 1

        if cursor != len(box_events):
            raise ValueError(
                "Quantum timeline could not place every event."
            )

        return _ValidatedQuantumLifecycleHistory(
            events=tuple(ordered),
            active_boxes=active_boxes,
        )
