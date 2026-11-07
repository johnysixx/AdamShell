import io
import json
import random
import tempfile
import unittest

from contextlib import redirect_stdout
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import patch

from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
)
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
    SymbolicReplayInboxReceipt,
)


class DurableSymbolicReplayInboxTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a18_inbox_"
        )

        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)
        self.path = self.directory / "inbox.json"

        self.event = SymbolicReplayOutboxEvent(
            id="a18_event_one",
            word_id="a18_word_one",
            sequence=0,
            message="Light is created.",
        )

        self.second = SymbolicReplayOutboxEvent(
            id="a18_event_two",
            word_id="a18_word_two",
            sequence=1,
            message="Space is separated from chaos.",
        )

    def inbox(self, universe_id="a18_target"):
        return DurableSymbolicReplayInbox(
            path=self.path,
            universe_id=universe_id,
        )

    def test_duplicate_is_accepted_once_before_and_after_restart(self):
        receiver = self.inbox()

        self.assertFalse(self.path.exists())
        self.assertTrue(receiver.accept(self.event))
        self.assertTrue(self.path.is_file())
        self.assertEqual(len(receiver.receipts), 1)

        with patch(
            "universe.symbolic_replay_inbox.os.replace",
            side_effect=AssertionError(
                "Duplicate caused disk write"
            ),
        ):
            self.assertTrue(receiver.accept(self.event))

        self.assertEqual(len(receiver.receipts), 1)

        restarted = self.inbox()

        self.assertTrue(restarted.accept(self.event))
        self.assertEqual(len(restarted.receipts), 1)
        self.assertEqual(
            restarted.receipts[0].id,
            self.event.id,
        )

        self.assertTrue(restarted.accept(self.second))
        self.assertEqual(len(restarted.receipts), 2)
        self.assertEqual(len(self.inbox().receipts), 2)

    def test_collision_with_different_message_is_rejected(self):
        receiver = self.inbox()
        receiver.accept(self.event)

        before = self.path.read_bytes()

        with self.assertRaisesRegex(
            ValueError,
            "identity collision",
        ):
            receiver.accept(
                replace(self.event, message="Different")
            )

        with self.assertRaisesRegex(
            ValueError,
            "identity collision",
        ):
            receiver.accept(
                replace(self.event, word_id="Other word")
            )

        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(len(receiver.receipts), 1)

    def test_foreign_universe_is_rejected_without_mutation(self):
        self.inbox().accept(self.event)
        before = self.path.read_bytes()

        with self.assertRaisesRegex(
            ValueError,
            "another universe",
        ):
            self.inbox("another_reality")

        self.assertEqual(self.path.read_bytes(), before)

    def test_corrupt_checksum_rejected(self):
        self.inbox().accept(self.event)

        document = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        document["receipts"][0]["message"] = "tampered"

        self.path.write_text(
            json.dumps(document),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            ValueError,
            "checksum mismatch",
        ):
            self.inbox()

    def test_unsupported_schema_is_rejected(self):
        self.inbox().accept(self.event)

        document = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        document["version"] = 2

        self.path.write_text(
            json.dumps(document),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported",
        ):
            self.inbox()

    def test_failed_atomic_replace_keeps_disk_and_memory_unchanged(self):
        receiver = self.inbox()

        with patch(
            "universe.symbolic_replay_inbox.os.replace",
            side_effect=OSError("A18 replace failed"),
        ):
            with self.assertRaisesRegex(
                OSError,
                "A18 replace failed",
            ):
                receiver.accept(self.event)

        self.assertEqual(receiver.receipts, ())
        self.assertFalse(self.path.exists())

        self.assertEqual(
            list(self.directory.glob("*.tmp")),
            [],
        )

        self.assertTrue(receiver.accept(self.event))
        before = self.path.read_bytes()

        with patch(
            "universe.symbolic_replay_inbox.os.replace",
            side_effect=OSError("A18 replace failed"),
        ):
            with self.assertRaisesRegex(
                OSError,
                "A18 replace failed",
            ):
                receiver.accept(self.second)

        self.assertEqual(len(receiver.receipts), 1)
        self.assertEqual(self.path.read_bytes(), before)

    def test_stale_receiver_cannot_overwrite_newer_checkpoint(self):
        first = self.inbox()
        stale = self.inbox()

        first.accept(self.event)
        before = self.path.read_bytes()

        with self.assertRaisesRegex(
            ValueError,
            "checkpoint changed",
        ):
            stale.accept(self.second)

        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(len(self.inbox().receipts), 1)

        self.assertTrue(self.inbox().accept(self.second))
        self.assertEqual(len(self.inbox().receipts), 2)

    def test_lost_sender_ack_retries_without_duplicate_receipt(self):
        from core.word.chronicle import Chronicle
        from core.word.word import Word
        from universe.logger import UniverseLogger
        from universe.symbolic_replay_outbox_store import (
            SymbolicReplayOutboxStore,
        )
        from universe.universe import Universe

        with redirect_stdout(io.StringIO()):
            source = Universe(universe_id="a18_source")
            source.enable_quantum_layer()
            source.should_collapse_quantum_box = (
                lambda _box: False
            )

            target = Universe(universe_id="a18_target")
            target.enable_quantum_layer()

        chronicle = Chronicle()
        chronicle.record(Word("LetThereBeLight"))
        chronicle.record(Word("LetThereBeSpace"))

        with redirect_stdout(io.StringIO()):
            chronicle.replay(source)

            source.create_quantum_box(
                box_id="a18_box",
                rng=random.Random(31),
            )

            source.tick_quantum_unprotected()

        outbox_path = self.directory / "outbox.json"

        with patch.object(
            UniverseLogger,
            "event",
            side_effect=RuntimeError(
                "A18 initial send blocked"
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "initial send",
            ):
                target.replay_symbolic_quantum_history(
                    chronicle=chronicle,
                    box_events=source.quantum_events,
                    clock_events=source.quantum_clock_events,
                    preserve_history=True,
                    durable_outbox_path=outbox_path,
                )

        self.assertEqual(
            len(target.pending_symbolic_replay_events),
            2,
        )

        receiver = self.inbox()

        with patch.object(
            SymbolicReplayOutboxStore,
            "persist_ack",
            side_effect=OSError(
                "A18 sender ack lost"
            ),
        ):
            with self.assertRaisesRegex(
                OSError,
                "sender ack lost",
            ):
                target.retry_symbolic_replay_events(
                    sink=receiver.accept,
                    durable_outbox_path=outbox_path,
                )

        self.assertEqual(len(receiver.receipts), 1)

        first_id = receiver.receipts[0].id

        self.assertEqual(
            len(target.pending_symbolic_replay_events),
            2,
        )

        with redirect_stdout(io.StringIO()):
            restarted = Universe(
                universe_id="a18_target"
            )
            restarted.enable_quantum_layer()

        restarted.load_symbolic_replay_outbox(
            outbox_path
        )

        recovered_receiver = self.inbox()

        completed = (
            restarted.retry_symbolic_replay_events(
                sink=recovered_receiver.accept,
                durable_outbox_path=outbox_path,
            )
        )

        self.assertEqual(completed, 2)

        self.assertEqual(
            len(recovered_receiver.receipts),
            2,
        )

        self.assertEqual(
            sum(
                receipt.id == first_id
                for receipt in recovered_receiver.receipts
            ),
            1,
        )

        self.assertEqual(
            restarted.pending_symbolic_replay_events,
            (),
        )

        self.assertEqual(restarted.quantum_boxes, [])
        self.assertEqual(
            restarted.quantum_state.tick_count,
            0,
        )

    def test_receipts_are_immutable_and_nonmapping(self):
        receiver = self.inbox()
        receiver.accept(self.event)

        receipt = receiver.receipts[0]

        self.assertIsInstance(
            receipt,
            SymbolicReplayInboxReceipt,
        )

        self.assertFalse(hasattr(receipt, "get"))

        with self.assertRaises(FrozenInstanceError):
            receipt.message = "modified"

        with self.assertRaises(TypeError):
            receiver.accept(
                {"id": self.event.id}
            )

        self.assertEqual(len(receiver.receipts), 1)


if __name__ == "__main__":
    unittest.main()
