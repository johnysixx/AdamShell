from dataclasses import fields, replace

from universe.quantum_state import UniverseQuantumState
from universe.quantum_tick_advanced_state import (
    UniverseQuantumTickAdvancedEvent,
)


class UniverseQuantumClockReplayer:
    """Atomically replay recorded quantum clock advancements."""

    @staticmethod
    def replay(universe, events):
        try:
            events = tuple(events)
        except TypeError as error:
            raise TypeError(
                "Quantum clock history must be iterable."
            ) from error

        state = universe.quantum_state

        if not isinstance(state, UniverseQuantumState):
            raise TypeError(
                "Quantum clock requires UniverseQuantumState."
            )

        if (
            state.tick_count != 0
            or state.collapse_count != 0
            or state.last_collapse_tick is not None
            or state.superposition
            or state.collapsed
            or state.observer is not None
            or state.fluctuation != 0.0
            or state.uncertainty != 0.0
            or state.entropy_delta != 0.0
            or state.entropy_total != 0.0
        ):
            raise ValueError(
                "Quantum clock replay requires "
                "an unused clock state."
            )

        if events and not state.enabled:
            raise ValueError(
                "Enable the quantum layer before clock replay."
            )

        # All changes happen on a detached state object.
        staged = replace(state)

        for index, event in enumerate(events):
            if not isinstance(
                event,
                UniverseQuantumTickAdvancedEvent,
            ):
                raise TypeError(
                    "Unsupported quantum clock event "
                    f"at index {index}."
                )

            expected_tick = staged.tick_count + 1

            if event.tick != expected_tick:
                raise ValueError(
                    "Quantum clock history must contain "
                    "consecutive ticks starting at 1."
                )

            staged.advance_tick(
                observer=event.observer,
            )

        # Commit only after the complete stream is valid.
        # Preserve the identity of the original state object.
        for item in fields(UniverseQuantumState):
            setattr(
                state,
                item.name,
                getattr(staged, item.name),
            )

        return state
