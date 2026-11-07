import io
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from universe.universe import Universe
from universe.symbolic_replay_bootstrap import (
    SymbolicReplayBootstrap,
)
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)
from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.symbolic_replay_recovery_auditor import (
    SymbolicReplayRecoveryAuditor,
)


CHILD_SOURCE = """
import io
import sys
import time

from contextlib import redirect_stdout
from pathlib import Path

from universe.universe import Universe
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)

identity, outbox, inbox, ready, release = sys.argv[1:]

ready = Path(ready)
release = Path(release)

with redirect_stdout(io.StringIO()):
    sender = Universe(universe_id=identity)

sender.load_symbolic_replay_outbox(outbox)

receiver = DurableSymbolicReplayInbox(
    path=inbox,
    universe_id=identity,
)


def sink(event):
    assert receiver.accept(event)

    ready.write_text("ready", encoding="utf-8")

    deadline = time.monotonic() + 15

    while not release.exists():
        if time.monotonic() >= deadline:
            raise TimeoutError("Release signal missing.")
        time.sleep(0.02)

    return True


assert sender.retry_symbolic_replay_events(
    sink=sink,
    durable_outbox_path=outbox,
) == 1

print("DISPATCH_COMPLETED", flush=True)
"""


class SymbolicReplayBootstrapConcurrencyTests(
    unittest.TestCase
):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a24_bootstrap_"
        )
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)
        self.root = Path(__file__).resolve().parents[1]

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create(self, label, count=1):
        folder = self.directory / label
        folder.mkdir()

        identity = "a24_" + label
        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"{identity}_event_{index}",
                word_id=f"{identity}_word_{index}",
                sequence=index,
                message=f"A24 message {index}.",
            )
            for index in range(count)
        )

        sender.symbolic_replay_outbox.extend(events)

        paths = (
            folder / "outbox.json",
            folder / "inbox.json",
            folder / "bootstrap.json",
        )

        return sender, events, paths

    @staticmethod
    def initialize(sender, paths):
        outbox, inbox, manifest = paths

        return SymbolicReplayBootstrap.initialize(
            sender,
            outbox_path=outbox,
            inbox_path=inbox,
            manifest_path=manifest,
        )

    @staticmethod
    def recover(target, paths):
        outbox, inbox, manifest = paths

        return SymbolicReplayBootstrap.recover(
            target,
            outbox_path=outbox,
            inbox_path=inbox,
            manifest_path=manifest,
        )

    @staticmethod
    def state(manifest):
        return json.loads(
            manifest.read_text(encoding="utf-8")
        )["state"]

    def test_successful_snapshot_matches_checkpoint(self):
        sender, events, paths = self.create(
            "consistent", count=2
        )
        outbox, inbox, manifest = paths

        report, receiver = self.initialize(
            sender, paths
        )

        persisted = SymbolicReplayOutboxStore.read(
            sender, outbox
        )

        fresh = SymbolicReplayRecoveryAuditor.inspect(
            sender,
            outbox_path=outbox,
            inbox_path=inbox,
        )

        self.assertEqual(persisted, events)
        self.assertEqual(report, fresh)
        self.assertEqual(report.outbox_count, 2)
        self.assertEqual(
            report.pending_delivery_ids,
            tuple(event.id for event in events),
        )
        self.assertEqual(receiver.receipts, ())
        self.assertEqual(self.state(manifest), "READY")

    def test_preparing_phase_drift_is_fail_closed(self):
        sender, events, paths = self.create(
            "preparing"
        )
        outbox, inbox, manifest = paths

        extra = SymbolicReplayOutboxEvent(
            id="a24_preparing_extra",
            word_id="a24_preparing_extra_word",
            sequence=1,
            message="Unexpected event.",
        )

        original = SymbolicReplayBootstrap._write

        def changed(path, document):
            original(path, document)

            if document["state"] == "PREPARING":
                sender.symbolic_replay_outbox.append(extra)

        with patch.object(
            SymbolicReplayBootstrap,
            "_write",
            new=staticmethod(changed),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "changed during initialization",
            ):
                self.initialize(sender, paths)

        self.assertEqual(self.state(manifest), "PREPARING")
        self.assertFalse(outbox.exists())
        self.assertFalse(inbox.exists())

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            RuntimeError, "not READY"
        ):
            self.recover(target, paths)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_outbox_write_drift_preserves_snapshot(self):
        sender, events, paths = self.create(
            "outbox_drift"
        )
        outbox, inbox, manifest = paths

        extra = SymbolicReplayOutboxEvent(
            id="a24_outbox_extra",
            word_id="a24_outbox_extra_word",
            sequence=1,
            message="Unexpected event.",
        )

        original = SymbolicReplayOutboxStore._write

        def changed(path, document):
            original(path, document)
            sender.symbolic_replay_outbox.append(extra)

        with patch.object(
            SymbolicReplayOutboxStore,
            "_write",
            new=staticmethod(changed),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "changed during initialization",
            ):
                self.initialize(sender, paths)

        persisted = SymbolicReplayOutboxStore.read(
            sender, outbox
        )

        self.assertEqual(persisted, events)
        self.assertEqual(self.state(manifest), "PREPARING")
        self.assertFalse(inbox.exists())

    def test_inbox_write_drift_preserves_preparing(self):
        sender, events, paths = self.create(
            "inbox_drift"
        )
        outbox, inbox, manifest = paths

        extra = SymbolicReplayOutboxEvent(
            id="a24_inbox_extra",
            word_id="a24_inbox_extra_word",
            sequence=1,
            message="Unexpected event.",
        )

        original = DurableSymbolicReplayInbox._write

        def changed(receiver, receipts):
            original(receiver, receipts)
            sender.symbolic_replay_outbox.append(extra)

        with patch.object(
            DurableSymbolicReplayInbox,
            "_write",
            new=changed,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "changed during initialization",
            ):
                self.initialize(sender, paths)

        self.assertEqual(
            SymbolicReplayOutboxStore.read(
                sender, outbox
            ),
            events,
        )
        self.assertTrue(inbox.is_file())
        self.assertEqual(self.state(manifest), "PREPARING")

    def test_ready_write_drift_never_returns_stale_report(self):
        sender, events, paths = self.create(
            "ready_drift"
        )
        outbox, inbox, manifest = paths

        extra = SymbolicReplayOutboxEvent(
            id="a24_ready_extra",
            word_id="a24_ready_extra_word",
            sequence=1,
            message="Unexpected event.",
        )

        original = SymbolicReplayBootstrap._write

        def changed(path, document):
            original(path, document)

            if document["state"] == "READY":
                sender.symbolic_replay_outbox.append(extra)

        with patch.object(
            SymbolicReplayBootstrap,
            "_write",
            new=staticmethod(changed),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "changed during initialization",
            ):
                self.initialize(sender, paths)

        # READY was persisted, but the single-event
        # snapshot remains valid and can be recovered
        # by an independent, fresh Universe.
        self.assertEqual(self.state(manifest), "READY")
        self.assertEqual(
            SymbolicReplayOutboxStore.read(
                sender, outbox
            ),
            events,
        )

        target = self.universe(sender.id)
        report, receiver = self.recover(
            target, paths
        )

        self.assertEqual(report.outbox_count, 1)
        self.assertEqual(
            tuple(target.symbolic_replay_outbox),
            events,
        )
        self.assertEqual(receiver.receipts, ())

    def test_concurrent_initializers_are_serialized(self):
        first, events, paths = self.create(
            "concurrent"
        )
        second = self.universe(first.id)

        second.symbolic_replay_outbox.extend(events)

        entered = threading.Event()
        release = threading.Event()

        original = SymbolicReplayBootstrap._write

        def held(path, document):
            original(path, document)

            if document["state"] == "PREPARING":
                entered.set()

                if not release.wait(timeout=10):
                    raise TimeoutError(
                        "Initialization release missing."
                    )

        with patch.object(
            SymbolicReplayBootstrap,
            "_write",
            new=staticmethod(held),
        ):
            with ThreadPoolExecutor(
                max_workers=2
            ) as pool:
                try:
                    left = pool.submit(
                        self.initialize, first, paths
                    )

                    self.assertTrue(
                        entered.wait(timeout=10)
                    )

                    right = pool.submit(
                        self.initialize, second, paths
                    )

                    time.sleep(0.05)
                    self.assertFalse(right.done())

                finally:
                    release.set()

                report, _ = left.result(timeout=10)

                with self.assertRaises(FileExistsError):
                    right.result(timeout=10)

        self.assertEqual(report.outbox_count, 1)

        target = self.universe(first.id)
        recovered, _ = self.recover(target, paths)

        self.assertEqual(recovered.outbox_count, 1)

    def test_recovery_waits_for_cross_process_dispatch(self):
        sender, events, paths = self.create(
            "active_dispatch"
        )
        outbox, inbox, manifest = paths

        self.initialize(sender, paths)

        ready = self.directory / "dispatch_ready.txt"
        release = self.directory / "dispatch_release.txt"

        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-c",
                CHILD_SOURCE,
                str(sender.id),
                str(outbox),
                str(inbox),
                str(ready),
                str(release),
            ],
            cwd=str(self.root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            deadline = time.monotonic() + 10

            while not ready.exists():
                if process.poll() is not None:
                    output, error = process.communicate()
                    self.fail(
                        f"Child exited: {output!r} {error!r}"
                    )

                if time.monotonic() >= deadline:
                    self.fail("Dispatch did not start.")

                time.sleep(0.02)

            target = self.universe(sender.id)

            with ThreadPoolExecutor(
                max_workers=1
            ) as pool:
                try:
                    future = pool.submit(
                        self.recover, target, paths
                    )

                    time.sleep(0.1)
                    self.assertFalse(future.done())

                    self.assertEqual(
                        target.symbolic_replay_outbox,
                        [],
                    )

                finally:
                    release.write_text(
                        "release",
                        encoding="utf-8",
                    )

                report, receiver = future.result(
                    timeout=15
                )

            output, error = process.communicate(
                timeout=20
            )

            self.assertEqual(
                process.returncode,
                0,
                msg=error,
            )
            self.assertIn(
                "DISPATCH_COMPLETED",
                output,
            )

            self.assertEqual(
                report.delivered_count,
                1,
            )
            self.assertEqual(len(receiver.receipts), 1)
            self.assertEqual(
                target.pending_symbolic_replay_events,
                (),
            )

        finally:
            release.write_text(
                "release",
                encoding="utf-8",
            )

            if process.poll() is None:
                process.kill()

            process.communicate()


if __name__ == "__main__":
    unittest.main()
