import io
import random
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from core.word.chronicle import Chronicle
from core.word.word import Word
from universe.logger import UniverseLogger
from universe.universe import Universe


NAMES = (
    "LetThereBeLight",
    "LetThereBeSpace",
    "LetThereBeDeep",
    "RewriteRule",
)

MESSAGES = (
    "Light is created.",
    "Space is separated from chaos.",
    "The Deep emerges from void.",
    "Reality rules are evolving...",
)


class SymbolicReplayOutboxTests(unittest.TestCase):

    def setUp(self):
        self.chronicle = Chronicle()

        for name in NAMES:
            self.chronicle.record(Word(name))

        with redirect_stdout(io.StringIO()):
            self.source = Universe(universe_id="a16_source")
            self.source.enable_quantum_layer()

            self.source.should_collapse_quantum_box = (
                lambda _box: False
            )

            self.chronicle.replay(self.source)

            self.source.create_quantum_box(
                box_id="a16_box",
                rng=random.Random(31),
            )

            self.source.tick_quantum_unprotected()
            self.source.tick_quantum_unprotected()

    @staticmethod
    def target(name="a16_target"):
        with redirect_stdout(io.StringIO()):
            universe = Universe(universe_id=name)
            universe.enable_quantum_layer()

        return universe

    @staticmethod
    def runtime(universe):
        return {
            "symbolic": tuple(
                (
                    name,
                    getattr(universe, name, None),
                )
                for name in (
                    "light", "space", "chaos",
                    "order", "deep", "rules_modified",
                )
            ),
            "clock": universe.quantum_state.to_dict(),
            "statistics": universe.statistics.public_state,
            "boxes": tuple(
                (box.public_state, box.age_ticks)
                for box in universe.quantum_boxes
            ),
            "box_events": tuple(universe.quantum_events),
            "clock_events": tuple(
                universe.quantum_clock_events
            ),
        }

    def replay(self, target, **overrides):
        arguments = {
            "chronicle": self.chronicle,
            "box_events": self.source.quantum_events,
            "clock_events": self.source.quantum_clock_events,
            "preserve_history": True,
        }
        arguments.update(overrides)

        return target.replay_symbolic_quantum_history(
            **arguments
        )

    def fail_second(self, target):
        attempted = []

        def deliver(message):
            attempted.append(message)

            if len(attempted) == 2:
                raise RuntimeError(
                    "A16 second delivery failed"
                )

        with patch.object(
            UniverseLogger,
            "event",
            side_effect=deliver,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "A16 second delivery failed",
            ):
                self.replay(target)

        self.assertEqual(attempted, list(MESSAGES[:2]))

    def test_partial_delivery_preserves_runtime_and_outbox(self):
        target = self.target()

        self.fail_second(target)

        self.assertEqual(
            self.runtime(target),
            self.runtime(self.source),
        )

        records = target.symbolic_replay_outbox

        self.assertEqual(len(records), 4)
        self.assertEqual(
            [record.delivered for record in records],
            [True, False, False, False],
        )

        self.assertEqual(
            [record.message for record in records],
            list(MESSAGES),
        )

        self.assertEqual(
            len({record.id for record in records}),
            4,
        )

        self.assertEqual(
            [record.word_id for record in records],
            [word.id for word in self.chronicle.all()],
        )

        self.assertEqual(
            [record.sequence for record in records],
            [0, 1, 2, 3],
        )

        self.assertEqual(
            len(target.pending_symbolic_replay_events),
            3,
        )

        before = self.runtime(target)

        with self.assertRaises(ValueError):
            self.replay(target)

        self.assertEqual(self.runtime(target), before)

    def test_retry_only_pending_without_runtime_replay(self):
        target = self.target()
        self.fail_second(target)

        runtime_before = self.runtime(target)
        first_id = target.symbolic_replay_outbox[0].id

        delivered = []

        completed = target.retry_symbolic_replay_events(
            sink=lambda event: delivered.append(
                (event.id, event.message)
            ),
        )

        self.assertEqual(completed, 3)
        self.assertEqual(
            [message for _id, message in delivered],
            list(MESSAGES[1:]),
        )

        self.assertNotIn(
            first_id,
            [event_id for event_id, _ in delivered],
        )

        self.assertTrue(
            all(
                event.delivered
                for event in target.symbolic_replay_outbox
            )
        )

        self.assertEqual(
            target.pending_symbolic_replay_events,
            (),
        )

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=lambda event: self.fail(
                    "Already delivered event was retried."
                ),
            ),
            0,
        )

        self.assertEqual(
            self.runtime(target),
            runtime_before,
        )

    def test_event_ids_are_deterministic_and_branch_isolated(self):
        first = self.target("a16_same")
        second = self.target("a16_same")
        other = self.target("a16_other")

        with patch.object(UniverseLogger, "event"):
            self.replay(first)
            self.replay(second)
            self.replay(other)

        first_ids = [
            event.id for event in first.symbolic_replay_outbox
        ]
        second_ids = [
            event.id for event in second.symbolic_replay_outbox
        ]
        other_ids = [
            event.id for event in other.symbolic_replay_outbox
        ]

        self.assertEqual(first_ids, second_ids)
        self.assertNotEqual(first_ids, other_ids)

        for left, right in zip(
            first.symbolic_replay_outbox,
            second.symbolic_replay_outbox,
        ):
            self.assertIsNot(left, right)

        self.assertEqual(
            first.pending_symbolic_replay_events,
            (),
        )

    def test_snapshot_restores_pending_delivery_independently(self):
        target = self.target()
        self.fail_second(target)

        serialized = target.snapshot[
            "symbolic_replay_outbox"
        ]

        self.assertEqual(len(serialized), 4)
        self.assertEqual(
            [row["delivered"] for row in serialized],
            [True, False, False, False],
        )

        restored = self.target("a16_restored")
        restored.restore_symbolic_replay_outbox(serialized)

        self.assertEqual(
            [
                event.id
                for event in restored.symbolic_replay_outbox
            ],
            [
                event.id
                for event in target.symbolic_replay_outbox
            ],
        )

        # Delivery recovery must not replay the runtime.
        self.assertEqual(restored.quantum_boxes, [])
        self.assertEqual(
            restored.quantum_state.tick_count,
            0,
        )

        delivered = []

        self.assertEqual(
            restored.retry_symbolic_replay_events(
                sink=delivered.append,
            ),
            3,
        )

        self.assertEqual(
            [event.message for event in delivered],
            list(MESSAGES[1:]),
        )

        self.assertEqual(
            restored.pending_symbolic_replay_events,
            (),
        )

        # Restoring and acknowledging cannot mutate
        # the original universe's delivery history.
        self.assertEqual(
            len(target.pending_symbolic_replay_events),
            3,
        )

        self.assertEqual(
            [row["delivered"] for row in serialized],
            [True, False, False, False],
        )

    def test_snapshot_is_detached_from_canonical_records(self):
        target = self.target()

        with patch.object(UniverseLogger, "event"):
            self.replay(target)

        snapshot = target.snapshot
        snapshot["symbolic_replay_outbox"][0]["id"] = "edited"
        snapshot["symbolic_replay_outbox"][0]["delivered"] = False

        event = target.symbolic_replay_outbox[0]

        self.assertNotEqual(event.id, "edited")
        self.assertTrue(event.delivered)

    def test_failed_preparation_does_not_create_outbox(self):
        target = self.target()
        clocks = tuple(self.source.quantum_clock_events)

        with patch.object(
            UniverseLogger,
            "event",
        ) as logger:
            with self.assertRaises(ValueError):
                self.replay(
                    target,
                    clock_events=(clocks[0], clocks[0]),
                )

        logger.assert_not_called()
        self.assertEqual(target.symbolic_replay_outbox, [])
        self.assertEqual(target.quantum_boxes, [])
        self.assertEqual(target.quantum_state.tick_count, 0)

    def test_outbox_publication_failure_rolls_back_runtime(self):
        class FaultyOutbox(list):
            def extend(self, values):
                values = tuple(values)

                if values:
                    self.append(values[0])

                raise RuntimeError(
                    "A16 outbox publication failure"
                )

        target = self.target()
        outbox = FaultyOutbox()
        target.symbolic_replay_outbox = outbox

        before = self.runtime(target)

        with patch.object(
            UniverseLogger,
            "event",
        ) as logger:
            with self.assertRaisesRegex(
                RuntimeError,
                "A16 outbox publication failure",
            ):
                self.replay(target)

        logger.assert_not_called()

        self.assertEqual(self.runtime(target), before)
        self.assertIs(target.symbolic_replay_outbox, outbox)
        self.assertEqual(outbox, [])
        self.assertEqual(
            target.pending_symbolic_replay_events,
            (),
        )

    def test_ambiguous_sink_failure_remains_retryable(self):
        target = self.target()

        with patch.object(UniverseLogger, "event"):
            self.replay(target)

        # Simulate an already committed event whose
        # downstream acknowledgement is uncertain.
        from dataclasses import replace

        first = target.symbolic_replay_outbox[0]
        target.symbolic_replay_outbox[0] = replace(
            first,
            delivered=False,
        )

        observed = []

        def ambiguous(event):
            observed.append(event.id)
            raise RuntimeError(
                "Downstream accepted, acknowledgement lost"
            )

        with self.assertRaisesRegex(
            RuntimeError,
            "acknowledgement lost",
        ):
            target.retry_symbolic_replay_events(
                sink=ambiguous,
            )

        self.assertFalse(
            target.symbolic_replay_outbox[0].delivered
        )

        target.retry_symbolic_replay_events(
            sink=lambda event: observed.append(event.id),
        )

        self.assertEqual(
            observed,
            [first.id, first.id],
        )

    def test_reentrant_dispatch_is_rejected(self):
        target = self.target()

        with patch.object(UniverseLogger, "event"):
            self.replay(target)

        from dataclasses import replace

        target.symbolic_replay_outbox[0] = replace(
            target.symbolic_replay_outbox[0],
            delivered=False,
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "already running",
        ):
            target.retry_symbolic_replay_events(
                sink=lambda event:
                    target.retry_symbolic_replay_events(),
            )

        self.assertFalse(
            target.symbolic_replay_outbox[0].delivered
        )

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=lambda event: True,
            ),
            1,
        )

    def test_restore_rejects_duplicates_without_mutation(self):
        target = self.target()

        with patch.object(UniverseLogger, "event"):
            self.replay(target)

        record = target.snapshot[
            "symbolic_replay_outbox"
        ][0]

        fresh = self.target("a16_restore_invalid")

        with self.assertRaises(ValueError):
            fresh.restore_symbolic_replay_outbox(
                (record, record)
            )

        self.assertEqual(
            fresh.symbolic_replay_outbox,
            [],
        )

        with self.assertRaises(ValueError):
            fresh.restore_symbolic_replay_outbox(
                ({"id": "missing_fields"},)
            )

        self.assertEqual(
            fresh.symbolic_replay_outbox,
            [],
        )


if __name__ == "__main__":
    unittest.main()
