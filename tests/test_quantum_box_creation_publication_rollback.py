import io
import random
import unittest

from contextlib import nullcontext, redirect_stdout
from unittest.mock import patch

from universe.logger import UniverseLogger
from universe.universe import Universe
from universe.universe_statistics import UniverseStatistics
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)


class FailOnceAppend(list):

    def __init__(self, failure):
        super().__init__()
        self.failure = failure
        self.armed = True

    def append(self, value):
        super().append(value)

        if self.armed:
            self.armed = False
            raise self.failure


class FailOnceStatistics(UniverseStatistics):

    def record_quantum_box_created(self):
        super().record_quantum_box_created()

        if self.armed:
            self.armed = False
            raise self.failure


class QuantumBoxCreationPublicationRollbackTests(
    unittest.TestCase
):

    @staticmethod
    def make_target():
        with redirect_stdout(io.StringIO()):
            target = Universe(
                universe_id="a41_creation_target"
            )
            target.enable_quantum_layer()

        target.record_universe_state()
        target.statistics.total_cats_created = 7

        return target

    @staticmethod
    def create(target):
        return target.create_quantum_box(
            box_id="a41_created_box",
            layer="meeting_place",
            rng=random.Random(41),
        )

    def test_failed_creation_rolls_back_and_retries(self):
        cases = (
            (
                "boxes",
                RuntimeError("A41 boxes failure"),
            ),
            (
                "statistics",
                RuntimeError("A41 statistics failure"),
            ),
            (
                "events",
                KeyboardInterrupt("A41 history interruption"),
            ),
            (
                "events",
                SystemExit("A41 history cancellation"),
            ),
            (
                "logging",
                RuntimeError("A41 logging failure"),
            ),
        )

        for failure_point, failure in cases:
            with self.subTest(
                failure_point=failure_point,
                failure_type=type(failure).__name__,
            ):
                target = self.make_target()

                if failure_point == "boxes":
                    target.quantum_boxes = FailOnceAppend(
                        failure
                    )

                elif failure_point == "events":
                    target.quantum_events = FailOnceAppend(
                        failure
                    )

                elif failure_point == "statistics":
                    statistics = FailOnceStatistics()
                    statistics.total_cats_created = 7
                    statistics.failure = failure
                    statistics.armed = True

                    target.statistics = statistics

                boxes = target.quantum_boxes
                events = target.quantum_events
                clock_events = target.quantum_clock_events
                clock = target.quantum_state
                statistics = target.statistics
                history = target.universe_history
                history_record = history[0]

                boxes_before = tuple(boxes)
                events_before = tuple(events)
                clock_events_before = tuple(clock_events)

                statistics_before = statistics.public_state
                clock_before = clock.to_dict()
                snapshot_before = target.snapshot

                logging_failure = (
                    patch.object(
                        UniverseLogger,
                        "event",
                        side_effect=failure,
                    )
                    if failure_point == "logging"
                    else nullcontext()
                )

                # Fail after some or all of the state
                # has already been changed.
                with logging_failure:
                    with self.assertRaises(
                        type(failure)
                    ) as caught:
                        with redirect_stdout(io.StringIO()):
                            self.create(target)

                self.assertIs(caught.exception, failure)

                # No canonical object was replaced.
                self.assertIs(target.quantum_boxes, boxes)
                self.assertIs(target.quantum_events, events)
                self.assertIs(
                    target.quantum_clock_events,
                    clock_events,
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
                    target.universe_history,
                    history,
                )
                self.assertIs(
                    target.universe_history[0],
                    history_record,
                )

                # No half-created box or orphan event.
                self.assertEqual(
                    tuple(target.quantum_boxes),
                    boxes_before,
                )
                self.assertEqual(
                    tuple(target.quantum_events),
                    events_before,
                )
                self.assertEqual(
                    tuple(target.quantum_clock_events),
                    clock_events_before,
                )
                self.assertEqual(
                    target.statistics.public_state,
                    statistics_before,
                )
                self.assertEqual(
                    target.quantum_state.to_dict(),
                    clock_before,
                )
                self.assertEqual(
                    target.snapshot,
                    snapshot_before,
                )

                self.assertEqual(
                    len(target.quantum_boxes),
                    0,
                )
                self.assertEqual(
                    len(target.quantum_events),
                    0,
                )

                # Retry the exact same box ID on the
                # same original registry objects.
                with redirect_stdout(io.StringIO()):
                    box = self.create(target)

                self.assertEqual(
                    box.id,
                    "a41_created_box",
                )
                self.assertEqual(
                    box.current_layer,
                    "meeting_place",
                )
                self.assertEqual(
                    target.quantum_boxes,
                    [box],
                )
                self.assertEqual(
                    len(target.quantum_events),
                    1,
                )

                event = target.quantum_events[0]

                self.assertIsInstance(
                    event,
                    QuantumBoxCreatedEvent,
                )
                self.assertEqual(
                    event.box_id,
                    box.id,
                )
                self.assertEqual(
                    event.position,
                    box.position,
                )
                self.assertEqual(
                    event.layer,
                    "meeting_place",
                )
                self.assertEqual(event.tick, 0)

                self.assertEqual(
                    target.statistics.total_quantum_boxes_created,
                    1,
                )
                self.assertEqual(
                    target.statistics.total_cats_created,
                    7,
                )
                self.assertEqual(
                    target.quantum_state.to_dict(),
                    clock_before,
                )
                self.assertEqual(
                    target.quantum_clock_events,
                    [],
                )

                self.assertIs(
                    target.universe_history[0],
                    history_record,
                )

                # A successful retry must produce a
                # valid, reconstructible lifecycle.
                target.quantum_lifecycle_timeline()

                restored = self.make_target()

                with redirect_stdout(io.StringIO()):
                    result = restored.replay_quantum_box_history(
                        tuple(target.quantum_events)
                    )

                self.assertEqual(
                    [item.public_state for item in result],
                    [box.public_state],
                )
                self.assertEqual(
                    restored.statistics.total_quantum_boxes_created,
                    1,
                )


if __name__ == "__main__":
    unittest.main()
