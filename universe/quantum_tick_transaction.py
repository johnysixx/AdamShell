import random
from dataclasses import fields

from universe.quantum_state import UniverseQuantumState


class QuantumTickTransaction:
    """Restore a whole failed quantum tick in place."""

    @staticmethod
    def execute(universe):
        clock = universe.quantum_state
        boxes = universe.quantum_boxes
        events = universe.quantum_events
        clock_events = universe.quantum_clock_events
        entities = universe.entities
        statistics = universe.statistics
        world = universe.world

        if not isinstance(clock, UniverseQuantumState):
            raise TypeError("Invalid quantum clock state.")

        if not all(
            isinstance(value, list)
            for value in (boxes, events, clock_events, entities)
        ):
            raise TypeError("Quantum tick requires list registries.")

        if not isinstance(world, dict):
            raise TypeError("Quantum tick requires a world dictionary.")

        clock_before = tuple(
            (field.name, getattr(clock, field.name))
            for field in fields(UniverseQuantumState)
        )

        boxes_before = tuple(boxes)
        events_before = tuple(events)
        clock_events_before = tuple(clock_events)
        entities_before = tuple(entities)
        world_before = dict(world)

        statistics_before = tuple(
            (name, getattr(statistics, name))
            for name in (
                "total_quantum_collapses",
                "total_quantum_boxes_disappeared",
                "total_cats_created",
            )
        )

        box_states = []

        for box in boxes_before:
            content = box.content
            collapse = box.collapse

            box_states.append((
                box,
                box.age_ticks,
                box.state,
                content,
                content.resolved,
                collapse,
                collapse.collapsed,
                collapse.cause,
                collapse.observer,
                collapse.tick,
            ))

        cats_layer = getattr(universe, "cats_layer", None)

        if cats_layer is not None:
            cat_registry = cats_layer.cats
            cat_events = cats_layer.events

            if not isinstance(cat_registry, list) or not isinstance(
                cat_events, list
            ):
                raise TypeError("Invalid cat registries.")

            cats_before = tuple(cat_registry)
            cat_events_before = tuple(cat_events)

        meeting_place = getattr(universe, "meeting_place", None)
        shelf = getattr(meeting_place, "glass_shelf", None)

        if shelf is not None:
            shared = shelf.shared_glasses
            reserved = shelf.reserved_glasses
            personal = shelf.personal_glasses

            if not (
                isinstance(shared, list)
                and isinstance(reserved, list)
                and isinstance(personal, dict)
            ):
                raise TypeError("Invalid bar glass registries.")

            shared_before = tuple(shared)
            reserved_before = tuple(reserved)
            personal_before = dict(personal)

        # Snapshot module RNG before executing the tick.
        random_before = random.getstate()

        try:
            return universe._tick_quantum_unprotected_impl()

        except BaseException:
            # Restore canonical registries, bypassing
            # potentially failing list overrides.
            for registry, previous in (
                (boxes, boxes_before),
                (events, events_before),
                (clock_events, clock_events_before),
                (entities, entities_before),
            ):
                list.__setitem__(
                    registry, slice(None), previous
                )

            # Restore every original clock field.
            for name, value in clock_before:
                object.__setattr__(clock, name, value)

            for name, value in statistics_before:
                object.__setattr__(statistics, name, value)

            # Restore ALL original boxes, not merely
            # the box being processed at failure.
            for (
                box, age, state, content, resolved,
                collapse, collapsed, cause, observer, tick
            ) in box_states:
                object.__setattr__(box, "age_ticks", age)
                object.__setattr__(box, "state", state)
                object.__setattr__(box, "content", content)
                object.__setattr__(content, "resolved", resolved)
                object.__setattr__(box, "collapse", collapse)

                for name, value in (
                    ("collapsed", collapsed),
                    ("cause", cause),
                    ("observer", observer),
                    ("tick", tick),
                ):
                    object.__setattr__(collapse, name, value)

            if cats_layer is None:
                universe.__dict__.pop("cats_layer", None)
            else:
                list.__setitem__(
                    cat_registry, slice(None), cats_before
                )
                list.__setitem__(
                    cat_events, slice(None), cat_events_before
                )
                object.__setattr__(
                    universe, "cats_layer", cats_layer
                )

            dict.clear(world)
            dict.update(world, world_before)

            if shelf is not None:
                list.__setitem__(
                    shared, slice(None), shared_before
                )
                list.__setitem__(
                    reserved, slice(None), reserved_before
                )
                dict.clear(personal)
                dict.update(personal, personal_before)

            # Restore RNG including cached gauss value.
            random.setstate(random_before)

            # The surrounding QuantumErrorBoundary
            # handles ordinary errors after rollback.
            raise
