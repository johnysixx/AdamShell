import io
import random
import unittest
from contextlib import redirect_stdout

from universe.universe import Universe


class FixedEmptyChoice:
    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError("Missing empty possibility.")
        return "empty"


class QuantumHistoryForkTests(unittest.TestCase):

    def setUp(self):
        with redirect_stdout(io.StringIO()):
            self.source = Universe(
                universe_id="a10_source"
            )
            self.source.enable_quantum_layer()

            self.source.should_collapse_quantum_box = (
                lambda _box: False
            )

            self.source.create_quantum_box(
                box_id="a10_shared_box",
                rng=random.Random(31),
            )

            self.source.tick_quantum_unprotected()
            self.source.tick_quantum_unprotected()

            self.left = self.make_fork("a10_left")
            self.right = self.make_fork("a10_right")

    @staticmethod
    def fingerprint(universe):
        return {
            "clock": universe.quantum_state.to_dict(),
            "statistics": universe.statistics.public_state,
            "boxes": tuple(
                box.public_state
                for box in universe.quantum_boxes
            ),
            "ages": tuple(
                box.age_ticks
                for box in universe.quantum_boxes
            ),
        }

    @staticmethod
    def make_target(name):
        universe = Universe(universe_id=name)
        universe.enable_quantum_layer()

        universe.should_collapse_quantum_box = (
            lambda _box: False
        )

        return universe

    def make_fork(self, name):
        fork = self.make_target(name)

        fork.replay_quantum_history(
            box_events=tuple(self.source.quantum_events),
            clock_events=tuple(
                self.source.quantum_clock_events
            ),
            preserve_history=True,
        )

        return fork

    def test_forks_share_state_but_not_runtime_objects(self):
        self.assertEqual(
            self.fingerprint(self.source),
            self.fingerprint(self.left),
        )
        self.assertEqual(
            self.fingerprint(self.left),
            self.fingerprint(self.right),
        )

        self.assertEqual(
            self.source.quantum_lifecycle_timeline(),
            self.left.quantum_lifecycle_timeline(),
        )
        self.assertEqual(
            self.left.quantum_lifecycle_timeline(),
            self.right.quantum_lifecycle_timeline(),
        )

        source_box = self.source.quantum_boxes[0]
        left_box = self.left.quantum_boxes[0]
        right_box = self.right.quantum_boxes[0]

        self.assertIsNot(source_box, left_box)
        self.assertIsNot(source_box, right_box)
        self.assertIsNot(left_box, right_box)

        self.assertIsNot(
            self.left.quantum_state,
            self.right.quantum_state,
        )
        self.assertIsNot(
            self.left.quantum_events,
            self.right.quantum_events,
        )
        self.assertIsNot(
            self.left.quantum_events[0],
            self.right.quantum_events[0],
        )
        self.assertIsNot(
            self.left.quantum_clock_events[0],
            self.source.quantum_clock_events[0],
        )

        self.assertEqual(
            [event.tick for event in self.left.quantum_clock_events],
            [1, 2],
        )

    def test_divergent_futures_can_each_be_replayed(self):
        original = self.fingerprint(self.source)
        original_box_events = tuple(
            self.source.quantum_events
        )
        original_clock_events = tuple(
            self.source.quantum_clock_events
        )

        with redirect_stdout(io.StringIO()):
            # Branch A removes the original box.
            self.left.open_quantum_box(
                "a10_shared_box",
                rng=FixedEmptyChoice(),
            )

            # Branch B creates a different future.
            self.right.create_quantum_box(
                box_id="a10_right_box",
                rng=random.Random(77),
            )

            # Both advance to the same logical clock time.
            self.left.tick_quantum_unprotected()
            self.right.tick_quantum_unprotected()

        self.assertEqual(
            self.left.quantum_state.tick_count,
            3,
        )
        self.assertEqual(
            self.right.quantum_state.tick_count,
            3,
        )

        self.assertEqual(self.left.quantum_boxes, [])
        self.assertEqual(
            [box.id for box in self.right.quantum_boxes],
            ["a10_shared_box", "a10_right_box"],
        )

        self.assertNotEqual(
            self.fingerprint(self.left),
            self.fingerprint(self.right),
        )

        # Neither branch may change its parent.
        self.assertEqual(
            self.fingerprint(self.source),
            original,
        )
        self.assertEqual(
            tuple(self.source.quantum_events),
            original_box_events,
        )
        self.assertEqual(
            tuple(self.source.quantum_clock_events),
            original_clock_events,
        )

        # Both divergent event streams remain valid.
        left_timeline = self.left.quantum_lifecycle_timeline()
        right_timeline = self.right.quantum_lifecycle_timeline()

        self.assertNotEqual(left_timeline, right_timeline)

        # Independently replay both divergent branches.
        for branch in (self.left, self.right):
            with self.subTest(branch=branch.id):
                with redirect_stdout(io.StringIO()):
                    restored = self.make_target(
                        branch.id + "_restored"
                    )

                    restored.replay_quantum_history(
                        box_events=tuple(branch.quantum_events),
                        clock_events=tuple(
                            branch.quantum_clock_events
                        ),
                        preserve_history=True,
                    )

                self.assertEqual(
                    self.fingerprint(restored),
                    self.fingerprint(branch),
                )
                self.assertEqual(
                    restored.quantum_lifecycle_timeline(),
                    branch.quantum_lifecycle_timeline(),
                )

    def test_fork_history_collections_are_independent(self):
        source_boxes = tuple(self.source.quantum_events)
        source_clock = tuple(
            self.source.quantum_clock_events
        )
        right_boxes = tuple(self.right.quantum_events)
        right_clock = tuple(
            self.right.quantum_clock_events
        )

        self.left.quantum_events.clear()
        self.left.quantum_clock_events.clear()

        self.assertEqual(
            tuple(self.source.quantum_events),
            source_boxes,
        )
        self.assertEqual(
            tuple(self.source.quantum_clock_events),
            source_clock,
        )
        self.assertEqual(
            tuple(self.right.quantum_events),
            right_boxes,
        )
        self.assertEqual(
            tuple(self.right.quantum_clock_events),
            right_clock,
        )

        self.assertEqual(
            self.right.quantum_lifecycle_timeline(),
            self.source.quantum_lifecycle_timeline(),
        )


if __name__ == "__main__":
    unittest.main()
