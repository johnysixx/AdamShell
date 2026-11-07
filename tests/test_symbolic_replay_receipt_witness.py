import io
import tempfile
import unittest

from contextlib import redirect_stdout
from dataclasses import FrozenInstanceError
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
from universe.symbolic_replay_recovery_auditor import (
    SymbolicReplayRecoveryAuditor,
)


class SymbolicReplayReceiptWitnessTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a27_receipt_witness_"
        )
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create(
        self, label, *, identity=None, specs=None,
    ):
        folder = self.directory / label
        folder.mkdir()

        if identity is None:
            identity = "a27_" + label

        if specs is None:
            specs = (
                (
                    f"{label}_event",
                    f"{label}_word",
                    f"A27 message from {label}.",
                ),
            )

        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=event_id,
                word_id=word_id,
                sequence=index,
                message=message,
            )
            for index, (event_id, word_id, message)
            in enumerate(specs)
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

        self.assertEqual(
            report.outbox_count, len(events)
        )

        return sender, events, receiver, paths

    @staticmethod
    def witness(sender, events, ids):
        return SymbolicReplayReceiptWitness(
            universe_id=str(sender.id),
            batch_sha256=(
                SymbolicReplayOutboxStore.lineage_digest(
                    sender.id, events,
                )
            ),
            receipt_ids=tuple(ids),
        )

    @staticmethod
    def deliver(sender, receiver, paths):
        return sender.retry_symbolic_replay_events(
            sink=receiver.accept,
            durable_outbox_path=paths[0],
        )

    @staticmethod
    def recover(target, paths, **kwargs):
        return SymbolicReplayBootstrap.recover(
            target,
            outbox_path=paths[0],
            inbox_path=paths[1],
            manifest_path=paths[2],
            **kwargs,
        )

    def rolled_back_two_events(self, label):
        sender, events, receiver, paths = self.create(
            label,
            specs=(
                ("shared_first", "first_word", "First"),
                ("shared_second", "second_word", "Second"),
            ),
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

        intermediate = tuple(
            path.read_bytes() for path in paths
        )

        self.assertEqual(
            self.deliver(sender, receiver, paths),
            1,
        )

        for path, data in zip(paths, intermediate):
            path.write_bytes(data)

        return sender, events, paths

    def test_witness_is_immutable(self):
        witness = SymbolicReplayReceiptWitness(
            universe_id="a27_immutable",
            batch_sha256="a" * 64,
            receipt_ids=("event_1",),
        )

        self.assertEqual(
            witness.receipt_ids, ("event_1",)
        )

        with self.assertRaises(FrozenInstanceError):
            witness.universe_id = "changed"

        with self.assertRaises(FrozenInstanceError):
            witness.receipt_ids = ()

    def test_witness_constructor_rejects_invalid_data(self):
        digest = "a" * 64

        cases = (
            (("", digest, ()), ValueError),
            ((123, digest, ()), ValueError),
            (("owner", "a" * 63, ()), ValueError),
            (("owner", "G" * 64, ()), ValueError),
            (("owner", digest, ["event"]), TypeError),
            (("owner", digest, ("",)), ValueError),
            (("owner", digest, (123,)), ValueError),
            (
                ("owner", digest, ("event", "event")),
                ValueError,
            ),
        )

        for arguments, expected_error in cases:
            with self.assertRaises(expected_error):
                SymbolicReplayReceiptWitness(
                    *arguments
                )

    def test_matching_witness_recovers_after_ack(self):
        sender, events, receiver, paths = self.create(
            "matching"
        )

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        witness = self.witness(
            sender, events, (events[0].id,)
        )

        target = self.universe(sender.id)

        report, restored_receiver = self.recover(
            target, paths,
            trusted_witness=witness,
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.inbox_count, 1)
        self.assertEqual(
            len(restored_receiver.receipts), 1
        )
        self.assertEqual(
            target.pending_symbolic_replay_events, ()
        )

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=lambda _: self.fail(
                    "Duplicate delivery"
                ),
                durable_outbox_path=paths[0],
            ),
            0,
        )

    def test_foreign_universe_witness_is_rejected(self):
        specs = (
            ("shared_event", "shared_word", "Shared"),
        )

        owner, events, owner_receiver, owner_paths = (
            self.create(
                "owner", identity="a27_owner",
                specs=specs,
            )
        )

        other, other_events, other_receiver, paths = (
            self.create(
                "foreign_owner",
                identity="a27_foreign_owner",
                specs=specs,
            )
        )

        self.assertEqual(
            self.deliver(owner, owner_receiver, owner_paths),
            1,
        )
        self.assertEqual(
            self.deliver(other, other_receiver, paths),
            1,
        )

        self.assertEqual(events[0].id, other_events[0].id)

        witness = self.witness(
            owner, events, (events[0].id,)
        )

        target = self.universe(other.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness universe mismatch"
        ):
            self.recover(
                target, paths, trusted_witness=witness
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_foreign_batch_witness_is_rejected(self):
        identity = "a27_shared_owner"

        first, events, first_receiver, first_paths = (
            self.create(
                "first_batch",
                identity=identity,
                specs=(
                    ("shared_event", "word_a", "Message A"),
                ),
            )
        )

        second, second_events, second_receiver, paths = (
            self.create(
                "second_batch",
                identity=identity,
                specs=(
                    ("shared_event", "word_b", "Message B"),
                ),
            )
        )

        self.assertEqual(
            self.deliver(first, first_receiver, first_paths),
            1,
        )
        self.assertEqual(
            self.deliver(second, second_receiver, paths),
            1,
        )

        self.assertEqual(
            events[0].id, second_events[0].id
        )

        witness = self.witness(
            first, events, (events[0].id,)
        )

        target = self.universe(identity)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness batch lineage mismatch"
        ):
            self.recover(
                target, paths, trusted_witness=witness
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_unconfirmed_receipt_is_rejected(self):
        sender, events, receiver, paths = self.create(
            "unconfirmed"
        )

        witness = self.witness(
            sender, events, (events[0].id,)
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness missing confirmed receipt"
        ):
            self.recover(
                target, paths, trusted_witness=witness
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_empty_witness_does_not_claim_ack(self):
        sender, events, receiver, paths = self.create(
            "empty_witness"
        )

        witness = self.witness(sender, events, ())

        target = self.universe(sender.id)

        report, _ = self.recover(
            target, paths, trusted_witness=witness
        )

        self.assertEqual(report.inbox_count, 0)
        self.assertEqual(
            report.pending_delivery_ids,
            (events[0].id,),
        )

    def test_current_witness_rejects_full_rollback(self):
        sender, events, receiver, paths = self.create(
            "full_rollback_guarded"
        )

        old_snapshot = tuple(
            path.read_bytes() for path in paths
        )

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        witness = self.witness(
            sender, events, (events[0].id,)
        )

        for path, data in zip(paths, old_snapshot):
            path.write_bytes(data)

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness missing confirmed receipt"
        ):
            self.recover(
                target, paths, trusted_witness=witness
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )
        self.assertEqual(
            tuple(path.read_bytes() for path in paths),
            old_snapshot,
        )

    def test_recovery_without_witness_keeps_known_limit(self):
        sender, events, receiver, paths = self.create(
            "full_rollback_unguarded"
        )

        old_snapshot = tuple(
            path.read_bytes() for path in paths
        )

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        for path, data in zip(paths, old_snapshot):
            path.write_bytes(data)

        target = self.universe(sender.id)

        report, _ = self.recover(target, paths)

        self.assertEqual(report.status, "CONSISTENT")
        self.assertEqual(report.inbox_count, 0)
        self.assertEqual(
            report.pending_delivery_ids,
            (events[0].id,),
        )

    def test_stale_witness_accepts_old_valid_state(self):
        sender, events, paths = (
            self.rolled_back_two_events("stale")
        )

        first, second = events

        stale_witness = self.witness(
            sender, events, (first.id,)
        )

        target = self.universe(sender.id)

        report, _ = self.recover(
            target, paths,
            trusted_witness=stale_witness,
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.inbox_count, 1)
        self.assertEqual(
            report.pending_delivery_ids,
            (second.id,),
        )

    def test_current_witness_rejects_old_valid_state(self):
        sender, events, paths = (
            self.rolled_back_two_events("fresh")
        )

        fresh_witness = self.witness(
            sender, events,
            tuple(event.id for event in events),
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness missing confirmed receipt"
        ):
            self.recover(
                target, paths,
                trusted_witness=fresh_witness,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_direct_auditor_enforces_batch_scope(self):
        identity = "a27_direct_auditor"

        donor, donor_events, _, _ = self.create(
            "auditor_donor",
            identity=identity,
            specs=(
                ("shared_event", "donor_word", "Donor"),
            ),
        )

        target_sender, target_events, _, paths = (
            self.create(
                "auditor_target",
                identity=identity,
                specs=(
                    ("shared_event", "target_word", "Target"),
                ),
            )
        )

        witness = self.witness(
            donor, donor_events, ()
        )

        target = self.universe(identity)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness batch lineage mismatch"
        ):
            SymbolicReplayRecoveryAuditor.restore(
                target,
                outbox_path=paths[0],
                inbox_path=paths[1],
                trusted_witness=witness,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_legacy_and_scoped_checks_both_apply(self):
        sender, events, receiver, paths = self.create(
            "combined"
        )

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        witness = self.witness(
            sender, events, (events[0].id,)
        )

        accepted = self.universe(sender.id)

        report, _ = self.recover(
            accepted, paths,
            trusted_witness=witness,
            required_receipt_ids=(events[0].id,),
        )

        self.assertEqual(report.delivered_count, 1)

        rejected = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted receipt witness mismatch"
        ):
            self.recover(
                rejected, paths,
                trusted_witness=witness,
                required_receipt_ids=("unknown_event",),
            )

        self.assertEqual(
            rejected.symbolic_replay_outbox, []
        )

    def test_noncanonical_witness_type_is_rejected(self):
        sender, events, receiver, paths = self.create(
            "wrong_type"
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            TypeError, "Trusted witness must be a canonical"
        ):
            self.recover(
                target, paths,
                trusted_witness={
                    "universe_id": str(sender.id),
                    "receipt_ids": (),
                },
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )


if __name__ == "__main__":
    unittest.main()
