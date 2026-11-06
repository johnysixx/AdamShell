import io
import random
import unittest
from contextlib import redirect_stdout
from dataclasses import replace

from core.word.chronicle import Chronicle
from core.word.word import Word
from universe.universe import Universe


SYMBOLIC_FIELDS = (
    "light",
    "space",
    "chaos",
    "order",
    "deep",
    "rules_modified",
)


class AtomicSymbolicQuantumReplayTests(unittest.TestCase):

    def setUp(self):
        self.chronicle = Chronicle()

        for name in (
            "LetThereBeLight",
            "LetThereBeSpace",
        ):
            self.chronicle.record(Word(name))

        with redirect_stdout(io.StringIO()):
            self.source = Universe(universe_id="a12_source")
            self.source.enable_quantum_layer()
            self.chronicle.replay(self.source)

            self.source.should_collapse_quantum_box = (
                lambda _box: False
            )

            self.source.create_quantum_box(
                box_id="a12_box",
                rng=random.Random(31),
            )

            self.source.tick_quantum_unprotected()
            self.source.tick_quantum_unprotected()

    @staticmethod
    def fingerprint(universe):
        return {
            "symbolic": tuple(
                (name, getattr(universe, name, None))
                for name in SYMBOLIC_FIELDS
            ),
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
            "box_history": tuple(universe.quantum_events),
            "clock_history": tuple(
                universe.quantum_clock_events
            ),
        }

    @staticmethod
    def make_target():
        with redirect_stdout(io.StringIO()):
            target = Universe(universe_id="a12_target")
            target.enable_quantum_layer()

        target.should_collapse_quantum_box = (
            lambda _box: False
        )
        return target

    def replay(self, target, **overrides):
        arguments = {
            "chronicle": self.chronicle,
            "box_events": self.source.quantum_events,
            "clock_events": self.source.quantum_clock_events,
            "preserve_history": True,
        }
        arguments.update(overrides)

        with redirect_stdout(io.StringIO()):
            return target.replay_symbolic_quantum_history(
                **arguments
            )

    def test_reconstructs_both_scopes_in_one_operation(self):
        target = self.make_target()

        clock = target.quantum_state
        statistics = target.statistics
        boxes = target.quantum_boxes
        box_events = target.quantum_events
        clock_events = target.quantum_clock_events

        result = self.replay(target)

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], target.quantum_boxes[0])

        self.assertIs(target.quantum_state, clock)
        self.assertIs(target.statistics, statistics)
        self.assertIs(target.quantum_boxes, boxes)
        self.assertIs(target.quantum_events, box_events)
        self.assertIs(target.quantum_clock_events, clock_events)

        self.assertEqual(
            self.fingerprint(target),
            self.fingerprint(self.source),
        )
        self.assertEqual(
            target.quantum_lifecycle_timeline(),
            self.source.quantum_lifecycle_timeline(),
        )

        self.assertIsNot(
            target.quantum_boxes[0],
            self.source.quantum_boxes[0],
        )
        self.assertIsNot(
            target.quantum_events[0],
            self.source.quantum_events[0],
        )

    def test_invalid_quantum_history_does_not_publish_words(self):
        target = self.make_target()
        before = self.fingerprint(target)

        clocks = tuple(self.source.quantum_clock_events)

        with self.assertRaises(ValueError):
            self.replay(
                target,
                clock_events=(clocks[0], clocks[0]),
            )

        self.assertEqual(self.fingerprint(target), before)
        self.assertIsNone(getattr(target, "light", None))
        self.assertIsNone(getattr(target, "space", None))

    def test_invalid_symbolic_history_does_not_publish_quantum(self):
        target = self.make_target()
        before = self.fingerprint(target)

        invalid = Chronicle()
        invalid.record(Word("LetThereBeLight"))
        invalid.record(object())

        with self.assertRaises(TypeError):
            self.replay(
                target,
                chronicle=invalid,
            )

        self.assertEqual(self.fingerprint(target), before)

    def test_history_copy_failure_is_atomic(self):
        target = self.make_target()
        before = self.fingerprint(target)

        class UncopyableLayer:
            def __deepcopy__(self, memo):
                raise ValueError("A12 copy failure")

        bad_creation = replace(
            self.source.quantum_events[0],
            layer=UncopyableLayer(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "A12 copy failure",
        ):
            self.replay(
                target,
                box_events=(bad_creation,),
            )

        self.assertEqual(self.fingerprint(target), before)

    def test_existing_target_history_rejects_without_changes(self):
        target = self.make_target()

        existing = self.source.quantum_clock_events[0]
        target.quantum_clock_events.append(existing)

        before = self.fingerprint(target)

        with self.assertRaises(ValueError):
            self.replay(target)

        self.assertEqual(self.fingerprint(target), before)

    def test_optional_runtime_only_mode(self):
        target = self.make_target()

        self.replay(
            target,
            preserve_history=False,
        )

        self.assertTrue(target.light)
        self.assertTrue(target.space)

        self.assertEqual(
            target.quantum_state.to_dict(),
            self.source.quantum_state.to_dict(),
        )

        self.assertEqual(
            [box.public_state for box in target.quantum_boxes],
            [box.public_state for box in self.source.quantum_boxes],
        )

        self.assertEqual(target.quantum_events, [])
        self.assertEqual(target.quantum_clock_events, [])

    def test_two_atomic_replays_are_independent(self):
        first = self.make_target()
        second = self.make_target()

        self.replay(first)
        self.replay(second)

        self.assertEqual(
            self.fingerprint(first),
            self.fingerprint(second),
        )

        self.assertIsNot(
            first.quantum_boxes[0],
            second.quantum_boxes[0],
        )

        before_second = self.fingerprint(second)
        before_source = self.fingerprint(self.source)

        with redirect_stdout(io.StringIO()):
            first.tick_quantum_unprotected()

        self.assertEqual(
            first.quantum_state.tick_count,
            3,
        )
        self.assertEqual(
            second.quantum_state.tick_count,
            2,
        )

        self.assertEqual(
            self.fingerprint(second),
            before_second,
        )
        self.assertEqual(
            self.fingerprint(self.source),
            before_source,
        )

        self.assertEqual(
            [event.tick for event in first.quantum_clock_events],
            [1, 2, 3],
        )

        self.assertEqual(
            len(first.quantum_lifecycle_timeline()),
            4,
        )


if __name__ == "__main__":
    unittest.main()
