import random
import unittest

from core.entity.components import SpatialVector3
from universe.quantum_universe_space import (
    QuantumStaircase,
    QuantumUniverseSpace,
)


class DieBoxStub:
    public_state = {}

    def __init__(self):
        self.position = None

    def move_to(self, position):
        self.position = position


class QuantumStaircaseReplayTests(unittest.TestCase):

    def make_space(self):
        return QuantumUniverseSpace(DieBoxStub())

    def test_same_seed_reproduces_ids_and_geometry(self):
        first = self.make_space()
        second = self.make_space()

        first.reconfigure(
            cause="replay",
            rng=random.Random(12345),
        )
        second.reconfigure(
            cause="replay",
            rng=random.Random(12345),
        )

        self.assertEqual(
            first.configuration_seed,
            second.configuration_seed,
        )
        self.assertEqual(
            first.configuration_id,
            second.configuration_id,
        )
        self.assertEqual(
            first.staircases,
            second.staircases,
        )
        self.assertEqual(
            first.geometry_engine.public_state,
            second.geometry_engine.public_state,
        )

        self.assertIsNot(
            first.staircases[0],
            second.staircases[0],
        )

    def test_staircase_ids_are_unique(self):
        space = self.make_space()

        space.reconfigure(
            cause="identity-test",
            rng=random.Random(987),
        )

        ids = [
            staircase.id
            for staircase in space.staircases
        ]

        self.assertGreaterEqual(len(ids), 8)
        self.assertLessEqual(len(ids), 16)
        self.assertEqual(len(ids), len(set(ids)))

        for index, staircase in enumerate(space.staircases):
            self.assertIsInstance(
                staircase,
                QuantumStaircase,
            )

            self.assertEqual(
                staircase.id,
                (
                    f"staircase_{space.configuration_seed:016x}"
                    f"_{index:02x}"
                ),
            )

    def test_reconfiguration_replays_same_seed(self):
        space = self.make_space()

        space.reconfigure(
            cause="first",
            rng=random.Random(777),
        )
        first = tuple(space.staircases)
        first_seed = space.configuration_seed

        space.reconfigure(
            cause="second",
            rng=random.Random(777),
        )

        self.assertEqual(
            tuple(space.staircases),
            first,
        )
        self.assertEqual(
            space.configuration_seed,
            first_seed,
        )

    def test_identity_generation_does_not_consume_rng(self):
        space = self.make_space()

        actual_rng = random.Random(555)
        expected_rng = random.Random(555)

        space.reconfigure(
            cause="rng-contract",
            rng=actual_rng,
        )

        count = expected_rng.randint(8, 16)

        for _ in range(count):
            for _ in range(6):
                expected_rng.uniform(-10.0, 10.0)

            expected_rng.choice(
                [
                    "up",
                    "down",
                    "left",
                    "right",
                    "inverted",
                    "impossible",
                ]
            )
            expected_rng.uniform(1.0, 8.0)

        expected_seed = expected_rng.randint(
            0,
            2 ** 63 - 1,
        )

        self.assertEqual(
            space.configuration_seed,
            expected_seed,
        )
        self.assertEqual(
            actual_rng.getstate(),
            expected_rng.getstate(),
        )

    def test_default_reconfiguration_still_works(self):
        die_box = DieBoxStub()
        space = QuantumUniverseSpace(die_box)

        self.assertGreaterEqual(len(space.staircases), 8)
        self.assertLessEqual(len(space.staircases), 16)
        self.assertEqual(
            die_box.position,
            SpatialVector3.zero(),
        )

        previous_count = space.reconfiguration_count
        space.reconfigure(cause="ordinary-runtime")

        self.assertEqual(
            space.reconfiguration_count,
            previous_count + 1,
        )
        self.assertTrue(
            all(
                staircase.id.startswith("staircase_")
                for staircase in space.staircases
            )
        )


if __name__ == "__main__":
    unittest.main()
