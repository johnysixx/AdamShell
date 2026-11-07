import io
import json
import tempfile
import unittest

from contextlib import contextmanager, redirect_stdout
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import patch

import universe.symbolic_replay_recovery_auditor as audit_module

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
from universe.universe import Universe


class SymbolicReplayRecoveryAuditorTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a22_recovery_"
        )
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create(self, label, count=1):
        folder = self.directory / label
        folder.mkdir()

        identity = f"a22_{label}"
        outbox = folder / "outbox.json"
        inbox = folder / "inbox.json"

        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"{identity}_event_{i}",
                word_id=f"{identity}_word_{i}",
                sequence=i,
                message=f"A22 message {i}.",
            )
            for i in range(count)
        )

        sender.symbolic_replay_outbox.extend(events)

        SymbolicReplayOutboxStore.save(
            sender, outbox, require_new=True,
        )

        return sender, events, outbox, inbox

    @staticmethod
    def receiver(sender, inbox):
        return DurableSymbolicReplayInbox(
            path=inbox,
            universe_id=str(sender.id),
        )

    @staticmethod
    def inspect(sender, outbox, inbox):
        return SymbolicReplayRecoveryAuditor.inspect(
            sender,
            outbox_path=outbox,
            inbox_path=inbox,
        )

    @staticmethod
    def restore(target, outbox, inbox):
        return SymbolicReplayRecoveryAuditor.restore(
            target,
            outbox_path=outbox,
            inbox_path=inbox,
        )

    def test_consistent_pair_restores_without_runtime_replay(self):
        sender, events, outbox, inbox = (
            self.create("consistent")
        )

        receiver = self.receiver(sender, inbox)

        self.assertEqual(
            sender.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=outbox,
            ),
            1,
        )

        before_outbox = outbox.read_bytes()
        before_inbox = inbox.read_bytes()

        report = self.inspect(sender, outbox, inbox)

        self.assertEqual(report.status, "CONSISTENT")
        self.assertEqual(report.outbox_count, 1)
        self.assertEqual(report.inbox_count, 1)
        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.pending_ack_ids, ())

        target = self.universe(sender.id)

        restored_report, recovered_receiver = (
            self.restore(target, outbox, inbox)
        )

        self.assertEqual(restored_report, report)
        self.assertEqual(
            recovered_receiver.receipts,
            receiver.receipts,
        )

        self.assertEqual(
            target.pending_symbolic_replay_events,
            (),
        )
        self.assertEqual(target.quantum_boxes, [])
        self.assertEqual(
            target.quantum_state.tick_count,
            0,
        )
        self.assertEqual(outbox.read_bytes(), before_outbox)
        self.assertEqual(inbox.read_bytes(), before_inbox)

    def test_pending_ack_can_be_recovered_idempotently(self):
        sender, events, outbox, inbox = (
            self.create("pending_ack")
        )

        receiver = self.receiver(sender, inbox)
        receiver.accept(events[0])

        report = self.inspect(sender, outbox, inbox)

        self.assertEqual(
            report.status,
            "RECOVERABLE_PENDING_ACK",
        )
        self.assertEqual(
            report.pending_ack_ids,
            (events[0].id,),
        )

        target = self.universe(sender.id)

        _, recovered_receiver = (
            self.restore(target, outbox, inbox)
        )

        with patch.object(
            recovered_receiver,
            "_write",
            side_effect=AssertionError(
                "Duplicate receipt write."
            ),
        ):
            completed = (
                target.retry_symbolic_replay_events(
                    sink=recovered_receiver.accept,
                    durable_outbox_path=outbox,
                )
            )

        self.assertEqual(completed, 1)
        self.assertEqual(
            self.inspect(target, outbox, inbox).status,
            "CONSISTENT",
        )

    def test_pending_delivery_without_receipt_is_valid(self):
        sender, events, outbox, inbox = (
            self.create("pending_delivery", count=2)
        )

        receiver = self.receiver(sender, inbox)
        receiver.accept(events[0])

        report = self.inspect(sender, outbox, inbox)

        self.assertEqual(
            report.pending_ack_ids,
            (events[0].id,),
        )
        self.assertEqual(
            report.pending_delivery_ids,
            (events[1].id,),
        )

        target = self.universe(sender.id)
        _, recovered_receiver = self.restore(
            target, outbox, inbox
        )

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=recovered_receiver.accept,
                durable_outbox_path=outbox,
            ),
            2,
        )

        self.assertEqual(
            len(self.receiver(sender, inbox).receipts),
            2,
        )
        self.assertEqual(
            self.inspect(target, outbox, inbox).status,
            "CONSISTENT",
        )

    def test_missing_outbox_rejects_without_publication(self):
        sender, events, outbox, inbox = (
            self.create("missing_outbox")
        )
        self.receiver(sender, inbox).accept(events[0])

        outbox.unlink()

        target = self.universe(sender.id)

        with self.assertRaises(FileNotFoundError):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_missing_inbox_without_ack_is_fail_closed(self):
        sender, events, outbox, inbox = (
            self.create("missing_inbox_pending")
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            FileNotFoundError, "inbox checkpoint missing"
        ):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )
        self.assertFalse(inbox.exists())

    def test_missing_inbox_after_ack_is_rejected(self):
        sender, events, outbox, inbox = (
            self.create("missing_inbox_acked")
        )

        receiver = self.receiver(sender, inbox)

        sender.retry_symbolic_replay_events(
            sink=receiver.accept,
            durable_outbox_path=outbox,
        )

        inbox.unlink()

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            FileNotFoundError, "inbox checkpoint missing"
        ):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_unknown_receipt_is_rejected(self):
        sender, events, outbox, inbox = (
            self.create("unknown_receipt")
        )

        receiver = self.receiver(sender, inbox)

        receiver.accept(
            SymbolicReplayOutboxEvent(
                id="unknown_event",
                word_id="unknown_word",
                sequence=0,
                message="Unknown event.",
            )
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Unknown inbox receipt"
        ):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_conflicting_receipt_payload_is_rejected(self):
        sender, events, outbox, inbox = (
            self.create("payload_conflict")
        )

        receiver = self.receiver(sender, inbox)

        receiver.accept(
            replace(
                events[0],
                message="Conflicting payload.",
            )
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "payload conflict"
        ):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_ack_without_receipt_is_rejected(self):
        sender, events, outbox, inbox = (
            self.create("missing_receipt", count=2)
        )

        self.receiver(sender, inbox).accept(events[0])

        SymbolicReplayOutboxStore.persist_ack(
            sender,
            outbox,
            1,
            replace(events[1], delivered=True),
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "ACK without matching"
        ):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_corrupted_outbox_is_rejected(self):
        sender, events, outbox, inbox = (
            self.create("corrupt_outbox")
        )

        self.receiver(sender, inbox).accept(events[0])

        document = json.loads(
            outbox.read_text(encoding="utf-8")
        )

        document["events"][0]["message"] = "tampered"

        outbox.write_text(
            json.dumps(document),
            encoding="utf-8",
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "checksum mismatch"
        ):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_corrupted_inbox_is_rejected(self):
        sender, events, outbox, inbox = (
            self.create("corrupt_inbox")
        )

        self.receiver(sender, inbox).accept(events[0])

        document = json.loads(
            inbox.read_text(encoding="utf-8")
        )

        document["receipts"][0]["message"] = "tampered"

        inbox.write_text(
            json.dumps(document),
            encoding="utf-8",
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "checksum mismatch"
        ):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_truncated_json_rejected_without_publication(self):
        sender, events, outbox, inbox = (
            self.create("truncated")
        )

        self.receiver(sender, inbox).accept(events[0])

        original = outbox.read_bytes()
        outbox.write_text('{"format":', encoding="utf-8")

        target = self.universe(sender.id)

        with self.assertRaises(json.JSONDecodeError):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

        outbox.write_bytes(original)
        inbox.write_text('{"format":', encoding="utf-8")

        with self.assertRaises(json.JSONDecodeError):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_foreign_universe_is_rejected(self):
        sender, events, outbox, inbox = (
            self.create("foreign")
        )

        self.receiver(sender, inbox).accept(events[0])

        foreign = self.universe("foreign_universe")

        with self.assertRaisesRegex(
            ValueError, "another universe"
        ):
            self.restore(foreign, outbox, inbox)

        self.assertEqual(
            foreign.symbolic_replay_outbox, []
        )

    def test_nonempty_target_is_not_overwritten(self):
        sender, events, outbox, inbox = (
            self.create("nonempty")
        )

        self.receiver(sender, inbox).accept(events[0])

        target = self.universe(sender.id)
        target.symbolic_replay_outbox.append(events[0])

        before = tuple(target.symbolic_replay_outbox)

        with self.assertRaisesRegex(
            ValueError, "empty target outbox"
        ):
            self.restore(target, outbox, inbox)

        self.assertEqual(
            tuple(target.symbolic_replay_outbox),
            before,
        )

    def test_orphan_temp_files_do_not_affect_audit(self):
        sender, events, outbox, inbox = (
            self.create("orphan")
        )

        self.receiver(sender, inbox).accept(events[0])

        outbox_temp = outbox.with_name(
            ".outbox.json.orphan.tmp"
        )
        inbox_temp = inbox.with_name(
            ".inbox.json.orphan.tmp"
        )

        outbox_temp.write_text(
            '{"partial":',
            encoding="utf-8",
        )
        inbox_temp.write_text(
            '{"partial":',
            encoding="utf-8",
        )

        self.assertEqual(
            self.inspect(sender, outbox, inbox).status,
            "RECOVERABLE_PENDING_ACK",
        )

        self.assertTrue(outbox_temp.exists())
        self.assertTrue(inbox_temp.exists())

    def test_lock_order_matches_delivery(self):
        sender, events, outbox, inbox = (
            self.create("lock_order")
        )

        self.receiver(sender, inbox).accept(events[0])

        original = audit_module.exclusive_inbox_lock
        acquired = []

        @contextmanager
        def observed(path):
            acquired.append(Path(path).resolve())
            with original(path):
                yield

        with patch.object(
            audit_module,
            "exclusive_inbox_lock",
            new=observed,
        ):
            self.inspect(sender, outbox, inbox)

        self.assertEqual(
            acquired,
            [outbox.resolve(), inbox.resolve()],
        )


if __name__ == "__main__":
    unittest.main()
