import io
import random
import unittest

from contextlib import redirect_stdout

from universe.universe import Universe


class FailOnceAppend(list):
    """Append successfully, then fail on selected call."""

    def __init__(self, values, nth, error):
        super().__init__(values)
        self.nth = nth
        self.error = error
        self.calls = 0

    def append(self, value):
        self.calls += 1
        super().append(value)

        if self.calls == self.nth:
            raise self.error


class CronenbergEncounterBatchRollbackTests(
    unittest.TestCase
):

    @staticmethod
    def make_world(number, pair_count=1, quantum=False):
        with redirect_stdout(io.StringIO()):
            world = Universe(
                universe_id=f"a415_regression_{number}"
            )

            if quantum:
                world.enable_quantum_layer()

            for index in range(pair_count):
                first = (
                    world.create_cronenberg_from_quantum_error(
                        RuntimeError("A41.5 seed"),
                        "a415",
                        f"seed_{index}",
                    )
                )

                second = (
                    world.create_cronenberg_quantum_counterpart(
                        first,
                        source="a415_seed",
                    ).counterpart
                )

                first.location = "shared_kernel"
                second.location = "shared_kernel"

        return world

    @staticmethod
    def geometry_state(world):
        space = getattr(world, "quantum_space", None)

        if space is None:
            return None

        engine = space.geometry_engine
        die = space.quantum_die_box

        return (
            id(space),
            space.configuration_id,
            space.configuration_seed,
            space.reconfiguration_count,
            id(space.staircases),
            tuple(space.staircases),
            id(engine),
            engine.configuration_seed,
            engine.geometry_version,
            id(die),
            die.position,
            die.state,
        )

    @classmethod
    def fingerprint(cls, world):
        detector = world.cronenberg_pair_encounter
        resolver = world.cronenberg_pair_encounter_resolver

        def entity_state(entity):
            quantum = entity.quantum_state
            links = entity.quantum_link_system

            return (
                id(entity),
                entity.active,
                entity.state,
                entity.location,
                entity.size,
                entity.energy,
                entity.juice_value,
                id(quantum),
                quantum.to_dict(),
                id(links),
                id(links.links),
                id(links.history),
                links.public_state,
                entity.origin.to_dict(),
                tuple(
                    (
                        name,
                        name in entity.__dict__,
                        entity.__dict__.get(name),
                    )
                    for name in (
                        "merged_into",
                        "recombined_into",
                    )
                ),
            )

        return {
            "detector_history": tuple(
                id(item) for item in detector.history
            ),
            "resolver_history": tuple(
                id(item) for item in resolver.history
            ),
            "universe_events": tuple(
                id(item) for item in world.quantum_events
            ),
            "clock_history": tuple(
                id(item) for item in world.quantum_clock_events
            ),
            "universe_history": tuple(
                id(item) for item in world.universe_history
            ),
            "registries": (
                id(world.cronenbergs),
                id(world.entities),
                id(world.quantum_events),
                id(world.quantum_clock_events),
                id(world.quantum_boxes),
                id(world.universe_history),
                id(detector.history),
                id(resolver.history),
                id(world.active_cronenberg_pair_encounters),
                id(world.world),
            ),
            "active_encounters": frozenset(
                world.active_cronenberg_pair_encounters
            ),
            "cronenbergs": tuple(world.cronenbergs),
            "entities": tuple(world.entities),
            "cronenberg_count": world.cronenberg_count,
            "participants": tuple(
                entity_state(entity)
                for entity in world.cronenbergs
            ),
            "quantum_boxes": tuple(
                (
                    id(box),
                    box.age_ticks,
                    box.state,
                    box.content.resolved,
                    box.collapse.collapsed,
                    box.collapse.cause,
                    box.collapse.observer,
                    box.collapse.tick,
                )
                for box in world.quantum_boxes
            ),
            "clock": (
                id(world.quantum_state),
                world.quantum_state.to_dict(),
            ),
            "statistics": (
                id(world.statistics),
                world.statistics.public_state,
            ),
            "energy": world.energy_pool,
            "dark_energy_exists": (
                "dark_energy" in world.__dict__
            ),
            "dark_energy": getattr(
                world, "dark_energy", None
            ),
            "physics": (
                id(world.physics_layers),
                world.physics_layers.classical,
                world.physics_layers.quantum,
                world.physics_model,
            ),
            "space_exists": (
                "quantum_space" in world.__dict__
            ),
            "geometry": cls.geometry_state(world),
            "die_exists": (
                "quantum_die_box" in world.__dict__
            ),
            "die_identity": id(
                getattr(world, "quantum_die_box", None)
            ),
            "world_entries": tuple(
                (key, id(value))
                for key, value in world.world.items()
            ),
            "cats_layer": (
                "cats_layer" in world.__dict__,
                id(getattr(world, "cats_layer", None)),
            ),
            "rng": random.getstate(),
        }

    def verify_case(
        self,
        number,
        effects,
        failure_point,
        pair_count=1,
        quantum=False,
    ):
        world = self.make_world(
            number,
            pair_count=pair_count,
            quantum=quantum,
        )

        detector = world.cronenberg_pair_encounter
        resolver = world.cronenberg_pair_encounter_resolver

        resolver._select_effects = (
            lambda rng: list(effects)
        )

        failure = RuntimeError(
            f"A41.5 injected failure {number}"
        )

        if failure_point == "detector":
            detector.history = FailOnceAppend(
                detector.history,
                1,
                failure,
            )

        elif failure_point == "resolver":
            resolver.history = FailOnceAppend(
                resolver.history,
                1,
                failure,
            )

        elif failure_point == "public":
            world.quantum_events = FailOnceAppend(
                world.quantum_events,
                1,
                failure,
            )

        elif failure_point in (
            "public_nested",
            "second_pair",
        ):
            world.quantum_events = FailOnceAppend(
                world.quantum_events,
                2,
                failure,
            )

        else:
            self.fail(
                f"Unknown failure point: {failure_point}"
            )

        before = self.fingerprint(world)
        caught = None

        with redirect_stdout(io.StringIO()):
            try:
                world.detect_cronenberg_pair_encounters()
            except Exception as error:
                caught = error

        self.assertIs(
            caught,
            failure,
            "Injected exception was not propagated.",
        )

        after = self.fingerprint(world)

        for component in before:
            self.assertEqual(
                after[component],
                before[component],
                f"Incomplete rollback: {component}",
            )

        # Retry after the injected failure.
        with redirect_stdout(io.StringIO()):
            retried = (
                world.detect_cronenberg_pair_encounters()
            )

        self.assertEqual(
            len(retried),
            pair_count,
        )

        published = [
            item
            for item in world.quantum_events
            if getattr(item, "name", None)
            == "cronenberg_quantum_pair_encountered"
        ]

        pair_ids = [
            item.pair_id
            for item in published
        ]

        self.assertEqual(
            len(published),
            pair_count,
        )

        self.assertEqual(
            len(set(pair_ids)),
            pair_count,
            "Duplicate encounter publication.",
        )

        self.assertEqual(
            len(detector.history),
            len(before["detector_history"]) + pair_count,
        )

        self.assertEqual(
            len(resolver.history),
            len(before["resolver_history"]) + pair_count,
        )

        self.assertEqual(
            len(world.active_cronenberg_pair_encounters),
            pair_count,
        )

        # A second successful detection must be idempotent.
        with redirect_stdout(io.StringIO()):
            repeated = (
                world.detect_cronenberg_pair_encounters()
            )

        self.assertEqual(
            repeated,
            [],
            "Duplicate detection after a successful retry.",
        )

        published_after = [
            item
            for item in world.quantum_events
            if getattr(item, "name", None)
            == "cronenberg_quantum_pair_encountered"
        ]

        self.assertEqual(
            len(published_after),
            pair_count,
        )

    def test_detector_history_rollback(self):
        self.verify_case(
            1,
            ("both_survive",),
            "detector",
        )

    def test_spin_exchange_resolver_rollback(self):
        self.verify_case(
            2,
            ("spin_exchange",),
            "resolver",
        )

    def test_nested_quantum_tick_rollback(self):
        self.verify_case(
            3,
            ("quantum_tick",),
            "public",
            quantum=True,
        )

    def test_nested_quantum_merge_rollback(self):
        self.verify_case(
            4,
            ("quantum_merge",),
            "public_nested",
        )

    def test_nested_pair_consumption_rollback(self):
        self.verify_case(
            5,
            ("quantum_pair_consumption",),
            "public_nested",
        )

    def test_two_pairs_second_publication_rollback(self):
        self.verify_case(
            6,
            ("both_survive",),
            "second_pair",
            pair_count=2,
        )

    def test_geometry_creation_rollback(self):
        self.verify_case(
            7,
            ("geometry_shift",),
            "public",
        )

    def test_existing_geometry_rollback(self):
        self.verify_case(
            8,
            ("geometry_shift",),
            "public",
            quantum=True,
        )

    def test_multi_effect_batch_rollback(self):
        self.verify_case(
            9,
            (
                "quantum_tick",
                "property_sum",
                "quantum_merge",
            ),
            "public_nested",
            quantum=True,
        )


if __name__ == "__main__":
    unittest.main()
