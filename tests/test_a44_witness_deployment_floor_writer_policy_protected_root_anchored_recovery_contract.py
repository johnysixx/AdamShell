"""Explicit anchor recovery and shared fencing contract.

The independent anchor is the authoritative state source.

Recovery may copy only a canonical, valid single-revision
transition into the local backend, using explicitly supplied
expected references for both states.

An already synchronized pair permits idempotent recovery.

Recovery never writes to the independent anchor.
No automatic repair, reverse synchronization or revision
skipping is permitted.

All storage and signing operations use temporary fixtures.
"""

import importlib
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_anchored_backend_contract as previous

import test_a44_witness_deployment_floor_writer_policy_protected_root_anchored_authority_contract as integration


MODULE = "core.existence.history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_anchored_backend"


class A44AnchoredProtectedRootRecoveryContractTests(unittest.TestCase):

    def setUp(self):

        self.m = importlib.import_module(MODULE)

        self.f = previous.A44AnchoredProtectedRootBackendContractTests(
            "test_01_open_equal_canonical_roots"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.local = self.f.local
        self.anchor = self.f.anchor
        self.guard = self.f.guard
        self.objects = self.f.objects
        self.identity = self.f.identity
        self.initial = self.f.initial

        self.pending = self.objects.pending()

        self.final = self.objects.finalized(
            self.pending
        )

    def recover(self, local_ref=None, anchor_ref=None):

        if local_ref is None:
            local_ref = self.local.read().reference()

        if anchor_ref is None:
            anchor_ref = self.anchor.read().reference()

        return self.m.AnchoredProtectedRootBackend.recover_local(
            local_backend=self.local,
            anchor_backend=self.anchor,
            expected_identity=self.identity,
            expected_local=local_ref,
            expected_anchor=anchor_ref,
        )

    def anchor_advance(self, old, new):

        return self.f.advance(
            old,
            new,
            backend=self.anchor,
        )

    def local_advance(self, old, new):

        return self.f.advance(
            old,
            new,
            backend=self.local,
        )

    def assert_recovery_rejected(self):

        local = self.local.read()
        anchor = self.anchor.read()

        before = self.f.f.path.read_bytes()

        with self.assertRaises(ValueError):
            self.recover()

        self.assertEqual(self.local.read(), local)
        self.assertEqual(self.anchor.read(), anchor)

        self.assertEqual(
            self.f.f.path.read_bytes(),
            before,
        )

        self.f.assert_fenced()

    def assert_recovered(self, expected):

        self.f.assert_equal_roots(expected)

        self.assertEqual(
            self.f.open_guard().read().reference(),
            expected.reference(),
        )

    def test_01_recover_after_local_cas_failure(self):

        with patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=OSError("Local write failed"),
        ):

            with self.assertRaises(ValueError):

                self.f.advance(
                    self.initial,
                    self.pending,
                )

        self.assertEqual(self.local.read(), self.initial)
        self.assertEqual(self.anchor.read(), self.pending)

        self.f.assert_fenced()

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=AssertionError("Recovery wrote anchor"),
        ) as forbidden:

            result = self.recover(
                self.initial.reference(),
                self.pending.reference(),
            )

            forbidden.assert_not_called()

        self.assertEqual(
            result,
            self.pending.reference(),
        )

        self.assert_recovered(self.pending)

        self.f.advance(
            self.pending,
            self.final,
        )

        self.assert_recovered(self.final)

    def test_02_recover_after_anchor_acknowledgement_loss(self):

        original = type(self.anchor).compare_and_set

        reached = []

        def lose_ack(instance, *, expected, replacement):

            receipt = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            reached.append(receipt)

            raise OSError("Anchor acknowledgement lost")

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            lose_ack,
        ):

            with self.assertRaises(ValueError):

                self.f.advance(
                    self.initial,
                    self.pending,
                )

        self.assertEqual(
            reached,
            [self.pending.reference()],
        )

        self.assertEqual(self.local.read(), self.initial)
        self.assertEqual(self.anchor.read(), self.pending)

        self.f.assert_fenced()

        self.assertEqual(
            self.recover(),
            self.pending.reference(),
        )

        self.assert_recovered(self.pending)

    def test_03_synchronized_recovery_is_idempotent(self):

        self.f.advance(self.initial, self.pending)

        before = self.f.f.path.read_bytes()

        with patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unexpected local CAS"),
        ) as local_cas, patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=AssertionError("Unexpected anchor CAS"),
        ) as anchor_cas:

            for _ in range(3):

                self.assertEqual(
                    self.recover(),
                    self.pending.reference(),
                )

            local_cas.assert_not_called()
            anchor_cas.assert_not_called()

        self.assertEqual(
            self.f.f.path.read_bytes(),
            before,
        )

        self.assert_recovered(self.pending)

    def test_04_revision_gap_cannot_be_repaired_automatically(self):

        self.anchor_advance(
            self.initial,
            self.pending,
        )

        self.anchor_advance(
            self.pending,
            self.final,
        )

        self.assertEqual(self.local.read().revision, 1)
        self.assertEqual(self.anchor.read().revision, 3)

        self.assert_recovery_rejected()

    def test_05_same_revision_conflict_cannot_be_overwritten(self):

        alternative = self.objects.pending(
            self.objects.prepared(
                message=b"conflicting-recovery-candidate"
            )
        )

        self.local_advance(
            self.initial,
            alternative,
        )

        self.anchor_advance(
            self.initial,
            self.pending,
        )

        self.assertEqual(
            alternative.revision,
            self.pending.revision,
        )

        self.assertNotEqual(
            alternative.reference(),
            self.pending.reference(),
        )

        self.assert_recovery_rejected()

    def test_06_local_ahead_never_updates_anchor(self):

        self.local_advance(
            self.initial,
            self.pending,
        )

        self.assertEqual(self.local.read().revision, 2)
        self.assertEqual(self.anchor.read().revision, 1)

        self.assert_recovery_rejected()

    def test_07_explicit_recovery_references_are_required(self):

        self.anchor_advance(
            self.initial,
            self.pending,
        )

        before = self.f.f.path.read_bytes()

        for local_ref, anchor_ref in (
            (
                self.pending.reference(),
                self.pending.reference(),
            ),
            (
                self.initial.reference(),
                self.initial.reference(),
            ),
            (
                {},
                self.pending.reference(),
            ),
            (
                self.initial.reference(),
                {},
            ),
        ):

            with self.assertRaises(ValueError):

                self.recover(
                    local_ref,
                    anchor_ref,
                )

            self.assertEqual(
                self.f.f.path.read_bytes(),
                before,
            )

            self.assertEqual(
                self.anchor.read(),
                self.pending,
            )

        self.assertEqual(
            self.recover(),
            self.pending.reference(),
        )

        self.assert_recovered(self.pending)

    def test_08_unavailable_anchor_blocks_explicit_recovery(self):

        self.anchor_advance(
            self.initial,
            self.pending,
        )

        local_ref = self.initial.reference()
        anchor_ref = self.pending.reference()

        before = self.f.f.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "read",
            side_effect=OSError("Anchor unavailable"),
        ), patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unauthorized recovery CAS"),
        ) as forbidden:

            with self.assertRaises(ValueError):

                self.recover(
                    local_ref,
                    anchor_ref,
                )

            forbidden.assert_not_called()

        self.assertEqual(
            self.f.f.path.read_bytes(),
            before,
        )

        self.assertEqual(self.local.read(), self.initial)
        self.assertEqual(self.anchor.read(), self.pending)

        self.f.assert_fenced()

    def test_09_recovery_ack_loss_is_resolved_by_exact_readback(self):

        self.anchor_advance(
            self.initial,
            self.pending,
        )

        original = type(self.local).compare_and_set

        reached = []

        def lose_ack(instance, *, expected, replacement):

            receipt = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            reached.append(receipt)

            raise OSError("Recovery acknowledgement lost")

        with patch.object(
            type(self.local),
            "compare_and_set",
            lose_ack,
        ):

            with self.assertRaises(ValueError):
                self.recover()

        self.assertEqual(
            reached,
            [self.pending.reference()],
        )

        self.assert_recovered(self.pending)

        with self.assertRaises(ValueError):

            self.recover(
                self.initial.reference(),
                self.pending.reference(),
            )

        self.assertEqual(
            self.recover(
                self.pending.reference(),
                self.pending.reference(),
            ),
            self.pending.reference(),
        )

        self.assert_recovered(self.pending)

    def test_10_independent_local_instances_share_anchor_fence(self):

        path = self.f.f.directory / "independent-local.sqlite3"

        peer_local = self.f.f.create(path=path)

        peer_local.provision(state=self.initial)

        peer = self.f.open_guard(
            local_backend=peer_local,
        )

        self.assertIsNot(peer_local, self.local)

        started = threading.Event()
        entered = threading.Event()

        def competing_operation():

            started.set()

            with peer.exclusive():

                entered.set()

                return peer.read()

        with ThreadPoolExecutor(max_workers=1) as pool:

            with self.guard.exclusive():

                future = pool.submit(competing_operation)

                self.assertTrue(
                    started.wait(timeout=10)
                )

                self.assertFalse(
                    entered.wait(timeout=0.35),
                    "Independent anchor fence escaped",
                )

                self.assertFalse(future.done())

                self.assertEqual(
                    self.guard.read(),
                    self.initial,
                )

            self.assertEqual(
                future.result(timeout=30),
                self.initial,
            )

        self.assertTrue(entered.is_set())

    def test_11_nested_guards_preserve_committed_transitions(self):

        peer = self.f.open_guard()

        with self.assertRaises(OSError):

            with self.guard.exclusive():

                with peer.exclusive():

                    self.f.advance(
                        self.initial,
                        self.pending,
                        backend=peer,
                    )

                    self.assertEqual(
                        self.guard.read(),
                        self.pending,
                    )

                    self.f.advance(
                        self.pending,
                        self.final,
                    )

                    self.assertEqual(
                        peer.read(),
                        self.final,
                    )

                raise OSError(
                    "Outer operation failed after commit"
                )

        self.assert_recovered(self.final)

    def test_12_anchor_fence_spans_authorized_floor_cas(self):

        fixture = integration.A44AnchoredProtectedRootAuthorityContractTests(
            "test_01_publication_and_revocation_use_both_roots"
        )

        self.addCleanup(fixture.doCleanups)
        fixture.setUp()

        entered = threading.Event()
        release = threading.Event()
        contender_started = threading.Event()
        contender_entered = threading.Event()

        backend_type = type(fixture.p.backend)

        original = backend_type.advance_if_current

        def blocking_cas(instance, **arguments):

            entered.set()

            if not release.wait(timeout=20):

                raise TimeoutError(
                    "Floor CAS release timed out"
                )

            return original(instance, **arguments)

        def independent_anchor_operation():

            contender_started.set()

            with fixture.anchor.exclusive():

                contender_entered.set()

                return fixture.anchor.read()

        with patch.object(
            backend_type,
            "advance_if_current",
            blocking_cas,
        ):

            with ThreadPoolExecutor(max_workers=2) as pool:

                cas = pool.submit(fixture.base.send)

                try:

                    self.assertTrue(
                        entered.wait(timeout=10)
                    )

                    contender = pool.submit(
                        independent_anchor_operation
                    )

                    self.assertTrue(
                        contender_started.wait(timeout=5)
                    )

                    self.assertFalse(
                        contender_entered.wait(timeout=0.35),
                        "Anchor fence released during floor CAS",
                    )

                    self.assertFalse(contender.done())

                finally:

                    release.set()

                fixture.d.assert_committed(
                    cas.result(timeout=30),
                    2,
                )

                self.assertEqual(
                    contender.result(timeout=30),
                    fixture.initial,
                )

        self.assertTrue(contender_entered.is_set())

        fixture.d.assert_floor(2, 1)

        fixture.assert_equal_roots(
            fixture.initial,
        )


if __name__ == "__main__":
    unittest.main()
