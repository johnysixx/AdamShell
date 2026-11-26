"""Adversarial anchored protected root contract.

Backend errors, ambiguous commits and incorrect receipts
must not authorize an unconfirmed local transition.

The independent anchor is an isolated in-memory test double.
All local storage belongs to temporary test fixtures.

These tests do not establish external anchor authenticity,
hardware durability or independence of trust domains.
"""

import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from unittest.mock import patch, PropertyMock

import test_a44_witness_deployment_floor_writer_policy_protected_root_anchored_backend_contract as previous


class A44AnchoredProtectedRootBackendAdversarialTests(unittest.TestCase):

    def setUp(self):

        self.f = previous.A44AnchoredProtectedRootBackendContractTests(
            "test_01_open_equal_canonical_roots"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.m = self.f.m
        self.local = self.f.local
        self.anchor = self.f.anchor
        self.guard = self.f.guard

        self.identity = self.f.identity
        self.initial = self.f.initial

        self.pending = self.f.objects.pending()

        self.final = self.f.objects.finalized(
            self.pending
        )

        self.path = self.f.f.path

    def advance(self):

        return self.guard.compare_and_set(
            expected=self.initial.reference(),
            replacement=self.pending,
        )

    def recover(self, local_ref, anchor_ref):

        return self.m.AnchoredProtectedRootBackend.recover_local(
            local_backend=self.local,
            anchor_backend=self.anchor,
            expected_identity=self.identity,
            expected_local=local_ref,
            expected_anchor=anchor_ref,
        )

    def prepare_anchor_only(self):

        result = self.anchor.compare_and_set(
            expected=self.initial.reference(),
            replacement=self.pending,
        )

        self.assertEqual(
            result,
            self.pending.reference(),
        )

        self.assertEqual(self.local.read(), self.initial)
        self.assertEqual(self.anchor.read(), self.pending)

    def assert_partial(self, old_bytes):

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        self.assertEqual(
            self.anchor.read(),
            self.pending,
        )

        self.assertEqual(
            self.path.read_bytes(),
            old_bytes,
        )

        self.f.assert_fenced()

    def assert_recovery(self):

        self.assertEqual(
            self.recover(
                self.initial.reference(),
                self.pending.reference(),
            ),
            self.pending.reference(),
        )

        self.f.assert_equal_roots(self.pending)

    def test_01_noncanonical_anchor_receipt_after_commit(self):

        old_bytes = self.path.read_bytes()

        original = type(self.anchor).compare_and_set

        reached = []

        def malformed_receipt(instance, *, expected, replacement):

            receipt = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            reached.append(receipt)

            return object()

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            malformed_receipt,
        ), patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unexpected local CAS"),
        ) as forbidden:

            with self.assertRaises(ValueError):
                self.advance()

            forbidden.assert_not_called()

        self.assertEqual(
            reached,
            [self.pending.reference()],
        )

        self.assert_partial(old_bytes)
        self.assert_recovery()

    def test_02_wrong_anchor_reference_after_actual_commit(self):

        old_bytes = self.path.read_bytes()

        original = type(self.anchor).compare_and_set

        def incorrect_receipt(instance, *, expected, replacement):

            original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            return self.initial.reference()

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            incorrect_receipt,
        ), patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unexpected local CAS"),
        ) as forbidden:

            with self.assertRaises(ValueError):
                self.advance()

            forbidden.assert_not_called()

        self.assert_partial(old_bytes)
        self.assert_recovery()

    def test_03_false_anchor_success_without_commit(self):

        old_bytes = self.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            return_value=self.pending.reference(),
        ) as false_success, patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unexpected local CAS"),
        ) as forbidden:

            with self.assertRaises(ValueError):
                self.advance()

            false_success.assert_called_once()
            forbidden.assert_not_called()

        self.assertEqual(
            self.path.read_bytes(),
            old_bytes,
        )

        self.f.assert_equal_roots(self.initial)

    def test_04_wrong_local_receipt_after_actual_commit(self):

        original = type(self.local).compare_and_set

        reached = []

        def incorrect_receipt(instance, *, expected, replacement):

            receipt = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            reached.append(receipt)

            return self.initial.reference()

        with patch.object(
            type(self.local),
            "compare_and_set",
            incorrect_receipt,
        ):

            with self.assertRaises(ValueError):
                self.advance()

        self.assertEqual(
            reached,
            [self.pending.reference()],
        )

        # Both commits occurred. An incorrect acknowledgement
        # must not cause either committed state to roll back.

        self.f.assert_equal_roots(self.pending)

        before = self.path.read_bytes()

        self.assertEqual(
            self.recover(
                self.pending.reference(),
                self.pending.reference(),
            ),
            self.pending.reference(),
        )

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.f.assert_equal_roots(self.pending)

    def test_05_false_local_success_without_commit(self):

        old_bytes = self.path.read_bytes()

        with patch.object(
            type(self.local),
            "compare_and_set",
            return_value=self.pending.reference(),
        ) as false_success:

            with self.assertRaises(ValueError):
                self.advance()

            false_success.assert_called_once()

        self.assert_partial(old_bytes)
        self.assert_recovery()

    def test_06_noncanonical_anchor_state_rejected(self):

        before = self.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "read",
            return_value=object(),
        ), patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unexpected local CAS"),
        ) as forbidden:

            self.f.assert_fenced()

            forbidden.assert_not_called()

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.f.assert_equal_roots(self.initial)

    def test_07_anchor_identity_drift_rejected(self):

        wrong = replace(
            self.identity,
            provisioning_nonce=b"x" * 32,
        )

        self.assertNotEqual(
            wrong,
            self.identity,
        )

        before = self.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "identity",
            new_callable=PropertyMock,
            return_value=wrong,
        ), patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unexpected local CAS"),
        ) as forbidden:

            self.f.assert_fenced()

            forbidden.assert_not_called()

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.f.assert_equal_roots(self.initial)

    def test_08_invalid_requests_do_not_reach_backend_cas(self):

        before = self.path.read_bytes()

        invalid_requests = (
            ({}, self.pending),
            (self.initial.reference(), {}),
            (self.initial.reference(), self.initial),
            (self.initial.reference(), self.final),
            (self.pending.reference(), self.pending),
        )

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=AssertionError("Unexpected anchor CAS"),
        ) as anchor_cas, patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unexpected local CAS"),
        ) as local_cas:

            for expected, replacement in invalid_requests:

                with self.assertRaises(ValueError):

                    self.guard.compare_and_set(
                        expected=expected,
                        replacement=replacement,
                    )

            anchor_cas.assert_not_called()
            local_cas.assert_not_called()

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.f.assert_equal_roots(self.initial)

    def test_09_anchor_fence_failure_prevents_local_fence(self):

        before = self.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "exclusive",
            side_effect=OSError("Anchor fence unavailable"),
        ) as failed, patch.object(
            type(self.local),
            "exclusive",
            side_effect=AssertionError("Unexpected local fence"),
        ) as forbidden:

            with self.assertRaises(ValueError):
                self.advance()

            failed.assert_called_once()
            forbidden.assert_not_called()

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.f.assert_equal_roots(self.initial)

    def test_10_local_fence_failure_releases_anchor_fence(self):

        original = type(self.anchor).exclusive

        events = []

        @contextmanager
        def observed_fence(instance):

            with original(instance):

                events.append("anchor-entered")

                try:
                    yield

                finally:
                    events.append("anchor-exiting")

            events.append("anchor-released")

        before = self.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "exclusive",
            observed_fence,
        ), patch.object(
            type(self.local),
            "exclusive",
            side_effect=OSError("Local fence unavailable"),
        ) as failed:

            with self.assertRaises(ValueError):
                self.advance()

            failed.assert_called_once()

        self.assertEqual(
            events,
            [
                "anchor-entered",
                "anchor-exiting",
            ],
        )

        # The exception propagated through the real anchor
        # context manager, whose underlying lock must unwind.
        # Verify a separate thread can subsequently acquire it.

        completed = threading.Event()
        results = []

        def competing_reader():

            with self.anchor.exclusive():

                results.append(self.anchor.read())

            completed.set()

        worker = threading.Thread(
            target=competing_reader,
            daemon=True,
        )

        worker.start()

        self.assertTrue(
            completed.wait(timeout=10),
            "Anchor fence remained held after local failure",
        )

        worker.join(timeout=5)

        self.assertFalse(worker.is_alive())

        self.assertEqual(
            results,
            [self.initial],
        )

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.f.assert_equal_roots(self.initial)

    def test_11_outer_anchor_release_failure_after_commit(self):

        original = type(self.anchor).exclusive

        depth = 0
        reached = []

        @contextmanager
        def lose_release_ack(instance):

            nonlocal depth

            depth += 1

            outermost = depth == 1

            try:

                with original(instance):

                    yield

                if outermost:

                    reached.append("released")

                    raise OSError(
                        "Anchor release acknowledgement lost"
                    )

            finally:

                depth -= 1

        with patch.object(
            type(self.anchor),
            "exclusive",
            lose_release_ack,
        ):

            with self.assertRaises(ValueError):
                self.advance()

        self.assertEqual(depth, 0)
        self.assertEqual(reached, ["released"])

        # The CAS was committed before the release failure.

        self.f.assert_equal_roots(self.pending)

        self.assertEqual(
            self.recover(
                self.pending.reference(),
                self.pending.reference(),
            ),
            self.pending.reference(),
        )

        self.f.assert_equal_roots(self.pending)

    def test_12_caller_exception_cannot_be_suppressed_by_local_fence(self):

        original = type(self.local).exclusive

        suppressed = []

        @contextmanager
        def suppressing_fence(instance):

            with original(instance):

                try:

                    yield

                except OSError as exc:

                    suppressed.append(str(exc))

        with patch.object(
            type(self.local),
            "exclusive",
            suppressing_fence,
        ):

            with self.assertRaisesRegex(
                OSError,
                "Protected caller failed",
            ):

                with self.guard.exclusive():

                    raise OSError(
                        "Protected caller failed"
                    )

        self.assertEqual(
            suppressed,
            ["Protected caller failed"],
        )

        self.f.assert_equal_roots(self.initial)

    def test_13_independent_sqlite_handles_cannot_alias_same_storage(self):

        alias = type(self.local).open(
            path=self.path,
            expected_identity=self.identity,
        )

        self.assertIsNot(
            alias,
            self.local,
        )

        before = self.path.read_bytes()

        with self.assertRaises(ValueError):

            self.f.open_guard(
                anchor_backend=alias,
            )

        with self.assertRaises(ValueError):

            self.m.AnchoredProtectedRootBackend.recover_local(
                local_backend=self.local,
                anchor_backend=alias,
                expected_identity=self.identity,
                expected_local=self.initial.reference(),
                expected_anchor=self.initial.reference(),
            )

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.f.assert_equal_roots(self.initial)

    def test_14_nested_anchored_backends_rejected(self):

        before = self.path.read_bytes()

        with self.assertRaises(ValueError):

            self.f.open_guard(
                anchor_backend=self.guard,
            )

        with self.assertRaises(ValueError):

            self.f.open_guard(
                local_backend=self.guard,
            )

        with self.assertRaises(ValueError):

            self.m.AnchoredProtectedRootBackend.recover_local(
                local_backend=self.guard,
                anchor_backend=self.anchor,
                expected_identity=self.identity,
                expected_local=self.initial.reference(),
                expected_anchor=self.initial.reference(),
            )

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.f.assert_equal_roots(self.initial)

    def test_15_concurrent_recovery_commits_exactly_once(self):

        self.prepare_anchor_only()

        local_ref = self.initial.reference()
        anchor_ref = self.pending.reference()

        start = threading.Barrier(2)

        original = type(self.local).compare_and_set

        committed = []

        def counted_cas(instance, *, expected, replacement):

            result = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            committed.append(result)

            return result

        def competing_recovery():

            start.wait(timeout=10)

            try:

                result = self.recover(
                    local_ref,
                    anchor_ref,
                )

            except ValueError:

                return ("stale", None)

            return ("committed", result)

        with patch.object(
            type(self.local),
            "compare_and_set",
            counted_cas,
        ), patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=AssertionError("Recovery wrote anchor"),
        ) as forbidden:

            with ThreadPoolExecutor(max_workers=2) as pool:

                first = pool.submit(
                    competing_recovery
                )

                second = pool.submit(
                    competing_recovery
                )

                results = [
                    first.result(timeout=30),
                    second.result(timeout=30),
                ]

            forbidden.assert_not_called()

        self.assertCountEqual(
            results,
            [
                ("committed", anchor_ref),
                ("stale", None),
            ],
        )

        self.assertEqual(
            committed,
            [anchor_ref],
        )

        self.f.assert_equal_roots(self.pending)

        self.assertEqual(
            self.recover(
                anchor_ref,
                anchor_ref,
            ),
            anchor_ref,
        )

        self.f.assert_equal_roots(self.pending)

    def test_16_false_recovery_success_without_local_commit(self):

        self.prepare_anchor_only()

        before = self.path.read_bytes()

        with patch.object(
            type(self.local),
            "compare_and_set",
            return_value=self.pending.reference(),
        ) as false_success, patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=AssertionError("Recovery wrote anchor"),
        ) as forbidden:

            with self.assertRaises(ValueError):

                self.recover(
                    self.initial.reference(),
                    self.pending.reference(),
                )

            false_success.assert_called_once()
            forbidden.assert_not_called()

        self.assert_partial(before)

        self.assert_recovery()


if __name__ == "__main__":
    unittest.main()
