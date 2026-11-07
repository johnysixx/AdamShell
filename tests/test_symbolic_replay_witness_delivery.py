import io
import tempfile
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
    """Test-only simulation; not independent or durable."""

    def __init__(self, initial):
        self.current = initial

        self.reads = 0
        self.publications = 0

        self.fail_read = False
        self.fail_publish = False
        self.ambiguous_publish = False
        self.invalid_read = False
        self.invalid_publish = False
        self.unconfirmed_publish = False

        self.fail_publication_number = None

    def read_current(
        self, *, universe_id, batch_sha256,
    ):
        self.reads += 1

        if self.fail_read:
            raise ConnectionError(
                "Authority read unavailable."
            )

        if self.invalid_read:
            return "invalid revision"

        return self.current

    def publish(
        self, witness, *, expected_revision,
    ):
        self.publications += 1

        if self.fail_publish:
            raise ConnectionError(
                "Authority publish unavailable."
            )

        if (
            self.fail_publication_number
            == self.publications
        ):
            raise ConnectionError(
                "Authority publication interrupted."
            )

        if self.invalid_publish:
            return "invalid publication"

        if self.unconfirmed_publish:
            return self.current

        next_revision = self.transition(
            self.current,
            witness,
            expected_revision=expected_revision,
        )

        self.current = next_revision

        if self.ambiguous_publish:
            self.ambiguous_publish = False
            raise TimeoutError(
                "Authority committed but response lost."
            )

        return self.current


