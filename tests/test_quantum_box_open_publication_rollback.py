import io
import random
import unittest

from contextlib import redirect_stdout
from types import SimpleNamespace

from cats import Cats
from meeting_place.bar_entity_policy import BarEntityPolicy
from meeting_place.glass_shelf import GlassShelf
from quantum.error_boundary import QuantumErrorResult

from universe.universe import Universe
from universe.universe_statistics import UniverseStatistics
from universe.quantum_box_open_transaction import (
    QuantumBoxOpenTransaction,
)
from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)
from universe.quantum_box_disappearance_state import (
    QuantumBoxDisappearedEvent,
)
from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.manifestation_result_state import (
    CatManifestedEvent,
    EmptyQuantumBoxOpenedEvent,
)


class FixedChoice:

    def __init__(self, value):
        self.value = value

    def choice(self, possibilities):
        if self.value not in possibilities:
            raise AssertionError(
                "Requested quantum result is unavailable."
            )
        return self.value


class FailNthAppend(list):

    def __init__(self, values, failure_at, failure):
        super().__init__(values)
        self.failure_at = failure_at
        self.failure = failure
        self.calls = 0

    def append(self, value):
        self.calls += 1
        super().append(value)

        if self.calls == self.failure_at:
            raise self.failure


class FailOnceRemove(list):

    def __init__(self, values, failure):
        super().__init__(values)
        self.failure = failure
        self.armed = True

    def remove(self, value):
        super().remove(value)

        if self.armed:
            self.armed = False
            raise self.failure


class FailOnceStatistics(UniverseStatistics):

    def __init__(self, original, failure):
        super().__init__()
        self.__dict__.update(original.__dict__)
        self.failure = failure
        self.armed = True

    def record_quantum_collapse(self):
        super().record_quantum_collapse()

        if self.armed:
            self.armed = False
            raise self.failure


