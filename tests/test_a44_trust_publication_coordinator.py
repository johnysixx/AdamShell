"""A44 publication-coordinator behavioral contracts.

The authority fixture is process-local and volatile. It is NOT
a production trust root, durable journal, or authenticated service.

The coordinator under test must validate state transitions,
but a real backend must separately guarantee durable atomic CAS,
authentication and cross-process exclusion.
"""

import tempfile
import unittest

import sqlite3

from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import patch

from core.existence import (
    history_receipt_trust_floor as floor_module,
    history_receipt_trust_publication_coordinator as coordinator_module,
)

from contextlib import contextmanager
from pathlib import Path
from threading import RLock

from core.existence.history_receipt_proof import ReceiptKeyStatus
from core.existence.history_receipt_trust_floor import (
    DurableProviderReceiptTrustFloor as Store,
    _catalog_fingerprints,
)
from test_a44_current_trust_enforcement import lifecycle_pair
from test_a44_versioned_receipt_keys import (
    CYCLE, EFFECT, OLD_KEY, SOURCE, issue, ring,
)


OPERATION = "rotation-2"


def snapshot(lifecycle):
    return (
        lifecycle.revision,
        *_catalog_fingerprints(lifecycle),
    )


def make_coordinator(store, authority):
    from core.existence.history_receipt_trust_publication_coordinator import (
        TrustPublicationCoordinator,
    )

    return TrustPublicationCoordinator(
        store=store,
        authority=authority,
    )


def guarded_verify(store, lifecycle, receipt, authority):
    return store.verify_publication_guarded_receipt(
        receipt,
        lifecycle=lifecycle,
        publication_anchor=authority,
        cycle_id=CYCLE,
        branch_id="root",
        effect_id=EFFECT,
        expected_source_id=SOURCE,
        receipt_id=receipt.receipt_id,
    )


class VolatileAuthorityForTests:
    """Test-only storage and shared process-local publication lock."""

    def __init__(self, committed):
        self._lock = RLock()
        self._committed = committed
        self._pending = None

    @contextmanager
    def hold_write(self):
        with self._lock:
            yield self

    @contextmanager
    def hold_publication(self):
        with self._lock:
            pending_snapshot = (
                None
                if self._pending is None
                else self._pending[1]
            )
            yield self._committed, pending_snapshot

    def read_state(self):
        return self._committed, self._pending

    def prepare(self, *, expected_committed, operation_id, target):
        if self._committed != expected_committed:
            raise ValueError("Committed anchor CAS conflict.")

        proposed = (operation_id, target)

        if self._pending is not None:
            if self._pending == proposed:
                return False
            raise ValueError("Conflicting pending publication.")

        self._pending = proposed
        return True

    def finalize(self, *, expected_committed, operation_id, target):
        if (
            self._committed != expected_committed
            or self._pending != (operation_id, target)
        ):
            raise ValueError("Finalization CAS conflict.")

        self._committed = target
        self._pending = None

    def state(self):
        with self._lock:
            return self._committed, self._pending


