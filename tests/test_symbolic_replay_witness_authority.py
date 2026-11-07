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
from universe.symbolic_replay_recovery_auditor import (
    SymbolicReplayRecoveryAuditor,
)
from universe.symbolic_replay_witness_authority import (
    SymbolicReplayWitnessAuthority,
    SymbolicReplayWitnessRevision,
)


class MemoryAuthority(SymbolicReplayWitnessAuthority):
    """Test double only. Not a durable trusted authority."""

    def __init__(self, current):
        self.current = current
        self.unavailable = False
        self.calls = 0

    def read_current(self, *, universe_id, batch_sha256):
        self.calls += 1

        if self.unavailable:
            raise ConnectionError("Authority unavailable.")

        return self.current

    def publish(self, witness, *, expected_revision):
        self.current = self.transition(
            self.current,
            witness,
            expected_revision=expected_revision,
        )
        return self.current


class InvalidAuthority(SymbolicReplayWitnessAuthority):

    def read_current(self, *, universe_id, batch_sha256):
        return "not a canonical revision"

    def publish(self, witness, *, expected_revision):
        raise NotImplementedError


class SymbolicReplayWitnessAuthorityTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a28_authority_"
        )
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create(self, label):
        folder = self.directory / label
        folder.mkdir()

        identity = "a28_" + label
        sender = self.universe(identity)

        event = SymbolicReplayOutboxEvent(
            id=f"{identity}_event",
            word_id=f"{identity}_word",
            sequence=0,
            message=f"A28 event from {label}.",
        )

        sender.symbolic_replay_outbox.append(event)

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

        self.assertEqual(report.outbox_count, 1)

        return sender, event, receiver, paths

    @staticmethod
    def witness(sender, event, ids):
        return SymbolicReplayReceiptWitness(
            universe_id=str(sender.id),
            batch_sha256=(
                SymbolicReplayOutboxStore.lineage_digest(
                    sender.id,
                    (event,),
                )
            ),
            receipt_ids=tuple(ids),
        )

    def authority(self, sender, event, ids):
        return MemoryAuthority(
            SymbolicReplayWitnessRevision(
                revision=0,
                witness=self.witness(sender, event, ids),
            )
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

    def test_revision_rejects_invalid_values(self):
        witness = SymbolicReplayReceiptWitness(
            universe_id="owner",
            batch_sha256="a" * 64,
            receipt_ids=(),
        )

        for value in (-1, True, 1.5, "1"):
            with self.subTest(revision=repr(value)):
                with self.assertRaises(ValueError):
                    SymbolicReplayWitnessRevision(
                        revision=value,
                        witness=witness,
                    )

        with self.assertRaises(TypeError):
            SymbolicReplayWitnessRevision(
                revision=0,
                witness=None,
            )

    def test_monotonic_publication_and_idempotency(self):
        sender, event, receiver, paths = self.create(
            "monotonic"
        )

        empty = self.witness(sender, event, ())
        confirmed = self.witness(
            sender, event, (event.id,)
        )

        authority = MemoryAuthority(
            SymbolicReplayWitnessRevision(0, empty)
        )

        self.assertEqual(
            authority.publish(
                confirmed,
                expected_revision=0,
            ).revision,
            1,
        )

        self.assertEqual(
            authority.publish(
                confirmed,
                expected_revision=1,
            ).revision,
            1,
        )

        self.assertEqual(
            authority.read_current(
                universe_id=str(sender.id),
                batch_sha256=confirmed.batch_sha256,
            ).witness,
            confirmed,
        )

    def test_stale_revision_and_revocation_rejected(self):
        sender, event, receiver, paths = self.create(
            "stale"
        )

        empty = self.witness(sender, event, ())
        confirmed = self.witness(
            sender, event, (event.id,)
        )

        authority = MemoryAuthority(
            SymbolicReplayWitnessRevision(0, empty)
        )

        authority.publish(
            confirmed,
            expected_revision=0,
        )

        with self.assertRaisesRegex(
            RuntimeError, "Stale witness authority revision"
        ):
            authority.publish(
                confirmed,
                expected_revision=0,
            )

        with self.assertRaisesRegex(
            ValueError, "receipt revocation forbidden"
        ):
            authority.publish(
                empty,
                expected_revision=1,
            )

        self.assertEqual(authority.current.revision, 1)

    def test_authority_scope_mismatch_rejected(self):
        sender, event, receiver, paths = self.create(
            "scope"
        )

        original = self.witness(sender, event, ())

        authority = MemoryAuthority(
            SymbolicReplayWitnessRevision(0, original)
        )

        foreign = SymbolicReplayReceiptWitness(
            universe_id="foreign",
            batch_sha256=original.batch_sha256,
            receipt_ids=(),
        )

        with self.assertRaisesRegex(
            ValueError, "scope mismatch"
        ):
            authority.publish(
                foreign,
                expected_revision=0,
            )

        other_batch = SymbolicReplayReceiptWitness(
            universe_id=original.universe_id,
            batch_sha256="b" * 64,
            receipt_ids=(),
        )

        with self.assertRaisesRegex(
            ValueError, "scope mismatch"
        ):
            authority.publish(
                other_batch,
                expected_revision=0,
            )

        self.assertEqual(authority.current.revision, 0)

    def test_current_authority_allows_valid_recovery(self):
        sender, event, receiver, paths = self.create(
            "valid_recovery"
        )

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        authority = self.authority(
            sender, event, (event.id,)
        )

        target = self.universe(sender.id)

        report, restored_receiver = self.recover(
            target,
            paths,
            witness_authority=authority,
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.inbox_count, 1)
        self.assertEqual(authority.calls, 1)
        self.assertEqual(len(restored_receiver.receipts), 1)
        self.assertEqual(
            target.pending_symbolic_replay_events,
            (),
        )

    def test_current_authority_rejects_full_rollback(self):
        sender, event, receiver, paths = self.create(
            "rollback"
        )

        old = tuple(path.read_bytes() for path in paths)

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        authority = self.authority(
            sender, event, (event.id,)
        )

        for path, contents in zip(paths, old):
            path.write_bytes(contents)

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness missing confirmed receipt"
        ):
            self.recover(
                target,
                paths,
                witness_authority=authority,
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )
        self.assertEqual(
            tuple(path.read_bytes() for path in paths),
            old,
        )

    def test_stale_authority_does_not_detect_rollback(self):
        """A stale source is not a trusted latest-state read."""
        sender, event, receiver, paths = self.create(
            "stale_source"
        )

        authority = self.authority(sender, event, ())

        old = tuple(path.read_bytes() for path in paths)

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        for path, contents in zip(paths, old):
            path.write_bytes(contents)

        target = self.universe(sender.id)

        report, _ = self.recover(
            target,
            paths,
            witness_authority=authority,
        )

        self.assertEqual(report.inbox_count, 0)
        self.assertEqual(
            report.pending_delivery_ids,
            (event.id,),
        )

    def test_authority_outage_fails_closed(self):
        sender, event, receiver, paths = self.create(
            "outage"
        )

        authority = self.authority(
            sender, event, ()
        )
        authority.unavailable = True

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ConnectionError, "Authority unavailable"
        ):
            self.recover(
                target,
                paths,
                witness_authority=authority,
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )

    def test_noncanonical_authority_response_fails_closed(self):
        sender, event, receiver, paths = self.create(
            "bad_response"
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            TypeError, "noncanonical revision"
        ):
            self.recover(
                target,
                paths,
                witness_authority=InvalidAuthority(),
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )

    def test_foreign_authority_owner_is_rejected(self):
        sender, event, receiver, paths = self.create(
            "foreign_owner"
        )

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        wrong = SymbolicReplayReceiptWitness(
            universe_id="different_universe",
            batch_sha256=self.witness(
                sender, event, ()
            ).batch_sha256,
            receipt_ids=(event.id,),
        )

        authority = MemoryAuthority(
            SymbolicReplayWitnessRevision(0, wrong)
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness universe mismatch"
        ):
            self.recover(
                target,
                paths,
                witness_authority=authority,
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )

    def test_foreign_authority_batch_is_rejected(self):
        sender, event, receiver, paths = self.create(
            "foreign_batch"
        )

        wrong = SymbolicReplayReceiptWitness(
            universe_id=str(sender.id),
            batch_sha256="f" * 64,
            receipt_ids=(),
        )

        authority = MemoryAuthority(
            SymbolicReplayWitnessRevision(0, wrong)
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Trusted witness batch lineage mismatch"
        ):
            self.recover(
                target,
                paths,
                witness_authority=authority,
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )

    def test_conflicting_witness_sources_rejected(self):
        sender, event, receiver, paths = self.create(
            "conflict"
        )

        witness = self.witness(sender, event, ())
        authority = self.authority(sender, event, ())

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "Provide trusted_witness or witness_authority",
        ):
            self.recover(
                target,
                paths,
                trusted_witness=witness,
                witness_authority=authority,
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )

    def test_existing_a27_witness_remains_supported(self):
        sender, event, receiver, paths = self.create(
            "a27_compat"
        )

        self.assertEqual(
            self.deliver(sender, receiver, paths), 1
        )

        witness = self.witness(
            sender, event, (event.id,)
        )

        target = self.universe(sender.id)

        report, _ = self.recover(
            target,
            paths,
            trusted_witness=witness,
            required_receipt_ids=(event.id,),
        )

        self.assertEqual(report.delivered_count, 1)

    def test_direct_auditor_and_invalid_authority_type(self):
        sender, event, receiver, paths = self.create(
            "direct"
        )

        authority = self.authority(sender, event, ())

        target = self.universe(sender.id)

        report, _ = SymbolicReplayRecoveryAuditor.restore(
            target,
            outbox_path=paths[0],
            inbox_path=paths[1],
            witness_authority=authority,
        )

        self.assertEqual(report.outbox_count, 1)
        self.assertEqual(authority.calls, 1)

        invalid_target = self.universe(sender.id)

        with self.assertRaisesRegex(
            TypeError,
            "Witness authority must implement",
        ):
            self.recover(
                invalid_target,
                paths,
                witness_authority=object(),
            )

        self.assertEqual(
            invalid_target.symbolic_replay_outbox,
            [],
        )


if __name__ == "__main__":
    unittest.main()
