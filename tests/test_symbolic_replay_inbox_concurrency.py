import subprocess
import sys
import tempfile
import threading
import time
import unittest

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from universe.symbolic_replay_file_lock import (
    exclusive_inbox_lock,
)
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)
from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
)


class SymbolicReplayInboxConcurrencyTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a19_inbox_"
        )
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)
        self.path = self.directory / "inbox.json"

        self.alpha = SymbolicReplayOutboxEvent(
            id="a19_alpha",
            word_id="a19_word_alpha",
            sequence=0,
            message="Alpha received.",
        )
        self.beta = SymbolicReplayOutboxEvent(
            id="a19_beta",
            word_id="a19_word_beta",
            sequence=1,
            message="Beta received.",
        )

    def inbox(self, path=None):
        return DurableSymbolicReplayInbox(
            path=self.path if path is None else path,
            universe_id="a19_reality",
        )

    def ids(self):
        return tuple(
            receipt.id
            for receipt in self.inbox().receipts
        )

    def test_same_id_concurrent_only_one_write(self):
        first = self.inbox()
        second = self.inbox()

        entered = threading.Event()
        release = threading.Event()
        original = first._write

        def held_write(records):
            entered.set()
            if not release.wait(timeout=5):
                raise TimeoutError("Writer release failed.")
            return original(records)

        with patch.object(
            first, "_write", side_effect=held_write,
        ):
            with patch.object(
                second,
                "_write",
                side_effect=AssertionError(
                    "Duplicate performed second write."
                ),
            ):
                with ThreadPoolExecutor(
                    max_workers=2
                ) as pool:
                    try:
                        left = pool.submit(
                            first.accept, self.alpha
                        )
                        self.assertTrue(
                            entered.wait(timeout=5)
                        )
                        right = pool.submit(
                            second.accept, self.alpha
                        )
                    finally:
                        release.set()

                    self.assertTrue(left.result(timeout=5))
                    self.assertTrue(right.result(timeout=5))

        self.assertEqual(self.ids(), ("a19_alpha",))
        self.assertEqual(
            second.receipts, first.receipts
        )

    def test_different_ids_cannot_lose_update(self):
        first = self.inbox()
        second = self.inbox()

        entered = threading.Event()
        release = threading.Event()
        original = first._write

        def held_write(records):
            entered.set()
            if not release.wait(timeout=5):
                raise TimeoutError("Writer release failed.")
            return original(records)

        with patch.object(
            first, "_write", side_effect=held_write,
        ):
            with ThreadPoolExecutor(
                max_workers=2
            ) as pool:
                try:
                    left = pool.submit(
                        first.accept, self.alpha
                    )
                    self.assertTrue(
                        entered.wait(timeout=5)
                    )
                    right = pool.submit(
                        second.accept, self.beta
                    )
                finally:
                    release.set()

                self.assertTrue(left.result(timeout=5))

                with self.assertRaisesRegex(
                    ValueError, "checkpoint changed"
                ):
                    right.result(timeout=5)

        self.assertEqual(self.ids(), ("a19_alpha",))

        refreshed = self.inbox()
        self.assertTrue(refreshed.accept(self.beta))

        self.assertEqual(
            self.ids(),
            ("a19_alpha", "a19_beta"),
        )

    def test_stale_duplicate_refreshes_receiver(self):
        first = self.inbox()
        stale = self.inbox()

        self.assertTrue(first.accept(self.alpha))
        self.assertTrue(stale.accept(self.alpha))
        self.assertEqual(stale.receipts, first.receipts)

        self.assertTrue(stale.accept(self.beta))
        self.assertEqual(
            self.ids(),
            ("a19_alpha", "a19_beta"),
        )

    def test_conflicting_identity_is_rejected(self):
        first = self.inbox()
        stale = self.inbox()

        first.accept(self.alpha)

        with self.assertRaisesRegex(
            ValueError, "identity collision"
        ):
            stale.accept(
                replace(
                    self.alpha,
                    message="Different content.",
                )
            )

        self.assertEqual(self.ids(), ("a19_alpha",))

    def test_failed_write_releases_lock(self):
        first = self.inbox()

        with patch(
            "universe.symbolic_replay_inbox.os.replace",
            side_effect=OSError("A19 write failed"),
        ):
            with self.assertRaisesRegex(
                OSError, "A19 write failed"
            ):
                first.accept(self.alpha)

        self.assertEqual(first.receipts, ())
        self.assertFalse(self.path.exists())

        second = self.inbox()
        self.assertTrue(second.accept(self.alpha))
        self.assertEqual(self.ids(), ("a19_alpha",))

    def test_lock_timeout_and_stable_lockfile(self):
        lockfile = self.path.with_name(
            self.path.name + ".lock"
        )

        with exclusive_inbox_lock(
            self.path, timeout=1.0
        ):
            self.assertTrue(lockfile.exists())

            with self.assertRaises(TimeoutError):
                with exclusive_inbox_lock(
                    self.path, timeout=0.05
                ):
                    self.fail("Lock was acquired twice.")

        self.assertTrue(self.inbox().accept(self.alpha))
        self.assertTrue(lockfile.exists())

    def test_second_process_waits_for_lock(self):
        ready = self.directory / "child_ready.txt"

        child_source = (
            "import sys\\n"
            "from pathlib import Path\\n"
            "from universe.symbolic_replay_inbox import "
            "DurableSymbolicReplayInbox\\n"
            "from universe.symbolic_replay_outbox import "
            "SymbolicReplayOutboxEvent\\n"
            "inbox = DurableSymbolicReplayInbox("
            "path=sys.argv[1], "
            "universe_id='a19_reality')\\n"
            "event = SymbolicReplayOutboxEvent("
            "id='a19_alpha', "
            "word_id='a19_word_alpha', "
            "sequence=0, "
            "message='Alpha received.')\\n"
            "Path(sys.argv[2]).write_text('ready')\\n"
            "assert inbox.accept(event) is True\\n"
            "print('ACCEPTED', flush=True)\\n"
        )

        # Convert literal backslash-n sequences into
        # actual Python source newlines.
        child_source = child_source.replace(
            "\\n", "\n"
        )

        root = Path(__file__).resolve().parents[1]
        child = None

        try:
            with exclusive_inbox_lock(
                self.path, timeout=5.0
            ):
                child = subprocess.Popen(
                    [
                        sys.executable,
                        "-B",
                        "-c",
                        child_source,
                        str(self.path),
                        str(ready),
                    ],
                    cwd=str(root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                deadline = time.monotonic() + 8

                while not ready.exists():
                    if child.poll() is not None:
                        output, errors = child.communicate()
                        self.fail(
                            f"Child stopped: {output} {errors}"
                        )

                    if time.monotonic() >= deadline:
                        self.fail(
                            "Child did not reach inbox accept."
                        )

                    time.sleep(0.01)

                time.sleep(0.1)
                self.assertIsNone(child.poll())

            output, errors = child.communicate(
                timeout=15
            )

            self.assertEqual(
                child.returncode, 0, msg=errors
            )
            self.assertIn("ACCEPTED", output)
            self.assertEqual(self.ids(), ("a19_alpha",))

        finally:
            if child is not None:
                if child.poll() is None:
                    child.kill()
                child.communicate()

    def test_independent_inboxes_use_separate_locks(self):
        other_path = self.directory / "other.json"

        with exclusive_inbox_lock(
            self.path, timeout=1.0
        ):
            other = self.inbox(other_path)
            self.assertTrue(other.accept(self.beta))

        self.assertFalse(self.path.exists())
        self.assertEqual(
            len(self.inbox(other_path).receipts), 1
        )

        self.assertTrue(
            self.inbox().accept(self.alpha)
        )
        self.assertEqual(self.ids(), ("a19_alpha",))


if __name__ == "__main__":
    unittest.main()
