import unittest
from dataclasses import FrozenInstanceError

from gods.god_memory_state import (
    GodMemoryNote,
    GodMemorySnapshot,
    GodSharedMemory,
)
from gods.gods import Gods
from quantum.director import QuantumDirector
from universe.universe import Universe


class GodSharedMemoryObjectStateTests(unittest.TestCase):

    def test_memory_uses_immutable_snapshots(self):
        memory = GodSharedMemory()
        initial = memory.state

        memory.learn("tiamat_defeated")
        first = memory.state

        self.assertIsNot(first, initial)
        self.assertEqual(initial.knowledge, ())
        self.assertTrue(memory.knows("tiamat_defeated"))

        memory.learn("tiamat_defeated")
        self.assertIs(memory.state, first)

        note = GodMemoryNote("cosmos_ordered")
        memory.record(note)

        second = memory.state

        self.assertIsNot(second, first)
        self.assertEqual(first.observations, ())
        self.assertIs(memory.record_at(0), note)

        with self.assertRaises(FrozenInstanceError):
            second.knowledge = ()

        with self.assertRaises(TypeError):
            _ = memory["knowledge"]

        for method in ("get", "items", "keys", "values"):
            self.assertFalse(hasattr(memory, method))

    def test_memory_rejects_mapping_records(self):
        memory = GodSharedMemory()

        with self.assertRaises(TypeError):
            memory.record({"event": "legacy"})

        with self.assertRaises(TypeError):
            memory.learn({"finding": "legacy"})

        with self.assertRaises(TypeError):
            memory._snapshot = {}

        self.assertEqual(memory.record_count, 0)
        self.assertEqual(memory.state.knowledge, ())

    def test_god_masks_and_director_share_one_memory(self):
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god("god")

        director = QuantumDirector(
            universe=universe,
            god=god,
            gods=gods,
        )

        owner = god.shared_memory

        self.assertIs(director.shared_memory, owner)
        self.assertIs(director.mask.shared_memory, owner)

        marduk = gods.assume_mask(
            god=god,
            mask_name="marduk",
            role="divine_champion",
        )

        self.assertIs(marduk.shared_memory, owner)

        before = owner.state
        owner.learn("cosmos_ordered")

        self.assertIsNot(owner.state, before)
        self.assertEqual(before.knowledge, ())
        self.assertTrue(director.shared_memory.knows(
            "cosmos_ordered"
        ))

        gods.release_mask(god, "marduk")

        self.assertIs(marduk.shared_memory, owner)
        self.assertTrue(owner.knows("cosmos_ordered"))

    def test_god_rejects_invalid_memory_assignment(self):
        god = Gods(Universe()).create_god("god")

        original = god.shared_memory

        with self.assertRaises(TypeError):
            god.shared_memory = {}

        self.assertIs(god.shared_memory, original)


if __name__ == "__main__":
    unittest.main()
