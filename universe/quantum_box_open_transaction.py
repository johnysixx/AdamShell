class QuantumBoxOpenTransaction:
    """Rollback live opening before the error boundary runs."""

    @staticmethod
    def execute(universe, *, box_id, observer=None, rng=None):
        boxes = universe.quantum_boxes
        events = universe.quantum_events
        entities = universe.entities
        statistics = universe.statistics
        world = universe.world

        box = next(
            (item for item in boxes if item.id == box_id),
            None,
        )

        if box is None:
            return universe._open_quantum_box_unprotected(
                box_id=box_id,
                observer=observer,
                rng=rng,
            )

        if not all(
            isinstance(registry, list)
            for registry in (boxes, events, entities)
        ):
            raise TypeError(
                "Quantum opening requires list registries."
            )

        if not isinstance(world, dict):
            raise TypeError(
                "Quantum opening requires a world dictionary."
            )

        boxes_before = tuple(boxes)
        events_before = tuple(events)
        entities_before = tuple(entities)
        world_before = dict(world)

        statistic_names = (
            "total_quantum_collapses",
            "total_quantum_boxes_disappeared",
            "total_cats_created",
        )

        statistics_before = tuple(
            (name, getattr(statistics, name))
            for name in statistic_names
        )

        content = box.content
        collapse = box.collapse

        box_before = (
            box.state,
            content.resolved,
            collapse.collapsed,
            collapse.cause,
            collapse.observer,
            collapse.tick,
        )

        cats_layer = getattr(
            universe,
            "cats_layer",
            None,
        )

        if cats_layer is not None:
            cat_registry = cats_layer.cats
            cat_events = cats_layer.events

            if not all(
                isinstance(items, list)
                for items in (cat_registry, cat_events)
            ):
                raise TypeError(
                    "Cat layer requires list registries."
                )

            cats_before = tuple(cat_registry)
            cat_events_before = tuple(cat_events)

        meeting_place = getattr(
            universe,
            "meeting_place",
            None,
        )

        shelf = getattr(
            meeting_place,
            "glass_shelf",
            None,
        )

        if shelf is not None:
            shared = shelf.shared_glasses
            reserved = shelf.reserved_glasses
            personal = shelf.personal_glasses

            if (
                not isinstance(shared, list)
                or not isinstance(reserved, list)
                or not isinstance(personal, dict)
            ):
                raise TypeError(
                    "Invalid bar glass registries."
                )

            shared_before = tuple(shared)
            reserved_before = tuple(reserved)
            personal_before = dict(personal)

        try:
            return universe._open_quantum_box_unprotected(
                box_id=box_id,
                observer=observer,
                rng=rng,
            )

        except BaseException:
            # Restore canonical lists without invoking
            # overridden append/remove implementations.
            list.__setitem__(
                boxes,
                slice(None),
                boxes_before,
            )

            list.__setitem__(
                events,
                slice(None),
                events_before,
            )

            list.__setitem__(
                entities,
                slice(None),
                entities_before,
            )

            # Preserve statistics identity.
            for name, value in statistics_before:
                object.__setattr__(
                    statistics,
                    name,
                    value,
                )

            # Restore original QuantumBox components.
            object.__setattr__(
                box,
                "state",
                box_before[0],
            )

            object.__setattr__(
                box,
                "content",
                content,
            )

            object.__setattr__(
                content,
                "resolved",
                box_before[1],
            )

            object.__setattr__(
                box,
                "collapse",
                collapse,
            )

            for name, value in zip(
                ("collapsed", "cause", "observer", "tick"),
                box_before[2:],
            ):
                object.__setattr__(
                    collapse,
                    name,
                    value,
                )

            # Existing cat layer: restore in place.
            # Newly created cat layer: remove it.
            if cats_layer is not None:
                list.__setitem__(
                    cat_registry,
                    slice(None),
                    cats_before,
                )

                list.__setitem__(
                    cat_events,
                    slice(None),
                    cat_events_before,
                )

                object.__setattr__(
                    universe,
                    "cats_layer",
                    cats_layer,
                )
            else:
                universe.__dict__.pop(
                    "cats_layer",
                    None,
                )

            # Restore world registry entries.
            dict.clear(world)
            dict.update(world, world_before)

            # Restore bar registry contents.
            if shelf is not None:
                list.__setitem__(
                    shared,
                    slice(None),
                    shared_before,
                )

                list.__setitem__(
                    reserved,
                    slice(None),
                    reserved_before,
                )

                dict.clear(personal)
                dict.update(
                    personal,
                    personal_before,
                )

            # The original QuantumErrorBoundary runs
            # after rollback and creates a Cronenberg
            # for ordinary exceptions.
            raise
