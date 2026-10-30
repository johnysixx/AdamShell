import random
import unittest

from core.entity.quantum_box import QuantumBox
from universe.universe import Universe


class QuantumBoxReplayIdentityTests(unittest.TestCase):

    def test_explicit_identity_and_seed_reproduce_box(self):
        first = QuantumBox(
            rng=random.Random(123),
            box_id="quantum_box_replay_1",
        )
        second = QuantumBox(
            rng=random.Random(123),
            box_id="quantum_box_replay_1",
        )

        self.assertIsNot(first, second)
        self.assertEqual(first.id, second.id)
        self.assertEqual(first.position, second.position)
        self.assertEqual(
            first.public_state,
            second.public_state,
        )

    def test_independent_universes_reproduce_box_snapshots(self):
        first = Universe(universe_id="replay-world")
        second = Universe(universe_id="replay-world")

        for index in range(2):
            box_id = f"quantum_box_replay_{index}"

            first.create_quantum_box(
                rng=random.Random(100 + index),
                box_id=box_id,
            )
            second.create_quantum_box(
                rng=random.Random(100 + index),
                box_id=box_id,
            )

        self.assertEqual(
            first.snapshot,
            second.snapshot,
        )
        self.assertIsNot(
            first.quantum_boxes[0],
            second.quantum_boxes[0],
        )

    def test_duplicate_identity_is_rejected(self):
        universe = Universe(universe_id="duplicate-test")

        universe.create_quantum_box(
            box_id="quantum_box_existing",
        )

        with self.assertRaises(ValueError):
            universe.create_quantum_box(
                box_id="quantum_box_existing",
            )

        self.assertEqual(len(universe.quantum_boxes), 1)
        self.assertEqual(
            universe.statistics.total_quantum_boxes_created,
            1,
        )

    def test_invalid_explicit_identity_is_rejected(self):
        for box_id in ("", 123):
            with self.subTest(box_id=box_id):
                with self.assertRaises(ValueError):
                    QuantumBox(box_id=box_id)

    def test_default_identity_remains_automatic(self):
        box = QuantumBox(rng=random.Random(42))

        self.assertRegex(
            box.id,
            r"^quantum_box_[0-9a-f]{8}$",
        )
        self.assertEqual(
            box.state,
            "superposition",
        )


if __name__ == "__main__":
    unittest.main()
