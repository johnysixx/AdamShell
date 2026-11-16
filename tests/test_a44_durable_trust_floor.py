"""A44 durable provider trust-floor regression tests."""

import tempfile
import unittest
from pathlib import Path

from core.existence.history_receipt_proof import (
    ProviderReceiptKeyRing,
    ProviderReceiptTrustLifecycle,
    ReceiptKeyStatus,
    TrustedReceiptKey,
)


SOURCE = "a44-durable-provider"
OLD_KEY = b"O" * 32
NEW_KEY = b"N" * 32
ALT_KEY = b"X" * 32


def ring(old_status, *, new_secret=NEW_KEY, include_new=False):
    keys = [
        TrustedReceiptKey("k1", OLD_KEY, old_status),
    ]

    if include_new:
        keys.append(TrustedReceiptKey(
            "k2", new_secret, ReceiptKeyStatus.ACTIVE,
        ))

    return ProviderReceiptKeyRing(
        keys=tuple(keys),
        legacy_key_id="k1",
    )


def lifecycle_pair():
    initial = ProviderReceiptTrustLifecycle.start(
        {SOURCE: ring(ReceiptKeyStatus.ACTIVE)},
        expected_source_ids=(SOURCE,),
        revision=1,
    )

    current = initial.advance(
        {
            SOURCE: ring(
                ReceiptKeyStatus.REVOKED,
                include_new=True,
            ),
        },
        revision=2,
    )

    return initial, current


class A44DurableTrustFloorTests(unittest.TestCase):

    def test_persisted_floor_rejects_stale_catalog_after_restart(self):
        from core.existence.history_receipt_trust_floor import (
            DurableProviderReceiptTrustFloor,
        )

        initial, current = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust-floor.sqlite3"

            store = DurableProviderReceiptTrustFloor.bootstrap(
                path, initial,
            )

            self.assertEqual(store.current_revision(), 1)

            store.publish(current)
            self.assertEqual(store.current_revision(), 2)

            reopened = DurableProviderReceiptTrustFloor.open(path)

            self.assertEqual(reopened.current_revision(), 2)
            reopened.require_current(current)

            with self.assertRaises(ValueError):
                reopened.require_current(initial)

            with self.assertRaises(ValueError):
                reopened.publish(initial)

            self.assertEqual(reopened.current_revision(), 2)

    def test_same_revision_cannot_substitute_different_trust(self):
        from core.existence.history_receipt_trust_floor import (
            DurableProviderReceiptTrustFloor,
        )

        initial, current = lifecycle_pair()

        altered_secret = ProviderReceiptTrustLifecycle.start(
            {
                SOURCE: ring(
                    ReceiptKeyStatus.REVOKED,
                    new_secret=ALT_KEY,
                    include_new=True,
                ),
            },
            expected_source_ids=(SOURCE,),
            revision=2,
        )

        altered_status = ProviderReceiptTrustLifecycle.start(
            {
                SOURCE: ring(
                    ReceiptKeyStatus.VERIFY_ONLY,
                    include_new=True,
                ),
            },
            expected_source_ids=(SOURCE,),
            revision=2,
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust-floor.sqlite3"

            store = DurableProviderReceiptTrustFloor.bootstrap(
                path, initial,
            )
            store.publish(current)

            for candidate in (altered_secret, altered_status):
                with self.subTest(candidate=candidate.registry):
                    with self.assertRaises(ValueError):
                        store.require_current(candidate)

            store.require_current(current)
            self.assertEqual(store.current_revision(), 2)

    def test_multiple_handles_reject_stale_publication(self):
        from core.existence.history_receipt_trust_floor import (
            DurableProviderReceiptTrustFloor,
        )

        initial, current = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust-floor.sqlite3"

            first = DurableProviderReceiptTrustFloor.bootstrap(
                path, initial,
            )

            second = DurableProviderReceiptTrustFloor.open(path)

            first.publish(current)

            with self.assertRaises(ValueError):
                second.publish(initial)

            with self.assertRaises(ValueError):
                second.require_current(initial)

            second.require_current(current)
            self.assertEqual(second.current_revision(), 2)

    def test_missing_corrupt_and_existing_store_fail_closed(self):
        from core.existence.history_receipt_trust_floor import (
            DurableProviderReceiptTrustFloor,
        )

        initial, _ = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust-floor.sqlite3"

            with self.assertRaises(ValueError):
                DurableProviderReceiptTrustFloor.open(path)

            self.assertFalse(path.exists())

            store = DurableProviderReceiptTrustFloor.bootstrap(
                path, initial,
            )

            with self.assertRaises(ValueError):
                DurableProviderReceiptTrustFloor.bootstrap(
                    path, initial,
                )

            self.assertEqual(store.current_revision(), 1)

            corrupt = Path(folder) / "corrupt.sqlite3"
            corrupt.write_bytes(b"not-a-valid-sqlite-database")

            with self.assertRaises(ValueError):
                DurableProviderReceiptTrustFloor.open(corrupt)

    def test_store_does_not_persist_raw_signing_secrets(self):
        from core.existence.history_receipt_trust_floor import (
            DurableProviderReceiptTrustFloor,
        )

        initial, current = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust-floor.sqlite3"

            store = DurableProviderReceiptTrustFloor.bootstrap(
                path, initial,
            )

            store.publish(current)

            raw = path.read_bytes()

            self.assertNotIn(OLD_KEY, raw)
            self.assertNotIn(NEW_KEY, raw)


if __name__ == "__main__":
    unittest.main()
