import io
import random
import unittest

from contextlib import redirect_stdout

from universe.quantum_state import UniverseQuantumState
from universe.universe_statistics import UniverseStatistics
from universe.universe import Universe


class FailOnceClock(UniverseQuantumState):

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

        if (
            name == "tick_count"
            and getattr(self, "armed", False)
        ):
            object.__setattr__(self, "armed", False)
            raise self.failure


class FailOnceBoxes(list):

    def __init__(self, failure):
        super().__init__()
        self.failure = failure
        self.armed = True

    def extend(self, values):
        values = tuple(values)

        if self.armed:
            self.armed = False

            if values:
                super().append(values[0])

            raise self.failure

        return super().extend(values)


class FailOnceStatistics(UniverseStatistics):

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

        if (
            name == "total_quantum_collapses"
            and getattr(self, "armed", False)
        ):
            object.__setattr__(self, "armed", False)
            raise self.failure


class FixedEmptyChoice:

    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError(
                "Missing empty quantum outcome."
            )
        return "empty"


class QuantumStandaloneReplayPublicationRollbackTests(
    unittest.TestCase
):

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            target = Universe(universe_id=identity)
            target.enable_quantum_layer()

        return target

    def clock_source(self):
        source = self.universe("a40_clock_source")

        with redirect_stdout(io.StringIO()):
            source.tick_quantum_unprotected()
            source.tick_quantum_unprotected()

        return source

    def box_source(self):
        source = self.universe("a40_box_source")

        with redirect_stdout(io.StringIO()):
            source.create_quantum_box(
                box_id="a40_disappearing",
                rng=random.Random(40),
            )

            source.create_quantum_box(
                box_id="a40_survivor",
                rng=random.Random(41),
            )

            source.open_quantum_box(
                "a40_disappearing",
                observer="a40_observer",
                rng=FixedEmptyChoice(),
            )

        return source

    def test_clock_publication_rolls_back_and_retries(self):
        source = self.clock_source()
        events = tuple(source.quantum_clock_events)

        failures = (
            RuntimeError("A40 clock runtime failure"),
            KeyboardInterrupt("A40 clock interruption"),
            SystemExit("A40 clock cancellation"),
        )

        for failure in failures:
            with self.subTest(
                failure_type=type(failure).__name__
            ):
                target = self.universe(
                    "a40_clock_target"
                )

                target.record_universe_state()

                clock = FailOnceClock(
                    **target.quantum_state.to_dict()
                )

                target.quantum_state = clock
                clock.failure = failure
                clock.armed = True

                clock_before = clock.to_dict()
                snapshot_before = target.snapshot

                history = target.universe_history
                history_record = history[0]

                statistics = target.statistics
                boxes = target.quantum_boxes
                box_events = target.quantum_events
                clock_events = target.quantum_clock_events

                with self.assertRaises(
                    type(failure)
                ) as caught:
                    target.replay_quantum_clock_history(
                        events
                    )

                self.assertIs(
                    caught.exception,
                    failure,
                )

                # Same objects, no partial clock state.
                self.assertIs(target.quantum_state, clock)
                self.assertIs(target.statistics, statistics)
                self.assertIs(target.quantum_boxes, boxes)
                self.assertIs(target.quantum_events, box_events)
                self.assertIs(
                    target.quantum_clock_events,
                    clock_events,
                )

                self.assertEqual(
                    clock.to_dict(),
                    clock_before,
                )

                self.assertEqual(
                    target.snapshot,
                    snapshot_before,
                )

                self.assertEqual(target.quantum_boxes, [])
                self.assertEqual(target.quantum_events, [])
                self.assertEqual(
                    target.quantum_clock_events,
                    [],
                )

                self.assertIs(
                    target.universe_history,
                    history,
                )

                self.assertIs(
                    target.universe_history[0],
                    history_record,
                )

                # The same clock must accept a valid
                # replay after the injected failure.
                result = target.replay_quantum_clock_history(
                    events
                )

                self.assertIs(result, clock)

                self.assertEqual(
                    clock.to_dict(),
                    source.quantum_state.to_dict(),
                )

                self.assertEqual(clock.tick_count, 2)

                # Standalone replay reconstructs runtime,
                # but does not append clock history.
                self.assertEqual(
                    target.quantum_clock_events,
                    [],
                )

    def test_box_publication_rolls_back_and_retries(self):
        source = self.box_source()
        events = tuple(source.quantum_events)

        self.assertEqual(
            source.statistics.total_quantum_boxes_created,
            2,
        )
        self.assertEqual(
            source.statistics.total_quantum_collapses,
            1,
        )
        self.assertEqual(
            source.statistics.total_quantum_boxes_disappeared,
            1,
        )

        cases = (
            (
                "boxes",
                RuntimeError("A40 box append failure"),
            ),
            (
                "boxes",
                KeyboardInterrupt("A40 box interruption"),
            ),
            (
                "statistics",
                RuntimeError("A40 statistics failure"),
            ),
            (
                "statistics",
                SystemExit("A40 statistics interruption"),
            ),
        )

        for failure_point, failure in cases:
            with self.subTest(
                failure_point=failure_point,
                failure_type=type(failure).__name__,
            ):
                target = self.universe(
                    "a40_box_target"
                )

                target.record_universe_state()

                if failure_point == "boxes":
                    target.quantum_boxes = FailOnceBoxes(
                        failure
                    )

                else:
                    statistics = FailOnceStatistics()
                    statistics.total_cats_created = 7
                    statistics.failure = failure
                    statistics.armed = True

                    target.statistics = statistics

                if failure_point == "boxes":
                    target.statistics.total_cats_created = 7

                boxes = target.quantum_boxes
                statistics = target.statistics
                clock = target.quantum_state
                box_events = target.quantum_events
                clock_events = target.quantum_clock_events
                history = target.universe_history
                history_record = history[0]

                snapshot_before = target.snapshot
                statistics_before = statistics.public_state
                clock_before = clock.to_dict()

                with self.assertRaises(
                    type(failure)
                ) as caught:
                    target.replay_quantum_box_history(
                        events
                    )

                self.assertIs(
                    caught.exception,
                    failure,
                )

                self.assertIs(target.quantum_boxes, boxes)
                self.assertIs(target.statistics, statistics)
                self.assertIs(target.quantum_state, clock)
                self.assertIs(target.quantum_events, box_events)
                self.assertIs(
                    target.quantum_clock_events,
                    clock_events,
                )
                self.assertIs(target.universe_history, history)
                self.assertIs(
                    target.universe_history[0],
                    history_record,
                )

                # Failed publication leaves no objects,
                # statistics, history or clock changes.
                self.assertEqual(target.quantum_boxes, [])
                self.assertEqual(target.quantum_events, [])
                self.assertEqual(
                    target.quantum_clock_events,
                    [],
                )
                self.assertEqual(
                    statistics.public_state,
                    statistics_before,
                )
                self.assertEqual(
                    clock.to_dict(),
                    clock_before,
                )
                self.assertEqual(
                    target.snapshot,
                    snapshot_before,
                )

                result = target.replay_quantum_box_history(
                    events
                )

                self.assertEqual(
                    [box.id for box in result],
                    ["a40_survivor"],
                )

                self.assertEqual(
                    [box.public_state for box in result],
                    [
                        box.public_state
                        for box in source.quantum_boxes
                    ],
                )

                self.assertEqual(
                    target.statistics.total_quantum_boxes_created,
                    2,
                )
                self.assertEqual(
                    target.statistics.total_quantum_collapses,
                    1,
                )
                self.assertEqual(
                    target.statistics.total_quantum_boxes_disappeared,
                    1,
                )

                self.assertEqual(
                    target.statistics.total_cats_created,
                    7,
                )

                self.assertEqual(
                    target.quantum_events,
                    [],
                )
                self.assertEqual(
                    target.quantum_clock_events,
                    [],
                )

                self.assertIs(
                    target.universe_history[0],
                    history_record,
                )


if __name__ == "__main__":
    unittest.main()
