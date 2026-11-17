"""A44 fail-closed publication-state classification contracts.

Classification is informational. It does not authenticate an
anchor, authorize verification, or repair persisted state.
"""

import tempfile
import unittest

from pathlib import Path

from core.existence.history_receipt_trust_floor import (
    DurableProviderReceiptTrustFloor as Store,
)
from test_a44_current_trust_enforcement import lifecycle_pair


def classify(sqlite_state, anchor_state, *,
             pending=None, available=True):
    from core.existence.history_receipt_trust_publication_state import (
        classify_publication_state,
    )

    return classify_publication_state(
        sqlite_snapshot=sqlite_state,
        committed_anchor_snapshot=anchor_state,
        pending_anchor_snapshot=pending,
        anchor_available=available,
    )


def assert_no_authority(test, report):
    test.assertFalse(report.authorizes_verification)
    test.assertFalse(report.retry_allowed)
    test.assertFalse(report.mutation_allowed)


class A44TrustPublicationStateTests(unittest.TestCase):

    def test_matching_committed_snapshot_is_informational(self):
        initial, _ = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            snapshot = store._read_current()

            report = classify(snapshot, snapshot)

            self.assertEqual(
                report.finding.value,
                "matched_committed",
            )

            assert_no_authority(self, report)

            self.assertEqual(store.current_revision(), 1)

    def test_sqlite_ahead_behind_and_conflict_hold(self):
        sources = "a" * 64

        old = (1, sources, "b" * 64)
        new = (2, sources, "c" * 64)
        conflict = (2, sources, "d" * 64)

        cases = (
            (old, new, "hold_sqlite_behind"),
            (new, old, "hold_sqlite_ahead"),
            (new, conflict, "hold_catalog_conflict"),
            (
                (2, "e" * 64, "c" * 64),
                new,
                "hold_catalog_conflict",
            ),
        )

        for sqlite_state, anchor_state, expected in cases:
            with self.subTest(expected=expected):
                report = classify(
                    sqlite_state, anchor_state
                )
                self.assertEqual(
                    report.finding.value, expected
                )
                assert_no_authority(self, report)

    def test_pending_publication_always_holds(self):
        sources = "a" * 64

        old = (1, sources, "b" * 64)
        new = (2, sources, "c" * 64)
        future = (3, sources, "d" * 64)

        cases = (
            (old, old, new),
            (new, old, new),
            (new, new, future),
        )

        for sqlite_state, committed, pending in cases:
            with self.subTest(
                sqlite_revision=sqlite_state[0],
                committed_revision=committed[0],
                pending_revision=pending[0],
            ):
                report = classify(
                    sqlite_state,
                    committed,
                    pending=pending,
                )
                self.assertEqual(
                    report.finding.value,
                    "hold_pending_publication",
                )
                assert_no_authority(self, report)

    def test_missing_and_unavailable_anchor_hold(self):
        snapshot = (
            1,
            "a" * 64,
            "b" * 64,
        )

        unavailable = classify(
            snapshot,
            snapshot,
            available=False,
        )

        self.assertEqual(
            unavailable.finding.value,
            "hold_anchor_unavailable",
        )
        assert_no_authority(self, unavailable)

        missing = classify(snapshot, None)

        self.assertEqual(
            missing.finding.value,
            "hold_anchor_unavailable",
        )
        assert_no_authority(self, missing)

    def test_malformed_snapshots_hold(self):
        valid = (
            1,
            "a" * 64,
            "b" * 64,
        )

        cases = (
            ((), valid, None),
            ((True, "a" * 64, "b" * 64), valid, None),
            ((1, "invalid", "b" * 64), valid, None),
            ((1, "a" * 64, "INVALID"), valid, None),
            ([1, "a" * 64, "b" * 64], valid, None),
            (valid, (0, "a" * 64, "b" * 64), None),
            (valid, valid, (1, "a" * 64, "c" * 64)),
        )

        for index, (sqlite_state, committed, pending) in (
            enumerate(cases, 1)
        ):
            with self.subTest(case=index):
                report = classify(
                    sqlite_state,
                    committed,
                    pending=pending,
                )

                self.assertEqual(
                    report.finding.value,
                    "hold_invalid_snapshot",
                )
                assert_no_authority(self, report)

    def test_sqlite_ahead_does_not_advance_anchor(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            committed = store._read_current()

            store.publish(revoked)

            current = store._read_current()

            report = classify(current, committed)

            self.assertEqual(
                report.finding.value,
                "hold_sqlite_ahead",
            )
            assert_no_authority(self, report)

            self.assertEqual(committed[0], 1)
            self.assertEqual(store.current_revision(), 2)

            # Classification must not repair either side.
            self.assertEqual(store._read_current(), current)


if __name__ == "__main__":
    unittest.main()
