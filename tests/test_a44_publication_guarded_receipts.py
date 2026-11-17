"""A44 publication-aware receipt verification contracts.

The publication witness is volatile and test-only.
No durable production authority or crash-safe publication is implied.
"""

import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import Event, RLock
from unittest.mock import patch

from core.existence import (
    history_receipt_trust_floor as floor_module,
)
from core.existence.history_receipt_trust_floor import (
    DurableProviderReceiptTrustFloor as Store,
    _catalog_fingerprints,
)
from test_a44_current_trust_enforcement import lifecycle_pair
from test_a44_versioned_receipt_keys import (
    CYCLE, EFFECT, OLD_KEY, SOURCE, issue,
)


def snapshot(lifecycle):
    return (
        lifecycle.revision,
        *_catalog_fingerprints(lifecycle),
    )


class PublicationWitnessForTests:
    """Atomically expose committed and pending publication."""

    def __init__(self, committed, pending=None):
        self._lock = RLock()
        self._committed = committed
        self._pending = pending

    @contextmanager
    def hold_publication(self):
        with self._lock:
            yield self._committed, self._pending

    def prepare(self, pending):
        with self._lock:
            self._pending = pending

    def finalize(self, committed):
        with self._lock:
            self._committed = committed
            self._pending = None

    def state(self):
        with self._lock:
            return self._committed, self._pending


def guarded_verify(store, lifecycle, receipt, witness):
    return store.verify_publication_guarded_receipt(
        receipt,
        lifecycle=lifecycle,
        publication_anchor=witness,
        cycle_id=CYCLE,
        branch_id="root",
        effect_id=EFFECT,
        expected_source_id=SOURCE,
        receipt_id=receipt.receipt_id,
    )


