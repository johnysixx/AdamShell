import io
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from universe.symbolic_replay_file_lock import (
    exclusive_inbox_lock,
)
from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.universe import Universe


class SymbolicReplayOutboxConcurrencyTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a20_outbox_"
        )
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)
        self.path = self.directory / "outbox.json"

        self.events = (
            SymbolicReplayOutboxEvent(
                id="a20_alpha",
                word_id="a20_word_alpha",
                sequence=0,
                message="Alpha event.",
            ),
            SymbolicReplayOutboxEvent(
                id="a20_beta",
                word_id="a20_word_beta",
                sequence=1,
                message="Beta event.",
            ),
        )

    @staticmethod
    def universe():
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id="a20_reality")

    def sender(self, count=2):
        result = self.universe()

        result.symbolic_replay_outbox.extend(
            self.events[:count]
        )

        return result

    def initialize(self, count=2):
        result = self.sender(count)

        SymbolicReplayOutboxStore.save(
            result,
            self.path,
            require_new=True,
        )

        return result

    def stored(self):
        return SymbolicReplayOutboxStore.read(
            self.universe(),
            self.path,
        )

    def test_concurrent_same_event_sends_only_once(self):
        first = self.initialize(count=1)
        second = self.sender(count=1)

        entered = threading.Event()
        release = threading.Event()
        effects = []

        def first_sink(event):
            entered.set()

            if not release.wait(timeout=5):
                raise TimeoutError(
                    "First delivery was not released."
                )

            effects.append(("first", event.id))
            return True

        def second_sink(event):
            effects.append(("second", event.id))
            return True

        with ThreadPoolExecutor(max_workers=2) as pool:
            try:
                left = pool.submit(
                    first.retry_symbolic_replay_events,
                    sink=first_sink,
                    durable_outbox_path=self.path,
                )

                self.assertTrue(
                    entered.wait(timeout=5)
                )

                right = pool.submit(
                    second.retry_symbolic_replay_events,
                    sink=second_sink,
                    durable_outbox_path=self.path,
                )

                time.sleep(0.05)
                self.assertFalse(right.done())

            finally:
                release.set()

            self.assertEqual(
                left.result(timeout=5),
                1,
            )

            with self.assertRaisesRegex(
                ValueError,
                "differs",
            ):
                right.result(timeout=5)

        self.assertEqual(
            effects,
            [("first", "a20_alpha")],
        )

        self.assertTrue(self.stored()[0].delivered)

    def test_parallel_ack_writes_cannot_lose_update(self):
        first = self.initialize()
        second = self.sender()

        ack0 = replace(
            self.events[0], delivered=True
        )
        ack1 = replace(
            self.events[1], delivered=True
        )

        entered = threading.Event()
        release = threading.Event()

        original = SymbolicReplayOutboxStore._write

        def held_write(path, document):
            if not entered.is_set():
                entered.set()

                if not release.wait(timeout=5):
                    raise TimeoutError(
                        "ACK writer release failed."
                    )

            return original(path, document)

        with patch.object(
            SymbolicReplayOutboxStore,
            "_write",
            side_effect=held_write,
        ):
            with ThreadPoolExecutor(
                max_workers=2
            ) as pool:
                try:
                    left = pool.submit(
                        SymbolicReplayOutboxStore.persist_ack,
                        first,
                        self.path,
                        0,
                        ack0,
                    )

                    self.assertTrue(
                        entered.wait(timeout=5)
                    )

                    right = pool.submit(
                        SymbolicReplayOutboxStore.persist_ack,
                        second,
                        self.path,
                        1,
                        ack1,
                    )

                    time.sleep(0.05)
                    self.assertFalse(right.done())

                finally:
                    release.set()

                left.result(timeout=5)

                with self.assertRaisesRegex(
                    ValueError, "differs"
                ):
                    right.result(timeout=5)

        self.assertEqual(
            [event.delivered for event in self.stored()],
            [True, False],
        )

        # The stale sender must reopen its checkpoint
        # before persisting its different ACK.
        fresh = self.universe()
        fresh.load_symbolic_replay_outbox(self.path)

        SymbolicReplayOutboxStore.persist_ack(
            fresh,
            self.path,
            1,
            ack1,
        )

        self.assertEqual(
            [event.delivered for event in self.stored()],
            [True, True],
        )

    def test_concurrent_save_rejects_stale_checkpoint(self):
        first = self.initialize(count=1)
        second = self.sender(count=1)

        first.symbolic_replay_outbox[0] = replace(
            self.events[0],
            delivered=True,
        )

        entered = threading.Event()
        release = threading.Event()

        original = SymbolicReplayOutboxStore._write

        def held_write(path, document):
            if not entered.is_set():
                entered.set()

                if not release.wait(timeout=5):
                    raise TimeoutError(
                        "Save writer release failed."
                    )

            return original(path, document)

        with patch.object(
            SymbolicReplayOutboxStore,
            "_write",
            side_effect=held_write,
        ):
            with ThreadPoolExecutor(
                max_workers=2
            ) as pool:
                try:
                    left = pool.submit(
                        SymbolicReplayOutboxStore.save,
                        first,
                        self.path,
                    )

                    self.assertTrue(
                        entered.wait(timeout=5)
                    )

                    right = pool.submit(
                        SymbolicReplayOutboxStore.save,
                        second,
                        self.path,
                    )

                finally:
                    release.set()

                left.result(timeout=5)

                with self.assertRaisesRegex(
                    ValueError,
                    "revoke",
                ):
                    right.result(timeout=5)

        self.assertTrue(self.stored()[0].delivered)

    def test_stale_sender_cannot_call_external_sink(self):
        first = self.initialize(count=1)
        stale = self.sender(count=1)

        effects = []

        self.assertEqual(
            first.retry_symbolic_replay_events(
                sink=lambda event: effects.append(
                    event.id
                ),
                durable_outbox_path=self.path,
            ),
            1,
        )

        with self.assertRaisesRegex(
            ValueError,
            "differs",
        ):
            stale.retry_symbolic_replay_events(
                sink=lambda event: effects.append(
                    "DUPLICATE:" + event.id
                ),
                durable_outbox_path=self.path,
            )

        self.assertEqual(effects, ["a20_alpha"])

    def test_failed_ack_write_releases_file_lock(self):
        first = self.initialize(count=1)

        effects = []

        with patch.object(
            SymbolicReplayOutboxStore,
            "_write",
            side_effect=OSError(
                "A20 injected ACK failure"
            ),
        ):
            with self.assertRaisesRegex(
                OSError,
                "A20 injected ACK failure",
            ):
                first.retry_symbolic_replay_events(
                    sink=lambda event: effects.append(
                        event.id
                    ),
                    durable_outbox_path=self.path,
                )

        self.assertEqual(effects, ["a20_alpha"])
        self.assertFalse(self.stored()[0].delivered)

        recovered = self.sender(count=1)

        self.assertEqual(
            recovered.retry_symbolic_replay_events(
                sink=lambda event: True,
                durable_outbox_path=self.path,
            ),
            1,
        )

        self.assertTrue(self.stored()[0].delivered)

    def test_sink_failure_releases_file_lock(self):
        first = self.initialize(count=1)

        def fail(event):
            raise RuntimeError(
                "A20 injected sink failure"
            )

        with self.assertRaisesRegex(
            RuntimeError,
            "A20 injected sink failure",
        ):
            first.retry_symbolic_replay_events(
                sink=fail,
                durable_outbox_path=self.path,
            )

        self.assertFalse(self.stored()[0].delivered)

        second = self.sender(count=1)

        self.assertEqual(
            second.retry_symbolic_replay_events(
                sink=lambda event: True,
                durable_outbox_path=self.path,
            ),
            1,
        )

        self.assertTrue(self.stored()[0].delivered)

    def test_duplicate_ack_cannot_rewrite_checkpoint(self):
        first = self.initialize(count=1)
        acknowledged = replace(
            self.events[0],
            delivered=True,
        )

        SymbolicReplayOutboxStore.persist_ack(
            first,
            self.path,
            0,
            acknowledged,
        )

        first.symbolic_replay_outbox[0] = acknowledged
        before = self.path.read_bytes()

        with self.assertRaisesRegex(
            ValueError,
            "Invalid durable acknowledgement",
        ):
            SymbolicReplayOutboxStore.persist_ack(
                first,
                self.path,
                0,
                acknowledged,
            )

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

    def test_locked_checkpoint_times_out_without_delivery(self):
        sender = self.initialize(count=1)
        effects = []

        original = exclusive_inbox_lock

        with original(
            self.path, timeout=1.0
        ):
            with patch(
                "universe.symbolic_replay_outbox_store."
                "exclusive_inbox_lock",
                side_effect=lambda path: original(
                    path,
                    timeout=0.05,
                ),
            ):
                with self.assertRaises(TimeoutError):
                    sender.retry_symbolic_replay_events(
                        sink=lambda event: effects.append(
                            event.id
                        ),
                        durable_outbox_path=self.path,
                    )

        self.assertEqual(effects, [])
        self.assertFalse(self.stored()[0].delivered)

    def test_second_process_waits_for_dispatch_lock(self):
        self.initialize(count=1)

        ready = self.directory / "a20_child_ready.txt"

        child_source = """
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from universe.universe import Universe

with redirect_stdout(io.StringIO()):
    universe = Universe(universe_id="a20_reality")

universe.load_symbolic_replay_outbox(sys.argv[1])
Path(sys.argv[2]).write_text("ready", encoding="utf-8")

assert universe.retry_symbolic_replay_events(
    sink=lambda event: True,
    durable_outbox_path=sys.argv[1],
) == 1

print("DELIVERED", flush=True)
"""

        root = Path(__file__).resolve().parents[1]
        child = None

        try:
            with exclusive_inbox_lock(
                self.path,
                timeout=5.0,
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
                        output, error = child.communicate()
                        self.fail(
                            f"Child exited: {output} {error}"
                        )

                    if time.monotonic() >= deadline:
                        self.fail(
                            "Child did not reach dispatch."
                        )

                    time.sleep(0.01)

                time.sleep(0.1)
                self.assertIsNone(child.poll())

            output, error = child.communicate(
                timeout=15,
            )

            self.assertEqual(
                child.returncode,
                0,
                msg=error,
            )

            self.assertIn("DELIVERED", output)
            self.assertTrue(self.stored()[0].delivered)

        finally:
            if child is not None:
                if child.poll() is None:
                    child.kill()

                child.communicate()


if __name__ == "__main__":
    unittest.main()