class A44TrustPublicationCoordinatorTests(unittest.TestCase):

    def test_prepare_records_pending_and_blocks_verification(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )

            self.assertEqual(
                authority.state(),
                (
                    snapshot(initial),
                    (OPERATION, snapshot(revoked)),
                ),
            )
            self.assertEqual(store.current_revision(), 1)

            with self.assertRaises(ValueError):
                guarded_verify(
                    store,
                    initial,
                    issue(key_id="k1", secret=OLD_KEY),
                    authority,
                )

    def test_apply_advances_sqlite_but_preserves_pending(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )

            coordinator.apply(
                revoked,
                operation_id=OPERATION,
            )

            self.assertEqual(
                store._read_current(),
                snapshot(revoked),
            )
            self.assertEqual(
                authority.state()[0],
                snapshot(initial),
            )
            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

            with self.assertRaises(ValueError):
                guarded_verify(
                    store,
                    revoked,
                    issue(),
                    authority,
                )

    def test_finalize_before_apply_is_rejected(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )

            with self.assertRaises(ValueError):
                coordinator.finalize(
                    revoked,
                    operation_id=OPERATION,
                )

            self.assertEqual(store.current_revision(), 1)
            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

    def test_finalize_enforces_new_trust_policy(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )
            coordinator.apply(
                revoked,
                operation_id=OPERATION,
            )
            coordinator.finalize(
                revoked,
                operation_id=OPERATION,
            )

            self.assertEqual(
                authority.state(),
                (snapshot(revoked), None),
            )

            for receipt in (
                issue(version=1, secret=OLD_KEY),
                issue(key_id="k1", secret=OLD_KEY),
            ):
                with self.subTest(
                    receipt_type=type(receipt).__name__
                ):
                    self.assertFalse(
                        guarded_verify(
                            store, revoked, receipt, authority
                        )
                    )

            self.assertTrue(
                guarded_verify(
                    store, revoked, issue(), authority
                )
            )

    def test_repeated_prepare_and_apply_are_idempotent(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            for _ in range(2):
                coordinator.prepare(
                    revoked,
                    operation_id=OPERATION,
                )

            for _ in range(2):
                coordinator.apply(
                    revoked,
                    operation_id=OPERATION,
                )

            self.assertEqual(
                store._read_current(),
                snapshot(revoked),
            )
            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

            with self.assertRaises(ValueError):
                coordinator.prepare(
                    revoked,
                    operation_id="different-operation",
                )

    def test_conflicting_sqlite_and_missing_authority_hold(self):
        initial, revoked = lifecycle_pair()

        alternate = initial.advance(
            {
                SOURCE: ring(
                    old=ReceiptKeyStatus.VERIFY_ONLY
                )
            },
            revision=2,
        )

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )

            # Simulate an uncoordinated SQLite writer.
            store.publish(alternate)

            self.assertEqual(store.current_revision(), 2)
            self.assertNotEqual(
                store._read_current(),
                snapshot(revoked),
            )

            with self.assertRaises(ValueError):
                coordinator.apply(
                    revoked,
                    operation_id=OPERATION,
                )

            with self.assertRaises(ValueError):
                coordinator.finalize(
                    revoked,
                    operation_id=OPERATION,
                )

            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )

            coordinator = make_coordinator(store, None)

            with self.assertRaises(ValueError):
                coordinator.prepare(
                    revoked,
                    operation_id=OPERATION,
                )

            self.assertEqual(store.current_revision(), 1)


    def test_wrong_operation_cannot_apply_or_finalize(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )

            with self.assertRaises(ValueError):
                coordinator.apply(
                    revoked,
                    operation_id="other-operation",
                )

            with self.assertRaises(ValueError):
                coordinator.finalize(
                    revoked,
                    operation_id="other-operation",
                )

            self.assertEqual(store.current_revision(), 1)
            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

            coordinator.apply(
                revoked,
                operation_id=OPERATION,
            )
            coordinator.finalize(
                revoked,
                operation_id=OPERATION,
            )

            self.assertEqual(
                authority.state(),
                (snapshot(revoked), None),
            )

    def test_duplicate_completion_cannot_change_committed_state(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )
            coordinator.apply(
                revoked,
                operation_id=OPERATION,
            )

            # A retry is safe while the operation is pending.
            self.assertFalse(
                coordinator.prepare(
                    revoked,
                    operation_id=OPERATION,
                )
            )

            self.assertFalse(
                coordinator.apply(
                    revoked,
                    operation_id=OPERATION,
                )
            )

            coordinator.finalize(
                revoked,
                operation_id=OPERATION,
            )

            committed = authority.state()
            sqlite_state = store._read_current()

            # The test authority discards completed operation IDs.
            # Therefore a duplicate FINALIZE cannot be authenticated
            # as the same prior operation and must be rejected.
            for action in (
                coordinator.prepare,
                coordinator.apply,
                coordinator.finalize,
            ):
                with self.assertRaises(ValueError):
                    action(
                        revoked,
                        operation_id=OPERATION,
                    )

            self.assertEqual(authority.state(), committed)
            self.assertEqual(store._read_current(), sqlite_state)

    def test_sqlite_reopen_between_publication_phases(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trust.sqlite3"

            store = Store.bootstrap(path, initial)
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )

            coordinator = make_coordinator(store, authority)
            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )

            # Reopen SQLite only. The authority stays in memory;
            # this is NOT a full process-restart recovery test.
            reopened = Store.open(path)
            coordinator = make_coordinator(reopened, authority)

            self.assertEqual(reopened.current_revision(), 1)
            self.assertIsNotNone(authority.state()[1])

            coordinator.apply(
                revoked,
                operation_id=OPERATION,
            )

            reopened_again = Store.open(path)
            coordinator = make_coordinator(
                reopened_again,
                authority,
            )

            self.assertEqual(
                reopened_again._read_current(),
                snapshot(revoked),
            )

            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

            coordinator.finalize(
                revoked,
                operation_id=OPERATION,
            )

            self.assertEqual(
                authority.state(),
                (snapshot(revoked), None),
            )

            self.assertTrue(
                guarded_verify(
                    reopened_again,
                    revoked,
                    issue(),
                    authority,
                )
            )

    def test_sqlite_apply_failure_keeps_pending_for_retry(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )

            with patch.object(
                coordinator_module,
                "_read_floor",
                side_effect=sqlite3.OperationalError(
                    "Injected SQLite failure."
                ),
            ):
                with self.assertRaises(ValueError):
                    coordinator.apply(
                        revoked,
                        operation_id=OPERATION,
                    )

            self.assertEqual(store.current_revision(), 1)
            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

            # Retry in another thread to check that the
            # SQLite transaction and authority lease ended.
            with ThreadPoolExecutor(max_workers=1) as pool:
                applying = pool.submit(
                    coordinator.apply,
                    revoked,
                    operation_id=OPERATION,
                )

                self.assertTrue(
                    applying.result(timeout=15)
                )

            self.assertEqual(
                store._read_current(),
                snapshot(revoked),
            )

            coordinator.finalize(
                revoked,
                operation_id=OPERATION,
            )

    def test_authority_prepare_failure_keeps_sqlite_unchanged(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            with patch.object(
                authority,
                "prepare",
                side_effect=OSError(
                    "Injected authority PREPARE outage."
                ),
            ):
                with self.assertRaises(ValueError):
                    coordinator.prepare(
                        revoked,
                        operation_id=OPERATION,
                    )

            self.assertEqual(store.current_revision(), 1)
            self.assertEqual(
                authority.state(),
                (snapshot(initial), None),
            )

            with ThreadPoolExecutor(max_workers=1) as pool:
                preparing = pool.submit(
                    coordinator.prepare,
                    revoked,
                    operation_id=OPERATION,
                )

                self.assertTrue(
                    preparing.result(timeout=15)
                )

            self.assertEqual(store.current_revision(), 1)
            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

    def test_authority_finalize_failure_preserves_pending(self):
        initial, revoked = lifecycle_pair()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            coordinator.prepare(
                revoked,
                operation_id=OPERATION,
            )
            coordinator.apply(
                revoked,
                operation_id=OPERATION,
            )

            with patch.object(
                authority,
                "finalize",
                side_effect=OSError(
                    "Injected authority FINALIZE outage."
                ),
            ):
                with self.assertRaises(ValueError):
                    coordinator.finalize(
                        revoked,
                        operation_id=OPERATION,
                    )

            self.assertEqual(
                store._read_current(),
                snapshot(revoked),
            )

            self.assertEqual(
                authority.state(),
                (
                    snapshot(initial),
                    (OPERATION, snapshot(revoked)),
                ),
            )

            with self.assertRaises(ValueError):
                guarded_verify(
                    store,
                    revoked,
                    issue(),
                    authority,
                )

            with ThreadPoolExecutor(max_workers=1) as pool:
                finalizing = pool.submit(
                    coordinator.finalize,
                    revoked,
                    operation_id=OPERATION,
                )

                self.assertTrue(
                    finalizing.result(timeout=15)
                )

            self.assertEqual(
                authority.state(),
                (snapshot(revoked), None),
            )

    def test_invalid_operation_identity_fails_without_mutation(self):
        initial, revoked = lifecycle_pair()

        invalid_ids = (
            None,
            "",
            " ",
            " padded ",
            7,
            True,
        )

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            for invalid in invalid_ids:
                with self.subTest(value=repr(invalid)):
                    with self.assertRaises(ValueError):
                        coordinator.prepare(
                            revoked,
                            operation_id=invalid,
                        )

                    self.assertEqual(
                        authority.state(),
                        (snapshot(initial), None),
                    )

                    self.assertEqual(
                        store.current_revision(),
                        1,
                    )

    def test_guarded_verification_blocks_concurrent_prepare(self):
        initial, revoked = lifecycle_pair()

        entered_crypto = Event()
        release_crypto = Event()
        prepare_started = Event()
        prepare_completed = Event()

        with tempfile.TemporaryDirectory() as folder:
            store = Store.bootstrap(
                Path(folder) / "trust.sqlite3",
                initial,
            )
            authority = VolatileAuthorityForTests(
                snapshot(initial)
            )
            coordinator = make_coordinator(store, authority)

            original_crypto = floor_module.verify_signed_receipt

            def held_crypto(*args, **kwargs):
                entered_crypto.set()

                if not release_crypto.wait(timeout=10):
                    raise AssertionError(
                        "Crypto release timed out."
                    )

                return original_crypto(*args, **kwargs)

            def prepare():
                prepare_started.set()

                coordinator.prepare(
                    revoked,
                    operation_id=OPERATION,
                )

                prepare_completed.set()

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
                        issue(key_id="k1", secret=OLD_KEY),
                        authority,
                    )

                    try:
                        self.assertTrue(
                            entered_crypto.wait(timeout=5)
                        )

                        preparing = pool.submit(prepare)

                        self.assertTrue(
                            prepare_started.wait(timeout=5)
                        )

                        self.assertFalse(
                            prepare_completed.wait(timeout=0.25),
                            "PREPARE completed during verification.",
                        )

                    finally:
                        release_crypto.set()

                    self.assertTrue(
                        verifying.result(timeout=15)
                    )

                    preparing.result(timeout=15)

            self.assertTrue(prepare_completed.is_set())

            self.assertEqual(
                authority.state()[1],
                (OPERATION, snapshot(revoked)),
            )

            with self.assertRaises(ValueError):
                guarded_verify(
                    store,
                    initial,
                    issue(key_id="k1", secret=OLD_KEY),
                    authority,
                )


if __name__ == "__main__":
    unittest.main()
