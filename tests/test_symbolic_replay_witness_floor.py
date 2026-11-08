"""A32 trusted witness floor regression tests.

The authority is a simulation. The floor must come
from an independently trusted, non-rolled-back source.
No cryptographic authentication is implemented here.
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
    """Controllable test double, not trusted storage."""

    def __init__(self, witness):
        self.current = SymbolicReplayWitnessRevision(
            revision=0,
            witness=witness,
        )

        self.override = None
        self.fake_publication = False
        self.fake_response = None
        self.reads = 0
        self.publications = 0

    def read_current(
        self, *, universe_id, batch_sha256,
    ):
        self.reads += 1

        if self.override is not None:
            return self.override

        if self.fake_response is not None:
            return self.fake_response

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

        if self.fake_publication:
            self.fake_response = proposed
            return proposed

        self.current = proposed
        return self.current


class WitnessFloorTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory(
            prefix="a32_witness_floor_"
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

        identity = "a32_" + label
        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"{identity}_event_{index}",
                word_id=f"{identity}_word_{index}",
                sequence=index,
                message=f"A32 event {index}.",
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

        initial = SymbolicReplayReceiptWitness(
            universe_id=str(sender.id),
            batch_sha256=(
                SymbolicReplayOutboxStore.lineage_digest(
                    sender.id,
                    events,
                )
            ),
            receipt_ids=(),
        )

        authority = MemoryAuthority(initial)

        return sender, events, receiver, paths, authority

    @staticmethod
    def evidence(sender, events, ids):
        return SymbolicReplayReceiptWitness(
            universe_id=str(sender.id),
            batch_sha256=(
                SymbolicReplayOutboxStore.lineage_digest(
                    sender.id,
                    events,
                )
            ),
            receipt_ids=tuple(ids),
        )

    @staticmethod
    def snapshot(paths):
        return tuple(
            path.read_bytes()
            for path in paths
        )

    @staticmethod
    def rollback(paths, contents):
        for path, data in zip(paths, contents):
            path.write_bytes(data)

    def delivery(
        self, sender, receiver, paths, authority,
        *, trusted_floor=None,
    ):
        return SymbolicReplayWitnessDelivery(
            sender,
            outbox_path=paths[0],
            receiver=receiver,
            witness_authority=authority,
            trusted_floor=trusted_floor,
        )

    def recover(
        self, sender, paths, *, authority=None,
        trusted_floor=None, trusted_witness=None,
    ):
        target = self.universe(sender.id)

        report, receiver = SymbolicReplayBootstrap.recover(
            target,
            outbox_path=paths[0],
            inbox_path=paths[1],
            manifest_path=paths[2],
            witness_authority=authority,
            trusted_floor=trusted_floor,
            trusted_witness=trusted_witness,
        )

        return target, report, receiver

    def test_matching_floor_allows_delivery_and_recovery(self):
        sender, events, receiver, paths, authority = (
            self.create("matching")
        )

        initial_floor = authority.current

        self.assertEqual(
            self.delivery(
                sender, receiver, paths, authority,
                trusted_floor=initial_floor,
            ).dispatch(),
            1,
        )

        self.assertEqual(authority.current.revision, 1)

        target, report, restored_receiver = self.recover(
            sender, paths,
            authority=authority,
            trusted_floor=authority.current,
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.inbox_count, 1)
        self.assertEqual(
            target.pending_symbolic_replay_events, ()
        )
        self.assertEqual(
            len(restored_receiver.receipts), 1
        )

    def test_stale_read_rejects_rolled_back_recovery(self):
        sender, events, receiver, paths, authority = (
            self.create("rollback")
        )

        original = self.snapshot(paths)
        old_revision = authority.current

        self.assertEqual(
            self.delivery(
                sender, receiver, paths, authority,
            ).dispatch(),
            1,
        )

        latest_floor = authority.current
        self.assertEqual(latest_floor.revision, 1)

        self.rollback(paths, original)

        authority.override = old_revision

        # A stale authority without an independently
        # supplied floor accepts the older checkpoint.
        old_target, old_report, _ = self.recover(
            sender, paths, authority=authority,
        )

        self.assertEqual(old_report.inbox_count, 0)
        self.assertEqual(
            old_report.pending_delivery_ids,
            (events[0].id,),
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "Witness authority below trusted floor",
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
                witness_authority=authority,
                trusted_floor=latest_floor,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )
        self.assertEqual(
            self.snapshot(paths), original
        )

    def test_floor_blocks_stale_delivery_before_write(self):
        sender, events, receiver, paths, authority = (
            self.create("stale_delivery")
        )

        trusted_floor = SymbolicReplayWitnessRevision(
            revision=1,
            witness=self.evidence(
                sender, events, (events[0].id,)
            ),
        )

        before = self.snapshot(paths)

        runner = self.delivery(
            sender, receiver, paths, authority,
            trusted_floor=trusted_floor,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Witness authority below trusted floor",
        ):
            runner.dispatch()

        self.assertEqual(
            self.snapshot(paths), before
        )
        self.assertEqual(receiver.receipts, ())
        self.assertEqual(authority.publications, 0)

    def test_same_revision_missing_ids_rejected(self):
        sender, events, receiver, paths, authority = (
            self.create("lost_ids")
        )

        floor = SymbolicReplayWitnessRevision(
            revision=1,
            witness=self.evidence(
                sender, events, (events[0].id,)
            ),
        )

        authority.current = SymbolicReplayWitnessRevision(
            revision=1,
            witness=self.evidence(sender, events, ()),
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "Witness authority contradicts trusted floor",
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
                witness_authority=authority,
                trusted_floor=floor,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_newer_revision_receipt_superset_allowed(self):
        sender, events, receiver, paths, authority = (
            self.create("newer", count=2)
        )

        for event in events:
            self.assertTrue(receiver.accept(event))

        floor = SymbolicReplayWitnessRevision(
            revision=1,
            witness=self.evidence(
                sender, events, (events[0].id,)
            ),
        )

        authority.current = SymbolicReplayWitnessRevision(
            revision=2,
            witness=self.evidence(
                sender, events,
                tuple(event.id for event in events),
            ),
        )

        target, report, _ = self.recover(
            sender, paths,
            authority=authority,
            trusted_floor=floor,
        )

        self.assertEqual(
            report.pending_ack_ids,
            tuple(event.id for event in events),
        )
        self.assertEqual(report.inbox_count, 2)
        self.assertEqual(
            len(target.pending_symbolic_replay_events), 2
        )

    def test_foreign_universe_floor_rejected(self):
        sender, events, receiver, paths, authority = (
            self.create("foreign_owner")
        )

        floor = SymbolicReplayWitnessRevision(
            revision=0,
            witness=SymbolicReplayReceiptWitness(
                universe_id="foreign_universe",
                batch_sha256=(
                    authority.current.witness.batch_sha256
                ),
                receipt_ids=(),
            ),
        )

        with self.assertRaisesRegex(
            ValueError, "Trusted witness floor scope mismatch"
        ):
            self.recover(
                sender, paths,
                authority=authority,
                trusted_floor=floor,
            )

    def test_foreign_batch_floor_rejected(self):
        sender, events, receiver, paths, authority = (
            self.create("foreign_batch")
        )

        floor = SymbolicReplayWitnessRevision(
            revision=0,
            witness=SymbolicReplayReceiptWitness(
                universe_id=str(sender.id),
                batch_sha256="f" * 64,
                receipt_ids=(),
            ),
        )

        with self.assertRaisesRegex(
            ValueError, "Trusted witness floor scope mismatch"
        ):
            self.recover(
                sender, paths,
                authority=authority,
                trusted_floor=floor,
            )

    def test_invalid_floor_type_rejected_in_recovery(self):
        sender, events, receiver, paths, authority = (
            self.create("invalid_recovery_floor")
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            TypeError, "Trusted witness floor must be canonical"
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
                witness_authority=authority,
                trusted_floor={"revision": 0},
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_floor_without_authority_rejected(self):
        sender, events, receiver, paths, authority = (
            self.create("missing_authority")
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness floor requires authority"
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
                trusted_floor=authority.current,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_invalid_floor_type_rejected_in_delivery(self):
        sender, events, receiver, paths, authority = (
            self.create("invalid_delivery_floor")
        )

        before = self.snapshot(paths)

        with self.assertRaisesRegex(
            TypeError, "Trusted witness floor must be canonical"
        ):
            self.delivery(
                sender, receiver, paths, authority,
                trusted_floor=object(),
            )

        self.assertEqual(
            self.snapshot(paths), before
        )

    def test_completed_batch_rejects_stale_authority(self):
        sender, events, receiver, paths, authority = (
            self.create("completed_stale")
        )

        old_revision = authority.current

        self.assertEqual(
            self.delivery(
                sender, receiver, paths, authority,
            ).dispatch(),
            1,
        )

        floor = authority.current

        protected = self.delivery(
            sender, receiver, paths, authority,
            trusted_floor=floor,
        )

        authority.override = old_revision

        before = self.snapshot(paths)

        with self.assertRaisesRegex(
            ValueError,
            "Witness authority below trusted floor",
        ):
            protected.dispatch()

        self.assertEqual(
            self.snapshot(paths), before
        )

    def test_legacy_witness_without_floor_remains_supported(self):
        sender, events, receiver, paths, authority = (
            self.create("legacy")
        )

        self.assertEqual(
            sender.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=paths[0],
            ),
            1,
        )

        target, report, _ = self.recover(
            sender, paths,
            trusted_witness=authority.current.witness,
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(
            target.pending_symbolic_replay_events, ()
        )

    def test_consistent_forgery_remains_trust_boundary(self):
        """A floor cannot authenticate dishonest remote data."""
        sender, events, receiver, paths, authority = (
            self.create("coherent_forgery")
        )

        floor = authority.current
        authority.fake_publication = True

        runner = self.delivery(
            sender, receiver, paths, authority,
            trusted_floor=floor,
        )

        # The mock lies on publish and readback.
        self.assertEqual(runner.dispatch(), 1)

        self.assertEqual(authority.current.revision, 0)
        self.assertEqual(
            authority.current.witness.receipt_ids, ()
        )

        self.assertTrue(
            SymbolicReplayOutboxStore.read(
                sender, paths[0],
            )[0].delivered
        )

        # Once the authority stops lying, strict
        # recovery notices the unwitnessed ACK.
        authority.fake_response = None

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
                trusted_floor=floor,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )


if __name__ == "__main__":
    unittest.main()
