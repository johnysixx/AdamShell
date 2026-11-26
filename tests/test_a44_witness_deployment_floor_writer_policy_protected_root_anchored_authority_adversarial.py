"""Anchored authority publication and recovery adversarial tests.

Exercise failures on both sides of each of the five publication
commit boundaries.

The local databases and writer credentials belong exclusively
to temporary test fixtures.

The anchor is a separately retained in-memory test double.

These are controlled exception and acknowledgement-loss tests,
not physical power-loss or independent hardware durability tests.
"""

import unittest

from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_anchored_authority_contract as previous


class A44AnchoredProtectedRootAuthorityAdversarialTests(unittest.TestCase):

    def setUp(self):

        self.f = previous.A44AnchoredProtectedRootAuthorityContractTests(
            "test_01_publication_and_revocation_use_both_roots"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.m = self.f.m
        self.base = self.f.base

        self.local = self.f.local
        self.anchor = self.f.anchor
        self.guard = self.f.guard

        self.authority = self.f.authority
        self.gateway = self.f.gateway

        self.identity = self.f.identity
        self.initial = self.f.initial

        self.genesis = self.f.genesis
        self.candidate = self.f.candidate

        self.d = self.f.d
        self.s = self.f.s
        self.p = self.f.p

        self.path = self.f.f.path

    def assert_state(self, state, revision):

        self.assertIs(
            type(state),
            self.m.ProtectedDurableRootState,
        )

        self.assertEqual(
            state.identity,
            self.identity,
        )

        self.assertEqual(
            state.revision,
            revision,
        )

        if revision == 1:

            self.assertEqual(
                state,
                self.initial,
            )

        elif revision == 2:

            self.assertEqual(
                state.durable_state.anchor,
                self.initial.durable_state.anchor,
            )

            prepared = state.durable_state.prepared

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

        elif revision == 3:

            self.assertIsNone(
                state.durable_state.prepared,
            )

            self.assertEqual(
                state.durable_state.anchor,
                self.d.ref(self.candidate, 2),
            )

        else:

            self.fail("Unexpected root revision")

    def assert_boundary(
        self,
        *,
        local_revision,
        anchor_revision,
        policy_epoch,
    ):

        local = self.local.read()
        anchor = self.anchor.read()

        self.assert_state(
            local,
            local_revision,
        )

        self.assert_state(
            anchor,
            anchor_revision,
        )

        self.assertEqual(
            self.f.f.open_root().read(),
            local,
        )

        if policy_epoch == 1:

            self.s.assert_history(
                self.genesis,
            )

        elif policy_epoch == 2:

            self.s.assert_history(
                self.genesis,
                self.candidate,
            )

        else:

            self.fail("Unexpected policy epoch")

        self.d.assert_floor(1, 0)

        return local, anchor

    def inject_root_failure(
        self,
        *,
        target,
        revision,
        after_commit,
    ):

        original = type(target).compare_and_set

        reached = []
        committed = []

        def injected(instance, *, expected, replacement):

            if (
                instance is target
                and replacement.revision == revision
            ):

                reached.append(
                    replacement.reference()
                )

                self.assertEqual(
                    expected.revision,
                    revision - 1,
                )

                if not after_commit:

                    raise OSError(
                        "Injected precommit root failure"
                    )

                result = original(
                    instance,
                    expected=expected,
                    replacement=replacement,
                )

                committed.append(result)

                raise OSError(
                    "Injected postcommit acknowledgement loss"
                )

            return original(
                instance,
                expected=expected,
                replacement=replacement,
            )

        with patch.object(
            type(target),
            "compare_and_set",
            injected,
        ):

            with self.assertRaises(ValueError):

                self.authority.publish_policy(
                    signed_policy=self.candidate,
                )

        self.assertEqual(
            len(reached),
            1,
            "Exact root failure boundary not reached",
        )

        self.assertEqual(
            committed,
            reached if after_commit else [],
        )

    def assert_interrupted_authorization(
        self,
        local,
        anchor,
    ):

        before_root = self.path.read_bytes()
        before_policy = self.s.path.read_bytes()

        if local != anchor:

            self.f.assert_authority_blocked()

            with self.assertRaises(ValueError):

                self.guard.read()

        elif anchor.revision == 2:

            with self.assertRaises(ValueError):

                self.authority.current_policy_reference()

            with self.assertRaises(ValueError):

                self.authority.retired_writer_keys()

            self.base.blocked(
                signed_policy=self.genesis,
                gateway=self.gateway,
            )

        elif anchor.revision == 1:

            # Publication never committed any root change.
            # The original policy remains valid.

            self.assertEqual(
                self.authority.current_policy_reference(),
                self.d.pair(self.genesis, 1),
            )

        elif anchor.revision == 3:

            # Both final commits already happened.
            # Losing an acknowledgement cannot undo revocation.

            self.assertEqual(
                self.authority.current_policy_reference(),
                self.d.pair(self.candidate, 2),
            )

            self.base.blocked(
                signed_policy=self.candidate,
                gateway=self.gateway,
            )

        else:

            self.fail("Unexpected authorization state")

        self.assertEqual(
            self.anchor.read(),
            anchor,
        )

        self.assertEqual(
            self.local.read(),
            local,
        )

        self.assertEqual(
            self.path.read_bytes(),
            before_root,
        )

        self.assertEqual(
            self.s.path.read_bytes(),
            before_policy,
        )

        self.d.assert_floor(1, 0)

    def reconcile_roots(self):

        # References here are obtained directly from trusted
        # test fixtures, not from a production discovery API.

        local = self.local.read()
        anchor = self.anchor.read()

        reopened_local = self.f.f.open_root()

        self.assertIsNot(
            reopened_local,
            self.local,
        )

        with patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=AssertionError(
                "Explicit root recovery wrote anchor"
            ),
        ) as forbidden:

            result = (
                self.m.AnchoredProtectedRootBackend.recover_local(
                    local_backend=reopened_local,
                    anchor_backend=self.anchor,
                    expected_identity=self.identity,
                    expected_local=local.reference(),
                    expected_anchor=anchor.reference(),
                )
            )

            forbidden.assert_not_called()

        self.assertEqual(
            result,
            anchor.reference(),
        )

        self.assertEqual(
            self.anchor.read(),
            anchor,
        )

        self.assertEqual(
            reopened_local.read(),
            anchor,
        )

        self.assertEqual(
            self.local.read(),
            anchor,
        )

        self.assertEqual(
            self.guard.read(),
            anchor,
        )

        before = self.path.read_bytes()

        with patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError(
                "Idempotent recovery wrote local root"
            ),
        ) as local_cas, patch.object(
            type(self.anchor),
            "compare_and_set",
            side_effect=AssertionError(
                "Idempotent recovery wrote anchor"
            ),
        ) as anchor_cas:

            self.assertEqual(
                self.m.AnchoredProtectedRootBackend.recover_local(
                    local_backend=reopened_local,
                    anchor_backend=self.anchor,
                    expected_identity=self.identity,
                    expected_local=anchor.reference(),
                    expected_anchor=anchor.reference(),
                ),
                anchor.reference(),
            )

            local_cas.assert_not_called()
            anchor_cas.assert_not_called()

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        return anchor

    def finish_publication(self):

        synchronized = self.reconcile_roots()

        fresh = self.f.reopen()

        self.assertEqual(
            fresh.root_state(),
            synchronized,
        )

        if synchronized.revision == 1:

            # No publication committed. Explicit retry is
            # necessary; recovery must not invent a candidate.

            self.assertEqual(
                fresh.recover_publication(),
                self.d.pair(self.genesis, 1),
            )

            self.assertEqual(
                fresh.publish_policy(
                    signed_policy=self.candidate,
                ),
                self.d.pair(self.candidate, 2),
            )

        elif synchronized.revision == 2:

            with self.assertRaises(ValueError):

                fresh.current_policy_reference()

            self.base.blocked(
                signed_policy=self.genesis,
                gateway=self.base.make_gateway(fresh),
            )

            self.assertEqual(
                fresh.recover_publication(),
                self.d.pair(self.candidate, 2),
            )

        elif synchronized.revision == 3:

            self.assertEqual(
                fresh.recover_publication(),
                self.d.pair(self.candidate, 2),
            )

        else:

            self.fail("Unexpected synchronized revision")

        finalized = self.anchor.read()

        self.assert_state(
            finalized,
            3,
        )

        self.assertEqual(
            self.local.read(),
            finalized,
        )

        self.assertEqual(
            fresh.root_state(),
            finalized,
        )

        self.f.assert_equal_roots(
            finalized,
        )

        self.s.assert_history(
            self.genesis,
            self.candidate,
        )

        self.d.assert_floor(1, 0)

        before_root = self.path.read_bytes()
        before_policy = self.s.path.read_bytes()

        reopened = self.f.reopen()

        for _ in range(2):

            self.assertEqual(
                reopened.recover_publication(),
                self.d.pair(self.candidate, 2),
            )

            self.assertEqual(
                reopened.root_state(),
                finalized,
            )

        self.assertEqual(
            self.path.read_bytes(),
            before_root,
        )

        self.assertEqual(
            self.s.path.read_bytes(),
            before_policy,
        )

        self.assertEqual(
            self.anchor.read(),
            finalized,
        )

        gateway = self.base.make_gateway(
            reopened,
        )

        # Both an obsolete policy and the current revocation
        # must reject the retired writer.

        self.base.blocked(
            signed_policy=self.genesis,
            gateway=gateway,
        )

        self.base.blocked(
            signed_policy=self.candidate,
            gateway=gateway,
        )

        self.d.assert_floor(1, 0)

        # A remaining authorized writer is still operational.

        response = self.base.send(
            self.candidate,
            gateway=gateway,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.d.assert_committed(
            response,
            2,
        )

        self.d.assert_floor(2, 1)

        self.f.assert_equal_roots(
            finalized,
        )

        self.s.assert_history(
            self.genesis,
            self.candidate,
        )

    def run_root_boundary(
        self,
        *,
        target,
        revision,
        after_commit,
        local_revision,
        anchor_revision,
        policy_epoch,
    ):

        self.inject_root_failure(
            target=target,
            revision=revision,
            after_commit=after_commit,
        )

        local, anchor = self.assert_boundary(
            local_revision=local_revision,
            anchor_revision=anchor_revision,
            policy_epoch=policy_epoch,
        )

        self.assert_interrupted_authorization(
            local,
            anchor,
        )

        self.finish_publication()

    def test_01_before_anchor_prepare_commit(self):

        self.run_root_boundary(
            target=self.anchor,
            revision=2,
            after_commit=False,
            local_revision=1,
            anchor_revision=1,
            policy_epoch=1,
        )

    def test_02_after_anchor_prepare_commit(self):

        self.run_root_boundary(
            target=self.anchor,
            revision=2,
            after_commit=True,
            local_revision=1,
            anchor_revision=2,
            policy_epoch=1,
        )

    def test_03_before_local_prepare_commit(self):

        self.run_root_boundary(
            target=self.local,
            revision=2,
            after_commit=False,
            local_revision=1,
            anchor_revision=2,
            policy_epoch=1,
        )

    def test_04_after_local_prepare_commit(self):

        self.run_root_boundary(
            target=self.local,
            revision=2,
            after_commit=True,
            local_revision=2,
            anchor_revision=2,
            policy_epoch=1,
        )

    def test_05_before_policy_commit(self):

        prepared = self.base.fail_publication(
            self.candidate,
            after_commit=False,
        )

        local, anchor = self.assert_boundary(
            local_revision=2,
            anchor_revision=2,
            policy_epoch=1,
        )

        self.assertEqual(
            local,
            prepared,
        )

        self.assertEqual(
            anchor,
            prepared,
        )

        self.assert_interrupted_authorization(
            local,
            anchor,
        )

        self.finish_publication()

    def test_06_after_policy_commit(self):

        prepared = self.base.fail_publication(
            self.candidate,
            after_commit=True,
        )

        local, anchor = self.assert_boundary(
            local_revision=2,
            anchor_revision=2,
            policy_epoch=2,
        )

        self.assertEqual(
            local,
            prepared,
        )

        self.assertEqual(
            anchor,
            prepared,
        )

        self.assert_interrupted_authorization(
            local,
            anchor,
        )

        self.finish_publication()

    def test_07_before_anchor_finalize_commit(self):

        self.run_root_boundary(
            target=self.anchor,
            revision=3,
            after_commit=False,
            local_revision=2,
            anchor_revision=2,
            policy_epoch=2,
        )

    def test_08_after_anchor_finalize_commit(self):

        self.run_root_boundary(
            target=self.anchor,
            revision=3,
            after_commit=True,
            local_revision=2,
            anchor_revision=3,
            policy_epoch=2,
        )

    def test_09_before_local_finalize_commit(self):

        self.run_root_boundary(
            target=self.local,
            revision=3,
            after_commit=False,
            local_revision=2,
            anchor_revision=3,
            policy_epoch=2,
        )

    def test_10_after_local_finalize_commit(self):

        self.run_root_boundary(
            target=self.local,
            revision=3,
            after_commit=True,
            local_revision=3,
            anchor_revision=3,
            policy_epoch=2,
        )

    def test_11_final_anchor_recovery_cannot_accept_policy_rollback(self):

        old_policy = self.d.snapshot(
            "anchored-old-policy.sqlite3"
        )

        self.inject_root_failure(
            target=self.anchor,
            revision=3,
            after_commit=True,
        )

        local, anchor = self.assert_boundary(
            local_revision=2,
            anchor_revision=3,
            policy_epoch=2,
        )

        self.assert_interrupted_authorization(
            local,
            anchor,
        )

        current_policy = self.d.snapshot(
            "anchored-current-policy.sqlite3"
        )

        self.d.restore(old_policy)

        self.s.assert_history(
            self.genesis,
        )

        self.f.assert_authority_blocked()

        retained = self.reconcile_roots()

        self.assertEqual(
            retained,
            anchor,
        )

        self.assert_state(
            retained,
            3,
        )

        # Root reconciliation alone cannot recreate a missing
        # finalized policy or authorize obsolete history.

        self.f.assert_authority_blocked()

        self.assertEqual(
            self.anchor.read(),
            retained,
        )

        self.assertEqual(
            self.local.read(),
            retained,
        )

        self.s.assert_history(
            self.genesis,
        )

        self.d.assert_floor(1, 0)

        # Restore the independently retained authenticated
        # current history, never a downgraded root.

        self.d.restore(current_policy)

        self.finish_publication()

    def test_12_prepared_anchor_rejects_conflicting_signed_history(self):

        old_policy = self.d.snapshot(
            "anchored-conflict-predecessor.sqlite3"
        )

        self.inject_root_failure(
            target=self.anchor,
            revision=2,
            after_commit=True,
        )

        local, anchor = self.assert_boundary(
            local_revision=1,
            anchor_revision=2,
            policy_epoch=1,
        )

        self.assert_interrupted_authorization(
            local,
            anchor,
        )

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.assertNotEqual(
            alternative,
            self.candidate,
        )

        self.d.h.publish_external(
            alternative,
        )

        self.s.assert_history(
            self.genesis,
            alternative,
        )

        retained = self.reconcile_roots()

        self.assertEqual(
            retained,
            anchor,
        )

        self.assert_state(
            retained,
            2,
        )

        before_root = self.path.read_bytes()
        before_policy = self.s.path.read_bytes()

        fresh = self.f.reopen()

        with self.assertRaises(ValueError):

            fresh.recover_publication()

        self.base.blocked(
            signed_policy=alternative,
            gateway=self.base.make_gateway(fresh),
        )

        with self.assertRaises(ValueError):

            fresh.publish_policy(
                signed_policy=alternative,
            )

        self.assertEqual(
            self.anchor.read(),
            retained,
        )

        self.assertEqual(
            self.local.read(),
            retained,
        )

        self.assertEqual(
            self.path.read_bytes(),
            before_root,
        )

        self.assertEqual(
            self.s.path.read_bytes(),
            before_policy,
        )

        self.d.assert_floor(1, 0)

        self.s.assert_history(
            self.genesis,
            alternative,
        )

        # Restore the authenticated predecessor, then recover
        # only the exact candidate already retained by anchor.

        self.d.restore(
            old_policy,
        )

        self.finish_publication()


if __name__ == "__main__":
    unittest.main()