class SymbolicReplayWitnessDeliveryTests(
    unittest.TestCase
):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a29_witness_delivery_"
        )
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create(self, label, *, count=1):
        directory = self.directory / label
        directory.mkdir()

        identity = "a29_" + label
        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"{identity}_event_{index}",
                word_id=f"{identity}_word_{index}",
                sequence=index,
                message=f"A29 event {index}.",
            )
            for index in range(count)
        )

        sender.symbolic_replay_outbox.extend(events)

        paths = (
            directory / "outbox.json",
            directory / "inbox.json",
            directory / "bootstrap.json",
        )

        report, receiver = (
            SymbolicReplayBootstrap.initialize(
                sender,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
            )
        )

        self.assertEqual(
            report.outbox_count, count
        )

        initial_witness = SymbolicReplayReceiptWitness(
            universe_id=str(sender.id),
            batch_sha256=(
                SymbolicReplayOutboxStore.lineage_digest(
                    sender.id,
                    events,
                )
            ),
            receipt_ids=(),
        )

        authority = MemoryAuthority(
            SymbolicReplayWitnessRevision(
                revision=0,
                witness=initial_witness,
            )
        )

        delivery = SymbolicReplayWitnessDelivery(
            sender,
            outbox_path=paths[0],
            receiver=receiver,
            witness_authority=authority,
        )

        return (
            sender,
            events,
            receiver,
            paths,
            authority,
            delivery,
        )

    @staticmethod
    def checkpoint(paths):
        return tuple(
            path.read_bytes()
            for path in paths
        )

    def test_success_publishes_before_outbox_ack(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("success")
        )

        self.assertEqual(
            delivery.dispatch(), 1
        )

        self.assertEqual(
            authority.current.revision, 1
        )
        self.assertEqual(
            authority.current.witness.receipt_ids,
            (events[0].id,),
        )

        self.assertEqual(
            len(receiver.receipts), 1
        )

        persisted = SymbolicReplayOutboxStore.read(
            sender, paths[0],
        )

        self.assertTrue(persisted[0].delivered)
        self.assertTrue(
            sender.symbolic_replay_outbox[0].delivered
        )

        # A second dispatch must not invoke the sink.
        self.assertEqual(
            delivery.dispatch(), 0
        )

        self.assertEqual(
            authority.publications, 1
        )

        target = self.universe(sender.id)

        report, _ = SymbolicReplayBootstrap.recover(
            target,
            outbox_path=paths[0],
            inbox_path=paths[1],
            manifest_path=paths[2],
            witness_authority=authority,
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.inbox_count, 1)

    def test_authority_read_failure_prevents_receipt(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("read_failure")
        )

        before = self.checkpoint(paths)
        authority.fail_read = True

        with self.assertRaisesRegex(
            ConnectionError,
            "Authority read unavailable",
        ):
            delivery.dispatch()

        self.assertEqual(
            self.checkpoint(paths), before
        )
        self.assertEqual(receiver.receipts, ())
        self.assertFalse(
            sender.symbolic_replay_outbox[0].delivered
        )

    def test_publish_failure_leaves_pending_and_retries(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("publish_failure")
        )

        pending_outbox = paths[0].read_bytes()

        authority.fail_publish = True

        with self.assertRaisesRegex(
            ConnectionError,
            "Authority publish unavailable",
        ):
            delivery.dispatch()

        self.assertEqual(len(receiver.receipts), 1)
        self.assertEqual(
            paths[0].read_bytes(), pending_outbox
        )
        self.assertEqual(authority.current.revision, 0)

        receipt_before = paths[1].read_bytes()

        authority.fail_publish = False

        self.assertEqual(
            delivery.dispatch(), 1
        )

        self.assertEqual(
            paths[1].read_bytes(), receipt_before
        )
        self.assertEqual(authority.current.revision, 1)

        self.assertTrue(
            sender.symbolic_replay_outbox[0].delivered
        )

    def test_ambiguous_publication_is_retryable(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("ambiguous")
        )

        authority.ambiguous_publish = True

        with self.assertRaisesRegex(
            TimeoutError,
            "response lost",
        ):
            delivery.dispatch()

        self.assertEqual(authority.current.revision, 1)
        self.assertEqual(len(receiver.receipts), 1)
        self.assertFalse(
            sender.symbolic_replay_outbox[0].delivered
        )

        before = paths[1].read_bytes()

        self.assertEqual(
            delivery.dispatch(), 1
        )

        self.assertEqual(
            paths[1].read_bytes(), before
        )
        self.assertEqual(
            authority.publications, 1
        )

        self.assertTrue(
            sender.symbolic_replay_outbox[0].delivered
        )

    def test_authority_ahead_of_inbox_fails_closed(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("ahead")
        )

        current = authority.current

        confirmed = SymbolicReplayReceiptWitness(
            universe_id=str(sender.id),
            batch_sha256=delivery.batch_sha256,
            receipt_ids=(events[0].id,),
        )

        authority.publish(
            confirmed,
            expected_revision=current.revision,
        )

        before = self.checkpoint(paths)

        with self.assertRaisesRegex(
            ValueError,
            "Witness authority ahead of local inbox",
        ):
            delivery.dispatch()

        self.assertEqual(
            self.checkpoint(paths), before
        )
        self.assertEqual(receiver.receipts, ())
        self.assertFalse(
            sender.symbolic_replay_outbox[0].delivered
        )

    def test_foreign_authority_scope_fails_closed(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("foreign_scope")
        )

        authority.current = SymbolicReplayWitnessRevision(
            revision=0,
            witness=SymbolicReplayReceiptWitness(
                universe_id="different_universe",
                batch_sha256=delivery.batch_sha256,
                receipt_ids=(),
            ),
        )

        before = self.checkpoint(paths)

        with self.assertRaisesRegex(
            ValueError,
            "Witness authority universe mismatch",
        ):
            delivery.dispatch()

        self.assertEqual(
            self.checkpoint(paths), before
        )

    def test_noncanonical_authority_read_fails_closed(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("invalid_read")
        )

        authority.invalid_read = True

        before = self.checkpoint(paths)

        with self.assertRaisesRegex(
            TypeError,
            "noncanonical revision",
        ):
            delivery.dispatch()

        self.assertEqual(
            self.checkpoint(paths), before
        )

    def test_noncanonical_publish_does_not_ack(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("invalid_publish")
        )

        authority.invalid_publish = True

        pending_outbox = paths[0].read_bytes()

        with self.assertRaisesRegex(
            TypeError,
            "noncanonical publication",
        ):
            delivery.dispatch()

        self.assertEqual(len(receiver.receipts), 1)
        self.assertEqual(
            paths[0].read_bytes(), pending_outbox
        )
        self.assertFalse(
            sender.symbolic_replay_outbox[0].delivered
        )

    def test_unconfirmed_publication_does_not_ack(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("unconfirmed")
        )

        authority.unconfirmed_publish = True

        pending_outbox = paths[0].read_bytes()

        with self.assertRaisesRegex(
            ValueError,
            "publication not confirmed",
        ):
            delivery.dispatch()

        self.assertEqual(
            paths[0].read_bytes(), pending_outbox
        )
        self.assertEqual(len(receiver.receipts), 1)
        self.assertFalse(
            sender.symbolic_replay_outbox[0].delivered
        )

    def test_stale_durable_outbox_prevents_receipt(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("outbox_drift")
        )

        SymbolicReplayOutboxStore._write(
            paths[0],
            SymbolicReplayOutboxStore._document(
                sender.id,
                (),
            ),
        )

        inbox_before = paths[1].read_bytes()

        with self.assertRaisesRegex(
            ValueError,
            "In-memory outbox differs",
        ):
            delivery.dispatch()

        self.assertEqual(
            paths[1].read_bytes(), inbox_before
        )
        self.assertEqual(receiver.receipts, ())
        self.assertEqual(authority.publications, 0)

    def test_authoritative_witness_rejects_rollback(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("rollback")
        )

        initial = self.checkpoint(paths)

        self.assertEqual(
            delivery.dispatch(), 1
        )

        self.assertEqual(authority.current.revision, 1)

        for path, content in zip(paths, initial):
            path.write_bytes(content)

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
            self.checkpoint(paths), initial
        )

    def test_partial_multi_event_failure_recovers(self):
        sender, events, receiver, paths, authority, delivery = (
            self.create("partial", count=2)
        )

        authority.fail_publication_number = 2

        with self.assertRaisesRegex(
            ConnectionError,
            "Authority publication interrupted",
        ):
            delivery.dispatch()

        persisted = SymbolicReplayOutboxStore.read(
            sender, paths[0],
        )

        self.assertTrue(persisted[0].delivered)
        self.assertFalse(persisted[1].delivered)

        self.assertEqual(
            authority.current.witness.receipt_ids,
            (events[0].id,),
        )

        self.assertEqual(
            len(receiver.receipts), 2
        )

        inbox_before = paths[1].read_bytes()

        authority.fail_publication_number = None

        self.assertEqual(
            delivery.dispatch(), 1
        )

        self.assertEqual(
            paths[1].read_bytes(), inbox_before
        )

        self.assertEqual(
            authority.current.witness.receipt_ids,
            (events[0].id, events[1].id),
        )

        self.assertEqual(authority.current.revision, 2)

        self.assertTrue(
            all(
                item.delivered
                for item in SymbolicReplayOutboxStore.read(
                    sender, paths[0],
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
