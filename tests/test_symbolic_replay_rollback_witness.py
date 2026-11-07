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
from universe.symbolic_replay_recovery_auditor import (
    SymbolicReplayRecoveryAuditor,
)


class SymbolicReplayRollbackWitnessTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a26_witness_"
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

        identity = "a26_" + label
        sender = self.universe(identity)

        event = SymbolicReplayOutboxEvent(
            id=f"{identity}_event",
            word_id=f"{identity}_word",
            sequence=0,
            message=f"A26 event from {label}.",
        )

        sender.symbolic_replay_outbox.append(event)

        paths = (
            folder / "outbox.json",
            folder / "inbox.json",
            folder / "bootstrap.json",
        )

        outbox, inbox, manifest = paths

        report, receiver = (
            SymbolicReplayBootstrap.initialize(
                sender,
                outbox_path=outbox,
                inbox_path=inbox,
                manifest_path=manifest,
            )
        )

        self.assertEqual(report.outbox_count, 1)

        return sender, event, paths, receiver

    @staticmethod
    def deliver(sender, paths, receiver):
        outbox = paths[0]

        count = sender.retry_symbolic_replay_events(
            sink=receiver.accept,
            durable_outbox_path=outbox,
        )

        if count != 1:
            raise AssertionError(
                "Expected one durable delivery."
            )

    def restore(self, identity, paths, *, required=None):
        target = self.universe(identity)

        outbox, inbox, manifest = paths

        report, receiver = (
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
                manifest_path=manifest,
                required_receipt_ids=required,
            )
        )

        return target, report, receiver

    def test_confirmed_receipt_witness_is_accepted(self):
        sender, event, paths, receiver = (
            self.create("confirmed")
        )

        self.deliver(sender, paths, receiver)

        target, report, restored_receiver = (
            self.restore(
                sender.id,
                paths,
                required=(event.id,),
            )
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(report.inbox_count, 1)
        self.assertEqual(
            len(restored_receiver.receipts),
            1,
        )

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=lambda _: self.fail(
                    "Duplicate delivery."
                ),
                durable_outbox_path=paths[0],
            ),
            0,
        )

    def test_frozenset_witness_is_supported(self):
        sender, event, paths, receiver = (
            self.create("frozenset")
        )

        self.deliver(sender, paths, receiver)

        target, report, _ = self.restore(
            sender.id,
            paths,
            required=frozenset((event.id,)),
        )

        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(
            target.pending_symbolic_replay_events,
            (),
        )

    def test_outbox_only_rollback_preserves_receipt(self):
        sender, event, paths, receiver = (
            self.create("outbox_only")
        )

        outbox, inbox, manifest = paths

        pending_outbox = outbox.read_bytes()

        self.deliver(sender, paths, receiver)

        confirmed_inbox = inbox.read_bytes()

        # Roll back only the outbox in temporary storage.
        outbox.write_bytes(pending_outbox)

        target, report, recovered_receiver = (
            self.restore(
                sender.id,
                paths,
                required=(event.id,),
            )
        )

        self.assertEqual(
            report.status,
            "RECOVERABLE_PENDING_ACK",
        )
        self.assertEqual(
            report.pending_ack_ids,
            (event.id,),
        )

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=recovered_receiver.accept,
                durable_outbox_path=outbox,
            ),
            1,
        )

        # The existing receipt must not be duplicated.
        self.assertEqual(
            inbox.read_bytes(),
            confirmed_inbox,
        )
        self.assertEqual(
            target.pending_symbolic_replay_events,
            (),
        )

    def test_full_rollback_with_witness_is_rejected(self):
        sender, event, paths, receiver = (
            self.create("full_rollback_guarded")
        )

        initial = tuple(
            path.read_bytes()
            for path in paths
        )

        self.deliver(sender, paths, receiver)

        # Simulate a rollback of the entire local
        # checkpoint set, including its manifest.
        for path, contents in zip(paths, initial):
            path.write_bytes(contents)

        target = self.universe(sender.id)
        outbox, inbox, manifest = paths

        with self.assertRaisesRegex(
            ValueError,
            "Trusted receipt witness mismatch",
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
                manifest_path=manifest,
                required_receipt_ids=(event.id,),
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )
        self.assertEqual(
            tuple(
                path.read_bytes()
                for path in paths
            ),
            initial,
        )

    def test_full_rollback_without_witness_is_not_detected(self):
        """Document the limit without independent evidence."""
        sender, event, paths, receiver = (
            self.create("full_rollback_unguarded")
        )

        initial = tuple(
            path.read_bytes()
            for path in paths
        )

        self.deliver(sender, paths, receiver)

        for path, contents in zip(paths, initial):
            path.write_bytes(contents)

        target, report, recovered_receiver = (
            self.restore(sender.id, paths)
        )

        self.assertEqual(report.status, "CONSISTENT")
        self.assertEqual(report.inbox_count, 0)
        self.assertEqual(
            report.pending_delivery_ids,
            (event.id,),
        )

        invoked = []

        def observed_sink(item):
            invoked.append(item.id)
            return recovered_receiver.accept(item)

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=observed_sink,
                durable_outbox_path=paths[0],
            ),
            1,
        )

        # The receiver can be invoked again after
        # complete loss of the prior receipt history.
        self.assertEqual(invoked, [event.id])

    def test_inbox_only_rollback_is_rejected_by_a22(self):
        sender, event, paths, receiver = (
            self.create("inbox_only")
        )

        outbox, inbox, manifest = paths

        empty_inbox = inbox.read_bytes()

        self.deliver(sender, paths, receiver)

        inbox.write_bytes(empty_inbox)

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "ACK without matching inbox receipt",
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
                manifest_path=manifest,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_invalid_witness_inputs_fail_closed(self):
        sender, event, paths, receiver = (
            self.create("invalid_inputs")
        )

        outbox, inbox, manifest = paths

        invalid_cases = (
            ([event.id], TypeError),
            (event.id, TypeError),
            (("",), ValueError),
            ((123,), ValueError),
            ((event.id, event.id), ValueError),
        )

        for bad, error_type in invalid_cases:
            with self.subTest(value=repr(bad)):
                target = self.universe(sender.id)

                with self.assertRaises(error_type):
                    SymbolicReplayBootstrap.recover(
                        target,
                        outbox_path=outbox,
                        inbox_path=inbox,
                        manifest_path=manifest,
                        required_receipt_ids=bad,
                    )

                self.assertEqual(
                    target.symbolic_replay_outbox,
                    [],
                )

    def test_unknown_required_receipt_fails_closed(self):
        sender, event, paths, receiver = (
            self.create("unknown_required")
        )

        outbox, inbox, manifest = paths

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "Trusted receipt witness mismatch",
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
                manifest_path=manifest,
                required_receipt_ids=(
                    "external_unknown_event",
                ),
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_direct_auditor_enforces_receipt_witness(self):
        sender, event, paths, receiver = (
            self.create("direct_auditor")
        )

        outbox, inbox, manifest = paths

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError,
            "Trusted receipt witness mismatch",
        ):
            SymbolicReplayRecoveryAuditor.restore(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
                required_receipt_ids=(event.id,),
            )

        self.assertEqual(
            target.symbolic_replay_outbox,
            [],
        )


if __name__ == "__main__":
    unittest.main()
