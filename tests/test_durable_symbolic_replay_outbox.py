import io
import json
import random
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from core.word.chronicle import Chronicle
from core.word.word import Word
from universe.logger import UniverseLogger
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.universe import Universe


class DurableSymbolicReplayOutboxTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix="a17_outbox_"
        )
        self.addCleanup(self.temp.cleanup)

        self.path = Path(self.temp.name) / "outbox.json"

        self.chronicle = Chronicle()
        for name in (
            "LetThereBeLight",
            "LetThereBeSpace",
            "LetThereBeDeep",
            "RewriteRule",
        ):
            self.chronicle.record(Word(name))

        with redirect_stdout(io.StringIO()):
            self.source = Universe(universe_id="a17_source")
            self.source.enable_quantum_layer()
            self.source.should_collapse_quantum_box = (
                lambda box: False
            )
            self.chronicle.replay(self.source)
            self.source.create_quantum_box(
                box_id="a17_box",
                rng=random.Random(31),
            )
            self.source.tick_quantum_unprotected()
            self.source.tick_quantum_unprotected()

    @staticmethod
    def target(name="a17_target"):
        with redirect_stdout(io.StringIO()):
            result = Universe(universe_id=name)
            result.enable_quantum_layer()
        return result

    def replay(self, target):
        return target.replay_symbolic_quantum_history(
            chronicle=self.chronicle,
            box_events=self.source.quantum_events,
            clock_events=self.source.quantum_clock_events,
            preserve_history=True,
            durable_outbox_path=self.path,
        )

    def fail_second(self, target):
        attempts = []

        def deliver(message):
            attempts.append(message)
            if len(attempts) == 2:
                raise RuntimeError("A17 delivery failure")

        with patch.object(
            UniverseLogger,
            "event",
            side_effect=deliver,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "A17 delivery failure",
            ):
                self.replay(target)

        self.assertEqual(len(attempts), 2)

    def test_restart_recovers_pending_and_acks(self):
        target = self.target()
        self.fail_second(target)

        records = SymbolicReplayOutboxStore.read(
            target, self.path
        )

        self.assertEqual(
            [event.delivered for event in records],
            [True, False, False, False],
        )

        recovered = self.target()
        recovered.load_symbolic_replay_outbox(self.path)

        received = []

        count = recovered.retry_symbolic_replay_events(
            sink=lambda event: received.append(event.id),
            durable_outbox_path=self.path,
        )

        self.assertEqual(count, 3)
        self.assertEqual(len(received), 3)

        restarted = self.target()
        restarted.load_symbolic_replay_outbox(self.path)

        self.assertEqual(
            restarted.pending_symbolic_replay_events,
            (),
        )

        self.assertEqual(
            restarted.retry_symbolic_replay_events(
                sink=lambda event: self.fail(
                    "Duplicate delivery"
                ),
                durable_outbox_path=self.path,
            ),
            0,
        )

        self.assertEqual(restarted.quantum_boxes, [])
        self.assertEqual(
            restarted.quantum_state.tick_count,
            0,
        )

    def test_checkpoint_precedes_delivery(self):
        target = self.target()
        observed = []

        def deliver(message):
            records = SymbolicReplayOutboxStore.read(
                target, self.path
            )
            observed.append(
                (
                    message,
                    len(records),
                    records[0].delivered,
                )
            )

        with patch.object(
            UniverseLogger,
            "event",
            side_effect=deliver,
        ):
            self.replay(target)

        self.assertEqual(len(observed), 4)
        self.assertEqual(observed[0][1:], (4, False))

        self.assertTrue(
            all(
                record.delivered
                for record in SymbolicReplayOutboxStore.read(
                    target, self.path
                )
            )
        )

    def test_foreign_universe_cannot_restore(self):
        self.fail_second(self.target())

        outsider = self.target("a17_foreign")

        with self.assertRaisesRegex(
            ValueError,
            "another universe",
        ):
            outsider.load_symbolic_replay_outbox(
                self.path
            )

        self.assertEqual(
            outsider.symbolic_replay_outbox,
            [],
        )

    def test_corrupted_checksum_is_rejected(self):
        self.fail_second(self.target())

        data = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        data["events"][1]["message"] = "corrupted"

        self.path.write_text(
            json.dumps(data),
            encoding="utf-8",
        )

        recovered = self.target()

        with self.assertRaisesRegex(
            ValueError,
            "checksum mismatch",
        ):
            recovered.load_symbolic_replay_outbox(
                self.path
            )

        self.assertEqual(
            recovered.symbolic_replay_outbox,
            [],
        )

    def test_failed_atomic_replace_preserves_checkpoint(self):
        self.fail_second(self.target())

        original = self.path.read_bytes()

        recovered = self.target()
        recovered.load_symbolic_replay_outbox(self.path)

        attempted = []

        with patch(
            "universe.symbolic_replay_outbox_store.os.replace",
            side_effect=OSError("A17 replace failure"),
        ):
            with self.assertRaisesRegex(
                OSError,
                "A17 replace failure",
            ):
                recovered.retry_symbolic_replay_events(
                    sink=lambda event: attempted.append(
                        event.id
                    ),
                    durable_outbox_path=self.path,
                )

        self.assertEqual(len(attempted), 1)
        self.assertEqual(
            self.path.read_bytes(),
            original,
        )
        self.assertEqual(
            len(recovered.pending_symbolic_replay_events),
            3,
        )
        self.assertEqual(
            list(self.path.parent.glob("*.tmp")),
            [],
        )

    def test_existing_checkpoint_prevents_replay(self):
        self.path.write_text(
            "protected checkpoint",
            encoding="utf-8",
        )

        target = self.target()

        with patch.object(
            UniverseLogger,
            "event",
        ) as logger:
            with self.assertRaises(FileExistsError):
                self.replay(target)

        logger.assert_not_called()

        self.assertEqual(target.quantum_boxes, [])
        self.assertEqual(
            target.quantum_state.tick_count,
            0,
        )
        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )
        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            "protected checkpoint",
        )

    def test_stale_memory_cannot_revoke_durable_ack(self):
        current = self.target()
        self.fail_second(current)

        stale = self.target()
        stale.load_symbolic_replay_outbox(self.path)

        current.retry_symbolic_replay_events(
            sink=lambda event: True,
            durable_outbox_path=self.path,
        )

        with self.assertRaisesRegex(
            ValueError,
            "differs",
        ):
            stale.retry_symbolic_replay_events(
                sink=lambda event: self.fail(
                    "Stale event dispatched"
                ),
                durable_outbox_path=self.path,
            )

        with self.assertRaisesRegex(
            ValueError,
            "revoke",
        ):
            stale.save_symbolic_replay_outbox(
                self.path
            )

    def test_manual_save_and_restore(self):
        target = self.target()

        with patch.object(UniverseLogger, "event"):
            target.replay_symbolic_quantum_history(
                chronicle=self.chronicle,
                box_events=self.source.quantum_events,
                clock_events=self.source.quantum_clock_events,
            )

        target.save_symbolic_replay_outbox(
            self.path
        )

        recovered = self.target()
        recovered.load_symbolic_replay_outbox(
            self.path
        )

        self.assertEqual(
            tuple(recovered.symbolic_replay_outbox),
            tuple(target.symbolic_replay_outbox),
        )

        self.assertEqual(
            recovered.pending_symbolic_replay_events,
            (),
        )


if __name__ == "__main__":
    unittest.main()
