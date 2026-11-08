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


class SymbolicReplayHistoryRecoveryBoundaryTests(
    unittest.TestCase
):

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def test_recovery_preserves_history_and_runtime(self):
        source = self.universe("a35_history_boundary")
        target = self.universe(source.id)

        target.record_universe_state()

        history = target.universe_history
        original_record = history[0]

        quantum_state = target.quantum_state
        statistics = target.statistics

        quantum_before = (
            tuple(target.quantum_boxes),
            tuple(target.quantum_events),
            tuple(target.quantum_clock_events),
            target.quantum_state.tick_count,
        )

        source.symbolic_replay_outbox.append(
            SymbolicReplayOutboxEvent(
                id="a35_history_event",
                word_id="a35_history_word",
                sequence=0,
                message="A35 recovery boundary event",
            )
        )

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            outbox = root / "outbox.json"
            inbox = root / "inbox.json"
            manifest = root / "manifest.json"

            SymbolicReplayBootstrap.initialize(
                source,
                outbox_path=outbox,
                inbox_path=inbox,
                manifest_path=manifest,
            )

            report, receiver = (
                SymbolicReplayBootstrap.recover(
                    target,
                    outbox_path=outbox,
                    inbox_path=inbox,
                    manifest_path=manifest,
                )
            )

            self.assertEqual(
                report.pending_delivery_ids,
                ("a35_history_event",),
            )

            first = target.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=outbox,
            )

            second = target.retry_symbolic_replay_events(
                sink=receiver.accept,
                durable_outbox_path=outbox,
            )

            self.assertEqual(first, 1)
            self.assertEqual(second, 0)

            self.assertEqual(
                target.pending_symbolic_replay_events,
                (),
            )

            persisted = DurableSymbolicReplayInbox(
                path=inbox,
                universe_id=str(target.id),
            )

            self.assertEqual(len(persisted.receipts), 1)
            self.assertEqual(
                persisted.receipts[0].id,
                "a35_history_event",
            )

            self.assertIs(target.universe_history, history)
            self.assertEqual(
                target.universe_history,
                [original_record],
            )
            self.assertIs(
                target.universe_history[0],
                original_record,
            )

            self.assertIs(
                target.quantum_state,
                quantum_state,
            )
            self.assertIs(
                target.statistics,
                statistics,
            )

            quantum_after = (
                tuple(target.quantum_boxes),
                tuple(target.quantum_events),
                tuple(target.quantum_clock_events),
                target.quantum_state.tick_count,
            )

            self.assertEqual(
                quantum_after,
                quantum_before,
            )


if __name__ == "__main__":
    unittest.main()