class A44PublicationGuardedReceiptTests(unittest.TestCase):

    def test_prepared_blocks_old_signature_before_sqlite_update(self):
        initial, revoked = lifecycle_pair()

        receipt = issue(
            key_id="k1",
            secret=OLD_KEY,
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            witness = PublicationWitnessForTests(
                snapshot(initial),
                pending=snapshot(revoked),
            )

            with self.assertRaises(ValueError):
                guarded_verify(
                    store, initial, receipt, witness
                )

            self.assertEqual(store.current_revision(), 1)
            self.assertEqual(
                witness.state()[1],
                snapshot(revoked),
            )

    def test_prepared_blocks_new_signature_after_sqlite_update(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            witness = PublicationWitnessForTests(
                snapshot(initial),
                pending=snapshot(revoked),
            )

            store.publish(revoked)

            with self.assertRaises(ValueError):
                guarded_verify(
                    store, revoked, issue(), witness
                )

            self.assertEqual(store.current_revision(), 2)
            self.assertEqual(
                witness.state(),
                (snapshot(initial), snapshot(revoked)),
            )

    def test_pending_holds_when_committed_matches_sqlite(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            witness = PublicationWitnessForTests(
                snapshot(initial),
                pending=snapshot(revoked),
            )

            with self.assertRaises(ValueError):
                guarded_verify(
                    store,
                    initial,
                    issue(version=1, secret=OLD_KEY),
                    witness,
                )

    def test_finalized_policy_verifies_correct_keys(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            witness = PublicationWitnessForTests(
                snapshot(initial),
                pending=snapshot(revoked),
            )

            store.publish(revoked)
            witness.finalize(snapshot(revoked))

            old_receipts = (
                issue(version=1, secret=OLD_KEY),
                issue(key_id="k1", secret=OLD_KEY),
            )

            for receipt in old_receipts:
                with self.subTest(
                    receipt_type=type(receipt).__name__
                ):
                    self.assertFalse(
                        guarded_verify(
                            store, revoked, receipt, witness
                        )
                    )

            self.assertTrue(
                guarded_verify(
                    store, revoked, issue(), witness
                )
            )

    def test_invalid_anchor_fails_closed(self):
        initial, _ = lifecycle_pair()

        class BadWitness:
            @contextmanager
            def hold_publication(self):
                yield (
                    (True, "a" * 64, "b" * 64),
                    None,
                )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            for witness in (
                None,
                object(),
                BadWitness(),
            ):
                with self.subTest(
                    kind=type(witness).__name__
                ):
                    with self.assertRaises(ValueError):
                        guarded_verify(
                            store, initial, issue(), witness
                        )

    def test_publication_lease_spans_crypto_verification(self):
        initial, revoked = lifecycle_pair()

        entered = Event()
        release = Event()
        started = Event()
        completed = Event()

        receipt = issue(
            key_id="k1",
            secret=OLD_KEY,
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"
            store = Store.bootstrap(path, initial)

            witness = PublicationWitnessForTests(
                snapshot(initial)
            )

            original = floor_module.verify_signed_receipt

            def held_crypto(*args, **kwargs):
                entered.set()

                if not release.wait(timeout=10):
                    raise AssertionError(
                        "Crypto release timed out."
                    )

                return original(*args, **kwargs)

            def prepare():
                started.set()
                witness.prepare(snapshot(revoked))
                completed.set()

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=held_crypto,
            ):
                with ThreadPoolExecutor(
                    max_workers=2
                ) as pool:
                    verifying = pool.submit(
                        guarded_verify,
                        store,
                        initial,
                        receipt,
                        witness,
                    )

                    try:
                        self.assertTrue(
                            entered.wait(timeout=5)
                        )

                        preparing = pool.submit(prepare)

                        self.assertTrue(
                            started.wait(timeout=5)
                        )

                        self.assertFalse(
                            completed.wait(timeout=0.25),
                            "PREPARE completed during crypto.",
                        )

                    finally:
                        release.set()

                    self.assertTrue(
                        verifying.result(timeout=15)
                    )

                    preparing.result(timeout=15)

            self.assertTrue(completed.is_set())

            with self.assertRaises(ValueError):
                guarded_verify(
                    store, initial, receipt, witness
                )


    def test_catalog_mismatch_short_circuits_crypto(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )

            current = snapshot(initial)

            altered_catalog = (
                current[0], current[1], "0" * 64,
            )

            altered_sources = (
                current[0], "0" * 64, current[2],
            )

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=AssertionError(
                    "Crypto must not run on a conflict."
                ),
            ):
                for committed in (
                    altered_catalog,
                    altered_sources,
                ):
                    with self.subTest(committed=committed):
                        witness = PublicationWitnessForTests(
                            committed
                        )

                        with self.assertRaises(ValueError):
                            guarded_verify(
                                store,
                                initial,
                                issue(),
                                witness,
                            )

                store.publish(revoked)

                witness = PublicationWitnessForTests(
                    snapshot(revoked)
                )

                with self.assertRaises(ValueError):
                    guarded_verify(
                        store,
                        initial,
                        issue(),
                        witness,
                    )

    def test_invalid_pending_never_reaches_crypto(self):
        initial, _ = lifecycle_pair()

        committed = snapshot(initial)
        revision, sources, catalog = committed

        pending_cases = (
            committed,
            (revision + 1, "0" * 64, catalog),
            (revision + 1, sources, "invalid"),
            [revision + 1, sources, catalog],
            (True, sources, catalog),
        )

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=AssertionError(
                    "Invalid pending state reached crypto."
                ),
            ):
                for pending in pending_cases:
                    with self.subTest(pending=pending):
                        witness = PublicationWitnessForTests(
                            committed,
                            pending=pending,
                        )

                        with self.assertRaises(ValueError):
                            guarded_verify(
                                store,
                                initial,
                                issue(),
                                witness,
                            )

    def test_anchor_outage_and_bad_shape_fail_closed(self):
        initial, _ = lifecycle_pair()

        class UnavailableWitness:
            @contextmanager
            def hold_publication(self):
                raise OSError("Injected anchor outage")
                yield

        class BadShapeWitness:
            @contextmanager
            def hold_publication(self):
                yield (
                    snapshot(initial),
                    None,
                    None,
                )

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=AssertionError(
                    "Unavailable anchor reached crypto."
                ),
            ):
                for witness in (
                    UnavailableWitness(),
                    BadShapeWitness(),
                ):
                    with self.subTest(
                        witness=type(witness).__name__
                    ):
                        with self.assertRaises(ValueError):
                            guarded_verify(
                                store,
                                initial,
                                issue(),
                                witness,
                            )

            valid_witness = PublicationWitnessForTests(
                snapshot(initial)
            )

            self.assertTrue(
                guarded_verify(
                    store,
                    initial,
                    issue(),
                    valid_witness,
                )
            )

    def test_crypto_failure_releases_both_resources(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )

            witness = PublicationWitnessForTests(
                snapshot(initial)
            )

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=RuntimeError(
                    "Injected crypto failure."
                ),
            ):
                with self.assertRaises(RuntimeError):
                    guarded_verify(
                        store,
                        initial,
                        issue(),
                        witness,
                    )

            # Use other threads to detect leaked locks.
            with ThreadPoolExecutor(max_workers=2) as pool:
                preparing = pool.submit(
                    witness.prepare,
                    snapshot(revoked),
                )

                publishing = pool.submit(
                    store.publish,
                    revoked,
                )

                preparing.result(timeout=15)
                publishing.result(timeout=15)

            self.assertEqual(store.current_revision(), 2)

            self.assertEqual(
                witness.state(),
                (snapshot(initial), snapshot(revoked)),
            )

            with self.assertRaises(ValueError):
                guarded_verify(
                    store,
                    revoked,
                    issue(),
                    witness,
                )

    def test_sqlite_failure_releases_publication_lease(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )

            witness = PublicationWitnessForTests(
                snapshot(initial)
            )

            with patch.object(
                floor_module,
                "_read_floor",
                side_effect=floor_module.sqlite3.OperationalError(
                    "Injected SQLite read failure."
                ),
            ):
                with self.assertRaises(ValueError):
                    guarded_verify(
                        store,
                        initial,
                        issue(),
                        witness,
                    )

            with ThreadPoolExecutor(max_workers=1) as pool:
                preparing = pool.submit(
                    witness.prepare,
                    snapshot(revoked),
                )

                preparing.result(timeout=10)

            self.assertEqual(store.current_revision(), 1)

            # SQLite must not retain a write lock.
            store.publish(revoked)

            self.assertEqual(store.current_revision(), 2)

    def test_sqlite_publish_waits_for_guarded_crypto(self):
        initial, revoked = lifecycle_pair()

        entered_crypto = Event()
        release_crypto = Event()
        publish_started = Event()
        publish_completed = Event()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )

            witness = PublicationWitnessForTests(
                snapshot(initial)
            )

            original_crypto = floor_module.verify_signed_receipt

            def held_crypto(*args, **kwargs):
                entered_crypto.set()

                if not release_crypto.wait(timeout=10):
                    raise AssertionError(
                        "Crypto release timed out."
                    )

                return original_crypto(*args, **kwargs)

            def publish():
                publish_started.set()
                store.publish(revoked)
                publish_completed.set()

            with patch.object(
                floor_module,
                "verify_signed_receipt",
                side_effect=held_crypto,
            ):
                with ThreadPoolExecutor(max_workers=2) as pool:
                    verifying = pool.submit(
                        guarded_verify,
                        store,
                        initial,
                        issue(),
                        witness,
                    )

                    try:
                        self.assertTrue(
                            entered_crypto.wait(timeout=5)
                        )

                        publishing = pool.submit(publish)

                        self.assertTrue(
                            publish_started.wait(timeout=5)
                        )

                        self.assertFalse(
                            publish_completed.wait(timeout=0.25),
                            "SQLite publication completed "
                            "during guarded verification.",
                        )

                    finally:
                        release_crypto.set()

                    self.assertTrue(
                        verifying.result(timeout=15)
                    )

                    publishing.result(timeout=15)

            self.assertTrue(publish_completed.is_set())
            self.assertEqual(store.current_revision(), 2)

            # The anchor was not updated by SQLite publish.
            with self.assertRaises(ValueError):
                guarded_verify(
                    store,
                    revoked,
                    issue(),
                    witness,
                )


if __name__ == "__main__":
    unittest.main()
