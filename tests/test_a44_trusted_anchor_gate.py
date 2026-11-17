"""A44 independent trust-anchor verification contracts.

The anchor fixture in these tests is VOLATILE.
It does not model a secure or durable production backend.
"""

import shutil
import sqlite3
import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import Event, RLock
from unittest.mock import patch

from core.existence import history_receipt_trust_floor as floor_module

from core.existence.history_receipt_proof import (
    ReceiptKeyStatus,
)
from core.existence.history_receipt_trust_floor import (
    DurableProviderReceiptTrustFloor as Store,
)
from test_a44_current_trust_enforcement import lifecycle_pair
from test_a44_versioned_receipt_keys import (
    CYCLE,
    EFFECT,
    OLD_KEY,
    SOURCE,
    issue,
    ring,
)


class VolatileAnchorForTests:
    """Independent in-memory witness with an exclusive lease."""

    def __init__(self, snapshot):
        self._lock = RLock()
        self._snapshot = tuple(snapshot)

    @contextmanager
    def hold(self):
        with self._lock:
            yield self._snapshot

    def replace(self, snapshot):
        with self._lock:
            self._snapshot = tuple(snapshot)


class UnavailableAnchorForTests:
    @contextmanager
    def hold(self):
        raise OSError("Injected trusted-anchor outage")
        yield


def anchored_verify(store, lifecycle, receipt, anchor):
    return store.verify_anchored_current_receipt(
        receipt,
        lifecycle=lifecycle,
        trusted_anchor=anchor,
        cycle_id=CYCLE,
        branch_id="root",
        effect_id=EFFECT,
        expected_source_id=SOURCE,
        receipt_id=receipt.receipt_id,
    )


