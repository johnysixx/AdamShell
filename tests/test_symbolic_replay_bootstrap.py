import io
import json
import subprocess
import sys
import tempfile
import unittest

from contextlib import contextmanager, redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import universe.symbolic_replay_bootstrap as bootstrap_module

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
import os
import sys
from contextlib import redirect_stdout

from universe.universe import Universe
from universe.symbolic_replay_bootstrap import (
    SymbolicReplayBootstrap,
)

mode, identity, outbox, inbox, manifest = sys.argv[1:]

with redirect_stdout(io.StringIO()):
    universe = Universe(universe_id=identity)

original_write = SymbolicReplayBootstrap._write

def crash_write(path, document):
    if (
        mode == "before_ready"
        and document["state"] == "READY"
    ):
        os._exit(72)

    original_write(path, document)

    if (
        mode == "after_preparing"
        and document["state"] == "PREPARING"
    ):
        os._exit(71)

SymbolicReplayBootstrap._write = staticmethod(crash_write)

SymbolicReplayBootstrap.initialize(
    universe,
    outbox_path=outbox,
    inbox_path=inbox,
    manifest_path=manifest,
)

raise AssertionError("Expected child process crash.")
"""


class SymbolicReplayBootstrapTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a23_bootstrap_"
        )
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)
        self.root = Path(__file__).resolve().parents[1]

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    @staticmethod
    def event(identity, *, delivered=False):
        return SymbolicReplayOutboxEvent(
            id=f"{identity}_event",
            word_id=f"{identity}_word",
            sequence=0,
            message=f"Bootstrap event for {identity}.",
            delivered=delivered,
        )

    def paths(self, label):
        folder = self.directory / label
        folder.mkdir()

        identity = f"a23_{label}"

        return (
            self.universe(identity),
            folder / "outbox.json",
            folder / "inbox.json",
            folder / "bootstrap.json",
        )

    @staticmethod
    def call(method, universe, outbox, inbox, manifest):
        return method(
            universe,
            outbox_path=outbox,
            inbox_path=inbox,
            manifest_path=manifest,
        )

    def initialize(self, label):
        universe, outbox, inbox, manifest = (
            self.paths(label)
        )

        report, receiver = self.call(
            SymbolicReplayBootstrap.initialize,
            universe, outbox, inbox, manifest,
        )

        return (
            universe, outbox, inbox,
            manifest, report, receiver,
        )

    def crash(self, mode, universe, outbox, inbox, manifest):
        expected_code = {
            "after_preparing": 71,
            "before_ready": 72,
        }[mode]

        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                CHILD_SOURCE,
                mode,
                str(universe.id),
                str(outbox),
                str(inbox),
                str(manifest),
            ],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            timeout=20,
        )

        self.assertEqual(
            result.returncode,
            expected_code,
            msg=result.stderr,
        )

    def test_initialize_empty_pair_and_ready_manifest(self):
        universe, outbox, inbox, manifest, report, receiver = (
            self.initialize("empty")
        )

        self.assertTrue(outbox.is_file())
        self.assertTrue(inbox.is_file())
        self.assertTrue(manifest.is_file())
        self.assertEqual(
            json.loads(manifest.read_text(
                encoding="utf-8"
            ))["state"],
            "READY",
        )

        self.assertEqual(report.status, "CONSISTENT")
        self.assertEqual(report.outbox_count, 0)
        self.assertEqual(report.inbox_count, 0)
        self.assertEqual(receiver.receipts, ())
        self.assertEqual(
            SymbolicReplayOutboxStore.read(
                universe, outbox,
            ),
            (),
        )

    def test_initialize_pending_event_and_recover(self):
        universe, outbox, inbox, manifest = (
            self.paths("pending")
        )

        event = self.event(str(universe.id))
        universe.symbolic_replay_outbox.append(event)

        report, _ = self.call(
            SymbolicReplayBootstrap.initialize,
            universe, outbox, inbox, manifest,
        )

        self.assertEqual(
            report.pending_delivery_ids,
            (event.id,),
        )

        target = self.universe(universe.id)

        recovered, receiver = self.call(
            SymbolicReplayBootstrap.recover,
            target, outbox, inbox, manifest,
        )

        self.assertEqual(
            recovered.pending_delivery_ids,
            (event.id,),
        )

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=outbox,
            ),
            1,
        )

        self.assertEqual(
            target.pending_symbolic_replay_events,
            (),
        )
        self.assertEqual(
            len(
                DurableSymbolicReplayInbox(
                    path=inbox,
                    universe_id=str(universe.id),
                ).receipts
            ),
            1,
        )
        self.assertEqual(
            SymbolicReplayRecoveryAuditor.inspect(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
            ).status,
            "CONSISTENT",
        )
        self.assertEqual(target.quantum_boxes, [])

    def test_recover_rejects_both_absent(self):
        universe, outbox, inbox, manifest = (
            self.paths("absent")
        )

        with self.assertRaises(FileNotFoundError):
            self.call(
                SymbolicReplayBootstrap.recover,
                universe, outbox, inbox, manifest,
            )

        self.assertFalse(outbox.exists())
        self.assertFalse(inbox.exists())
        self.assertFalse(manifest.exists())
        self.assertEqual(universe.symbolic_replay_outbox, [])

    def test_initialize_rejects_existing_outbox(self):
        universe, outbox, inbox, manifest = (
            self.paths("existing_outbox")
        )

        outbox.write_bytes(b"existing outbox")
        before = outbox.read_bytes()

        with self.assertRaises(FileExistsError):
            self.call(
                SymbolicReplayBootstrap.initialize,
                universe, outbox, inbox, manifest,
            )

        self.assertEqual(outbox.read_bytes(), before)
        self.assertFalse(inbox.exists())
        self.assertFalse(manifest.exists())

    def test_initialize_rejects_existing_inbox(self):
        universe, outbox, inbox, manifest = (
            self.paths("existing_inbox")
        )

        inbox.write_bytes(b"existing inbox")
        before = inbox.read_bytes()

        with self.assertRaises(FileExistsError):
            self.call(
                SymbolicReplayBootstrap.initialize,
                universe, outbox, inbox, manifest,
            )

        self.assertEqual(inbox.read_bytes(), before)
        self.assertFalse(outbox.exists())
        self.assertFalse(manifest.exists())

    def test_existing_pair_without_manifest_is_rejected(self):
        universe, outbox, inbox, manifest = (
            self.paths("no_manifest")
        )

        SymbolicReplayOutboxStore.save(
            universe,
            outbox,
            require_new=True,
        )

        receiver = DurableSymbolicReplayInbox(
            path=inbox,
            universe_id=str(universe.id),
        )
        receiver._write(())

        target = self.universe(universe.id)

        with self.assertRaises(FileNotFoundError):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        self.assertTrue(outbox.exists())
        self.assertTrue(inbox.exists())
        self.assertFalse(manifest.exists())
        self.assertEqual(target.symbolic_replay_outbox, [])

    def test_double_initialize_preserves_checkpoint_bytes(self):
        universe, outbox, inbox, manifest, _, _ = (
            self.initialize("double")
        )

        before = tuple(
            path.read_bytes()
            for path in (outbox, inbox, manifest)
        )

        with self.assertRaises(FileExistsError):
            self.call(
                SymbolicReplayBootstrap.initialize,
                universe, outbox, inbox, manifest,
            )

        self.assertEqual(
            tuple(
                path.read_bytes()
                for path in (outbox, inbox, manifest)
            ),
            before,
        )

    def test_missing_inbox_after_ready_is_rejected(self):
        universe, outbox, inbox, manifest, _, _ = (
            self.initialize("lost_inbox")
        )

        inbox.unlink()
        target = self.universe(universe.id)

        with self.assertRaises(FileNotFoundError):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        self.assertEqual(target.symbolic_replay_outbox, [])
        self.assertTrue(manifest.exists())
        self.assertFalse(inbox.exists())

    def test_missing_outbox_after_ready_is_rejected(self):
        universe, outbox, inbox, manifest, _, _ = (
            self.initialize("lost_outbox")
        )

        outbox.unlink()
        target = self.universe(universe.id)

        with self.assertRaises(FileNotFoundError):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        self.assertEqual(target.symbolic_replay_outbox, [])
        self.assertTrue(manifest.exists())
        self.assertFalse(outbox.exists())

    def test_foreign_universe_is_rejected(self):
        universe, outbox, inbox, manifest, _, _ = (
            self.initialize("foreign")
        )

        target = self.universe("a23_other_universe")

        with self.assertRaisesRegex(
            ValueError,
            "another universe",
        ):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        self.assertEqual(target.symbolic_replay_outbox, [])

    def test_manifest_checksum_corruption_is_rejected(self):
        universe, outbox, inbox, manifest, _, _ = (
            self.initialize("checksum")
        )

        document = json.loads(
            manifest.read_text(encoding="utf-8")
        )
        document["state"] = "PREPARING"

        manifest.write_text(
            json.dumps(document),
            encoding="utf-8",
        )

        target = self.universe(universe.id)

        with self.assertRaisesRegex(
            ValueError, "checksum mismatch"
        ):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        self.assertEqual(target.symbolic_replay_outbox, [])

    def test_truncated_manifest_is_rejected(self):
        universe, outbox, inbox, manifest, _, _ = (
            self.initialize("truncated")
        )

        manifest.write_text(
            '{"format":',
            encoding="utf-8",
        )

        target = self.universe(universe.id)

        with self.assertRaises(json.JSONDecodeError):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        self.assertEqual(target.symbolic_replay_outbox, [])

    def test_manifest_checkpoint_binding_is_enforced(self):
        universe, outbox, inbox, manifest, _, _ = (
            self.initialize("binding")
        )

        other_inbox = inbox.with_name("other_inbox.json")
        target = self.universe(universe.id)

        with self.assertRaisesRegex(
            ValueError, "path mismatch"
        ):
            self.call(
                SymbolicReplayBootstrap.recover,
                target,
                outbox,
                other_inbox,
                manifest,
            )

        self.assertEqual(target.symbolic_replay_outbox, [])

    def test_crash_after_preparing_marker_is_fail_closed(self):
        universe, outbox, inbox, manifest = (
            self.paths("crash_preparing")
        )

        self.crash(
            "after_preparing",
            universe, outbox, inbox, manifest,
        )

        self.assertTrue(manifest.is_file())
        self.assertFalse(outbox.exists())
        self.assertFalse(inbox.exists())

        self.assertEqual(
            json.loads(
                manifest.read_text(encoding="utf-8")
            )["state"],
            "PREPARING",
        )

        target = self.universe(universe.id)

        with self.assertRaisesRegex(
            RuntimeError, "not READY"
        ):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        with self.assertRaises(FileExistsError):
            self.call(
                SymbolicReplayBootstrap.initialize,
                target, outbox, inbox, manifest,
            )

        self.assertEqual(target.symbolic_replay_outbox, [])

    def test_crash_before_ready_preserves_complete_pair(self):
        universe, outbox, inbox, manifest = (
            self.paths("crash_before_ready")
        )

        self.crash(
            "before_ready",
            universe, outbox, inbox, manifest,
        )

        self.assertTrue(manifest.is_file())
        self.assertTrue(outbox.is_file())
        self.assertTrue(inbox.is_file())

        self.assertEqual(
            json.loads(
                manifest.read_text(encoding="utf-8")
            )["state"],
            "PREPARING",
        )

        self.assertEqual(
            SymbolicReplayOutboxStore.read(
                universe, outbox,
            ),
            (),
        )

        self.assertEqual(
            DurableSymbolicReplayInbox(
                path=inbox,
                universe_id=str(universe.id),
            ).receipts,
            (),
        )

        target = self.universe(universe.id)

        with self.assertRaisesRegex(
            RuntimeError, "not READY"
        ):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        self.assertEqual(target.symbolic_replay_outbox, [])

    def test_recover_refuses_nonempty_target(self):
        universe, outbox, inbox, manifest, _, _ = (
            self.initialize("nonempty_target")
        )

        target = self.universe(universe.id)
        event = self.event(str(universe.id))

        target.symbolic_replay_outbox.append(event)

        with self.assertRaisesRegex(
            ValueError, "empty target outbox"
        ):
            self.call(
                SymbolicReplayBootstrap.recover,
                target, outbox, inbox, manifest,
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [event],
        )

    def test_initialize_refuses_predelivered_event(self):
        universe, outbox, inbox, manifest = (
            self.paths("predelivered")
        )

        event = self.event(
            str(universe.id),
            delivered=True,
        )

        universe.symbolic_replay_outbox.append(event)

        with self.assertRaisesRegex(
            ValueError, "must be pending"
        ):
            self.call(
                SymbolicReplayBootstrap.initialize,
                universe, outbox, inbox, manifest,
            )

        self.assertFalse(outbox.exists())
        self.assertFalse(inbox.exists())
        self.assertFalse(manifest.exists())

    def test_bootstrap_lock_order(self):
        universe, outbox, inbox, manifest = (
            self.paths("lock_order")
        )

        original = bootstrap_module.exclusive_inbox_lock
        acquired = []

        @contextmanager
        def observed(path):
            acquired.append(Path(path).resolve())

            with original(path):
                yield

        with patch.object(
            bootstrap_module,
            "exclusive_inbox_lock",
            new=observed,
        ):
            self.call(
                SymbolicReplayBootstrap.initialize,
                universe, outbox, inbox, manifest,
            )

        self.assertEqual(
            acquired,
            [
                manifest.resolve(),
                outbox.resolve(),
                inbox.resolve(),
            ],
        )

    def test_invalid_paths_are_rejected(self):
        universe, outbox, inbox, manifest = (
            self.paths("invalid_paths")
        )

        with self.assertRaisesRegex(
            ValueError, "distinct"
        ):
            self.call(
                SymbolicReplayBootstrap.initialize,
                universe, outbox, outbox, manifest,
            )

        other_folder = self.directory / "other"
        other_folder.mkdir()

        with self.assertRaisesRegex(
            ValueError, "same directory"
        ):
            self.call(
                SymbolicReplayBootstrap.initialize,
                universe,
                outbox,
                other_folder / "inbox.json",
                manifest,
            )

        self.assertFalse(outbox.exists())
        self.assertFalse(inbox.exists())
        self.assertFalse(manifest.exists())


if __name__ == "__main__":
    unittest.main()
