"""A31 witnessed-ACK authority consistency regressions.

The authority here is a controlled test double.
No test claims independent durable remote storage.
"""

import io
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path

from universe.universe import Universe
from universe.symbolic_replay_bootstrap import (
    SymbolicReplayBootstrap,
)
from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.symbolic_replay_receipt_witness import (
    SymbolicReplayReceiptWitness,
)
from universe.symbolic_replay_witness_authority import (
    SymbolicReplayWitnessAuthority,
    SymbolicReplayWitnessRevision,
)
from universe.symbolic_replay_witness_delivery import (
    SymbolicReplayWitnessDelivery,
)


class MemoryAuthority(SymbolicReplayWitnessAuthority):
    """Test double with controllable inconsistent responses."""

    def __init__(self, witness):
        self.initial = SymbolicReplayWitnessRevision(
            revision=0,
            witness=witness,
        )

        self.current = self.initial
        self.reads = 0
        self.publications = 0

        self.unavailable = False
        self.fail_read_number = None
        self.fake_success = False
        self.stale_after_publication = False
        self._stale_next = None

    def read_current(
        self, *, universe_id, batch_sha256,
    ):
        self.reads += 1

        if (
            self.unavailable
            or self.fail_read_number == self.reads
        ):
            raise ConnectionError(
                "Authority read unavailable."
            )

        if self._stale_next is not None:
            previous = self._stale_next
            self._stale_next = None
            return previous

        return self.current

    def publish(
        self, witness, *, expected_revision,
    ):
        self.publications += 1

        proposed = self.transition(
            self.current,
            witness,
            expected_revision=expected_revision,
        )

        if self.fake_success:
            # Return a canonical revision without commit.
            return proposed

        previous = self.current
        self.current = proposed

        if self.stale_after_publication:
            self.stale_after_publication = False
            self._stale_next = previous

        return self.current


class WitnessConsistencyTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a31_witness_consistency_"
        )
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create(self, label, *, count=1):
        folder = self.directory / label
        folder.mkdir()

        identity = "a31_" + label
        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"{identity}_event_{index}",
                word_id=f"{identity}_word_{index}",
                sequence=index,
                message=f"A31 event {index}.",
            )
            for index in range(count)
        )

        sender.symbolic_replay_outbox.extend(events)

        paths = (
            folder / "outbox.json",
            folder / "inbox.json",
            folder / "bootstrap.json",
        )

        report, receiver = (
            SymbolicReplayBootstrap.initialize(
                sender,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
            )
        )

        self.assertEqual(report.outbox_count, count)

        witness = SymbolicReplayReceiptWitness(
            universe_id=str(sender.id),
            batch_sha256=(
                SymbolicReplayOutboxStore.lineage_digest(
                    sender.id,
                    events,
                )
            ),
            receipt_ids=(),
        )

        authority = MemoryAuthority(witness)

        runner = SymbolicReplayWitnessDelivery(
            sender,
            outbox_path=paths[0],
            receiver=receiver,
            witness_authority=authority,
        )

        return (
            sender, events, receiver,
            paths, authority, runner,
        )

    @staticmethod
    def checkpoint(paths):
        return tuple(path.read_bytes() for path in paths)

    def recover(self, sender, paths, **kwargs):
        target = self.universe(sender.id)

        report, receiver = SymbolicReplayBootstrap.recover(
            target,
            outbox_path=paths[0],
            inbox_path=paths[1],
            manifest_path=paths[2],
            **kwargs,
        )

        return target, report, receiver

    def test_valid_readback_and_completed_batch_preflight(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("valid")
        )

        self.assertEqual(runner.dispatch(), 1)
        self.assertEqual(authority.current.revision, 1)
        self.assertGreaterEqual(authority.reads, 3)

        before = self.checkpoint(paths)
        reads_before = authority.reads

        self.assertEqual(runner.dispatch(), 0)

        self.assertGreater(authority.reads, reads_before)
        self.assertEqual(
            self.checkpoint(paths), before
        )
        self.assertEqual(authority.publications, 1)

    def test_false_publication_response_cannot_ack(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("false_success")
        )

        authority.fake_success = True
        original_outbox = paths[0].read_bytes()

        with self.assertRaisesRegex(
            ValueError, "read-back mismatch"
        ):
            runner.dispatch()

        self.assertEqual(authority.current.revision, 0)
        self.assertEqual(len(receiver.receipts), 1)
        self.assertEqual(
            paths[0].read_bytes(), original_outbox
        )
        self.assertFalse(
            sender.symbolic_replay_outbox[0].delivered
        )

        authority.fake_success = False

        self.assertEqual(runner.dispatch(), 1)
        self.assertEqual(authority.current.revision, 1)

    def test_readback_outage_keeps_ack_pending(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("readback_outage")
        )

        # Preflight read: 1
        # Per-event read: 2
        # Post-publication read-back: 3
        authority.fail_read_number = 3

        with self.assertRaisesRegex(
            ConnectionError, "read unavailable"
        ):
            runner.dispatch()

        self.assertEqual(authority.current.revision, 1)
        self.assertEqual(authority.publications, 1)
        self.assertEqual(len(receiver.receipts), 1)

        self.assertFalse(
            SymbolicReplayOutboxStore.read(
                sender, paths[0]
            )[0].delivered
        )

        receipt_before = paths[1].read_bytes()

        authority.fail_read_number = None

        self.assertEqual(runner.dispatch(), 1)
        self.assertEqual(authority.publications, 1)
        self.assertEqual(
            paths[1].read_bytes(), receipt_before
        )

    def test_stale_readback_cannot_ack(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("stale_readback")
        )

        authority.stale_after_publication = True

        with self.assertRaisesRegex(
            ValueError, "read-back mismatch"
        ):
            runner.dispatch()

        self.assertEqual(authority.current.revision, 1)
        self.assertFalse(
            sender.symbolic_replay_outbox[0].delivered
        )

        self.assertEqual(runner.dispatch(), 1)
        self.assertEqual(authority.publications, 1)
        self.assertTrue(
            sender.symbolic_replay_outbox[0].delivered
        )

    def test_completed_batch_authority_outage_fails_closed(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("completed_outage")
        )

        self.assertEqual(runner.dispatch(), 1)

        before = self.checkpoint(paths)
        reads_before = authority.reads

        authority.unavailable = True

        with self.assertRaisesRegex(
            ConnectionError, "read unavailable"
        ):
            runner.dispatch()

        self.assertEqual(
            self.checkpoint(paths), before
        )
        self.assertGreater(authority.reads, reads_before)

    def test_completed_batch_missing_witness_fails_closed(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("completed_rollback")
        )

        self.assertEqual(runner.dispatch(), 1)

        before = self.checkpoint(paths)

        # Simulated remote rollback or inconsistent read.
        authority.current = authority.initial

        with self.assertRaisesRegex(
            ValueError, "Delivered outbox ACK missing witness"
        ):
            runner.dispatch()

        self.assertEqual(
            self.checkpoint(paths), before
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "Durable ACK missing trusted authority witness",
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
                witness_authority=authority,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_completed_batch_missing_inbox_fails_closed(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("missing_inbox")
        )

        self.assertEqual(runner.dispatch(), 1)

        outbox_before = paths[0].read_bytes()
        paths[1].unlink()

        with self.assertRaises(
            FileNotFoundError
        ):
            runner.dispatch()

        self.assertEqual(
            paths[0].read_bytes(), outbox_before
        )

    def test_legacy_ack_rejected_with_current_authority(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("legacy_recovery")
        )

        self.assertEqual(
            sender.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=paths[0],
            ),
            1,
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "Durable ACK missing trusted authority witness",
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
                witness_authority=authority,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_caller_supplied_a27_witness_stays_compatible(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("a27_compatibility")
        )

        self.assertEqual(
            sender.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=paths[0],
            ),
            1,
        )

        target, report, _ = self.recover(
            sender,
            paths,
            trusted_witness=authority.current.witness,
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.inbox_count, 1)
        self.assertEqual(
            target.pending_symbolic_replay_events, ()
        )

    def test_pending_receipt_without_witness_is_recoverable(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("pending_receipt")
        )

        self.assertTrue(receiver.accept(events[0]))

        target, report, restored_receiver = self.recover(
            sender,
            paths,
            witness_authority=authority,
        )

        self.assertEqual(
            report.status, "RECOVERABLE_PENDING_ACK"
        )
        self.assertEqual(
            report.pending_ack_ids, (events[0].id,)
        )

        resumed = SymbolicReplayWitnessDelivery(
            target,
            outbox_path=paths[0],
            receiver=restored_receiver,
            witness_authority=authority,
        )

        self.assertEqual(resumed.dispatch(), 1)
        self.assertEqual(authority.current.revision, 1)

    def test_unwitnessed_previous_ack_blocks_next_delivery(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("partial_legacy", count=2)
        )

        first, second = events

        def first_only(event):
            if event.id == first.id:
                return receiver.accept(event)
            return False

        with self.assertRaisesRegex(
            RuntimeError, "not acknowledged"
        ):
            sender.retry_symbolic_replay_events(
                sink=first_only,
                durable_outbox_path=paths[0],
            )

        records = SymbolicReplayOutboxStore.read(
            sender, paths[0]
        )

        self.assertTrue(records[0].delivered)
        self.assertFalse(records[1].delivered)

        before = self.checkpoint(paths)

        with self.assertRaisesRegex(
            ValueError, "Delivered outbox ACK missing witness"
        ):
            runner.dispatch()

        self.assertEqual(
            self.checkpoint(paths), before
        )
        self.assertEqual(
            tuple(item.id for item in receiver.receipts),
            (first.id,),
        )

    def test_durable_preflight_blocks_sink_without_breaking_legacy(self):
        sender, events, receiver, paths, authority, runner = (
            self.create("preflight_hook")
        )

        calls = []

        def reject():
            calls.append("preflight")
            raise RuntimeError("Preflight blocked.")

        def sink(event):
            calls.append("sink")
            return receiver.accept(event)

        before = self.checkpoint(paths)

        with self.assertRaisesRegex(
            RuntimeError, "Preflight blocked"
        ):
            SymbolicReplayOutboxStore.dispatch(
                sender,
                paths[0],
                sink=sink,
                preflight=reject,
            )

        self.assertEqual(calls, ["preflight"])
        self.assertEqual(
            self.checkpoint(paths), before
        )

        # Legacy API continues to work without hook.
        self.assertEqual(
            SymbolicReplayOutboxStore.dispatch(
                sender,
                paths[0],
                sink=sink,
            ),
            1,
        )

        self.assertEqual(
            calls, ["preflight", "sink"]
        )
        self.assertTrue(
            sender.symbolic_replay_outbox[0].delivered
        )


if __name__ == "__main__":
    unittest.main()
