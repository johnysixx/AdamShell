import io
import json
import subprocess
import sys
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from core.word.chronicle import Chronicle
from core.word.word import Word
from universe.logger import UniverseLogger
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.universe import Universe


CHILD_SOURCE = r"""
import io
import json
import sys

from contextlib import redirect_stdout
from unittest.mock import patch

from core.word.chronicle import Chronicle
from core.word.word import Word
from universe.logger import UniverseLogger
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)
from universe.universe import Universe


identity, word_id, outbox_path, inbox_path = sys.argv[1:]

chronicle = Chronicle()
chronicle.record(
    Word("LetThereBeLight", id=word_id)
)

with redirect_stdout(io.StringIO()):
    recreated = Universe(universe_id=identity)
    recreated.enable_quantum_layer()

    with patch.object(UniverseLogger, "event"):
        recreated.replay_symbolic_quantum_history(
            chronicle=chronicle,
            box_events=(),
            clock_events=(),
            preserve_history=True,
        )

    recovered = Universe(universe_id=identity)

regenerated = recreated.symbolic_replay_outbox

assert len(regenerated) == 1

recovered.load_symbolic_replay_outbox(
    outbox_path
)

pending = recovered.pending_symbolic_replay_events

assert len(pending) == 1
assert pending[0].id == regenerated[0].id
assert pending[0].word_id == word_id
assert pending[0].message == regenerated[0].message

receiver = DurableSymbolicReplayInbox(
    path=inbox_path,
    universe_id=identity,
)

assert len(receiver.receipts) == 1

first = recovered.retry_symbolic_replay_events(
    sink=receiver.accept,
    durable_outbox_path=outbox_path,
)

second = recovered.retry_symbolic_replay_events(
    sink=receiver.accept,
    durable_outbox_path=outbox_path,
)

assert first == 1
assert second == 0
assert len(receiver.receipts) == 1
assert recovered.pending_symbolic_replay_events == ()

print(json.dumps({
    "regenerated_id": regenerated[0].id,
    "recovered_id": pending[0].id,
    "first_retry": first,
    "second_retry": second,
    "receipt_count": len(receiver.receipts),
}))
"""


class SymbolicReplayIdentityProcessRecoveryTests(
    unittest.TestCase
):

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            result = Universe(universe_id=identity)
            result.enable_quantum_layer()
        return result

    def test_regenerated_identity_survives_process_restart(self):
        identity = "a36_process_identity"
        word_id = "a36_canonical_word"

        chronicle = Chronicle()
        chronicle.record(
            Word("LetThereBeLight", id=word_id)
        )

        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            outbox = directory / "outbox.json"
            inbox = directory / "inbox.json"

            sender = self.universe(identity)

            # Runtime and outbox are committed, but
            # the initial delivery fails.
            with patch.object(
                UniverseLogger,
                "event",
                side_effect=RuntimeError(
                    "A36 interrupted delivery"
                ),
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "A36 interrupted delivery",
                ):
                    sender.replay_symbolic_quantum_history(
                        chronicle=chronicle,
                        box_events=(),
                        clock_events=(),
                        preserve_history=True,
                        durable_outbox_path=outbox,
                    )

            self.assertTrue(sender.light)

            self.assertEqual(
                len(sender.symbolic_replay_outbox),
                1,
            )

            original = sender.symbolic_replay_outbox[0]

            self.assertFalse(original.delivered)
            self.assertEqual(original.word_id, word_id)

            stored = SymbolicReplayOutboxStore.read(
                sender, outbox
            )

            self.assertEqual(len(stored), 1)
            self.assertEqual(stored[0].id, original.id)
            self.assertFalse(stored[0].delivered)

            # Receiver persists the event, but the
            # sender's durable ACK is still missing.
            receiver = DurableSymbolicReplayInbox(
                path=inbox,
                universe_id=identity,
            )

            self.assertTrue(receiver.accept(original))

            inbox_before = inbox.read_bytes()

            self.assertEqual(
                len(receiver.receipts),
                1,
            )

            # A fresh Python process reconstructs
            # the original event from the same Word ID,
            # loads the durable checkpoint and finishes
            # the missing ACK.
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-c",
                    CHILD_SOURCE,
                    identity,
                    word_id,
                    str(outbox),
                    str(inbox),
                ],
                cwd=str(
                    Path(__file__).resolve().parents[1]
                ),
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.assertEqual(
                result.returncode,
                0,
                msg=(
                    f"stdout={result.stdout!r}\n"
                    f"stderr={result.stderr!r}"
                ),
            )

            outcome = json.loads(result.stdout)

            self.assertEqual(
                outcome["regenerated_id"],
                original.id,
            )
            self.assertEqual(
                outcome["recovered_id"],
                original.id,
            )
            self.assertEqual(outcome["first_retry"], 1)
            self.assertEqual(outcome["second_retry"], 0)
            self.assertEqual(outcome["receipt_count"], 1)

            # The receiver must not create a second
            # receipt during recovery.
            self.assertEqual(
                inbox.read_bytes(),
                inbox_before,
            )

            persisted = SymbolicReplayOutboxStore.read(
                sender, outbox
            )

            self.assertEqual(len(persisted), 1)
            self.assertEqual(persisted[0].id, original.id)
            self.assertTrue(persisted[0].delivered)

            reopened = DurableSymbolicReplayInbox(
                path=inbox,
                universe_id=identity,
            )

            self.assertEqual(len(reopened.receipts), 1)
            self.assertEqual(
                reopened.receipts[0].id,
                original.id,
            )


if __name__ == "__main__":
    unittest.main()
