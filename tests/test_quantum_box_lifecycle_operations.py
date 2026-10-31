import random
import unittest
from unittest.mock import patch

from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_lifecycle_operations import (
    QuantumBoxLifecycleOperations,
    QuantumBoxReplayStage,
)
from universe.universe import Universe


class FixedChoice:
    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError("Missing empty result")
        return "empty"


class QuantumBoxLifecycleOperationsTests(unittest.TestCase):

    def make_history(self):
        source = Universe(universe_id="operations")

        source.create_quantum_box(
            box_id="operations_box",
            rng=random.Random(42),
        )
        source.open_quantum_box(
            "operations_box",
            observer="tester",
            rng=FixedChoice(),
        )

        return source, tuple(source.quantum_events)

    def test_universe_methods_delegate_to_operations(self):
        target = Universe(universe_id="delegation")
        sentinel = object()

        methods = (
            ("replay_created", "replay_quantum_box_created"),
            ("replay_collapsed", "replay_quantum_box_collapsed"),
            (
                "replay_disappeared",
                "replay_quantum_box_disappeared",
            ),
        )

        for operation, wrapper in methods:
            with self.subTest(operation=operation):
                with patch.object(
                    QuantumBoxLifecycleOperations,
                    operation,
                    return_value=sentinel,
                ) as mocked:
                    result = getattr(target, wrapper)(
                        sentinel
                    )

                self.assertIs(result, sentinel)
                mocked.assert_called_once_with(
                    target,
                    sentinel,
                )

    def test_stage_is_explicit_object_state(self):
        stage = QuantumBoxReplayStage()

        self.assertEqual(stage.quantum_boxes, [])
        self.assertEqual(
            stage.statistics.total_quantum_boxes_created,
            0,
        )

        self.assertFalse(hasattr(stage, "get"))
        self.assertFalse(hasattr(stage, "__getitem__"))
        self.assertFalse(hasattr(stage, "__dict__"))

        with self.assertRaises(TypeError):
            _ = stage["quantum_boxes"]

    def test_direct_operations_reconstruct_full_lifecycle(self):
        source, events = self.make_history()
        created, collapsed, disappeared = events

        stage = QuantumBoxReplayStage()

        box = QuantumBoxLifecycleOperations.replay_created(
            stage, created
        )
        result = QuantumBoxLifecycleOperations.replay_collapsed(
            stage, collapsed
        )
        removed = (
            QuantumBoxLifecycleOperations.replay_disappeared(
                stage, disappeared
            )
        )

        self.assertIs(box, removed)
        self.assertEqual(result, collapsed)
        self.assertEqual(stage.quantum_boxes, [])
        self.assertEqual(
            stage.statistics.public_state,
            source.statistics.public_state,
        )

    def test_stage_retains_intermediate_collapsed_box(self):
        _, events = self.make_history()
        stage = QuantumBoxReplayStage()

        QuantumBoxLifecycleOperations.replay_created(
            stage, events[0]
        )
        QuantumBoxLifecycleOperations.replay_collapsed(
            stage, events[1]
        )

        self.assertEqual(len(stage.quantum_boxes), 1)
        self.assertTrue(
            stage.quantum_boxes[0].collapse.collapsed
        )
        self.assertEqual(
            stage.quantum_boxes[0].content.resolved,
            "empty",
        )
        self.assertEqual(
            stage.statistics.total_quantum_boxes_disappeared,
            0,
        )

    def test_unified_engine_does_not_use_universe_handlers(self):
        source, events = self.make_history()
        target = Universe(universe_id="operations")

        with (
            patch.object(
                Universe,
                "replay_quantum_box_created",
                side_effect=AssertionError(
                    "Universe creation handler used"
                ),
            ),
            patch.object(
                Universe,
                "replay_quantum_box_collapsed",
                side_effect=AssertionError(
                    "Universe collapse handler used"
                ),
            ),
            patch.object(
                Universe,
                "replay_quantum_box_disappeared",
                side_effect=AssertionError(
                    "Universe disappearance handler used"
                ),
            ),
        ):
            result = target.replay_quantum_box_history(
                events
            )

        self.assertEqual(result, ())
        self.assertEqual(target.snapshot, source.snapshot)

    def test_existing_public_methods_keep_returns(self):
        _, events = self.make_history()
        created, collapsed, disappeared = events

        target = Universe(universe_id="public")

        box = target.replay_quantum_box_created(created)
        result = target.replay_quantum_box_collapsed(
            collapsed
        )
        removed = target.replay_quantum_box_disappeared(
            disappeared
        )

        self.assertIs(removed, box)
        self.assertEqual(result, collapsed)
        self.assertEqual(target.quantum_boxes, [])
        self.assertEqual(
            target.statistics.total_quantum_collapses,
            1,
        )

    def test_duplicate_operations_do_not_change_statistics(self):
        _, events = self.make_history()
        created, collapsed, disappeared = events

        stage = QuantumBoxReplayStage()

        QuantumBoxLifecycleOperations.replay_created(
            stage, created
        )

        with self.assertRaises(ValueError):
            QuantumBoxLifecycleOperations.replay_created(
                stage, created
            )

        self.assertEqual(
            stage.statistics.total_quantum_boxes_created,
            1,
        )

        QuantumBoxLifecycleOperations.replay_collapsed(
            stage, collapsed
        )

        with self.assertRaises(ValueError):
            QuantumBoxLifecycleOperations.replay_collapsed(
                stage, collapsed
            )

        self.assertEqual(
            stage.statistics.total_quantum_collapses,
            1,
        )

        QuantumBoxLifecycleOperations.replay_disappeared(
            stage, disappeared
        )

        with self.assertRaises(ValueError):
            QuantumBoxLifecycleOperations.replay_disappeared(
                stage, disappeared
            )

        self.assertEqual(
            stage.statistics.total_quantum_boxes_disappeared,
            1,
        )

    def test_invalid_result_does_not_mutate_stage(self):
        _, events = self.make_history()
        stage = QuantumBoxReplayStage()

        box = QuantumBoxLifecycleOperations.replay_created(
            stage, events[0]
        )

        before = box.public_state

        invalid = QuantumBoxCollapsedEvent(
            quantum_box_id=box.id,
            result="invalid_result",
            cause="opened",
            observer=None,
            tick=0,
        )

        with self.assertRaises(ValueError):
            QuantumBoxLifecycleOperations.replay_collapsed(
                stage,
                invalid,
            )

        self.assertEqual(box.public_state, before)
        self.assertEqual(
            stage.statistics.total_quantum_collapses,
            0,
        )

    def test_unified_replay_uses_no_rng_or_uuid(self):
        source, events = self.make_history()
        target = Universe(universe_id="operations")

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
            result = target.replay_quantum_box_history(
                events
            )

        self.assertEqual(result, ())
        self.assertEqual(target.snapshot, source.snapshot)


if __name__ == "__main__":
    unittest.main()
