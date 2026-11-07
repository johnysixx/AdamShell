import io
import subprocess
import sys
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from universe.universe import Universe
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)
from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)


CHILD_SOURCE = '''
import io
import os
import sys

from contextlib import redirect_stdout

from universe.universe import Universe
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.symbolic_replay_file_lock import (
    exclusive_inbox_lock,
)

mode, identity, outbox_path, inbox_path = sys.argv[1:]

with redirect_stdout(io.StringIO()):
    sender = Universe(universe_id=identity)

sender.load_symbolic_replay_outbox(outbox_path)

receiver = DurableSymbolicReplayInbox(
    path=inbox_path,
    universe_id=identity,
)

if mode == "while_outbox_locked":
    with exclusive_inbox_lock(outbox_path):
        os._exit(65)

if mode == "while_inbox_locked":
    with exclusive_inbox_lock(inbox_path):
        os._exit(66)

if mode == "after_inbox_checkpoint":
    original = receiver._write

    def checkpoint_then_exit(receipts):
        original(receipts)
        os._exit(63)

    receiver._write = checkpoint_then_exit

if mode == "after_ack_checkpoint":
    original = SymbolicReplayOutboxStore._write

    def ack_then_exit(path, document):
        original(path, document)
        os._exit(64)

    SymbolicReplayOutboxStore._write = ack_then_exit


def sink(event):
    if mode == "before_inbox":
        os._exit(61)

    accepted = receiver.accept(event)
    assert accepted is True

    if mode == "after_inbox":
        os._exit(62)

    return True


sender.retry_symbolic_replay_events(
    sink=sink,
    durable_outbox_path=outbox_path,
)

raise AssertionError(
    "Crash scenario returned without termination."
)
'''


EXIT_CODES = {
    "before_inbox": 61,
    "after_inbox": 62,
    "after_inbox_checkpoint": 63,
    "after_ack_checkpoint": 64,
    "while_outbox_locked": 65,
    "while_inbox_locked": 66,
}


class SymbolicReplayCrashRecoveryTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a21_crash_"
        )
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)
        self.root = Path(__file__).resolve().parents[1]

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create_case(self, label, count=1):
        identity = f"a21_{label}"
        outbox = self.directory / f"{label}_outbox.json"
        inbox = self.directory / f"{label}_inbox.json"

        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"a21_{label}_event_{i}",
                word_id=f"a21_{label}_word_{i}",
                sequence=i,
                message=f"A21 {label} message {i}.",
            )
            for i in range(count)
        )

        sender.symbolic_replay_outbox.extend(events)

        SymbolicReplayOutboxStore.save(
            sender,
            outbox,
            require_new=True,
        )

        return identity, outbox, inbox, events

    def crash(self, mode, identity, outbox, inbox):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                CHILD_SOURCE,
                mode,
                identity,
                str(outbox),
                str(inbox),
            ],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            timeout=20,
        )

        self.assertEqual(
            result.returncode,
            EXIT_CODES[mode],
            msg=(
                f"mode={mode}, stdout={result.stdout!r}, "
                f"stderr={result.stderr!r}"
            ),
        )

    def restore(self, identity, outbox, inbox):
        sender = self.universe(identity)
        sender.load_symbolic_replay_outbox(outbox)

        receiver = DurableSymbolicReplayInbox(
            path=inbox,
            universe_id=identity,
        )

        return sender, receiver

    def assert_complete(
        self, identity, outbox, inbox, events,
    ):
        sender, receiver = self.restore(
            identity, outbox, inbox
        )

        self.assertEqual(
            tuple(item.id for item in receiver.receipts),
            tuple(item.id for item in events),
        )

        self.assertEqual(
            sender.pending_symbolic_replay_events,
            (),
        )

        self.assertTrue(
            all(
                item.delivered
                for item in SymbolicReplayOutboxStore.read(
                    sender, outbox
                )
            )
        )

        self.assertEqual(sender.quantum_boxes, [])
        self.assertEqual(
            sender.quantum_state.tick_count,
            0,
        )

        self.assertEqual(
            sender.retry_symbolic_replay_events(
                sink=lambda event: self.fail(
                    "Already acknowledged event redelivered."
                ),
                durable_outbox_path=outbox,
            ),
            0,
        )

    def exercise_single(
        self, mode, *, receipt, acknowledged,
    ):
        identity, outbox, inbox, events = (
            self.create_case(mode)
        )

        self.crash(mode, identity, outbox, inbox)

        sender, receiver = self.restore(
            identity, outbox, inbox
        )

        stored = SymbolicReplayOutboxStore.read(
            sender, outbox
        )

        self.assertEqual(len(stored), 1)
        self.assertIs(
            stored[0].delivered,
            acknowledged,
        )

        self.assertEqual(
            len(receiver.receipts),
            1 if receipt else 0,
        )

        if acknowledged:
            completed = sender.retry_symbolic_replay_events(
                sink=lambda event: self.fail(
                    "Durable ACK was ignored."
                ),
                durable_outbox_path=outbox,
            )

            self.assertEqual(completed, 0)

        elif receipt:
            with patch.object(
                receiver,
                "_write",
                side_effect=AssertionError(
                    "Duplicate inbox receipt write."
                ),
            ):
                completed = (
                    sender.retry_symbolic_replay_events(
                        sink=receiver.accept,
                        durable_outbox_path=outbox,
                    )
                )

            self.assertEqual(completed, 1)

        else:
            completed = sender.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=outbox,
            )

            self.assertEqual(completed, 1)

        self.assert_complete(
            identity, outbox, inbox, events
        )

    def test_crash_before_inbox(self):
        self.exercise_single(
            "before_inbox",
            receipt=False,
            acknowledged=False,
        )

    def test_crash_after_inbox_before_ack(self):
        self.exercise_single(
            "after_inbox",
            receipt=True,
            acknowledged=False,
        )

    def test_crash_after_inbox_checkpoint_write(self):
        self.exercise_single(
            "after_inbox_checkpoint",
            receipt=True,
            acknowledged=False,
        )

    def test_crash_after_ack_checkpoint_write(self):
        self.exercise_single(
            "after_ack_checkpoint",
            receipt=True,
            acknowledged=True,
        )

    def test_crash_while_outbox_lock_held(self):
        self.exercise_single(
            "while_outbox_locked",
            receipt=False,
            acknowledged=False,
        )

    def test_crash_while_inbox_lock_held(self):
        self.exercise_single(
            "while_inbox_locked",
            receipt=False,
            acknowledged=False,
        )

    def test_partial_ack_recovers_remaining_events(self):
        identity, outbox, inbox, events = (
            self.create_case("partial", count=3)
        )

        self.crash(
            "after_ack_checkpoint",
            identity,
            outbox,
            inbox,
        )

        sender, receiver = self.restore(
            identity, outbox, inbox
        )

        self.assertEqual(
            [
                item.delivered
                for item in SymbolicReplayOutboxStore.read(
                    sender, outbox
                )
            ],
            [True, False, False],
        )

        self.assertEqual(
            tuple(item.id for item in receiver.receipts),
            (events[0].id,),
        )

        completed = sender.retry_symbolic_replay_events(
            sink=receiver.accept,
            durable_outbox_path=outbox,
        )

        self.assertEqual(completed, 2)

        self.assert_complete(
            identity, outbox, inbox, events
        )

    def test_repeated_crash_does_not_duplicate_receipt(self):
        identity, outbox, inbox, events = (
            self.create_case("repeated")
        )

        self.crash(
            "after_inbox",
            identity,
            outbox,
            inbox,
        )

        before = inbox.read_bytes()

        # A second subprocess retries the same pending
        # event and also crashes before saving its ACK.
        self.crash(
            "after_inbox",
            identity,
            outbox,
            inbox,
        )

        self.assertEqual(inbox.read_bytes(), before)

        sender, receiver = self.restore(
            identity, outbox, inbox
        )

        self.assertEqual(len(receiver.receipts), 1)

        with patch.object(
            receiver,
            "_write",
            side_effect=AssertionError(
                "Repeated crash caused duplicate write."
            ),
        ):
            completed = (
                sender.retry_symbolic_replay_events(
                    sink=receiver.accept,
                    durable_outbox_path=outbox,
                )
            )

        self.assertEqual(completed, 1)

        self.assert_complete(
            identity, outbox, inbox, events
        )


if __name__ == "__main__":
    unittest.main()
