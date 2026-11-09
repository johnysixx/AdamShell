import io
import random
import unittest

from contextlib import redirect_stdout
from dataclasses import dataclass
from types import SimpleNamespace

from universe.universe import Universe


class ProbeEntity:
    def __init__(self, name, action=None):
        self.name = name
        self.type = "a416_regression_probe"
        self.active = True
        self.age = 0
        self.ticks = 0
        self.energy = 10.0
        self.state = "ready"
        self.observed = []
        self.action = action

    def tick(self, universe):
        self.ticks += 1
        if self.action is not None:
            self.action(self, universe)


@dataclass(slots=True)
class NestedSlotState:
    status: str
    values: list


class FrozenMember:
    def __init__(self):
        self.values = ["ready"]


class EntityTickRollbackTests(unittest.TestCase):

    @staticmethod
    def make_world(number, *entities):
        with redirect_stdout(io.StringIO()):
            world = Universe(
                universe_id=f"a416_regression_{number}"
            )
            for entity in entities:
                world.add_entity(entity)
        return world

    def run_entity_ticks(
        self,
        world,
        cronenberg_count=1,
    ):
        with redirect_stdout(io.StringIO()):
            results = world.tick_entities()

        failures = [
            item
            for item in results
            if type(item).__name__
            == "UniverseTickPhaseErrorResult"
        ]

        self.assertEqual(len(failures), 1)
        self.assertEqual(
            world.cronenberg_count,
            cronenberg_count,
        )
        self.assertEqual(
            type(results[-1]).__name__,
            "UniverseTickPhaseCompletedResult",
        )
        self.assertEqual(failures[0].phase, "entities")
        self.assertIsNotNone(
            failures[0].cronenberg_id
        )
        return results

    def test_01_failed_self_state_restored_attempt_recorded(self):
        def failure(entity, world):
            entity.age += 1
            entity.energy -= 4.0
            entity.state = "half_written"
            raise RuntimeError("a416-self")

        broken = ProbeEntity("broken_self", failure)
        world = self.make_world(1, broken)
        self.run_entity_ticks(world)

        self.assertEqual(
            (
                broken.age,
                broken.energy,
                broken.state,
                broken.ticks,
            ),
            (0, 10.0, "ready", 1),
        )

    def test_02_universe_energy_events_and_rng_boundary(self):
        def failure(entity, world):
            world.energy_pool -= 7.0
            world.quantum_events.append(
                SimpleNamespace(
                    name="a416_partial_event"
                )
            )
            random.random()
            raise RuntimeError("a416-universe")

        broken = ProbeEntity(
            "broken_universe",
            failure,
        )
        world = self.make_world(2, broken)

        before_energy = world.energy_pool
        before_events = tuple(world.quantum_events)
        before_rng = random.getstate()
        seen_rng = []

        original = (
            world.create_cronenberg_from_quantum_error
        )

        def observe_manifestation(*args, **kwargs):
            seen_rng.append(random.getstate())
            return original(*args, **kwargs)

        world.create_cronenberg_from_quantum_error = (
            observe_manifestation
        )

        self.run_entity_ticks(world)

        # RNG must be restored BEFORE the legitimate
        # Cronenberg manifestation consumes randomness.
        self.assertEqual(seen_rng, [before_rng])
        self.assertNotEqual(
            random.getstate(),
            before_rng,
        )

        self.assertEqual(
            world.energy_pool,
            before_energy,
        )
        self.assertEqual(
            len(world.quantum_events),
            len(before_events) + 1,
        )
        self.assertEqual(
            tuple(
                world.quantum_events[
                    :len(before_events)
                ]
            ),
            before_events,
        )
        self.assertFalse(any(
            getattr(item, "name", None)
            == "a416_partial_event"
            for item in world.quantum_events
        ))

    def test_03_failed_child_creation_does_not_leak(self):
        children = []

        def failure(entity, world):
            child = ProbeEntity("orphan_child")
            children.append(child)
            world.add_entity(child)
            raise RuntimeError("a416-spawn")

        broken = ProbeEntity(
            "broken_spawn",
            failure,
        )
        world = self.make_world(3, broken)
        original_registry = world.entities

        self.run_entity_ticks(world)

        self.assertIs(
            world.entities,
            original_registry,
        )
        self.assertNotIn(
            children[0],
            world.entities,
        )
        self.assertEqual(
            len(world.entities),
            2,
        )
        self.assertIn(
            broken,
            world.entities,
        )

    def test_04_failed_tick_does_not_disable_other_entity(self):
        healthy = ProbeEntity("healthy")

        def failure(entity, world):
            healthy.active = False
            raise RuntimeError("a416-disable")

        broken = ProbeEntity(
            "broken_disable",
            failure,
        )
        world = self.make_world(
            4,
            broken,
            healthy,
        )

        self.run_entity_ticks(world)

        self.assertTrue(healthy.active)
        self.assertEqual(healthy.ticks, 1)

    def test_05_failed_tick_does_not_corrupt_next_entity(self):
        def observe(entity, world):
            entity.observed.append(entity.energy)

        healthy = ProbeEntity(
            "healthy_observer",
            observe,
        )

        def failure(entity, world):
            healthy.energy += 5.0
            raise RuntimeError("a416-cross-energy")

        broken = ProbeEntity(
            "broken_corrupt",
            failure,
        )
        world = self.make_world(
            5,
            broken,
            healthy,
        )

        self.run_entity_ticks(world)

        self.assertEqual(
            healthy.energy,
            10.0,
        )
        self.assertEqual(
            healthy.observed,
            [10.0],
        )

    def test_06_repeated_failures_do_not_accumulate_simulation_state(self):
        def failure(entity, world):
            entity.age += 1
            entity.energy -= 2.0
            raise RuntimeError("a416-repeat")

        broken = ProbeEntity(
            "broken_repeat",
            failure,
        )
        world = self.make_world(6, broken)

        self.run_entity_ticks(
            world,
            cronenberg_count=1,
        )
        self.run_entity_ticks(
            world,
            cronenberg_count=2,
        )

        self.assertEqual(
            (
                broken.age,
                broken.energy,
                broken.ticks,
            ),
            (0, 10.0, 2),
        )

    def test_07_healthy_scheduler_continuation(self):
        def failure(entity, world):
            raise RuntimeError("a416-control")

        broken = ProbeEntity(
            "broken",
            failure,
        )
        healthy = ProbeEntity("healthy")

        world = self.make_world(
            7,
            broken,
            healthy,
        )

        self.run_entity_ticks(world)

        self.assertEqual(
            (broken.ticks, healthy.ticks),
            (1, 1),
        )

    def test_08_prior_successful_tick_remains_committed(self):
        def success(entity, world):
            entity.age += 2
            entity.energy -= 1.0
            entity.state = "advanced"

        good = ProbeEntity("good", success)

        def failure(entity, world):
            good.energy = 999.0
            good.state = "corrupted"
            raise RuntimeError("a416-late")

        broken = ProbeEntity("broken", failure)
        world = self.make_world(
            8,
            good,
            broken,
        )

        self.run_entity_ticks(world)

        self.assertEqual(
            (
                good.age,
                good.energy,
                good.state,
                good.ticks,
            ),
            (2, 9.0, "advanced", 1),
        )
        self.assertEqual(broken.ticks, 1)

    def test_09_nested_dict_list_and_object_identity(self):
        def failure(entity, world):
            entity.payload["flags"].append(
                "leaked"
            )
            entity.payload["meta"].status = (
                "corrupted"
            )
            entity.payload["extra"] = True
            raise RuntimeError("a416-nested")

        broken = ProbeEntity(
            "broken_nested",
            failure,
        )
        broken.payload = {
            "flags": ["ready"],
            "meta": SimpleNamespace(
                status="ready"
            ),
        }

        payload = broken.payload
        flags = payload["flags"]
        meta = payload["meta"]

        world = self.make_world(9, broken)
        self.run_entity_ticks(world)

        self.assertIs(
            broken.payload,
            payload,
        )
        self.assertIs(
            payload["flags"],
            flags,
        )
        self.assertIs(
            payload["meta"],
            meta,
        )
        self.assertEqual(flags, ["ready"])
        self.assertEqual(meta.status, "ready")
        self.assertNotIn("extra", payload)

    def test_10_deep_nested_list_state_restored(self):
        def failure(entity, world):
            entity.deep["middle"]["items"].append(
                "leaked"
            )
            raise RuntimeError("a416-deep")

        broken = ProbeEntity(
            "broken_deep",
            failure,
        )
        broken.deep = {
            "middle": {
                "items": ["ready"],
            }
        }

        deep = broken.deep
        middle = deep["middle"]
        items = middle["items"]

        world = self.make_world(10, broken)
        self.run_entity_ticks(world)

        self.assertIs(broken.deep, deep)
        self.assertIs(deep["middle"], middle)
        self.assertIs(middle["items"], items)
        self.assertEqual(items, ["ready"])

    def test_11_tuple_contained_mutable_state_restored(self):
        def failure(entity, world):
            entity.payload[0]["values"].append(
                "leaked"
            )
            raise RuntimeError("a416-tuple")

        broken = ProbeEntity(
            "broken_tuple",
            failure,
        )

        values = ["ready"]
        container = ({"values": values},)
        broken.payload = container

        world = self.make_world(11, broken)
        self.run_entity_ticks(world)

        self.assertIs(
            broken.payload,
            container,
        )
        self.assertIs(
            container[0]["values"],
            values,
        )
        self.assertEqual(values, ["ready"])

    def test_12_cyclic_object_graph_restored(self):
        def failure(entity, world):
            entity.graph["entries"].append(
                "leaked"
            )
            entity.graph["counter"] += 1
            raise RuntimeError("a416-cycle")

        broken = ProbeEntity(
            "broken_cycle",
            failure,
        )

        graph = {
            "entries": ["ready"],
            "counter": 0,
        }
        graph["self"] = graph

        entries = graph["entries"]
        broken.graph = graph

        world = self.make_world(12, broken)
        self.run_entity_ticks(world)

        self.assertIs(broken.graph, graph)
        self.assertIs(graph["self"], graph)
        self.assertIs(
            graph["entries"],
            entries,
        )
        self.assertEqual(
            entries,
            ["ready"],
        )
        self.assertEqual(
            graph["counter"],
            0,
        )

    def test_13_deep_chain_identity_and_state_restored(self):
        def failure(entity, world):
            node = entity.root
            for _ in range(9):
                node = node["next"]

            node["values"].append("leaked")
            raise RuntimeError("a416-chain")

        broken = ProbeEntity(
            "broken_chain",
            failure,
        )

        root = {}
        node = root

        for _ in range(9):
            following = {}
            node["next"] = following
            node = following

        original_values = ["ready"]
        node["values"] = original_values
        broken.root = root

        world = self.make_world(13, broken)
        self.run_entity_ticks(world)

        self.assertIs(
            broken.root,
            root,
        )
        self.assertIs(
            node["values"],
            original_values,
        )
        self.assertEqual(
            original_values,
            ["ready"],
        )

    def test_14_frozenset_contained_mutable_member_restored(self):
        member = FrozenMember()

        def failure(entity, world):
            next(
                iter(entity.members)
            ).values.append("leaked")
            raise RuntimeError("a416-frozenset")

        broken = ProbeEntity(
            "broken_frozen",
            failure,
        )

        members = frozenset((member,))
        broken.members = members
        values = member.values

        world = self.make_world(14, broken)
        self.run_entity_ticks(world)

        self.assertIs(
            broken.members,
            members,
        )
        self.assertIs(
            member.values,
            values,
        )
        self.assertEqual(values, ["ready"])

    def test_15_slots_dataclass_state_restored(self):
        def failure(entity, world):
            entity.nested.status = "corrupted"
            entity.nested.values.append(
                "leaked"
            )
            raise RuntimeError("a416-dataclass")

        broken = ProbeEntity(
            "broken_dataclass",
            failure,
        )

        nested = NestedSlotState(
            status="ready",
            values=["ready"],
        )
        broken.nested = nested
        values = nested.values

        world = self.make_world(15, broken)
        self.run_entity_ticks(world)

        self.assertIs(
            broken.nested,
            nested,
        )
        self.assertIs(
            nested.values,
            values,
        )
        self.assertEqual(
            nested.status,
            "ready",
        )
        self.assertEqual(
            values,
            ["ready"],
        )


if __name__ == "__main__":
    unittest.main()
