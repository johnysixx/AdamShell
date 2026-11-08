import io
import random
import unittest

from contextlib import redirect_stdout

from universe.quantum_state import UniverseQuantumState
from universe.universe import Universe
from universe.universe_statistics import UniverseStatistics


class FailOnceList(list):

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


class FailOnceQuantumState(UniverseQuantumState):

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

        if (
            name == "tick_count"
            and getattr(self, "armed", False)
        ):
            object.__setattr__(self, "armed", False)
            raise self.failure


class QuantumHistoryPublicationRollbackTests(
    unittest.TestCase
):

    @staticmethod
    def source():
        with redirect_stdout(io.StringIO()):
            source = Universe(universe_id="a38_source")
            source.enable_quantum_layer()

            source.should_collapse_quantum_box = (
                lambda _box: False
            )

            source.create_quantum_box(
                box_id="a38_box",
                rng=random.Random(38),
            )

            source.tick_quantum_unprotected()

        return source

    @staticmethod
    def target():
        with redirect_stdout(io.StringIO()):
            target = Universe(universe_id="a38_target")
            target.enable_quantum_layer()

        target.record_universe_state()
        target.statistics.total_cats_created = 7

        return target

    @staticmethod
    def replay(target, source):
        return target.replay_quantum_history(
            box_events=tuple(source.quantum_events),
            clock_events=tuple(
                source.quantum_clock_events
            ),
            preserve_history=True,
        )

    def test_publication_failures_rollback_and_retry(self):
        source = self.source()

        cases = (
            (
                "quantum_boxes",
                RuntimeError("A38 boxes failure"),
            ),
            (
                "statistics",
                RuntimeError("A38 statistics failure"),
            ),
            (
                "quantum_state",
                RuntimeError("A38 clock failure"),
            ),
            (
                "quantum_events",
                KeyboardInterrupt("A38 history interruption"),
            ),
            (
                "quantum_clock_events",
                SystemExit("A38 clock history interruption"),
            ),
        )

        for failure_point, failure in cases:
            with self.subTest(failure_point=failure_point):
                target = self.target()

                if failure_point in (
                    "quantum_boxes",
                    "quantum_events",
                    "quantum_clock_events",
                ):
                    setattr(
                        target,
                        failure_point,
                        FailOnceList(failure),
                    )

                elif failure_point == "statistics":
                    target.statistics = FailOnceStatistics()
                    target.statistics.total_cats_created = 7
                    target.statistics.failure = failure
                    target.statistics.armed = True

                elif failure_point == "quantum_state":
                    target.quantum_state = FailOnceQuantumState(
                        **target.quantum_state.to_dict()
                    )
                    target.quantum_state.failure = failure
                    target.quantum_state.armed = True

                boxes = target.quantum_boxes
                box_events = target.quantum_events
                clock_events = target.quantum_clock_events
                statistics = target.statistics
                quantum_state = target.quantum_state
                history = target.universe_history
                history_record = history[0]

                before_snapshot = target.snapshot
                before_statistics = (
                    statistics.public_state
                )
                before_clock = quantum_state.to_dict()

                with self.assertRaises(
                    type(failure)
                ) as caught:
                    self.replay(target, source)

                self.assertIs(
                    caught.exception,
                    failure,
                )

                # All original object identities survive.
                self.assertIs(
                    target.quantum_boxes,
                    boxes,
                )
                self.assertIs(
                    target.quantum_events,
                    box_events,
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
                    quantum_state,
                )
                self.assertIs(
                    target.universe_history,
                    history,
                )
                self.assertIs(
                    target.universe_history[0],
                    history_record,
                )

                # No partially published runtime survives.
                self.assertEqual(target.quantum_boxes, [])
                self.assertEqual(target.quantum_events, [])
                self.assertEqual(
                    target.quantum_clock_events,
                    [],
                )
                self.assertEqual(
                    target.statistics.public_state,
                    before_statistics,
                )
                self.assertEqual(
                    target.quantum_state.to_dict(),
                    before_clock,
                )
                self.assertEqual(
                    target.snapshot,
                    before_snapshot,
                )
                self.assertEqual(
                    target.universe_history,
                    [history_record],
                )

                # The injected fault fires only once.
                # A retry on the very same objects must
                # reconstruct the complete valid state.
                result = self.replay(target, source)

                self.assertEqual(
                    [box.id for box in result],
                    ["a38_box"],
                )
                self.assertEqual(
                    [box.age_ticks for box in result],
                    [1],
                )
                self.assertEqual(
                    target.quantum_state.to_dict(),
                    source.quantum_state.to_dict(),
                )
                self.assertEqual(
                    tuple(target.quantum_events),
                    tuple(source.quantum_events),
                )
                self.assertEqual(
                    tuple(target.quantum_clock_events),
                    tuple(source.quantum_clock_events),
                )
                self.assertEqual(
                    target.statistics.total_cats_created,
                    7,
                )
                self.assertIs(
                    target.universe_history[0],
                    history_record,
                )


if __name__ == "__main__":
    unittest.main()
