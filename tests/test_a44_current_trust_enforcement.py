"""A44 atomic current-trust verification regressions."""

import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from unittest.mock import patch

from core.existence import history_receipt_proof as proof

from core.existence.history_receipt_proof import (
    ProviderReceiptTrustLifecycle,
    ReceiptKeyStatus,
)

from core.existence.history_receipt_trust_floor import (
    DurableProviderReceiptTrustFloor,
)

from test_a44_versioned_receipt_keys import (
    SOURCE,
    CYCLE,
    EFFECT,
    OLD_KEY,
    issue,
    ring,
)


def lifecycle_pair():
    initial = ProviderReceiptTrustLifecycle.start(
        {SOURCE: ring(old=ReceiptKeyStatus.ACTIVE)},
        expected_source_ids=(SOURCE,),
        revision=1,
    )

    revoked = initial.advance(
        {SOURCE: ring(old=ReceiptKeyStatus.REVOKED)},
        revision=2,
    )

    return initial, revoked


def verify_current(store, lifecycle, receipt):
    return store.verify_current_receipt(
        receipt,
        lifecycle=lifecycle,
        cycle_id=CYCLE,
        branch_id="root",
        effect_id=EFFECT,
        expected_source_id=SOURCE,
        receipt_id=receipt.receipt_id,
    )


class A44CurrentTrustEnforcementTests(unittest.TestCase):

    def test_current_catalog_requires_atomic_verification(self):
        initial, revoked = lifecycle_pair()

        old_v1 = issue(version=1, secret=OLD_KEY)
        old_v2 = issue(key_id="k1", secret=OLD_KEY)
        new_v2 = issue()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust-floor.sqlite3"

            store = DurableProviderReceiptTrustFloor.bootstrap(
                path, initial,
            )

            self.assertTrue(
                verify_current(store, initial, old_v1)
            )
            self.assertTrue(
                verify_current(store, initial, old_v2)
            )

            store.publish(revoked)

            with self.assertRaises(ValueError):
                verify_current(store, initial, old_v1)

            with self.assertRaises(ValueError):
                verify_current(store, initial, old_v2)

            self.assertFalse(
                verify_current(store, revoked, old_v1)
            )
            self.assertFalse(
                verify_current(store, revoked, old_v2)
            )
            self.assertTrue(
                verify_current(store, revoked, new_v2)
            )

    def test_same_revision_substituted_catalog_is_rejected(self):
        initial, _ = lifecycle_pair()

        substituted = ProviderReceiptTrustLifecycle.start(
            {SOURCE: ring(old=ReceiptKeyStatus.REVOKED)},
            expected_source_ids=(SOURCE,),
            revision=1,
        )

        receipt = issue(key_id="k1", secret=OLD_KEY)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust-floor.sqlite3"

            store = DurableProviderReceiptTrustFloor.bootstrap(
                path, initial,
            )

            with self.assertRaises(ValueError):
                verify_current(store, substituted, receipt)

            self.assertTrue(
                verify_current(store, initial, receipt)
            )

    def test_publication_waits_for_inflight_verification(self):
        initial, revoked = lifecycle_pair()

        receipt = issue(key_id="k1", secret=OLD_KEY)

        entered_verifier = Event()
        release_verifier = Event()
        publisher_started = Event()
        publisher_completed = Event()

        original_verify_v2 = proof._verify_v2_receipt

        def held_verify(*args, **kwargs):
            entered_verifier.set()

            if not release_verifier.wait(timeout=10):
                raise AssertionError(
                    "Timed out waiting to release verification."
                )

            return original_verify_v2(*args, **kwargs)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust-floor.sqlite3"

            store = DurableProviderReceiptTrustFloor.bootstrap(
                path, initial,
            )

            def publisher():
                publisher_started.set()
                store.publish(revoked)
                publisher_completed.set()

            with patch.object(
                proof,
                "_verify_v2_receipt",
                side_effect=held_verify,
            ):
                with ThreadPoolExecutor(max_workers=2) as pool:
                    verifying = pool.submit(
                        verify_current,
                        store,
                        initial,
                        receipt,
                    )

                    try:
                        self.assertTrue(
                            entered_verifier.wait(timeout=5),
                            "Verification did not reach crypto step.",
                        )

                        publishing = pool.submit(publisher)

                        self.assertTrue(
                            publisher_started.wait(timeout=5)
                        )

                        self.assertFalse(
                            publisher_completed.wait(timeout=0.25),
                            "Revocation committed during verification.",
                        )

                    finally:
                        release_verifier.set()

                    self.assertTrue(
                        verifying.result(timeout=15)
                    )

                    publishing.result(timeout=15)

            self.assertTrue(publisher_completed.is_set())

            self.assertEqual(
                store.current_revision(), 2
            )

            with self.assertRaises(ValueError):
                verify_current(store, initial, receipt)

            self.assertFalse(
                verify_current(store, revoked, receipt)
            )


if __name__ == "__main__":
    unittest.main()
