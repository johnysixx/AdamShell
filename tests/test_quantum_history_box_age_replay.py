import random
import unittest

from universe.universe import Universe


class FixedChoice:
    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError("Missing empty possibility")
        return "empty"


class FixedRandom:
    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value


class QuantumHistoryBoxAgeReplayTests(unittest.TestCase):

    def make_source(self):
        source = Universe(universe_id="age-replay")
        source.enable_quantum_layer()

        # Disable spontaneous collapse in this fixture.
        source.should_collapse_quantum_box = (
            lambda _box: False
        )

        early = source.create_quantum_box(
            box_id="early",
            rng=random.Random(1),
        )

        for _ in range(2):
            source.tick_quantum_unprotected()

        late = source.create_quantum_box(
            box_id="late",
            rng=random.Random(2),
        )

        for _ in range(3):
            source.tick_quantum_unprotected()

        self.assertEqual(early.age_ticks, 5)
        self.assertEqual(late.age_ticks, 3)

        return source

    def test_combined_replay_restores_active_box_ages(self):
        source = self.make_source()

        target = Universe(universe_id="age-replay")
        target.enable_quantum_layer()

        result = target.replay_quantum_history(
            box_events=source.quantum_events,
            clock_events=source.quantum_clock_events,
        )

        self.assertEqual(
            [box.id for box in result],
            ["early", "late"],
        )
        self.assertEqual(
            [box.age_ticks for box in result],
            [5, 3],
        )
        self.assertEqual(
            [box.age_ticks for box in result],
            [box.age_ticks for box in source.quantum_boxes],
        )
        self.assertEqual(target.quantum_state.tick_count, 5)
        self.assertEqual(target.quantum_events, [])
        self.assertEqual(target.quantum_clock_events, [])

        # Age must also restore collapse probabilities.
        outcomes = [
            target.should_collapse_quantum_box(
                box,
                rng=FixedRandom(0.014),
            )
            for box in result
        ]

        self.assertEqual(outcomes, [True, False])

    def test_reused_box_id_uses_latest_creation_tick(self):
        source = Universe(universe_id="age-reuse")
        source.enable_quantum_layer()
        source.should_collapse_quantum_box = (
            lambda _box: False
        )

        source.create_quantum_box(
            box_id="reused",
            rng=random.Random(3),
        )

        for _ in range(2):
            source.tick_quantum_unprotected()

        source.open_quantum_box(
            "reused",
            rng=FixedChoice(),
        )

        replacement = source.create_quantum_box(
            box_id="reused",
            rng=random.Random(4),
        )

        for _ in range(3):
            source.tick_quantum_unprotected()

        target = Universe(universe_id="age-reuse")
        target.enable_quantum_layer()

        result = target.replay_quantum_history(
            box_events=source.quantum_events,
            clock_events=source.quantum_clock_events,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "reused")
        self.assertEqual(replacement.age_ticks, 3)
        self.assertEqual(result[0].age_ticks, 3)
        self.assertEqual(
            target.statistics.total_quantum_boxes_created,
            2,
        )
        self.assertEqual(
            target.statistics.total_quantum_boxes_disappeared,
            1,
        )

    def test_standalone_box_replay_does_not_infer_clock(self):
        source = self.make_source()

        target = Universe(universe_id="age-standalone")

        result = target.replay_quantum_box_history(
            source.quantum_events
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(
            [box.age_ticks for box in result],
            [0, 0],
        )
        self.assertEqual(target.quantum_state.tick_count, 0)


if __name__ == "__main__":
    unittest.main()