class QuantumBoxOpenPublicationRollbackTests(
    unittest.TestCase
):

    @staticmethod
    def make_world(identity):
        with redirect_stdout(io.StringIO()):
            world = Universe(universe_id=identity)
            world.enable_quantum_layer()

            box = world.create_quantum_box(
                box_id="a412_box",
                rng=random.Random(412),
            )

        world.record_universe_state()
        return world, box

    @staticmethod
    def box_fingerprint(box):
        return (
            box.state,
            box.content.resolved,
            box.collapse.collapsed,
            box.collapse.cause,
            box.collapse.observer,
            box.collapse.tick,
        )

    @staticmethod
    def glass_fingerprint(shelf):
        return (
            tuple(shelf.shared_glasses),
            tuple(shelf.reserved_glasses),
            dict(shelf.personal_glasses),
        )

    @staticmethod
    def add_bar(world):
        with redirect_stdout(io.StringIO()):
            shelf = GlassShelf()

        world.meeting_place = SimpleNamespace(
            glass_shelf=shelf,
            bar_entity_policy=BarEntityPolicy(),
        )
        return shelf

    @staticmethod
    def assert_successful_open(testcase, world, box, outcome, result):
        expected_type = (
            CatManifestedEvent
            if outcome == "cat"
            else EmptyQuantumBoxOpenedEvent
        )

        testcase.assertIsInstance(
            result,
            expected_type,
        )

        testcase.assertNotIn(
            box,
            world.quantum_boxes,
        )

        testcase.assertEqual(
            world.statistics.total_quantum_boxes_created,
            1,
        )
        testcase.assertEqual(
            world.statistics.total_quantum_collapses,
            1,
        )
        testcase.assertEqual(
            world.statistics.total_quantum_boxes_disappeared,
            1,
        )

        testcase.assertEqual(
            sum(
                isinstance(event, QuantumBoxCollapsedEvent)
                for event in world.quantum_events
            ),
            1,
        )

        testcase.assertEqual(
            sum(
                isinstance(event, QuantumBoxDisappearedEvent)
                for event in world.quantum_events
            ),
            1,
        )

        testcase.assertEqual(
            sum(
                isinstance(event, CatManifestedEvent)
                for event in world.quantum_events
            ),
            1 if outcome == "cat" else 0,
        )

        testcase.assertEqual(
            world.statistics.total_cats_created,
            1 if outcome == "cat" else 0,
        )

    def test_direct_transaction_rolls_back_and_retries(self):
        cases = (
            (
                "empty_collapse_event",
                "empty",
                "events",
                1,
                RuntimeError("collapse event failed"),
                False,
                False,
            ),
            (
                "empty_disappearance_event",
                "empty",
                "events",
                2,
                RuntimeError("disappearance event failed"),
                False,
                False,
            ),
            (
                "empty_removal",
                "empty",
                "remove",
                None,
                RuntimeError("removal failed"),
                False,
                False,
            ),
            (
                "empty_statistics",
                "empty",
                "statistics",
                None,
                RuntimeError("statistics failed"),
                False,
                False,
            ),
            (
                "cat_manifestation",
                "cat",
                "events",
                2,
                RuntimeError("cat event failed"),
                False,
                False,
            ),
            (
                "cat_existing_layer",
                "cat",
                "events",
                2,
                RuntimeError("resident layer failed"),
                True,
                False,
            ),
            (
                "cat_bar_side_effects",
                "cat",
                "events",
                3,
                RuntimeError("bar transaction failed"),
                False,
                True,
            ),
            (
                "empty_keyboard_interrupt",
                "empty",
                "events",
                2,
                KeyboardInterrupt("opening interrupted"),
                False,
                False,
            ),
            (
                "cat_system_exit",
                "cat",
                "events",
                3,
                SystemExit("opening cancelled"),
                False,
                False,
            ),
        )

        for (
            label,
            outcome,
            failure_point,
            failure_at,
            failure,
            existing_cats,
            with_bar,
        ) in cases:
            with self.subTest(case=label):
                world, box = self.make_world(label)

                if existing_cats:
                    with redirect_stdout(io.StringIO()):
                        cats = Cats(world)
                        resident = cats.create_cat(
                            name="resident_cat",
                            color="black",
                            fur_length="short",
                        )
                    self.assertIsNotNone(resident)

                shelf = (
                    self.add_bar(world)
                    if with_bar
                    else None
                )

                if failure_point == "events":
                    world.quantum_events = FailNthAppend(
                        world.quantum_events,
                        failure_at,
                        failure,
                    )

                elif failure_point == "remove":
                    world.quantum_boxes = FailOnceRemove(
                        world.quantum_boxes,
                        failure,
                    )

                elif failure_point == "statistics":
                    world.statistics = FailOnceStatistics(
                        world.statistics,
                        failure,
                    )

                boxes = world.quantum_boxes
                events = world.quantum_events
                entities = world.entities
                statistics = world.statistics
                clock = world.quantum_state
                clock_events = world.quantum_clock_events
                history = world.universe_history

                box_content = box.content
                box_collapse = box.collapse

                box_before = self.box_fingerprint(box)
                boxes_before = tuple(boxes)
                events_before = tuple(events)
                entities_before = tuple(entities)
                clock_events_before = tuple(clock_events)
                stats_before = statistics.public_state
                clock_before = clock.to_dict()
                world_before = dict(world.world)
                history_before = tuple(history)
                snapshot_before = world.snapshot

                cats_before_layer = getattr(
                    world,
                    "cats_layer",
                    None,
                )

                if cats_before_layer is not None:
                    cat_registry = cats_before_layer.cats
                    cat_events = cats_before_layer.events
                    cats_before = tuple(cat_registry)
                    cat_events_before = tuple(cat_events)

                if shelf is not None:
                    shared = shelf.shared_glasses
                    reserved = shelf.reserved_glasses
                    personal = shelf.personal_glasses
                    glass_before = self.glass_fingerprint(
                        shelf
                    )

                with self.assertRaises(
                    type(failure)
                ) as caught:
                    with redirect_stdout(io.StringIO()):
                        QuantumBoxOpenTransaction.execute(
                            world,
                            box_id=box.id,
                            observer="a412_observer",
                            rng=FixedChoice(outcome),
                        )

                self.assertIs(
                    caught.exception,
                    failure,
                )

                # Original canonical identities survive.
                self.assertIs(world.quantum_boxes, boxes)
                self.assertIs(world.quantum_events, events)
                self.assertIs(world.entities, entities)
                self.assertIs(world.statistics, statistics)
                self.assertIs(world.quantum_state, clock)
                self.assertIs(
                    world.quantum_clock_events,
                    clock_events,
                )
                self.assertIs(world.universe_history, history)

                self.assertEqual(
                    tuple(world.quantum_boxes),
                    boxes_before,
                )
                self.assertEqual(
                    tuple(world.quantum_events),
                    events_before,
                )
                self.assertEqual(
                    tuple(world.entities),
                    entities_before,
                )
                self.assertEqual(
                    tuple(world.quantum_clock_events),
                    clock_events_before,
                )
                self.assertEqual(
                    statistics.public_state,
                    stats_before,
                )
                self.assertEqual(
                    clock.to_dict(),
                    clock_before,
                )
                self.assertEqual(
                    tuple(world.universe_history),
                    history_before,
                )
                self.assertEqual(
                    world.snapshot,
                    snapshot_before,
                )

                self.assertEqual(
                    self.box_fingerprint(box),
                    box_before,
                )
                self.assertIs(box.content, box_content)
                self.assertIs(box.collapse, box_collapse)

                self.assertEqual(
                    set(world.world),
                    set(world_before),
                )
                for key, value in world_before.items():
                    self.assertIs(
                        world.world[key],
                        value,
                    )

                if cats_before_layer is None:
                    self.assertFalse(
                        hasattr(world, "cats_layer")
                    )
                else:
                    self.assertIs(
                        world.cats_layer,
                        cats_before_layer,
                    )
                    self.assertIs(
                        world.cats_layer.cats,
                        cat_registry,
                    )
                    self.assertIs(
                        world.cats_layer.events,
                        cat_events,
                    )
                    self.assertEqual(
                        tuple(cat_registry),
                        cats_before,
                    )
                    self.assertEqual(
                        tuple(cat_events),
                        cat_events_before,
                    )

                if shelf is not None:
                    self.assertIs(
                        shelf.shared_glasses,
                        shared,
                    )
                    self.assertIs(
                        shelf.reserved_glasses,
                        reserved,
                    )
                    self.assertIs(
                        shelf.personal_glasses,
                        personal,
                    )
                    self.assertEqual(
                        self.glass_fingerprint(shelf),
                        glass_before,
                    )

                # Direct transaction does not create
                # Cronenbergs. That belongs to the
                # surrounding QuantumErrorBoundary.
                self.assertEqual(world.cronenbergs, [])
                self.assertEqual(world.cronenberg_count, 0)

                # Retry the same box, same registries.
                with redirect_stdout(io.StringIO()):
                    result = QuantumBoxOpenTransaction.execute(
                        world,
                        box_id=box.id,
                        observer="a412_observer",
                        rng=FixedChoice(outcome),
                    )

                self.assert_successful_open(
                    self,
                    world,
                    box,
                    outcome,
                    result,
                )

                self.assertIs(world.quantum_boxes, boxes)
                self.assertIs(world.quantum_events, events)
                self.assertIs(world.entities, entities)

                if outcome == "cat":
                    self.assertTrue(
                        hasattr(world, "cats_layer")
                    )

                    expected_cat_count = (
                        len(cats_before)
                        if cats_before_layer is not None
                        else 0
                    ) + 1

                    self.assertEqual(
                        len(world.cats_layer.cats),
                        expected_cat_count,
                    )

    def test_public_boundary_preserves_cronenberg_and_retry(self):
        for outcome in ("empty", "cat"):
            with self.subTest(outcome=outcome):
                world, box = self.make_world(
                    "public_" + outcome
                )

                initial_history = tuple(
                    world.quantum_events
                )

                world.quantum_events = FailNthAppend(
                    initial_history,
                    2,
                    RuntimeError(
                        "A41.2 public history failure"
                    ),
                )

                event_registry = world.quantum_events
                box_registry = world.quantum_boxes
                original_box = self.box_fingerprint(box)

                with redirect_stdout(io.StringIO()):
                    failed = world.open_quantum_box(
                        box.id,
                        rng=FixedChoice(outcome),
                    )

                self.assertIsInstance(
                    failed,
                    QuantumErrorResult,
                )

                self.assertEqual(
                    failed.error_type,
                    "RuntimeError",
                )

                self.assertEqual(len(world.cronenbergs), 1)
                self.assertEqual(world.cronenberg_count, 1)

                self.assertIs(
                    failed.cronenberg,
                    world.cronenbergs[0],
                )

                self.assertIs(
                    world.quantum_boxes,
                    box_registry,
                )
                self.assertIs(
                    world.quantum_events,
                    event_registry,
                )

                self.assertEqual(
                    self.box_fingerprint(box),
                    original_box,
                )

                self.assertIn(box, world.quantum_boxes)

                self.assertEqual(
                    world.statistics.total_quantum_collapses,
                    0,
                )
                self.assertEqual(
                    world.statistics.total_quantum_boxes_disappeared,
                    0,
                )
                self.assertEqual(
                    world.statistics.total_cats_created,
                    0,
                )

                self.assertEqual(
                    sum(
                        isinstance(e, CatManifestedEvent)
                        for e in world.quantum_events
                    ),
                    0,
                )

                # Only the intended error record
                # follows the original creation event.
                appended = world.quantum_events[
                    len(initial_history):
                ]

                self.assertEqual(len(appended), 1)
                self.assertIsInstance(
                    appended[0],
                    CronenbergManifestedEvent,
                )
                self.assertEqual(
                    appended[0].cronenberg_id,
                    failed.cronenberg.id,
                )

                self.assertEqual(len(world.entities), 1)

                if outcome == "cat":
                    self.assertFalse(
                        hasattr(world, "cats_layer")
                    )

                # A successful retry must still work,
                # even after the canonical Cronenberg
                # error record was appended.
                with redirect_stdout(io.StringIO()):
                    result = world.open_quantum_box(
                        box.id,
                        rng=FixedChoice(outcome),
                    )

                self.assert_successful_open(
                    self,
                    world,
                    box,
                    outcome,
                    result,
                )

                self.assertEqual(
                    len(world.cronenbergs),
                    1,
                )

                self.assertEqual(
                    sum(
                        isinstance(e, CronenbergManifestedEvent)
                        for e in world.quantum_events
                    ),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
