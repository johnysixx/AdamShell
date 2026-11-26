"""Independent protected root anchor contract.

The in-memory anchor is an isolated test double.
It is not a production rollback-resistant storage provider.

All local storage operations use temporary fixture databases.
"""

import importlib
import unittest

from dataclasses import replace
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_sqlite_contract as previous


MODULE = "core.existence.history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_anchored_backend"


class A44AnchoredProtectedRootBackendContractTests(unittest.TestCase):

    def setUp(self):

        self.m = importlib.import_module(MODULE)

        self.f = previous.A44SQLiteProtectedRootContractTests(
            "test_01_explicit_create_and_unprovisioned_open"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.local = self.f.backend
        self.objects = self.f.f
        self.anchor = self.objects.backend
        self.identity = self.f.identity
        self.initial = self.f.initial

        self.assertIsNot(self.local, self.anchor)

        self.f.provision()
        self.anchor.provision(state=self.initial)

        self.guard = self.open_guard()

    def open_guard(self, **changes):

        params = {
            "local_backend": self.local,
            "anchor_backend": self.anchor,
            "expected_identity": self.identity,
        }

        params.update(changes)

        return self.m.AnchoredProtectedRootBackend.open(
            **params
        )

    def advance(self, previous, replacement, backend=None):

        if backend is None:
            backend = self.guard

        result = backend.compare_and_set(
            expected=previous.reference(),
            replacement=replacement,
        )

        self.assertEqual(
            result,
            replacement.reference(),
        )

        return result

    def assert_equal_roots(self, expected):

        self.assertEqual(self.local.read(), expected)
        self.assertEqual(self.anchor.read(), expected)
        self.assertEqual(self.guard.read(), expected)
        self.assertEqual(self.open_guard().read(), expected)

    def assert_fenced(self):

        with self.assertRaises(ValueError):
            self.guard.read()

        with self.assertRaises(ValueError):
            self.open_guard()

        with self.assertRaises(ValueError):
            with self.guard.exclusive():
                self.fail("Inconsistent protected root entered fence")

        with self.assertRaises(ValueError):

            self.guard.compare_and_set(
                expected=self.initial.reference(),
                replacement=self.objects.pending(),
            )

    def test_01_open_equal_canonical_roots(self):

        self.assertEqual(
            self.guard.identity,
            self.identity,
        )

        self.assert_equal_roots(self.initial)

        self.assertIsNot(
            self.guard.read(),
            self.local.read(),
        )

    def test_02_monotonic_compare_and_set_both_roots(self):

        pending = self.objects.pending()
        final = self.objects.finalized(pending)

        self.advance(self.initial, pending)
        self.assert_equal_roots(pending)

        self.advance(pending, final)
        self.assert_equal_roots(final)

        self.assertEqual(final.revision, 3)

    def test_03_stale_reference_cannot_mutate_either_root(self):

        pending = self.objects.pending()

        self.advance(self.initial, pending)

        before = self.f.path.read_bytes()

        with self.assertRaises(ValueError):

            self.guard.compare_and_set(
                expected=self.initial.reference(),
                replacement=self.objects.finalized(pending),
            )

        self.assert_equal_roots(pending)

        self.assertEqual(
            self.f.path.read_bytes(),
            before,
        )

    def test_04_local_root_rollback_rejected(self):

        old = self.f.path.read_bytes()

        pending = self.objects.pending()
        final = self.objects.finalized(pending)

        self.advance(self.initial, pending)
        self.advance(pending, final)

        self.f.path.write_bytes(old)

        self.assertEqual(self.local.read(), self.initial)
        self.assertEqual(self.anchor.read(), final)

        self.assert_fenced()

        self.assertEqual(self.anchor.read(), final)
        self.assertEqual(self.f.path.read_bytes(), old)

    def test_05_same_revision_different_digest_rejected(self):

        first = self.objects.pending()

        second = self.objects.pending(
            self.objects.prepared(message=b"conflicting-candidate")
        )

        self.advance(self.initial, first, self.local)
        self.advance(self.initial, second, self.anchor)

        self.assertEqual(first.revision, second.revision)

        self.assertNotEqual(
            first.reference(),
            second.reference(),
        )

        self.assert_fenced()

        self.assertEqual(self.local.read(), first)
        self.assertEqual(self.anchor.read(), second)

    def test_06_unavailable_anchor_fails_closed(self):

        before = self.f.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "read",
            side_effect=OSError("Anchor unavailable"),
        ):

            self.assert_fenced()

        self.assertEqual(self.f.path.read_bytes(), before)
        self.assert_equal_roots(self.initial)

    def test_07_failed_anchor_cas_never_mutates_local_root(self):

        pending = self.objects.pending()

        before = self.f.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=OSError("Anchor CAS failed"),
        ) as failed:

            with self.assertRaises(ValueError):

                self.guard.compare_and_set(
                    expected=self.initial.reference(),
                    replacement=pending,
                )

            failed.assert_called_once()

        self.assertEqual(self.f.path.read_bytes(), before)
        self.assert_equal_roots(self.initial)

    def test_08_failed_local_cas_retains_authoritative_advance(self):

        pending = self.objects.pending()

        with patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=OSError("Local CAS failed"),
        ) as failed:

            with self.assertRaises(ValueError):

                self.guard.compare_and_set(
                    expected=self.initial.reference(),
                    replacement=pending,
                )

            failed.assert_called_once()

        self.assertEqual(self.anchor.read(), pending)
        self.assertEqual(self.local.read(), self.initial)

        self.assert_fenced()

        self.assertEqual(self.anchor.read(), pending)
        self.assertEqual(self.local.read(), self.initial)

    def test_09_same_backend_and_wrong_identity_rejected(self):

        with self.assertRaises(ValueError):

            self.open_guard(anchor_backend=self.local)

        wrong = replace(
            self.identity,
            provisioning_nonce=b"x" * 32,
        )

        self.assertNotEqual(wrong, self.identity)

        with self.assertRaises(ValueError):

            self.open_guard(expected_identity=wrong)

        self.assert_equal_roots(self.initial)

    def test_10_no_implicit_provisioning(self):

        path = self.f.directory / "unprovisioned-local.sqlite3"

        unprovisioned = self.f.create(path=path)

        before = path.read_bytes()

        with self.assertRaises(ValueError):

            self.open_guard(local_backend=unprovisioned)

        self.assertEqual(path.read_bytes(), before)

        with self.assertRaises(ValueError):

            unprovisioned.read()

        with self.assertRaises(ValueError):

            self.guard.provision(state=self.initial)

        self.assert_equal_roots(self.initial)


if __name__ == "__main__":
    unittest.main()
