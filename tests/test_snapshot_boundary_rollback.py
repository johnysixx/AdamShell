import io
import random
import unittest

from contextlib import redirect_stdout
from types import SimpleNamespace

from universe.universe import Universe
from universe.entity_tick_transaction import (
    EntityTickTransaction,
)
from universe.universe_phase_transaction import (
    UniversePhaseTransaction,
)


class GraphNode:
    def __init__(self):
        self.value = 1
        self.child = None


class PlainSlots:
    __slots__ = ("value",)

    def __init__(self):
        self.value = 1


class HybridSlots:
    __slots__ = ("slot_value", "__dict__")

    def __init__(self):
        self.slot_value = 1
        self.details = {"items": [1]}


class SnapshotBoundaryRollbackTests(unittest.TestCase):

    def setUp(self):
        rng_state = random.getstate()
        self.addCleanup(
            random.setstate,
            rng_state,
        )

    @staticmethod
    def make_world(number):
        with redirect_stdout(io.StringIO()):
            return Universe(
                universe_id=f"a419_regression_{number}"
            )

    @staticmethod
    def add_entity(world, name, **kwargs):
        item = SimpleNamespace(
            name=name,
            type="a419_probe",
            active=True,
            ticks=0,
            **kwargs,
        )

        with redirect_stdout(io.StringIO()):
            world.add_entity(item)

        return item

    def failed_entity(
        self,
        world,
        entity,
        mutation,
    ):
        def operation():
            mutation()
            raise RuntimeError("a419_injected")

        with redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(
                RuntimeError,
                "^a419_injected$",
            ):
                EntityTickTransaction.execute(
                    world,
                    entity,
                    operation,
                )

    def failed_phase(
        self,
        world,
        phase,
        mutation,
    ):
        def operation():
            mutation()
            raise RuntimeError("a419_injected")

        with redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(
                RuntimeError,
                "^a419_injected$",
            ):
                UniversePhaseTransaction.execute(
                    world,
                    phase,
                    operation,
                )

    def test_01_depth_twenty_graph_is_restored(self):
        world = self.make_world(1)
        root = GraphNode()
        leaf = root

        for _ in range(20):
            leaf.child = GraphNode()
            leaf = leaf.child

        entity = self.add_entity(
            world,
            "deep_graph",
            graph=root,
        )

        self.failed_entity(
            world,
            entity,
            lambda: setattr(leaf, "value", 500),
        )

        self.assertIs(entity.graph, root)
        self.assertEqual(leaf.value, 1)

    def test_02_plain_slots_state_is_restored(self):
        world = self.make_world(2)
        state = PlainSlots()

        entity = self.add_entity(
            world,
            "plain_slots",
            state=state,
        )

        self.failed_entity(
            world,
            entity,
            lambda: setattr(state, "value", 500),
        )

        self.assertIs(entity.state, state)
        self.assertEqual(state.value, 1)

    def test_03_nested_world_registry_is_restored(self):
        world = self.make_world(3)
        entity = self.add_entity(world, "world_mutator")

        registry = world.world
        nested = {"items": [1]}
        items = nested["items"]

        registry["a419"] = nested

        self.failed_entity(
            world,
            entity,
            lambda: items.append(2),
        )

        self.assertIs(world.world, registry)
        self.assertIs(registry["a419"], nested)
        self.assertIs(nested["items"], items)
        self.assertEqual(items, [1])

    def test_04_nested_entity_memory_is_restored(self):
        world = self.make_world(4)
        entity = self.add_entity(world, "memory_mutator")

        registry = world.entity_memory
        memory = {"entries": ["committed"]}
        entries = memory["entries"]

        registry["a419"] = memory

        self.failed_entity(
            world,
            entity,
            lambda: entries.append("partial"),
        )

        self.assertIs(world.entity_memory, registry)
        self.assertIs(registry["a419"], memory)
        self.assertIs(memory["entries"], entries)
        self.assertEqual(entries, ["committed"])

    def test_05_conflict_history_is_restored(self):
        world = self.make_world(5)
        entity = self.add_entity(
            world,
            "conflict_mutator",
        )

        registry = world.conflict_history
        before = tuple(registry)

        self.failed_entity(
            world,
            entity,
            lambda: registry.append("partial"),
        )

        self.assertIs(world.conflict_history, registry)
        self.assertEqual(tuple(registry), before)

    def test_06_symbolic_replay_outbox_is_restored(self):
        world = self.make_world(6)
        entity = self.add_entity(
            world,
            "replay_mutator",
        )

        registry = world.symbolic_replay_outbox
        before = tuple(registry)

        self.failed_entity(
            world,
            entity,
            lambda: registry.append("partial"),
        )

        self.assertIs(
            world.symbolic_replay_outbox,
            registry,
        )
        self.assertEqual(tuple(registry), before)

    def test_07_private_rng_is_restored(self):
        world = self.make_world(7)

        local_rng = random.Random(1234)
        entity = self.add_entity(
            world,
            "private_rng",
            rng=local_rng,
        )

        before = local_rng.getstate()

        self.failed_entity(
            world,
            entity,
            lambda: local_rng.random(),
        )

        self.assertIs(entity.rng, local_rng)
        self.assertEqual(
            local_rng.getstate(),
            before,
        )

    def test_08_history_failure_restores_lifecycle(self):
        world = self.make_world(8)

        lifecycle = world.life_cycle_system
        lifecycle.day = 3

        history = lifecycle.history
        before_history = tuple(history)

        def corrupt():
            lifecycle.day = 999
            lifecycle.history.append("partial")

            world.life_cycle_system = (
                SimpleNamespace(day=888)
            )

        self.failed_phase(
            world,
            "history",
            corrupt,
        )

        self.assertIs(
            world.life_cycle_system,
            lifecycle,
        )
        self.assertEqual(lifecycle.day, 3)
        self.assertIs(lifecycle.history, history)
        self.assertEqual(
            tuple(history),
            before_history,
        )

    def test_09_hybrid_dict_and_slots_are_restored(self):
        world = self.make_world(9)

        state = HybridSlots()
        items = state.details["items"]

        entity = self.add_entity(
            world,
            "hybrid_slots",
            state=state,
        )

        def corrupt():
            state.slot_value = 500
            items.append(2)
            state.new_attribute = "partial"

        self.failed_entity(
            world,
            entity,
            corrupt,
        )

        self.assertIs(entity.state, state)
        self.assertEqual(state.slot_value, 1)
        self.assertIs(state.details["items"], items)
        self.assertEqual(items, [1])
        self.assertFalse(
            hasattr(state, "new_attribute")
        )

    def test_10_prior_successful_entity_is_preserved(self):
        world = self.make_world(10)

        first = self.add_entity(
            world,
            "committed_entity",
            state={"energy": 10},
        )

        second = self.add_entity(
            world,
            "failing_entity",
        )

        committed_state = first.state

        with redirect_stdout(io.StringIO()):
            EntityTickTransaction.execute(
                world,
                first,
                lambda: committed_state.update(
                    energy=12
                ),
            )

        self.assertEqual(
            committed_state["energy"],
            12,
        )

        self.failed_entity(
            world,
            second,
            lambda: committed_state.update(
                energy=999
            ),
        )

        self.assertIs(first.state, committed_state)
        self.assertEqual(
            committed_state["energy"],
            12,
        )


if __name__ == "__main__":
    unittest.main()
