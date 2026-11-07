import io
import json
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
from universe.symbolic_replay_recovery_auditor import (
    SymbolicReplayRecoveryAuditor,
)


class SymbolicReplayBootstrapLineageTests(
    unittest.TestCase
):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix="a25_lineage_"
        )
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def create(self, label, *, identity=None, count=1):
        folder = self.directory / label
        folder.mkdir()

        if identity is None:
            identity = "a25_" + label

        sender = self.universe(identity)

        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"{label}_event_{index}",
                word_id=f"{label}_word_{index}",
                sequence=index,
                message=f"A25 {label} message {index}.",
            )
            for index in range(count)
        )

        sender.symbolic_replay_outbox.extend(events)

        paths = (
            folder / "outbox.json",
            folder / "inbox.json",
            folder / "bootstrap.json",
        )

        outbox, inbox, manifest = paths

        SymbolicReplayBootstrap.initialize(
            sender,
            outbox_path=outbox,
            inbox_path=inbox,
            manifest_path=manifest,
        )

        return sender, events, paths

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
    def document(path):
        return json.loads(
            path.read_text(encoding="utf-8")
        )

    @staticmethod
    def rewrite_manifest(path, document):
        payload = {
            key: value
            for key, value in document.items()
            if key != "sha256"
        }

        document["sha256"] = (
            SymbolicReplayBootstrap._checksum(payload)
        )

        path.write_text(
            json.dumps(
                document,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def test_manifest_v2_binds_canonical_batch(self):
        sender, events, paths = self.create(
            "manifest_v2", count=2
        )

        outbox, inbox, manifest = paths

        document = self.document(manifest)

        expected_digest = (
            SymbolicReplayOutboxStore.lineage_digest(
                sender.id, events,
            )
        )

        self.assertEqual(document["version"], 2)
        self.assertEqual(document["state"], "READY")
        self.assertEqual(
            document["batch_sha256"],
            expected_digest,
        )
        self.assertEqual(len(expected_digest), 64)

        target = self.universe(sender.id)
        report, receiver = self.recover(target, paths)

        self.assertEqual(report.outbox_count, 2)
        self.assertEqual(receiver.receipts, ())
        self.assertEqual(
            tuple(target.symbolic_replay_outbox),
            events,
        )

    def test_legitimate_ack_does_not_change_lineage(self):
        sender, events, paths = self.create(
            "ack", count=2
        )

        outbox, inbox, manifest = paths

        manifest_before = manifest.read_bytes()

        initial_digest = (
            SymbolicReplayOutboxStore.lineage_digest(
                sender.id,
                SymbolicReplayOutboxStore.read(
                    sender, outbox,
                ),
            )
        )

        target = self.universe(sender.id)
        initial_report, receiver = self.recover(
            target, paths
        )

        self.assertEqual(
            initial_report.pending_delivery_ids,
            tuple(item.id for item in events),
        )

        self.assertEqual(
            target.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=outbox,
            ),
            2,
        )

        persisted = SymbolicReplayOutboxStore.read(
            target, outbox,
        )

        self.assertTrue(
            all(item.delivered for item in persisted)
        )

        self.assertEqual(
            SymbolicReplayOutboxStore.lineage_digest(
                sender.id, persisted,
            ),
            initial_digest,
        )

        self.assertEqual(
            manifest.read_bytes(),
            manifest_before,
        )

        restarted = self.universe(sender.id)
        final_report, final_receiver = self.recover(
            restarted, paths
        )

        self.assertEqual(final_report.delivered_count, 2)
        self.assertEqual(final_report.inbox_count, 2)
        self.assertEqual(len(final_receiver.receipts), 2)
        self.assertEqual(
            restarted.pending_symbolic_replay_events,
            (),
        )

    def test_valid_outbox_from_another_batch_is_rejected(self):
        identity = "a25_shared_owner"

        original, events, paths = self.create(
            "original",
            identity=identity,
        )

        donor, donor_events, donor_paths = self.create(
            "donor",
            identity=identity,
        )

        outbox, inbox, manifest = paths

        manifest_before = manifest.read_bytes()

        outbox.write_bytes(
            donor_paths[0].read_bytes()
        )

        target = self.universe(identity)

        # Both individual checkpoints remain valid.
        self.assertEqual(
            SymbolicReplayOutboxStore.read(
                target, outbox,
            ),
            donor_events,
        )

        self.assertEqual(
            SymbolicReplayRecoveryAuditor.inspect(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
            ).status,
            "CONSISTENT",
        )

        with self.assertRaisesRegex(
            ValueError, "batch lineage mismatch"
        ):
            self.recover(target, paths)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )
        self.assertEqual(
            manifest.read_bytes(),
            manifest_before,
        )

    def test_valid_empty_outbox_replacement_is_rejected(self):
        identity = "a25_lost_events"

        sender, events, paths = self.create(
            "nonempty",
            identity=identity,
        )

        donor, _, donor_paths = self.create(
            "empty",
            identity=identity,
            count=0,
        )

        outbox, inbox, manifest = paths

        self.assertEqual(len(events), 1)

        outbox.write_bytes(
            donor_paths[0].read_bytes()
        )

        target = self.universe(identity)

        self.assertEqual(
            SymbolicReplayOutboxStore.read(
                target, outbox,
            ),
            (),
        )

        with self.assertRaisesRegex(
            ValueError, "batch lineage mismatch"
        ):
            self.recover(target, paths)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_resigned_wrong_digest_is_rejected(self):
        sender, events, paths = self.create(
            "resigned_manifest"
        )

        outbox, inbox, manifest = paths

        document = self.document(manifest)

        document["batch_sha256"] = "0" * 64

        self.rewrite_manifest(
            manifest, document,
        )

        # The manifest checksum is now valid,
        # but the binding refers to another batch.
        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "batch lineage mismatch"
        ):
            self.recover(target, paths)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_malformed_batch_digest_is_rejected(self):
        sender, events, paths = self.create(
            "malformed_digest"
        )

        outbox, inbox, manifest = paths

        document = self.document(manifest)
        document["batch_sha256"] = "not-a-sha256"

        self.rewrite_manifest(
            manifest, document,
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Invalid bootstrap manifest fields"
        ):
            self.recover(target, paths)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_legacy_manifest_v1_is_fail_closed(self):
        sender, events, paths = self.create(
            "legacy_v1"
        )

        outbox, inbox, manifest = paths

        document = self.document(manifest)

        document.pop("batch_sha256")
        document["version"] = 1

        self.rewrite_manifest(
            manifest, document,
        )

        before = tuple(
            path.read_bytes()
            for path in (outbox, inbox, manifest)
        )

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Legacy bootstrap manifest v1"
        ):
            self.recover(target, paths)

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

        self.assertEqual(
            tuple(
                path.read_bytes()
                for path in (outbox, inbox, manifest)
            ),
            before,
        )

    def test_auditor_checks_lineage_before_publication(self):
        identity = "a25_auditor_owner"

        original, original_events, paths = self.create(
            "auditor_original",
            identity=identity,
        )

        donor, donor_events, donor_paths = self.create(
            "auditor_donor",
            identity=identity,
        )

        outbox, inbox, manifest = paths

        expected_digest = (
            SymbolicReplayOutboxStore.lineage_digest(
                identity,
                original_events,
            )
        )

        outbox.write_bytes(
            donor_paths[0].read_bytes()
        )

        target = self.universe(identity)

        with self.assertRaisesRegex(
            ValueError, "batch lineage mismatch"
        ):
            SymbolicReplayRecoveryAuditor.restore(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
                expected_batch_sha256=expected_digest,
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )

    def test_invalid_expected_digest_is_rejected(self):
        sender, events, paths = self.create(
            "invalid_expected_digest"
        )

        outbox, inbox, manifest = paths

        target = self.universe(sender.id)

        with self.assertRaisesRegex(
            ValueError, "Invalid expected batch lineage digest"
        ):
            SymbolicReplayRecoveryAuditor.restore(
                target,
                outbox_path=outbox,
                inbox_path=inbox,
                expected_batch_sha256="invalid",
            )

        self.assertEqual(
            target.symbolic_replay_outbox, []
        )


if __name__ == "__main__":
    unittest.main()
