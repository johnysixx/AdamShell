import random
from dataclasses import fields


class CronenbergEncounterBatchTransaction:
    """Rollback an entire failed encounter detection batch."""

    REGISTRIES = (
        "cronenbergs",
        "entities",
        "quantum_events",
        "quantum_clock_events",
        "quantum_boxes",
        "universe_history",
    )

    ENTITY_FIELDS = (
        "active",
        "state",
        "location",
        "size",
        "energy",
        "juice_value",
        "merged_into",
        "recombined_into",
    )

    @staticmethod
    def restore_list(registry, previous):
        list.__setitem__(
            registry, slice(None), previous
        )

    @classmethod
    def execute(cls, universe, operation):
        registries = {
            name: getattr(universe, name)
            for name in cls.REGISTRIES
        }

        if not all(
            isinstance(items, list)
            for items in registries.values()
        ):
            raise TypeError(
                "Encounter batch requires list registries."
            )

        registry_before = {
            name: tuple(items)
            for name, items in registries.items()
        }

        detector = universe.cronenberg_pair_encounter
        resolver = universe.cronenberg_pair_encounter_resolver

        detector_history = detector.history
        resolver_history = resolver.history

        if not all(
            isinstance(items, list)
            for items in (detector_history, resolver_history)
        ):
            raise TypeError(
                "Encounter histories must be lists."
            )

        detector_before = tuple(detector_history)
        resolver_before = tuple(resolver_history)

        active = universe.active_cronenberg_pair_encounters

        if not isinstance(active, set):
            raise TypeError(
                "Active encounters must be a set."
            )

        active_before = set(active)

        world = universe.world

        if not isinstance(world, dict):
            raise TypeError(
                "World registry must be a dictionary."
            )

        world_before = dict(world)

        clock = universe.quantum_state
        clock_before = tuple(
            (field.name, getattr(clock, field.name))
            for field in fields(type(clock))
        )

        statistics = universe.statistics
        statistics_before = tuple(
            (name, value)
            for name, value in vars(statistics).items()
            if name.startswith("total_")
        )

        count_before = universe.cronenberg_count
        energy_before = universe.energy_pool

        dark_existed = "dark_energy" in universe.__dict__
        dark_before = getattr(universe, "dark_energy", None)

        participants = []

        for entity in registry_before["cronenbergs"]:
            attrs = tuple(
                (
                    name,
                    name in entity.__dict__,
                    entity.__dict__.get(name),
                )
                for name in cls.ENTITY_FIELDS
            )

            quantum = entity.quantum_state
            quantum_before = tuple(
                (field.name, getattr(quantum, field.name))
                for field in fields(type(quantum))
            )

            link_system = entity.quantum_link_system
            links = link_system.links
            history = link_system.history

            if not (
                isinstance(links, list)
                and isinstance(history, list)
            ):
                raise TypeError(
                    "Quantum link histories must be lists."
                )

            participants.append((
                entity,
                attrs,
                quantum,
                quantum_before,
                link_system,
                links,
                tuple(links),
                history,
                tuple(history),
                tuple((link, link.strength) for link in links),
            ))

        box_states = []

        for box in registry_before["quantum_boxes"]:
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

        had_cats = "cats_layer" in universe.__dict__
        cats_layer = universe.__dict__.get("cats_layer")
        cats_snapshot = None

        if cats_layer is not None:
            cats = cats_layer.cats
            cat_events = cats_layer.events

            if not (
                isinstance(cats, list)
                and isinstance(cat_events, list)
            ):
                raise TypeError("Cat registries must be lists.")

            cats_snapshot = (
                cats,
                tuple(cats),
                cat_events,
                tuple(cat_events),
            )

        physics_layers = universe.physics_layers
        physics_before = (
            physics_layers.classical,
            physics_layers.quantum,
            universe.physics_model,
        )

        had_space = "quantum_space" in universe.__dict__
        space = universe.__dict__.get("quantum_space")
        space_snapshot = None

        if space is not None:
            stairs = space.staircases
            engine = space.geometry_engine
            die = space.quantum_die_box

            if not isinstance(stairs, list):
                raise TypeError(
                    "Quantum staircases must be a list."
                )

            space_snapshot = (
                space.configuration_id,
                space.configuration_seed,
                space.reconfiguration_count,
                stairs,
                tuple(stairs),
                engine,
                engine.configuration_seed,
                engine.geometry_version,
                die,
                die.position,
                die.state,
            )

        had_die = "quantum_die_box" in universe.__dict__
        die_object = universe.__dict__.get("quantum_die_box")

        meeting_place = getattr(
            universe, "meeting_place", None
        )
        shelf = getattr(
            meeting_place, "glass_shelf", None
        )
        glass_snapshot = None

        if shelf is not None:
            shared = shelf.shared_glasses
            reserved = shelf.reserved_glasses
            personal = shelf.personal_glasses

            if not (
                isinstance(shared, list)
                and isinstance(reserved, list)
                and isinstance(personal, dict)
            ):
                raise TypeError(
                    "Invalid glass shelf registries."
                )

            glass_snapshot = (
                shared,
                tuple(shared),
                reserved,
                tuple(reserved),
                personal,
                dict(personal),
            )

        rng_before = random.getstate()

        try:
            return operation()

        except BaseException:
            # Restore original canonical registry identities.
            for name, registry in registries.items():
                cls.restore_list(
                    registry, registry_before[name]
                )
                object.__setattr__(
                    universe, name, registry
                )

            object.__setattr__(
                detector, "history", detector_history
            )
            object.__setattr__(
                resolver, "history", resolver_history
            )

            cls.restore_list(
                detector_history, detector_before
            )
            cls.restore_list(
                resolver_history, resolver_before
            )

            set.clear(active)
            set.update(active, active_before)
            object.__setattr__(
                universe,
                "active_cronenberg_pair_encounters",
                active,
            )

            object.__setattr__(
                universe, "cronenberg_count", count_before
            )
            object.__setattr__(
                universe, "energy_pool", energy_before
            )

            if dark_existed:
                object.__setattr__(
                    universe, "dark_energy", dark_before
                )
            else:
                universe.__dict__.pop("dark_energy", None)

            object.__setattr__(
                universe, "quantum_state", clock
            )
            for name, value in clock_before:
                object.__setattr__(clock, name, value)

            object.__setattr__(
                universe, "statistics", statistics
            )
            for name, value in statistics_before:
                object.__setattr__(statistics, name, value)

            # Restore existing entities, including nested
            # mutable quantum state and quantum links.
            for (
                entity,
                attrs,
                quantum,
                quantum_before,
                link_system,
                links,
                links_before,
                history,
                history_before,
                strengths,
            ) in participants:
                for name, existed, value in attrs:
                    if existed:
                        object.__setattr__(
                            entity, name, value
                        )
                    else:
                        entity.__dict__.pop(name, None)

                object.__setattr__(
                    entity, "quantum_state", quantum
                )

                for name, value in quantum_before:
                    object.__setattr__(
                        quantum, name, value
                    )

                object.__setattr__(
                    entity, "quantum_link_system", link_system
                )
                object.__setattr__(
                    link_system, "links", links
                )
                object.__setattr__(
                    link_system, "history", history
                )

                cls.restore_list(links, links_before)
                cls.restore_list(history, history_before)

                for link, strength in strengths:
                    object.__setattr__(
                        link, "strength", strength
                    )

            # A nested quantum tick may have aged or
            # collapsed existing boxes.
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

            if had_cats:
                object.__setattr__(
                    universe, "cats_layer", cats_layer
                )
                if cats_snapshot is not None:
                    (
                        cats, cats_before,
                        cat_events, cat_events_before
                    ) = cats_snapshot

                    cls.restore_list(cats, cats_before)
                    cls.restore_list(
                        cat_events, cat_events_before
                    )
            else:
                universe.__dict__.pop("cats_layer", None)

            object.__setattr__(
                universe, "physics_layers", physics_layers
            )
            object.__setattr__(
                physics_layers, "classical", physics_before[0]
            )
            object.__setattr__(
                physics_layers, "quantum", physics_before[1]
            )
            object.__setattr__(
                universe, "physics_model", physics_before[2]
            )

            # Restore geometry, including a previous
            # staircase list and die-box position.
            if had_space:
                object.__setattr__(
                    universe, "quantum_space", space
                )

                if space_snapshot is not None:
                    (
                        config_id, config_seed, count,
                        stairs, stairs_before,
                        engine, engine_seed, version,
                        die, position, state
                    ) = space_snapshot

                    object.__setattr__(
                        space, "configuration_id", config_id
                    )
                    object.__setattr__(
                        space, "configuration_seed", config_seed
                    )
                    object.__setattr__(
                        space, "reconfiguration_count", count
                    )
                    object.__setattr__(
                        space, "staircases", stairs
                    )
                    cls.restore_list(stairs, stairs_before)

                    object.__setattr__(
                        space, "geometry_engine", engine
                    )
                    object.__setattr__(
                        engine, "configuration_seed", engine_seed
                    )
                    object.__setattr__(
                        engine, "geometry_version", version
                    )
                    object.__setattr__(
                        space, "quantum_die_box", die
                    )
                    object.__setattr__(
                        die, "_position", position
                    )
                    object.__setattr__(
                        die, "state", state
                    )
            else:
                universe.__dict__.pop("quantum_space", None)

            if had_die:
                object.__setattr__(
                    universe, "quantum_die_box", die_object
                )
            else:
                universe.__dict__.pop("quantum_die_box", None)

            object.__setattr__(
                universe, "world", world
            )
            dict.clear(world)
            dict.update(world, world_before)

            if glass_snapshot is not None:
                (
                    shared, shared_before,
                    reserved, reserved_before,
                    personal, personal_before
                ) = glass_snapshot

                object.__setattr__(
                    shelf, "shared_glasses", shared
                )
                object.__setattr__(
                    shelf, "reserved_glasses", reserved
                )
                object.__setattr__(
                    shelf, "personal_glasses", personal
                )

                cls.restore_list(shared, shared_before)
                cls.restore_list(reserved, reserved_before)
                dict.clear(personal)
                dict.update(personal, personal_before)

            random.setstate(rng_before)

            # Original exception propagates to the
            # surrounding Universe tick error boundary.
            raise
