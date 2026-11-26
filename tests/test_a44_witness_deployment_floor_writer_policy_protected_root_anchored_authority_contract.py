"""Independent root anchor integration contract.

All databases belong to temporary test fixtures.

The isolated in-memory anchor models a separately trusted
authoritative backend. It is not a production hardware anchor.
"""

import importlib
import unittest

from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_sqlite_authority_contract as previous


MODULE = "core.existence.history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_anchored_backend"


class A44AnchoredProtectedRootAuthorityContractTests(unittest.TestCase):

    def setUp(self):

        self.m = importlib.import_module(MODULE)

        self.f = previous.A44SQLiteProtectedRootAuthorityContractTests(
            "test_01_existing_authority_bootstrap_and_fresh_root_open"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.base = self.f.f

        self.d = self.f.d
        self.p = self.f.p
        self.s = self.f.s

        self.identity = self.f.identity
        self.genesis = self.f.genesis
        self.candidate = self.base.candidate()

        self.local = self.f.root
        self.initial = self.local.read()

        self.anchor = self.base.new_root()

        self.anchor.provision(state=self.initial)

        self.guard = self.open_guard()

        self.authority = self.base.reopen(
            root_backend=self.guard,
        )

        self.gateway = self.base.make_gateway(
            self.authority,
        )

        self.base.root = self.guard
        self.base.authority = self.authority
        self.base.gateway = self.gateway

        self.assert_equal_roots(self.initial)

    def open_guard(self, local=None):

        if local is None:
            local = self.local

        return self.m.AnchoredProtectedRootBackend.open(
            local_backend=local,
            anchor_backend=self.anchor,
            expected_identity=self.identity,
        )

    def reopen(self):

        return self.base.reopen(
            root_backend=self.open_guard(
                self.f.open_root(),
            ),
        )

    def assert_equal_roots(self, expected):

        self.assertEqual(self.anchor.read(), expected)
        self.assertEqual(self.local.read(), expected)
        self.assertEqual(self.guard.read(), expected)

        self.assertEqual(
            self.authority.root_state(),
            expected,
        )

    def publish(self):

        self.assertEqual(
            self.authority.publish_policy(
                signed_policy=self.candidate,
            ),
            self.d.pair(self.candidate, 2),
        )

        finalized = self.base.stable(
            self.candidate,
            2,
            3,
        )

        self.assert_equal_roots(finalized)

        self.s.assert_history(
            self.genesis,
            self.candidate,
        )

        return finalized

    def assert_authority_blocked(self):

        with self.assertRaises(ValueError):
            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):
            self.authority.retired_writer_keys()

        with self.assertRaises(ValueError):
            self.authority.recover_publication()

        with self.assertRaises(ValueError):
            self.reopen()

        self.base.blocked(
            signed_policy=self.genesis,
            gateway=self.gateway,
        )

        self.d.assert_floor(1, 0)

    def assert_local_rollback_rejected(self, *, policy, fence):

        old_root = self.f.path.read_bytes()
        old_fence = self.f.fence_path.read_bytes()
        old_policy = self.d.snapshot()

        finalized = self.publish()

        if policy:
            self.d.restore(old_policy)

        self.f.path.write_bytes(old_root)

        if fence:
            self.f.fence_path.write_bytes(old_fence)

        self.assertEqual(
            self.f.open_root().read(),
            self.initial,
        )

        self.assertEqual(
            self.anchor.read(),
            finalized,
        )

        before_policy = self.s.path.read_bytes()
        before_fence = self.f.fence_path.read_bytes()

        self.assert_authority_blocked()

        self.assertEqual(
            self.anchor.read(),
            finalized,
        )

        self.assertEqual(
            self.f.path.read_bytes(),
            old_root,
        )

        self.assertEqual(
            self.f.fence_path.read_bytes(),
            before_fence,
        )

        self.assertEqual(
            self.s.path.read_bytes(),
            before_policy,
        )

    def test_01_publication_and_revocation_use_both_roots(self):

        finalized = self.publish()

        fresh = self.reopen()

        self.assertEqual(
            fresh.root_state(),
            finalized,
        )

        self.base.blocked(
            signed_policy=self.candidate,
            gateway=self.base.make_gateway(fresh),
        )

        self.d.assert_floor(1, 0)

        response = self.base.send(
            self.candidate,
            gateway=self.base.make_gateway(fresh),
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.d.assert_committed(response, 2)

        self.d.assert_floor(2, 1)

        self.assert_equal_roots(finalized)

    def test_02_root_only_rollback_cannot_be_silently_observed(self):

        self.assert_local_rollback_rejected(
            policy=False,
            fence=False,
        )

    def test_03_root_and_policy_rollback_cannot_restore_revocation(self):

        self.assert_local_rollback_rejected(
            policy=True,
            fence=False,
        )

    def test_04_complete_local_pair_rollback_cannot_restore_revocation(self):

        self.assert_local_rollback_rejected(
            policy=True,
            fence=True,
        )

    def test_05_anchor_unavailability_blocks_writer_authority(self):

        before_root = self.f.path.read_bytes()
        before_policy = self.s.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "read",
            side_effect=OSError("Independent anchor unavailable"),
        ):

            self.assert_authority_blocked()

            with self.assertRaises(ValueError):

                self.authority.publish_policy(
                    signed_policy=self.candidate,
                )

        self.assertEqual(
            self.f.path.read_bytes(),
            before_root,
        )

        self.assertEqual(
            self.s.path.read_bytes(),
            before_policy,
        )

        self.assert_equal_roots(self.initial)

    def test_06_failed_anchor_cas_cannot_publish_policy(self):

        before_root = self.f.path.read_bytes()
        before_policy = self.s.path.read_bytes()

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=OSError("Independent anchor CAS failed"),
        ) as failure:

            with self.assertRaises(ValueError):

                self.authority.publish_policy(
                    signed_policy=self.candidate,
                )

            failure.assert_called_once()

        self.assertEqual(
            self.f.path.read_bytes(),
            before_root,
        )

        self.assertEqual(
            self.s.path.read_bytes(),
            before_policy,
        )

        self.assert_equal_roots(self.initial)
        self.s.assert_history(self.genesis)
        self.d.assert_floor(1, 0)

    def test_07_local_cas_failure_retains_independent_prepared_state(self):

        before_root = self.f.path.read_bytes()

        with patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=OSError("Local root CAS failed"),
        ) as failure:

            with self.assertRaises(ValueError):

                self.authority.publish_policy(
                    signed_policy=self.candidate,
                )

            failure.assert_called_once()

        retained = self.anchor.read()

        self.assertEqual(retained.revision, 2)

        prepared = retained.durable_state.prepared

        self.assertIsNotNone(prepared)

        self.assertEqual(
            prepared.predecessor,
            self.initial.durable_state.anchor,
        )

        self.assertEqual(
            prepared.candidate,
            self.d.ref(self.candidate, 2),
        )

        self.assertEqual(
            prepared.signed_policy,
            self.candidate,
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        self.assertEqual(
            self.f.path.read_bytes(),
            before_root,
        )

        self.s.assert_history(self.genesis)

        self.assert_authority_blocked()

        self.assertEqual(self.anchor.read(), retained)
        self.assertEqual(self.local.read(), self.initial)

    def test_08_policy_recovery_preserves_exact_anchor_and_local_state(self):

        pending = self.base.fail_publication(
            self.candidate,
            after_commit=False,
        )

        self.assertEqual(pending.revision, 2)

        self.assert_equal_roots(pending)

        self.s.assert_history(self.genesis)

        fresh = self.reopen()

        self.assertEqual(fresh.root_state(), pending)

        self.base.blocked(
            gateway=self.base.make_gateway(fresh),
        )

        self.assertEqual(
            fresh.recover_publication(),
            self.d.pair(self.candidate, 2),
        )

        finalized = self.base.stable(
            self.candidate,
            2,
            3,
        )

        self.assert_equal_roots(finalized)

        reopened = self.reopen()

        self.assertEqual(
            reopened.recover_publication(),
            self.d.pair(self.candidate, 2),
        )

        self.assertEqual(
            reopened.root_state(),
            finalized,
        )

        self.assert_equal_roots(finalized)

        self.s.assert_history(
            self.genesis,
            self.candidate,
        )

        self.base.blocked(
            signed_policy=self.candidate,
            gateway=self.base.make_gateway(reopened),
        )

        self.d.assert_floor(1, 0)


if __name__ == "__main__":
    unittest.main()
