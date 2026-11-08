import io
import random
import unittest

from contextlib import redirect_stdout

from universe.universe import Universe


class FailTwiceList(list):

    def __init__(self):
        super().__init__()
        self.remaining = 2

    def extend(self, values):
        values = tuple(values)

        if self.remaining:
            self.remaining -= 1

            if values:
                super().append(values[0])

            raise RuntimeError(
                "A39 injected publication failure"
            )

        return super().extend(values)


class FixedEmptyChoice:

    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError(
                "Empty collapse possibility missing."
            )

        return "empty"


class QuantumHistoryFailureForkTests(
    unittest.TestCase
):

    @staticmethod
    def make_universe(identity):
        with redirect_stdout(io.StringIO()):
            universe = Universe(
                universe_id=identity
            )
            universe.enable_quantum_layer()

        universe.should_collapse_quantum_box = (
            lambda _box: False
        )

        return universe

    @staticmethod
    def fingerprint(universe):
        return {
            "clock": universe.quantum_state.to_dict(),
            "statistics": universe.statistics.public_state,
            "boxes": tuple(
                (
                    box.public_state,
                    box.age_ticks,
                )
                for box in universe.quantum_boxes
            ),
            "box_events": tuple(
                universe.quantum_events
            ),
            "clock_events": tuple(
                universe.quantum_clock_events
            ),
        }

    def make_fork(
        self,
        identity,
        box_events,
        clock_events,
    ):
        fork = self.make_universe(identity)

        with redirect_stdout(io.StringIO()):
            fork.replay_quantum_history(
                box_events=box_events,
                clock_events=clock_events,
                preserve_history=True,
            )

        return fork

    @staticmethod
    def evolve(universe):
        with redirect_stdout(io.StringIO()):
            universe.create_quantum_box(
                box_id="a39_original",
                rng=random.Random(41),
            )

            universe.tick_quantum_unprotected()

            universe.create_quantum_box(
                box_id="a39_second",
                rng=random.Random(42),
            )

            universe.tick_quantum_unprotected()

    def test_failed_replays_do_not_contaminate_forks(self):
        foreign = self.make_universe(
            "a39_foreign"
        )

        with redirect_stdout(io.StringIO()):
            foreign.create_quantum_box(
                box_id="foreign_box",
                rng=random.Random(39),
            )
            foreign.tick_quantum_unprotected()

        foreign_boxes = tuple(
            foreign.quantum_events
        )
        foreign_clock = tuple(
            foreign.quantum_clock_events
        )

        foreign_before = self.fingerprint(foreign)

        target = self.make_universe(
            "a39_world"
        )
        control = self.make_universe(
            "a39_world"
        )

        target.record_universe_state()
        control.record_universe_state()

        faulty = FailTwiceList()
        target.quantum_boxes = faulty

        original_boxes = target.quantum_boxes
        original_events = target.quantum_events
        original_clock_events = (
            target.quantum_clock_events
        )
        original_state = target.quantum_state
        original_statistics = target.statistics
        original_history = target.universe_history
        original_history_record = (
            target.universe_history[0]
        )

        before = self.fingerprint(target)
        before_snapshot = target.snapshot
        before_history = tuple(target.universe_history)

        # Two failures must restore every canonical
        # object and all previously existing history.
        for attempt in (1, 2):
            with self.subTest(failed_attempt=attempt):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "A39 injected publication failure",
                ):
                    with redirect_stdout(io.StringIO()):
                        target.replay_quantum_history(
                            box_events=foreign_boxes,
                            clock_events=foreign_clock,
                            preserve_history=True,
                        )

                self.assertEqual(
                    self.fingerprint(target),
                    before,
                )

                self.assertIs(
                    target.quantum_boxes,
                    original_boxes,
                )
                self.assertIs(
                    target.quantum_events,
                    original_events,
                )
                self.assertIs(
                    target.quantum_clock_events,
                    original_clock_events,
                )
                self.assertIs(
                    target.quantum_state,
                    original_state,
                )
                self.assertIs(
                    target.statistics,
                    original_statistics,
                )
                self.assertIs(
                    target.universe_history,
                    original_history,
                )
                self.assertIs(
                    target.universe_history[0],
                    original_history_record,
                )

                self.assertEqual(
                    target.snapshot,
                    before_snapshot,
                )

                self.assertEqual(
                    tuple(target.universe_history),
                    before_history,
                )

        self.assertEqual(faulty.remaining, 0)

        # Continuing after both failures must produce
        # the same state as a never-failed control.
        self.evolve(target)
        self.evolve(control)

        self.assertEqual(
            self.fingerprint(target),
            self.fingerprint(control),
        )

        self.assertEqual(
            target.quantum_state.tick_count,
            2,
        )

        self.assertEqual(
            [box.age_ticks for box in target.quantum_boxes],
            [2, 1],
        )

        self.assertFalse(
            any(
                getattr(event, "box_id", None)
                == "foreign_box"
                for event in target.quantum_events
            )
        )

        base_boxes = tuple(
            target.quantum_events
        )
        base_clock = tuple(
            target.quantum_clock_events
        )
        base_state = self.fingerprint(target)

        # Both forks inherit the successful target
        # history, not the two failed replay attempts.
        left = self.make_fork(
            "a39_left",
            base_boxes,
            base_clock,
        )
        right = self.make_fork(
            "a39_right",
            base_boxes,
            base_clock,
        )

        self.assertEqual(
            self.fingerprint(left),
            base_state,
        )
        self.assertEqual(
            self.fingerprint(right),
            base_state,
        )

        self.assertIsNot(
            left.quantum_boxes[0],
            target.quantum_boxes[0],
        )
        self.assertIsNot(
            right.quantum_boxes[0],
            target.quantum_boxes[0],
        )
        self.assertIsNot(
            left.quantum_boxes[0],
            right.quantum_boxes[0],
        )

        self.assertIsNot(
            left.quantum_events[0],
            target.quantum_events[0],
        )
        self.assertIsNot(
            right.quantum_clock_events[0],
            target.quantum_clock_events[0],
        )

        # Branch A removes an existing box.
        with redirect_stdout(io.StringIO()):
            left.open_quantum_box(
                "a39_original",
                rng=FixedEmptyChoice(),
            )
            left.tick_quantum_unprotected()

        # Branch B creates a new box.
        with redirect_stdout(io.StringIO()):
            right.create_quantum_box(
                box_id="a39_right_future",
                rng=random.Random(43),
            )
            right.tick_quantum_unprotected()

        self.assertEqual(
            self.fingerprint(target),
            base_state,
        )

        self.assertNotEqual(
            self.fingerprint(left),
            self.fingerprint(right),
        )

        self.assertNotEqual(
            left.quantum_lifecycle_timeline(),
            right.quantum_lifecycle_timeline(),
        )

        # Each future must be independently
        # reconstructible from its own event streams.
        for branch in (left, right):
            with self.subTest(branch=branch.id):
                restored = self.make_fork(
                    branch.id + "_restored",
                    tuple(branch.quantum_events),
                    tuple(branch.quantum_clock_events),
                )

                self.assertEqual(
                    self.fingerprint(restored),
                    self.fingerprint(branch),
                )
                self.assertEqual(
                    restored.quantum_lifecycle_timeline(),
                    branch.quantum_lifecycle_timeline(),
                )

                self.assertIsNot(
                    restored.quantum_state,
                    branch.quantum_state,
                )

        # Source and parent never change when
        # constructing or evolving the branches.
        self.assertEqual(
            self.fingerprint(foreign),
            foreign_before,
        )
        self.assertEqual(
            self.fingerprint(target),
            base_state,
        )
        self.assertEqual(
            tuple(target.universe_history),
            before_history,
        )
        self.assertIs(
            target.universe_history[0],
            original_history_record,
        )
        self.assertEqual(
            tuple(foreign.quantum_events),
            foreign_boxes,
        )
        self.assertEqual(
            tuple(foreign.quantum_clock_events),
            foreign_clock,
        )


if __name__ == "__main__":
    unittest.main()
