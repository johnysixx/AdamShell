import random
import unittest
from unittest.mock import patch

from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_lifecycle_replayer import (
    QuantumBoxLifecycleReplayer,
)
from universe.universe import Universe


class FixedChoice:
    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError("Missing empty possibility")
        return "empty"


class QuantumBoxLifecycleReplayerComponentTests(
    unittest.TestCase
):

    def make_history(self):
        source = Universe(universe_id="component")

        for index in range(3):
            source.create_quantum_box(
                box_id=f"component_box_{index}",
                rng=random.Random(100 + index),
            )

        source.open_quantum_box(
            "component_box_0",
            rng=FixedChoice(),
        )

        return source, tuple(source.quantum_events)

    def test_universe_delegates_to_engine(self):
        target = Universe(universe_id="delegation")
        events = ()
        sentinel = object()

        with patch.object(
            QuantumBoxLifecycleReplayer,
            "replay",
            return_value=sentinel,
        ) as replay:
            result = target.replay_quantum_box_history(
                events
            )

        self.assertIs(result, sentinel)
        replay.assert_called_once_with(target, events)

    def test_component_reconstructs_multiple_boxes(self):
        source, events = self.make_history()
        target = Universe(universe_id="component")

        result = QuantumBoxLifecycleReplayer.replay(
            target,
            events,
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(
            [box.id for box in result],
            ["component_box_1", "component_box_2"],
        )
        self.assertEqual(target.snapshot, source.snapshot)
        self.assertEqual(target.quantum_events, [])

    def test_component_supports_partial_history(self):
        source, events = self.make_history()
        target = Universe(universe_id="partial")

        # Three creations followed by collapse,
        # but no disappearance.
        result = QuantumBoxLifecycleReplayer.replay(
            target,
            events[:-1],
        )

        self.assertEqual(len(result), 3)
        self.assertTrue(result[0].collapse.collapsed)
        self.assertEqual(result[0].content.resolved, "empty")
        self.assertEqual(
            target.statistics.total_quantum_boxes_disappeared,
            0,
        )

    def test_late_failure_does_not_mutate_target(self):
        _, events = self.make_history()
        target = Universe(universe_id="atomic")
        before = target.snapshot

        # Repeat an already completed disappearance.
        invalid_history = events + (events[-1],)

        with self.assertRaises(ValueError):
            QuantumBoxLifecycleReplayer.replay(
                target,
                invalid_history,
            )

        self.assertEqual(target.snapshot, before)
        self.assertEqual(target.quantum_events, [])

    def test_unsupported_event_is_atomic(self):
        _, events = self.make_history()
        target = Universe(universe_id="unsupported")
        before = target.snapshot

        with self.assertRaises(TypeError):
            QuantumBoxLifecycleReplayer.replay(
                target,
                events + (object(),),
            )

        self.assertEqual(target.snapshot, before)

    def test_component_accepts_one_pass_generator(self):
        source, events = self.make_history()
        target = Universe(universe_id="component")

        generator = (event for event in events)

        result = QuantumBoxLifecycleReplayer.replay(
            target,
            generator,
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(target.snapshot, source.snapshot)

    def test_unrelated_statistics_are_preserved(self):
        _, events = self.make_history()
        target = Universe(universe_id="statistics")

        target.statistics.total_cats_created = 7
        target.statistics.total_dice_rolls = 3

        QuantumBoxLifecycleReplayer.replay(
            target,
            events,
        )

        self.assertEqual(
            target.statistics.total_cats_created,
            7,
        )
        self.assertEqual(
            target.statistics.total_dice_rolls,
            3,
        )
        self.assertEqual(
            target.statistics.total_quantum_boxes_created,
            3,
        )
        self.assertEqual(
            target.statistics.total_quantum_boxes_disappeared,
            1,
        )

    def test_staging_does_not_call_universe_constructor(self):
        _, events = self.make_history()
        target = Universe(universe_id="constructor")

        with patch.object(
            Universe,
            "__init__",
            side_effect=AssertionError(
                "Universe constructor invoked during replay"
            ),
        ):
            result = QuantumBoxLifecycleReplayer.replay(
                target,
                events,
            )

        self.assertEqual(len(result), 2)

    def test_component_uses_no_rng_or_uuid(self):
        _, events = self.make_history()
        target = Universe(universe_id="deterministic")

        with (
            patch(
                "core.entity.quantum_box.random.uniform",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.random.choice",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.uuid.uuid4",
                side_effect=AssertionError("UUID used"),
            ),
        ):
            QuantumBoxLifecycleReplayer.replay(
                target,
                events,
            )

        self.assertEqual(len(target.quantum_boxes), 2)


if __name__ == "__main__":
    unittest.main()
