"""A30 regression tests for witnessed delivery recovery.

Failures are simulated with exceptions and checkpoint
rollback. Actual OS process termination and power loss
are outside this suite.

The authority below is test-only, not independent storage.
"""

import io
import tempfile
import threading
import unittest

from contextlib import redirect_stdout
from pathlib import Path

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
    """Thread-safe simulation of a monotonic authority."""

    def __init__(self, witness):
        self._lock = threading.Lock()
        self.current = SymbolicReplayWitnessRevision(
            revision=0,
            witness=witness,
        )
        self.publications = 0
        self.fail_publication = False
        self.fail_publication_at = None
        self.ambiguous_once = False
        self.fail_read = False

    def read_current(
        self, *, universe_id, batch_sha256,
    ):
        with self._lock:
            if self.fail_read:
                raise ConnectionError(
                    "Authority read unavailable."
                )

            if (
                self.current.witness.universe_id
                != universe_id
                or self.current.witness.batch_sha256
                != batch_sha256
            ):
                raise ValueError(
                    "Authority scope mismatch."
                )

            return self.current

    def publish(
        self, witness, *, expected_revision,
    ):
        with self._lock:
            self.publications += 1

            if (
                self.fail_publication
                or self.fail_publication_at
                == self.publications
            ):
                raise ConnectionError(
                    "Authority publication failed."
                )

            self.current = self.transition(
                self.current,
                witness,
                expected_revision=expected_revision,
            )

            if self.ambiguous_once:
                self.ambiguous_once = False
                raise TimeoutError(
                    "Authority response lost."
                )

            return self.current


class WitnessCrashConcurrencyTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory(
            prefix="a30_witness_regression_"
        )
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create(self, label, *, count=1):
        folder = self.directory / label
        folder.mkdir()

        identity = "a30_" + label
        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"{identity}_event_{index}",
                word_id=f"{identity}_word_{index}",
                sequence=index,
                message=f"A30 event {index}.",
            )
            for index in range(count)
        )

        sender.symbolic_replay_outbox.extend(events)

        paths = (
            folder / "outbox.json",
            folder / "inbox.json",
            folder / "bootstrap.json",
        )

        report, receiver = SymbolicReplayBootstrap.initialize(
            sender,
            outbox_path=paths[0],
            inbox_path=paths[1],
            manifest_path=paths[2],
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

        return sender, events, receiver, paths, authority

    @staticmethod
    def delivery(target, receiver, paths, authority):
        return SymbolicReplayWitnessDelivery(
            target,
            outbox_path=paths[0],
            receiver=receiver,
            witness_authority=authority,
        )

    def recover(self, sender, paths, authority):
        target = self.universe(sender.id)

        report, receiver = SymbolicReplayBootstrap.recover(
            target,
            outbox_path=paths[0],
            inbox_path=paths[1],
            manifest_path=paths[2],
            witness_authority=authority,
        )

        return target, report, receiver

    @staticmethod
    def snapshot(paths):
        return tuple(path.read_bytes() for path in paths)

    @staticmethod
    def rollback(paths, old):
        for path, data in zip(paths, old):
            path.write_bytes(data)

    def test_publication_failure_recovers_without_inbox_rewrite(self):
        sender, events, receiver, paths, authority = (
            self.create("publication_failure")
        )

        runner = self.delivery(
            sender, receiver, paths, authority
        )

        pending_outbox = paths[0].read_bytes()
        authority.fail_publication = True

        with self.assertRaisesRegex(
            ConnectionError, "publication failed"
        ):
            runner.dispatch()

        self.assertEqual(len(receiver.receipts), 1)
        self.assertEqual(
            paths[0].read_bytes(), pending_outbox
        )
        self.assertEqual(authority.current.revision, 0)

        inbox_before = paths[1].read_bytes()

        authority.fail_publication = False

        target, report, restored_receiver = self.recover(
            sender, paths, authority
        )

        self.assertEqual(
            report.status,
            "RECOVERABLE_PENDING_ACK",
        )
        self.assertEqual(
            report.pending_ack_ids,
            (events[0].id,),
        )

        resumed = self.delivery(
            target, restored_receiver, paths, authority
        )

        self.assertEqual(resumed.dispatch(), 1)
        self.assertEqual(
            paths[1].read_bytes(), inbox_before
        )
        self.assertEqual(authority.current.revision, 1)
        self.assertEqual(
            target.pending_symbolic_replay_events, ()
        )

    def test_ambiguous_authority_response_cold_recovery(self):
        sender, events, receiver, paths, authority = (
            self.create("ambiguous")
        )

        runner = self.delivery(
            sender, receiver, paths, authority
        )

        authority.ambiguous_once = True

        with self.assertRaisesRegex(
            TimeoutError, "response lost"
        ):
            runner.dispatch()

        self.assertEqual(authority.current.revision, 1)

        self.assertFalse(
            SymbolicReplayOutboxStore.read(
                sender, paths[0],
            )[0].delivered
        )

        publication_count = authority.publications
        inbox_before = paths[1].read_bytes()

        target, report, restored_receiver = self.recover(
            sender, paths, authority
        )

        self.assertEqual(
            report.status,
            "RECOVERABLE_PENDING_ACK",
        )

        resumed = self.delivery(
            target, restored_receiver, paths, authority
        )

        self.assertEqual(resumed.dispatch(), 1)
        self.assertEqual(
            authority.publications, publication_count
        )
        self.assertEqual(
            paths[1].read_bytes(), inbox_before
        )
        self.assertEqual(authority.current.revision, 1)

    def test_concurrent_recovered_senders_are_serialized(self):
        sender, events, receiver, paths, authority = (
            self.create("concurrent")
        )

        first, _, first_receiver = self.recover(
            sender, paths, authority
        )
        second, _, second_receiver = self.recover(
            sender, paths, authority
        )

        runners = (
            self.delivery(
                first, first_receiver, paths, authority
            ),
            self.delivery(
                second, second_receiver, paths, authority
            ),
        )

        barrier = threading.Barrier(3)
        results = []
        guard = threading.Lock()

        def worker(runner):
            try:
                barrier.wait(timeout=10)
                result = ("success", runner.dispatch())
            except Exception as error:
                result = (
                    type(error).__name__,
                    str(error),
                )

            with guard:
                results.append(result)

        threads = [
            threading.Thread(target=worker, args=(runner,))
            for runner in runners
        ]

        for thread in threads:
            thread.start()

        barrier.wait(timeout=10)

        for thread in threads:
            thread.join(timeout=15)

        self.assertTrue(
            all(not thread.is_alive() for thread in threads)
        )

        successes = [
            value
            for value in results
            if value[0] == "success"
        ]

        failures = [
            value
            for value in results
            if value[0] != "success"
        ]

        self.assertEqual(successes, [("success", 1)])
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0][0], "ValueError")
        self.assertIn(
            "In-memory outbox differs", failures[0][1]
        )

        self.assertEqual(authority.current.revision, 1)
        self.assertEqual(authority.publications, 1)

        disk_inbox = DurableSymbolicReplayInbox(
            path=paths[1],
            universe_id=str(sender.id),
        )

        self.assertEqual(len(disk_inbox.receipts), 1)

        final, report, _ = self.recover(
            sender, paths, authority
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.inbox_count, 1)
        self.assertEqual(
            final.pending_symbolic_replay_events, ()
        )

    def test_full_rollback_rejected_before_runtime_publication(self):
        sender, events, receiver, paths, authority = (
            self.create("rollback")
        )

        original = self.snapshot(paths)

        runner = self.delivery(
            sender, receiver, paths, authority
        )

        self.assertEqual(runner.dispatch(), 1)
        self.assertEqual(authority.current.revision, 1)

        self.rollback(paths, original)

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "Trusted witness missing confirmed receipt",
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
        self.assertEqual(
            self.snapshot(paths), original
        )

    def test_legacy_path_remains_unwitnessed(self):
        """Document the opt-in protection boundary."""
        sender, events, receiver, paths, authority = (
            self.create("legacy")
        )

        original = self.snapshot(paths)

        self.assertEqual(
            sender.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=paths[0],
            ),
            1,
        )

        self.assertEqual(authority.current.revision, 0)

        self.rollback(paths, original)

        target, report, restored_receiver = self.recover(
            sender, paths, authority
        )

        self.assertEqual(
            report.pending_delivery_ids,
            (events[0].id,),
        )

        runner = self.delivery(
            target, restored_receiver, paths, authority
        )

        self.assertEqual(runner.dispatch(), 1)
        self.assertEqual(authority.current.revision, 1)

    def test_authority_outage_fails_recovery_closed(self):
        sender, events, receiver, paths, authority = (
            self.create("outage")
        )

        original = self.snapshot(paths)
        authority.fail_read = True

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ConnectionError, "read unavailable"
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
        self.assertEqual(
            self.snapshot(paths), original
        )

        authority.fail_read = False

        recovered, report, restored_receiver = (
            self.recover(sender, paths, authority)
        )

        self.assertEqual(report.inbox_count, 0)

        self.assertEqual(
            self.delivery(
                recovered,
                restored_receiver,
                paths,
                authority,
            ).dispatch(),
            1,
        )

    def test_second_publication_failure_preserves_first_ack(self):
        sender, events, receiver, paths, authority = (
            self.create("partial", count=2)
        )

        runner = self.delivery(
            sender, receiver, paths, authority
        )

        authority.fail_publication_at = 2

        with self.assertRaisesRegex(
            ConnectionError, "publication failed"
        ):
            runner.dispatch()

        stored = SymbolicReplayOutboxStore.read(
            sender, paths[0]
        )

        self.assertTrue(stored[0].delivered)
        self.assertFalse(stored[1].delivered)

        self.assertEqual(
            authority.current.witness.receipt_ids,
            (events[0].id,),
        )
        self.assertEqual(len(receiver.receipts), 2)

        inbox_before = paths[1].read_bytes()

        target, report, restored_receiver = self.recover(
            sender, paths, authority
        )

        self.assertEqual(
            report.status, "RECOVERABLE_PENDING_ACK"
        )
        self.assertEqual(
            report.pending_ack_ids, (events[1].id,)
        )

        authority.fail_publication_at = None

        resumed = self.delivery(
            target, restored_receiver, paths, authority
        )

        self.assertEqual(resumed.dispatch(), 1)
        self.assertEqual(
            paths[1].read_bytes(), inbox_before
        )
        self.assertEqual(authority.current.revision, 2)
        self.assertEqual(
            authority.current.witness.receipt_ids,
            tuple(event.id for event in events),
        )

    def test_stale_sender_rejected_after_competing_commit(self):
        sender, events, receiver, paths, authority = (
            self.create("stale_sender")
        )

        first, _, first_receiver = self.recover(
            sender, paths, authority
        )
        stale, _, stale_receiver = self.recover(
            sender, paths, authority
        )

        winner = self.delivery(
            first, first_receiver, paths, authority
        )
        loser = self.delivery(
            stale, stale_receiver, paths, authority
        )

        self.assertEqual(winner.dispatch(), 1)

        inbox_before = paths[1].read_bytes()
        revisions_before = authority.current.revision

        with self.assertRaisesRegex(
            ValueError, "In-memory outbox differs"
        ):
            loser.dispatch()

        self.assertEqual(
            paths[1].read_bytes(), inbox_before
        )
        self.assertEqual(
            authority.current.revision, revisions_before
        )

    def test_authority_read_failure_prevents_new_receipt(self):
        sender, events, receiver, paths, authority = (
            self.create("preflight")
        )

        runner = self.delivery(
            sender, receiver, paths, authority
        )

        before = self.snapshot(paths)
        authority.fail_read = True

        with self.assertRaisesRegex(
            ConnectionError, "read unavailable"
        ):
            runner.dispatch()

        self.assertEqual(
            self.snapshot(paths), before
        )
        self.assertEqual(receiver.receipts, ())
        self.assertEqual(authority.publications, 0)


if __name__ == "__main__":
    unittest.main()
