import io
import random
import unittest

from contextlib import redirect_stdout
from types import SimpleNamespace

from universe.universe import Universe
from meeting_place.glass_shelf import GlassShelf
from meeting_place.bar_entity_policy import BarEntityPolicy


class FailOnceAppend(list):
    def __init__(self, values):
        super().__init__(values)
        self.armed = True

    def append(self, value):
        super().append(value)

        if self.armed:
            self.armed = False
            raise RuntimeError(
                "A41.4 injected failure"
            )


class CronenbergPublicationRollbackTests(
    unittest.TestCase
):

    @staticmethod
    def make_world(number, operation):
        with redirect_stdout(io.StringIO()):
            world = Universe(
                universe_id=f"a414_regression_{number}"
            )

            first = None
            second = None

            if operation != "manifest":
                first = (
                    world.create_cronenberg_from_quantum_error(
                        RuntimeError("A41.4 seed"),
                        "a414",
                        "seed",
                    )
                )

            if operation in ("merge", "consume"):
                second = (
                    world.create_cronenberg_quantum_counterpart(
                        first,
                        source="a414_seed",
                    ).counterpart
                )

                first.location = "between_layers"
                second.location = "between_layers"

            shelf = GlassShelf()

            world.meeting_place = SimpleNamespace(
                glass_shelf=shelf,
                bar_entity_policy=BarEntityPolicy(),
            )

        return world, first, second, shelf

    @staticmethod
    def execute(world, first, second, operation):
        if operation == "manifest":
            return world.create_cronenberg_from_quantum_error(
                RuntimeError("A41.4 regression"),
                "a414",
                "manifest",
            )

        if operation == "counterpart":
            return world.create_cronenberg_quantum_counterpart(
                first,
                source="a414_regression",
            )

        if operation == "merge":
            return world.merge_cronenberg_quantum_pair(
                first,
                second,
                source="a414_regression",
            )

        if operation == "consume":
            return world.resolve_quantum_pair_consumption(
                first,
                second,
            )

        raise AssertionError(
            f"Unknown operation: {operation}"
        )

    @staticmethod
    def fingerprint(world, participants, shelf):
        def entity_state(entity):
            quantum = entity.quantum_state
            links = entity.quantum_link_system

            return (
                id(entity),
                entity.active,
                entity.state,
                entity.location,
                entity.energy,
                entity.size,
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
            "cronenbergs": tuple(world.cronenbergs),
            "entities": tuple(world.entities),
            "events": tuple(world.quantum_events),
            "registry_ids": tuple(
                id(getattr(world, name))
                for name in (
                    "cronenbergs",
                    "entities",
                    "quantum_events",
                    "statistics",
                    "world",
                )
            ),
            "count": world.cronenberg_count,
            "participants": tuple(
                entity_state(entity)
                for entity in participants
            ),
            "energy": world.energy_pool,
            "dark_energy_exists": (
                "dark_energy" in world.__dict__
            ),
            "dark_energy": getattr(
                world, "dark_energy", None
            ),
            "statistics": world.statistics.public_state,
            "clock": world.quantum_state.to_dict(),
            "world_entries": tuple(
                (key, id(value))
                for key, value in world.world.items()
            ),
            "glass": (
                id(shelf.shared_glasses),
                tuple(
                    id(item)
                    for item in shelf.shared_glasses
                ),
                id(shelf.reserved_glasses),
                tuple(
                    id(item)
                    for item in shelf.reserved_glasses
                ),
                id(shelf.personal_glasses),
                tuple(
                    (key, id(value))
                    for key, value
                    in shelf.personal_glasses.items()
                ),
            ),
            "random": random.getstate(),
        }

    def verify_case(
        self,
        number,
        operation,
        failure_point,
    ):
        world, first, second, shelf = self.make_world(
            number,
            operation,
        )

        if failure_point == "events":
            world.quantum_events = FailOnceAppend(
                world.quantum_events
            )

        elif failure_point == "entities":
            world.entities = FailOnceAppend(
                world.entities
            )

        elif failure_point == "links":
            first.quantum_link_system.history = FailOnceAppend(
                first.quantum_link_system.history
            )

        else:
            self.fail(
                f"Unknown failure point: {failure_point}"
            )

        participants = tuple(
            item
            for item in (first, second)
            if item is not None
        )

        before = self.fingerprint(
            world, participants, shelf
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "A41.4 injected failure",
        ):
            with redirect_stdout(io.StringIO()):
                self.execute(
                    world,
                    first,
                    second,
                    operation,
                )

        after = self.fingerprint(
            world, participants, shelf
        )

        for component in before:
            self.assertEqual(
                after[component],
                before[component],
                f"Rollback changed {component}",
            )

        # Retry the original operation after failure.
        with redirect_stdout(io.StringIO()):
            result = self.execute(
                world,
                first,
                second,
                operation,
            )

        self.assertIsNotNone(result)

        self.assertEqual(
            world.cronenberg_count,
            before["count"] + 1,
        )

        self.assertEqual(
            len(world.cronenbergs),
            len(before["cronenbergs"]) + 1,
        )

        self.assertEqual(
            len(world.entities),
            len(before["entities"]) + 1,
        )

        self.assertEqual(
            len(world.quantum_events),
            len(before["events"]) + 1,
        )

        if operation == "counterpart":
            counterpart = result.counterpart

            self.assertEqual(
                first.quantum_state.counterpart_id,
                counterpart.id,
            )

            self.assertEqual(
                counterpart.quantum_state.counterpart_id,
                first.id,
            )

            self.assertTrue(
                first.quantum_link_system.has_link_to(
                    counterpart.id
                )
            )

        elif operation == "merge":
            self.assertFalse(first.active)
            self.assertFalse(second.active)
            self.assertTrue(result.merged.active)

        elif operation == "consume":
            self.assertFalse(first.active)
            self.assertFalse(second.active)
            self.assertTrue(result.recombined.active)

            self.assertGreater(
                world.energy_pool,
                before["energy"],
            )

            self.assertTrue(
                hasattr(world, "dark_energy")
            )

    def test_manifestation_event_failure(self):
        self.verify_case(
            1, "manifest", "events"
        )

    def test_counterpart_event_failure(self):
        self.verify_case(
            2, "counterpart", "events"
        )

    def test_merge_event_failure(self):
        self.verify_case(
            3, "merge", "events"
        )

    def test_consumption_event_failure(self):
        self.verify_case(
            4, "consume", "events"
        )

    def test_counterpart_link_history_failure(self):
        self.verify_case(
            5, "counterpart", "links"
        )

    def test_merge_entity_registration_failure(self):
        self.verify_case(
            6, "merge", "entities"
        )


if __name__ == "__main__":
    unittest.main()
