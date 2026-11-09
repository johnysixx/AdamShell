import random
from dataclasses import fields

from core.entity.cronenberg import Cronenberg


class CronenbergPublicationTransaction:
    """Rollback an incomplete Cronenberg publication in place."""

    ENTITY_ATTRIBUTES = (
        "active",
        "state",
        "location",
        "merged_into",
        "recombined_into",
    )

    STATISTIC_ATTRIBUTES = (
        "total_quantum_boxes_created",
        "total_quantum_boxes_disappeared",
        "total_cats_created",
        "total_cat_arrivals",
        "total_quantum_collapses",
        "total_geometry_reconfigurations",
        "total_dice_rolls",
    )

    @classmethod
    def execute(cls, universe, operation, participants=()):
        registries = {
            name: getattr(universe, name)
            for name in (
                "cronenbergs",
                "entities",
                "quantum_events",
            )
        }

        if not all(
            isinstance(registry, list)
            for registry in registries.values()
        ):
            raise TypeError(
                "Cronenberg publication requires list registries."
            )

        registry_before = {
            name: tuple(registry)
            for name, registry in registries.items()
        }

        world = universe.world

        if not isinstance(world, dict):
            raise TypeError(
                "Cronenberg publication requires a world dictionary."
            )

        world_before = dict(world)
        count_before = universe.cronenberg_count
        energy_before = universe.energy_pool

        dark_energy_existed = (
            "dark_energy" in universe.__dict__
        )
        dark_energy_before = getattr(
            universe, "dark_energy", None
        )

        statistics = universe.statistics
        statistics_before = tuple(
            (name, getattr(statistics, name))
            for name in cls.STATISTIC_ATTRIBUTES
        )

        # Only pre-existing participants can be mutated
        # by the four protected operations.
        participant_states = []
        seen = set()

        for entity in participants:
            if not isinstance(entity, Cronenberg):
                continue

            if id(entity) in seen:
                continue

            seen.add(id(entity))

            attributes = tuple(
                (
                    name,
                    name in entity.__dict__,
                    entity.__dict__.get(name),
                )
                for name in cls.ENTITY_ATTRIBUTES
            )

            quantum = entity.quantum_state
            quantum_before = tuple(
                (item.name, getattr(quantum, item.name))
                for item in fields(type(quantum))
            )

            links_system = entity.quantum_link_system
            links = links_system.links
            history = links_system.history

            if not (
                isinstance(links, list)
                and isinstance(history, list)
            ):
                raise TypeError(
                    "Cronenberg link registries must be lists."
                )

            links_before = tuple(links)
            history_before = tuple(history)
            link_strengths = tuple(
                (link, link.strength)
                for link in links_before
            )

            participant_states.append(
                (
                    entity,
                    attributes,
                    quantum,
                    quantum_before,
                    links_system,
                    links,
                    links_before,
                    history,
                    history_before,
                    link_strengths,
                )
            )

        meeting_place = getattr(
            universe, "meeting_place", None
        )
        shelf = getattr(
            meeting_place, "glass_shelf", None
        )

        glass_before = None

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
                    "Invalid bar glass registries."
                )

            glass_before = (
                shared,
                tuple(shared),
                reserved,
                tuple(reserved),
                personal,
                dict(personal),
            )

        random_before = random.getstate()

        try:
            return operation()

        except BaseException:
            # Restore canonical registry identity
            # and exact original membership.
            for name, registry in registries.items():
                list.__setitem__(
                    registry,
                    slice(None),
                    registry_before[name],
                )
                object.__setattr__(
                    universe, name, registry
                )

            object.__setattr__(
                universe,
                "cronenberg_count",
                count_before,
            )
            object.__setattr__(
                universe,
                "energy_pool",
                energy_before,
            )

            if dark_energy_existed:
                object.__setattr__(
                    universe,
                    "dark_energy",
                    dark_energy_before,
                )
            else:
                universe.__dict__.pop(
                    "dark_energy", None
                )

            object.__setattr__(
                universe, "statistics", statistics
            )

            for name, value in statistics_before:
                object.__setattr__(
                    statistics, name, value
                )

            # Restore both original Cronenbergs
            # without replacing their identities.
            for (
                entity,
                attributes,
                quantum,
                quantum_before,
                links_system,
                links,
                links_before,
                history,
                history_before,
                link_strengths,
            ) in participant_states:

                for name, existed, value in attributes:
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
                    entity,
                    "quantum_link_system",
                    links_system,
                )

                object.__setattr__(
                    links_system, "links", links
                )
                object.__setattr__(
                    links_system, "history", history
                )

                list.__setitem__(
                    links,
                    slice(None),
                    links_before,
                )
                list.__setitem__(
                    history,
                    slice(None),
                    history_before,
                )

                for link, strength in link_strengths:
                    object.__setattr__(
                        link, "strength", strength
                    )

            object.__setattr__(
                universe, "world", world
            )
            dict.clear(world)
            dict.update(world, world_before)

            if glass_before is not None:
                (
                    shared,
                    shared_before,
                    reserved,
                    reserved_before,
                    personal,
                    personal_before,
                ) = glass_before

                object.__setattr__(
                    shelf, "shared_glasses", shared
                )
                object.__setattr__(
                    shelf, "reserved_glasses", reserved
                )
                object.__setattr__(
                    shelf, "personal_glasses", personal
                )

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
                dict.update(personal, personal_before)

            random.setstate(random_before)
            raise
