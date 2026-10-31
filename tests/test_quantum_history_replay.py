import random
import unittest
from dataclasses import replace
from unittest.mock import patch

from universe.universe import Universe


class FixedChoice:
    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError("Missing empty possibility")
        return "empty"


class QuantumHistoryReplayTests(unittest.TestCase):

    def make_source(self, active=False):
        source = Universe(universe_id="combined")
        source.enable_quantum_layer()

        # Prevent random collapses while producing
        # deterministic test histories.
        source.should_collapse_quantum_box = (
            lambda _box: False
        )

        source.create_quantum_box(
            box_id="combined_first",
            rng=random.Random(11),
        )

        source.tick_quantum_unprotected()
        source.tick_quantum_unprotected()

        source.open_quantum_box(
            "combined_first",
            rng=FixedChoice(),
        )

        if active:
            source.create_quantum_box(
                box_id="combined_second",
                rng=random.Random(22),
            )

        return source

    def make_target(self):
        target = Universe(universe_id="combined")
        target.enable_quantum_layer()
        return target

    def replay(self, target, source):
        return target.replay_quantum_history(
            box_events=source.quantum_events,
            clock_events=source.quantum_clock_events,
        )

    def test_complete_history_restores_both_subsystems(self):
        source = self.make_source()
        target = self.make_target()

        clock = target.quantum_state
        statistics = target.statistics
        box_collection = target.quantum_boxes

        result = self.replay(target, source)

        self.assertEqual(result, ())
        self.assertIs(target.quantum_state, clock)
        self.assertIs(target.statistics, statistics)
        self.assertIs(target.quantum_boxes, box_collection)

        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )
        self.assertEqual(
            target.statistics.public_state,
            source.statistics.public_state,
        )
        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )
        self.assertEqual(
            target.statistics.public_state,
            source.statistics.public_state,
        )
        self.assertEqual(
            [box.public_state for box in target.quantum_boxes],
            [box.public_state for box in source.quantum_boxes],
        )
        self.assertEqual(target.quantum_events, [])
        self.assertEqual(target.quantum_clock_events, [])

    def test_empty_histories_are_noop(self):
        target = Universe(universe_id="empty")

        before_snapshot = target.snapshot
        before_clock = target.quantum_state.to_dict()

        result = target.replay_quantum_history(
            box_events=(),
            clock_events=(),
        )

        self.assertEqual(result, ())
        self.assertEqual(target.snapshot, before_snapshot)
        self.assertEqual(
            target.quantum_state.to_dict(),
            before_clock,
        )

    def test_tick_zero_boxes_need_no_clock_events(self):
        source = Universe(universe_id="tick-zero")

        source.create_quantum_box(
            box_id="tick_zero_box",
            rng=random.Random(33),
        )
        source.open_quantum_box(
            "tick_zero_box",
            rng=FixedChoice(),
        )

        target = Universe(universe_id="tick-zero")

        result = target.replay_quantum_history(
            box_events=source.quantum_events,
            clock_events=(),
        )

        self.assertEqual(result, ())
        self.assertEqual(target.snapshot, source.snapshot)
        self.assertEqual(target.quantum_state.tick_count, 0)

    def test_clock_only_history(self):
        source = Universe(universe_id="clock-only")
        source.enable_quantum_layer()

        for _ in range(3):
            source.tick_quantum_unprotected()

        target = Universe(universe_id="clock-only")
        target.enable_quantum_layer()

        result = target.replay_quantum_history(
            box_events=(),
            clock_events=source.quantum_clock_events,
        )

        self.assertEqual(result, ())
        self.assertEqual(target.quantum_boxes, [])
        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )

    def test_partial_history_preserves_active_box(self):
        source = self.make_source(active=True)
        target = self.make_target()

        result = self.replay(target, source)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].id,
            "combined_second",
        )
        self.assertIs(target.quantum_boxes[0], result[0])

        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )
        self.assertEqual(
            target.statistics.public_state,
            source.statistics.public_state,
        )
        self.assertEqual(
            [box.public_state for box in target.quantum_boxes],
            [box.public_state for box in source.quantum_boxes],
        )
        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )

    def test_accepts_two_one_pass_generators(self):
        source = self.make_source(active=True)
        target = self.make_target()

        result = target.replay_quantum_history(
            box_events=(
                event for event in source.quantum_events
            ),
            clock_events=(
                event for event in source.quantum_clock_events
            ),
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )
        self.assertEqual(
            target.statistics.public_state,
            source.statistics.public_state,
        )
        self.assertEqual(
            [box.public_state for box in target.quantum_boxes],
            [box.public_state for box in source.quantum_boxes],
        )
        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )

    def test_invalid_late_box_event_preserves_clock(self):
        source = self.make_source()
        target = self.make_target()

        events = tuple(source.quantum_events)

        # This event passes the timeline validator,
        # but fails when applied to the staged box.
        invalid = replace(
            events[1],
            result="impossible_result",
        )
        bad_history = (
            events[0],
            invalid,
            *events[2:],
        )

        before_snapshot = target.snapshot
        before_clock = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            target.replay_quantum_history(
                box_events=bad_history,
                clock_events=source.quantum_clock_events,
            )

        self.assertEqual(target.snapshot, before_snapshot)
        self.assertEqual(
            target.quantum_state.to_dict(),
            before_clock,
        )
        self.assertEqual(target.quantum_clock_events, [])

    def test_invalid_clock_history_preserves_boxes(self):
        source = self.make_source()
        target = self.make_target()

        clock = tuple(source.quantum_clock_events)
        bad_clock = (
            clock[0],
            clock[0],
        )

        before_snapshot = target.snapshot
        before_clock = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            target.replay_quantum_history(
                box_events=source.quantum_events,
                clock_events=bad_clock,
            )

        self.assertEqual(target.snapshot, before_snapshot)
        self.assertEqual(
            target.quantum_state.to_dict(),
            before_clock,
        )

    def test_unrecorded_future_box_tick_is_atomic(self):
        source = self.make_source()
        target = self.make_target()

        future_creation = replace(
            source.quantum_events[0],
            tick=3,
        )

        before_snapshot = target.snapshot
        before_clock = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            target.replay_quantum_history(
                box_events=(future_creation,),
                clock_events=source.quantum_clock_events,
            )

        self.assertEqual(target.snapshot, before_snapshot)
        self.assertEqual(
            target.quantum_state.to_dict(),
            before_clock,
        )

    def test_existing_box_lifecycle_is_rejected(self):
        source = self.make_source()
        target = self.make_target()

        original = target.create_quantum_box(
            box_id="existing_box"
        )
        before_snapshot = target.snapshot
        before_clock = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            self.replay(target, source)

        self.assertIs(target.quantum_boxes[0], original)
        self.assertEqual(target.snapshot, before_snapshot)
        self.assertEqual(
            target.quantum_state.to_dict(),
            before_clock,
        )

    def test_existing_clock_lifecycle_is_rejected(self):
        source = self.make_source()
        target = self.make_target()

        target.tick_quantum_unprotected()

        before_snapshot = target.snapshot
        before_clock = target.quantum_state.to_dict()
        before_events = tuple(target.quantum_clock_events)

        with self.assertRaises(ValueError):
            self.replay(target, source)

        self.assertEqual(target.snapshot, before_snapshot)
        self.assertEqual(
            target.quantum_state.to_dict(),
            before_clock,
        )
        self.assertEqual(
            tuple(target.quantum_clock_events),
            before_events,
        )

    def test_unrelated_statistics_are_preserved(self):
        source = self.make_source()
        target = self.make_target()

        target.statistics.total_cats_created = 8
        target.statistics.total_dice_rolls = 2

        statistics = target.statistics

        self.replay(target, source)

        self.assertIs(target.statistics, statistics)
        self.assertEqual(
            target.statistics.total_cats_created,
            8,
        )
        self.assertEqual(
            target.statistics.total_dice_rolls,
            2,
        )
        self.assertEqual(
            target.statistics.total_quantum_boxes_created,
            1,
        )
        self.assertEqual(
            target.statistics.total_quantum_collapses,
            1,
        )

    def test_replay_uses_no_rng_uuid_or_simulation(self):
        source = self.make_source()
        target = self.make_target()

        with (
            patch.object(
                target,
                "should_collapse_quantum_box",
                side_effect=AssertionError(
                    "Simulation invoked"
                ),
            ),
            patch(
                "core.entity.quantum_box.random.choice",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.random.uniform",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.uuid.uuid4",
                side_effect=AssertionError("UUID used"),
            ),
        ):
            result = self.replay(target, source)

        self.assertEqual(result, ())
        self.assertEqual(target.quantum_state.tick_count, 2)

    def test_noniterable_streams_are_rejected_atomically(self):
        source = self.make_source()

        for box_events, clock_events in (
            (None, source.quantum_clock_events),
            (source.quantum_events, None),
        ):
            with self.subTest(
                invalid_box_stream=box_events is None
            ):
                target = self.make_target()
                before_snapshot = target.snapshot
                before_clock = target.quantum_state.to_dict()

                with self.assertRaises(TypeError):
                    target.replay_quantum_history(
                        box_events=box_events,
                        clock_events=clock_events,
                    )

                self.assertEqual(
                    target.snapshot,
                    before_snapshot,
                )
                self.assertEqual(
                    target.quantum_state.to_dict(),
                    before_clock,
                )


if __name__ == "__main__":
    unittest.main()
