import io
import random
import unittest

from contextlib import redirect_stdout
from unittest.mock import patch

from universe.universe import Universe
from core.word.chronicle import Chronicle
from core.word.word import Word


class EmptyChoice:

    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError(
                "Empty box outcome unavailable."
            )
        return "empty"


class FailOnceList(list):

    def __init__(self):
        super().__init__()
        self.armed = True

    def extend(self, items):
        values = tuple(items)

        if self.armed:
            self.armed = False

            if values:
                super().append(values[0])

            raise RuntimeError(
                "a42_injected_replay_publication_failure"
            )

        return super().extend(values)


class A42CrossUniverseReplayIntegrationTests(
    unittest.TestCase
):

    def setUp(self):
        original_rng = random.getstate()
        self.addCleanup(
            random.setstate,
            original_rng,
        )

    @staticmethod
    def quiet(operation, *args, **kwargs):
        with redirect_stdout(io.StringIO()):
            return operation(*args, **kwargs)

    def make_world(self, identity):
        world = self.quiet(
            Universe,
            universe_id=identity,
        )

        self.quiet(
            world.enable_quantum_layer
        )

        world.should_collapse_quantum_box = (
            lambda _box: False
        )

        return world

    def make_source(self):
        source = self.make_world(
            "a42_replay_source"
        )

        self.quiet(
            source.create_quantum_box,
            box_id="a42_first",
            rng=random.Random(111),
        )

        self.quiet(
            source.tick_quantum_unprotected
        )
        self.quiet(
            source.tick_quantum_unprotected
        )

        opened = self.quiet(
            source.open_quantum_box,
            "a42_first",
            rng=EmptyChoice(),
        )

        self.assertEqual(
            opened.name,
            "empty_quantum_box_opened",
        )

        self.quiet(
            source.create_quantum_box,
            box_id="a42_second",
            rng=random.Random(222),
        )

        self.quiet(
            source.tick_quantum_unprotected
        )

        self.quiet(
            source.create_quantum_box,
            box_id="a42_third",
            rng=random.Random(333),
        )

        return source

    @staticmethod
    def fingerprint(world, include_history=True):
        state = {
            "clock": (
                world.quantum_state.to_dict()
            ),
            "statistics": (
                world.statistics.public_state
            ),
            "boxes": tuple(
                (
                    box.public_state,
                    box.age_ticks,
                )
                for box in world.quantum_boxes
            ),
        }

        if include_history:
            state["box_events"] = tuple(
                world.quantum_events
            )
            state["clock_events"] = tuple(
                world.quantum_clock_events
            )

        return state

    def replay(self, target, source, preserve=True):
        return self.quiet(
            target.replay_quantum_history,
            box_events=tuple(
                source.quantum_events
            ),
            clock_events=tuple(
                source.quantum_clock_events
            ),
            preserve_history=preserve,
        )

    def test_01_complete_cross_universe_replay(self):
        source = self.make_source()
        target = self.make_world(
            "a42_replay_target"
        )

        clock = target.quantum_state
        statistics = target.statistics
        boxes = target.quantum_boxes
        events = target.quantum_events
        clock_events = target.quantum_clock_events

        restored = self.replay(
            target,
            source,
        )

        self.assertEqual(
            self.fingerprint(target),
            self.fingerprint(source),
        )

        self.assertEqual(
            len(restored),
            2,
        )

        self.assertEqual(
            target.quantum_state.tick_count,
            3,
        )

        self.assertIs(
            target.quantum_state,
            clock,
        )
        self.assertIs(
            target.statistics,
            statistics,
        )
        self.assertIs(
            target.quantum_boxes,
            boxes,
        )
        self.assertIs(
            target.quantum_events,
            events,
        )
        self.assertIs(
            target.quantum_clock_events,
            clock_events,
        )

        for original, copy in zip(
            source.quantum_boxes,
            target.quantum_boxes,
        ):
            self.assertIsNot(
                original,
                copy,
            )

    def test_02_timeline_order_and_identity(self):
        source = self.make_source()
        target = self.make_world(
            "a42_timeline_target"
        )

        self.replay(target, source)

        timeline = (
            source.quantum_lifecycle_timeline()
        )

        target_timeline = (
            target.quantum_lifecycle_timeline()
        )

        self.assertIsInstance(
            timeline,
            tuple,
        )
        self.assertEqual(
            timeline,
            target_timeline,
        )
        self.assertEqual(
            timeline,
            source.quantum_lifecycle_timeline(),
        )

        self.assertEqual(
            len(timeline),
            len(source.quantum_events)
            + len(source.quantum_clock_events),
        )

        ticks = [
            event.tick
            for event in timeline
        ]

        self.assertEqual(
            ticks,
            sorted(ticks),
        )

        for original, copy in zip(
            source.quantum_events,
            target.quantum_events,
        ):
            self.assertIsNot(
                original,
                copy,
            )

    def test_03_independent_replay_forks(self):
        source = self.make_source()

        first = self.make_world(
            "a42_fork_one"
        )
        second = self.make_world(
            "a42_fork_two"
        )

        self.replay(first, source)
        self.replay(second, source)

        self.assertEqual(
            self.fingerprint(first),
            self.fingerprint(second),
        )

        source_before = self.fingerprint(
            source
        )
        second_before = self.fingerprint(
            second
        )

        self.quiet(
            first.tick_quantum_unprotected
        )

        self.assertEqual(
            first.quantum_state.tick_count,
            4,
        )
        self.assertEqual(
            second.quantum_state.tick_count,
            3,
        )

        self.assertEqual(
            self.fingerprint(source),
            source_before,
        )
        self.assertEqual(
            self.fingerprint(second),
            second_before,
        )

    def test_04_deterministic_continuation(self):
        source = self.make_source()
        target = self.make_world(
            "a42_continuation_target"
        )

        self.replay(target, source)

        for step in range(1, 6):
            with self.subTest(step=step):
                self.quiet(
                    source.tick_quantum_unprotected
                )
                self.quiet(
                    target.tick_quantum_unprotected
                )

                self.assertEqual(
                    self.fingerprint(source),
                    self.fingerprint(target),
                )

                self.assertEqual(
                    source.quantum_lifecycle_timeline(),
                    target.quantum_lifecycle_timeline(),
                )

        self.assertEqual(
            target.quantum_state.tick_count,
            8,
        )

        self.assertEqual(
            [
                box.age_ticks
                for box in target.quantum_boxes
            ],
            [6, 5],
        )

    def test_05_invalid_history_is_atomic(self):
        source = self.make_source()
        target = self.make_world(
            "a42_invalid_target"
        )

        before = self.fingerprint(
            target
        )

        clocks = tuple(
            source.quantum_clock_events
        )

        with self.assertRaises(ValueError):
            self.quiet(
                target.replay_quantum_history,
                box_events=tuple(
                    source.quantum_events
                ),
                clock_events=(
                    clocks[0],
                    clocks[0],
                ),
                preserve_history=True,
            )

        self.assertEqual(
            self.fingerprint(target),
            before,
        )

        self.replay(target, source)

        self.assertEqual(
            self.fingerprint(target),
            self.fingerprint(source),
        )

    def test_06_publication_rollback_and_retry(self):
        source = self.make_source()
        target = self.make_world(
            "a42_fault_target"
        )

        target.quantum_events = (
            FailOnceList()
        )

        boxes = target.quantum_boxes
        events = target.quantum_events
        clock_events = target.quantum_clock_events
        statistics = target.statistics
        clock = target.quantum_state

        before = self.fingerprint(
            target
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "a42_injected_replay_publication_failure",
        ):
            self.replay(target, source)

        self.assertEqual(
            self.fingerprint(target),
            before,
        )

        self.assertIs(
            target.quantum_boxes,
            boxes,
        )
        self.assertIs(
            target.quantum_events,
            events,
        )
        self.assertIs(
            target.quantum_clock_events,
            clock_events,
        )
        self.assertIs(
            target.statistics,
            statistics,
        )
        self.assertIs(
            target.quantum_state,
            clock,
        )

        self.assertFalse(
            events.armed
        )

        self.replay(target, source)

        self.assertEqual(
            self.fingerprint(target),
            self.fingerprint(source),
        )

    def test_07_atomic_symbolic_quantum_replay(self):
        source = self.make_source()

        chronicle = Chronicle()

        chronicle.record(
            Word("LetThereBeLight")
        )
        chronicle.record(
            Word("LetThereBeSpace")
        )

        self.quiet(
            chronicle.replay,
            source,
        )

        target = self.make_world(
            "a42_symbolic_target"
        )

        self.quiet(
            target.replay_symbolic_quantum_history,
            chronicle=chronicle,
            box_events=tuple(
                source.quantum_events
            ),
            clock_events=tuple(
                source.quantum_clock_events
            ),
            preserve_history=True,
        )

        self.assertEqual(
            self.fingerprint(target),
            self.fingerprint(source),
        )

        for field in (
            "light",
            "space",
            "chaos",
            "order",
        ):
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(target, field, None),
                    getattr(source, field, None),
                )

        self.assertEqual(
            target.quantum_lifecycle_timeline(),
            source.quantum_lifecycle_timeline(),
        )

    def test_08_runtime_only_replay(self):
        source = self.make_source()
        target = self.make_world(
            "a42_runtime_only"
        )

        self.replay(
            target,
            source,
            preserve=False,
        )

        self.assertEqual(
            self.fingerprint(
                target,
                include_history=False,
            ),
            self.fingerprint(
                source,
                include_history=False,
            ),
        )

        self.assertEqual(
            target.quantum_events,
            [],
        )
        self.assertEqual(
            target.quantum_clock_events,
            [],
        )

        for original, copy in zip(
            source.quantum_boxes,
            target.quantum_boxes,
        ):
            self.assertIsNot(
                original,
                copy,
            )

    def test_09_replay_uses_no_rng_or_uuid(self):
        source = self.make_source()
        target = self.make_world(
            "a42_no_randomness"
        )

        before_rng = random.getstate()

        with (
            patch(
                "core.entity.quantum_box.random.uniform",
                side_effect=AssertionError(
                    "Unexpected RNG usage in replay"
                ),
            ),
            patch(
                "core.entity.quantum_box.uuid.uuid4",
                side_effect=AssertionError(
                    "Unexpected UUID usage in replay"
                ),
            ),
        ):
            self.replay(
                target,
                source,
            )

        self.assertEqual(
            self.fingerprint(target),
            self.fingerprint(source),
        )

        self.assertEqual(
            random.getstate(),
            before_rng,
        )


if __name__ == "__main__":
    unittest.main()