class A44TrustedAnchorGateTests(unittest.TestCase):

    def test_anchor_rejects_database_rollback(self):
        initial, revoked = lifecycle_pair()
        receipts = (
            issue(version=1, secret=OLD_KEY),
            issue(key_id="k1", secret=OLD_KEY),
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            backup = Path(folder) / "previous.sqlite3"

            store = Store.bootstrap(path, initial)
            shutil.copyfile(path, backup)

            store.publish(revoked)

            # Test-only witness, retained outside SQLite.
            anchor = VolatileAnchorForTests(
                store._read_current()
            )

            shutil.copyfile(backup, path)
            restored = Store.open(path)

            self.assertEqual(restored.current_revision(), 1)

            for receipt in receipts:
                with self.subTest(
                    receipt_type=type(receipt).__name__
                ):
                    with self.assertRaises(ValueError):
                        anchored_verify(
                            restored, initial, receipt, anchor
                        )

    def test_same_revision_catalog_substitution_rejected(self):
        initial, revoked = lifecycle_pair()

        altered = initial.advance(
            {SOURCE: ring(old=ReceiptKeyStatus.VERIFY_ONLY)},
            revision=2,
        )

        with tempfile.TemporaryDirectory() as folder:
            trusted_path = Path(folder) / "trusted.sqlite3"
            alternate_path = Path(folder) / "alternate.sqlite3"

            trusted = Store.bootstrap(trusted_path, initial)
            trusted.publish(revoked)

            anchor = VolatileAnchorForTests(
                trusted._read_current()
            )

            alternate = Store.bootstrap(
                alternate_path, initial
            )
            alternate.publish(altered)

            shutil.copyfile(
                alternate_path, trusted_path
            )

            substituted = Store.open(trusted_path)

            self.assertEqual(
                substituted.current_revision(), 2
            )

            receipt = issue(
                key_id="k1",
                secret=OLD_KEY,
            )

            with self.assertRaises(ValueError):
                anchored_verify(
                    substituted, altered, receipt, anchor
                )

    def test_current_and_revoked_receipts_use_anchor(self):
        initial, revoked = lifecycle_pair()

        old_v1 = issue(version=1, secret=OLD_KEY)
        old_v2 = issue(key_id="k1", secret=OLD_KEY)
        active_v2 = issue()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"

            store = Store.bootstrap(path, initial)
            anchor = VolatileAnchorForTests(
                store._read_current()
            )

            self.assertTrue(
                anchored_verify(
                    store, initial, old_v1, anchor
                )
            )
            self.assertTrue(
                anchored_verify(
                    store, initial, old_v2, anchor
                )
            )

            store.publish(revoked)
            anchor.replace(store._read_current())

            self.assertFalse(
                anchored_verify(
                    store, revoked, old_v1, anchor
                )
            )
            self.assertFalse(
                anchored_verify(
                    store, revoked, old_v2, anchor
                )
            )
            self.assertTrue(
                anchored_verify(
                    store, revoked, active_v2, anchor
                )
            )

            with self.assertRaises(ValueError):
                anchored_verify(
                    store, initial, old_v2, anchor
                )

    def test_missing_or_unavailable_anchor_fails_closed(self):
        initial, _ = lifecycle_pair()
        receipt = issue(key_id="k1", secret=OLD_KEY)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            for anchor in (
                None,
                object(),
                UnavailableAnchorForTests(),
            ):
                with self.subTest(
                    anchor_type=type(anchor).__name__
                ):
                    with self.assertRaises(ValueError):
                        anchored_verify(
                            store, initial, receipt, anchor
                        )

    def test_anchor_lease_spans_cryptographic_verification(self):
        initial, _ = lifecycle_pair()
        receipt = issue(key_id="k1", secret=OLD_KEY)

        entered_crypto = Event()
        release_crypto = Event()
        advance_started = Event()
        advance_complete = Event()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"

            store = Store.bootstrap(path, initial)
            anchor = VolatileAnchorForTests(
                store._read_current()
            )

            original = floor_module.verify_signed_receipt

            def held_crypto(*args, **kwargs):
                entered_crypto.set()

                if not release_crypto.wait(timeout=10):
                    raise AssertionError(
                        "Crypto release timed out."
                    )

                return original(*args, **kwargs)

            def advance_anchor():
                advance_started.set()
                anchor.replace(
                    (2, "a" * 64, "b" * 64)
                )
                advance_complete.set()

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=held_crypto,
            ):
                with ThreadPoolExecutor(
                    max_workers=2
                ) as pool:

                    verifying = pool.submit(
                        anchored_verify,
                        store,
                        initial,
                        receipt,
                        anchor,
                    )

                    try:
                        self.assertTrue(
                            entered_crypto.wait(timeout=5),
                            "Verification did not enter crypto.",
                        )

                        advancing = pool.submit(
                            advance_anchor
                        )

                        self.assertTrue(
                            advance_started.wait(timeout=5)
                        )

                        self.assertFalse(
                            advance_complete.wait(timeout=0.25),
                            "Anchor changed before crypto finished.",
                        )

                    finally:
                        release_crypto.set()

                    self.assertTrue(
                        verifying.result(timeout=15)
                    )
                    advancing.result(timeout=15)

            self.assertTrue(advance_complete.is_set())


    def test_malformed_anchor_snapshots_fail_closed(self):
        initial, _ = lifecycle_pair()
        receipt = issue(key_id="k1", secret=OLD_KEY)

        class SnapshotAnchor:
            def __init__(self, snapshot):
                self.snapshot = snapshot

            @contextmanager
            def hold(self):
                yield self.snapshot

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            _, sources, catalog = store._read_current()

            snapshots = (
                (),
                (True, sources, catalog),
                (1, "invalid", catalog),
                (1, sources, "A" * 64),
                (1, "0" * 64, catalog),
                (1, sources, "0" * 64),
                [1, sources, catalog],
            )

            for index, snapshot in enumerate(snapshots, 1):
                with self.subTest(case=index):
                    with self.assertRaises(ValueError):
                        anchored_verify(
                            store,
                            initial,
                            receipt,
                            SnapshotAnchor(snapshot),
                        )

            valid_anchor = VolatileAnchorForTests(
                store._read_current()
            )

            self.assertTrue(
                anchored_verify(
                    store, initial, receipt, valid_anchor
                )
            )

    def test_crypto_exception_releases_both_resources(self):
        initial, revoked = lifecycle_pair()
        receipt = issue(key_id="k1", secret=OLD_KEY)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            anchor = VolatileAnchorForTests(
                store._read_current()
            )

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=RuntimeError(
                    "Injected crypto exception"
                ),
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "Injected crypto exception",
                ):
                    anchored_verify(
                        store, initial, receipt, anchor
                    )

            with ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(
                    anchor.replace,
                    tuple(store._read_current()),
                ).result(timeout=5)

                pool.submit(
                    store.publish,
                    revoked,
                ).result(timeout=5)

            self.assertEqual(store.current_revision(), 2)

            anchor.replace(store._read_current())

            self.assertFalse(
                anchored_verify(
                    store, revoked, receipt, anchor
                )
            )

    def test_sqlite_exception_releases_both_resources(self):
        initial, revoked = lifecycle_pair()
        receipt = issue(key_id="k1", secret=OLD_KEY)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            anchor = VolatileAnchorForTests(
                store._read_current()
            )

            with patch.object(
                floor_module,
                "_read_floor",
                side_effect=sqlite3.DatabaseError(
                    "Injected database exception"
                ),
            ):
                with self.assertRaises(ValueError):
                    anchored_verify(
                        store, initial, receipt, anchor
                    )

            with ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(
                    anchor.replace,
                    tuple(store._read_current()),
                ).result(timeout=5)

                pool.submit(
                    store.publish,
                    revoked,
                ).result(timeout=5)

            self.assertEqual(store.current_revision(), 2)

            anchor.replace(store._read_current())

            self.assertFalse(
                anchored_verify(
                    store, revoked, receipt, anchor
                )
            )

    def test_anchor_mismatch_prevents_crypto_execution(self):
        initial, revoked = lifecycle_pair()
        receipt = issue()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            stale_anchor = VolatileAnchorForTests(
                store._read_current()
            )

            store.publish(revoked)

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=AssertionError(
                    "Crypto must not execute."
                ),
            ) as crypto:
                with self.assertRaises(ValueError):
                    anchored_verify(
                        store,
                        revoked,
                        receipt,
                        stale_anchor,
                    )

                crypto.assert_not_called()


if __name__ == "__main__":
    unittest.main()
