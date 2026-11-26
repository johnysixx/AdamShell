"""Persistent protected root integration with existing authority.

The existing protected authority must work without production
changes when supplied with a SQLiteProtectedRootBackend.

Fresh backend instances retain canonical root state, exact
prepared publications and authenticated policy observations.

The root fence spans the existing policy and floor operations.

Local policy history remains replaceable and therefore must
never override the independently retained protected root.

This contract assumes trusted persistent root and fence stores.
It does not claim resistance to replacement of that trusted pair.
"""

import importlib
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authority_contract as previous


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_sqlite_reference"
)


class A44SQLiteProtectedRootAuthorityContractTests(unittest.TestCase):

    def setUp(self):

        self.m = importlib.import_module(MODULE)

        self.f = previous.A44ProtectedRootAuthorityContractTests(
            "test_01_explicit_bootstrap_and_open"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.d = self.f.d
        self.p = self.f.p
        self.s = self.f.s
        self.identity = self.f.identity
        self.genesis = self.f.genesis

        self.root_type = self.m.SQLiteProtectedRootBackend

        self.path = (
            self.s.directory / "sqlite-protected-root.sqlite3"
        )

        self.fence_path = self.path.with_name(
            self.path.name + ".fence.sqlite3"
        )

        # Replace only the fixture's reference backend.
        # The existing production authority remains unchanged.

        self.root = self.create_root()

        self.f.root = self.root
        self.f.authority = self.f.bootstrap()
        self.f.gateway = self.f.make_gateway()

        self.authority = self.f.authority
        self.gateway = self.f.gateway

    def create_root(self, path=None):

        if path is None:
            path = self.path

        return self.root_type.create(
            path=path,
            expected_identity=self.identity,
        )

    def open_root(self, path=None):

        if path is None:
            path = self.path

        return self.root_type.open(
            path=path,
            expected_identity=self.identity,
        )

    def reopen(self, **changes):

        params = {
            "root_backend": self.open_root(),
        }

        params.update(changes)

        return self.f.reopen(**params)

    def stable(self, signed_policy, epoch, revision):

        retained = self.f.stable(
            signed_policy,
            epoch,
            revision,
        )

        self.assertEqual(
            self.open_root().read(),
            retained,
        )

        return retained

    def pending(self, candidate):

        retained = self.f.pending(candidate)

        self.assertEqual(
            self.open_root().read(),
            retained,
        )

        return retained

    def test_01_existing_authority_bootstrap_and_fresh_root_open(self):

        retained = self.stable(self.genesis, 1, 1)

        reopened_root = self.open_root()

        self.assertIsNot(reopened_root, self.root)

        fresh = self.f.reopen(
            root_backend=reopened_root,
        )

        self.assertEqual(fresh.root_state(), retained)

        self.assertEqual(
            fresh.current_policy_reference(),
            self.d.pair(self.genesis, 1),
        )

        with self.assertRaises(ValueError):

            self.f.bootstrap(
                root_backend=reopened_root,
            )

        # The legacy durable and fence pair is not needed.

        legacy_state = self.d.store_path

        legacy_fence = legacy_state.with_name(
            legacy_state.name + ".fence.sqlite3"
        )

        legacy_state.unlink()
        legacy_fence.unlink()

        fresh = self.reopen()

        self.assertEqual(
            fresh.current_policy_reference(),
            self.d.pair(self.genesis, 1),
        )

        self.d.assert_committed(
            self.f.send(
                gateway=self.f.make_gateway(fresh),
            ),
            2,
        )

        self.assertFalse(legacy_state.exists())
        self.assertFalse(legacy_fence.exists())

        self.stable(self.genesis, 1, 1)
        self.d.assert_floor(2, 1)

    def test_02_policy_rollback_rejected_by_reopened_root(self):

        old = self.d.snapshot()

        second = self.f.candidate()

        self.assertEqual(
            self.f.publish(second),
            self.d.pair(second, 2),
        )

        retained = self.stable(second, 2, 3)

        self.d.restore(old)

        fresh_root = self.open_root()

        self.assertEqual(fresh_root.read(), retained)

        with self.assertRaises(ValueError):

            self.f.reopen(
                root_backend=fresh_root,
            )

        with self.assertRaises(ValueError):
            self.authority.current_policy_reference()

        self.f.blocked()

        self.assertEqual(
            self.open_root().read(),
            retained,
        )

        self.d.assert_floor(1, 0)

    def test_03_precommit_failure_recovers_using_fresh_root(self):

        second = self.f.candidate()

        retained = self.f.fail_publication(
            second,
            after_commit=False,
        )

        self.assertEqual(
            self.pending(second),
            retained,
        )

        self.s.assert_history(self.genesis)

        fresh = self.reopen()

        self.assertEqual(fresh.root_state(), retained)

        with self.assertRaises(ValueError):
            fresh.current_policy_reference()

        with self.assertRaises(ValueError):
            fresh.retired_writer_keys()

        self.f.blocked(
            gateway=self.f.make_gateway(fresh),
        )

        self.assertEqual(
            fresh.recover_publication(),
            self.d.pair(second, 2),
        )

        finalized = self.stable(second, 2, 3)

        reopened = self.reopen()

        self.assertEqual(
            reopened.recover_publication(),
            self.d.pair(second, 2),
        )

        self.assertEqual(
            reopened.root_state(),
            finalized,
        )

        self.s.assert_history(self.genesis, second)
        self.f.blocked(signed_policy=second)
        self.d.assert_floor(1, 0)

    def test_04_postcommit_pending_survives_policy_rollback(self):

        old = self.d.snapshot()

        second = self.f.candidate()

        retained = self.f.fail_publication(
            second,
            after_commit=True,
        )

        self.s.assert_history(self.genesis, second)

        self.d.restore(old)

        self.assertEqual(
            self.open_root().read(),
            retained,
        )

        fresh = self.reopen()

        self.assertEqual(fresh.root_state(), retained)

        self.f.blocked(
            gateway=self.f.make_gateway(fresh),
        )

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        with self.assertRaises(ValueError):

            fresh.publish_policy(
                signed_policy=alternative,
            )

        self.assertEqual(fresh.root_state(), retained)

        self.assertEqual(
            fresh.recover_publication(),
            self.d.pair(second, 2),
        )

        self.stable(second, 2, 3)

        self.s.assert_history(self.genesis, second)
        self.f.blocked(signed_policy=second)
        self.d.assert_floor(1, 0)

    def test_05_conflicting_history_cannot_replace_prepared(self):

        old = self.d.snapshot()

        second = self.f.candidate()

        retained = self.f.fail_publication(
            second,
            after_commit=False,
        )

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.d.h.publish_external(alternative)

        fresh = self.reopen()

        with self.assertRaises(ValueError):
            fresh.recover_publication()

        self.f.blocked(
            gateway=self.f.make_gateway(fresh),
            signed_policy=alternative,
        )

        self.assertEqual(
            self.open_root().read(),
            retained,
        )

        self.d.restore(old)

        reopened = self.reopen()

        self.assertEqual(
            reopened.recover_publication(),
            self.d.pair(second, 2),
        )

        self.stable(second, 2, 3)
        self.s.assert_history(self.genesis, second)
        self.d.assert_floor(1, 0)

    def test_06_independent_root_instances_fence_floor_cas(self):

        copy = self.d.snapshot(
            "sqlite-protected-policy-copy.sqlite3"
        )

        peer_root = self.open_root()

        self.assertIsNot(peer_root, self.root)

        peer = self.f.reopen(
            path=copy,
            root_backend=peer_root,
        )

        second = self.f.candidate()

        entered = threading.Event()
        release = threading.Event()
        started = threading.Event()

        backend_type = type(self.p.backend)
        original = backend_type.advance_if_current

        def blocking_backend(instance, **arguments):

            entered.set()

            if not release.wait(timeout=20):
                raise TimeoutError("CAS release timed out")

            return original(instance, **arguments)

        def competing_publication():

            started.set()

            return self.f.publish(
                second,
                authority=peer,
            )

        with patch.object(
            backend_type,
            "advance_if_current",
            blocking_backend,
        ):

            with ThreadPoolExecutor(max_workers=2) as pool:

                cas = pool.submit(self.f.send)

                try:

                    self.assertTrue(
                        entered.wait(timeout=10)
                    )

                    publication = pool.submit(
                        competing_publication
                    )

                    self.assertTrue(
                        started.wait(timeout=5)
                    )

                    with self.assertRaises(TimeoutError):
                        publication.result(timeout=0.35)

                finally:
                    release.set()

                self.d.assert_committed(
                    cas.result(timeout=30),
                    2,
                )

                self.assertEqual(
                    publication.result(timeout=30),
                    self.d.pair(second, 2),
                )

        retained = self.open_root().read()

        self.assertEqual(retained.revision, 3)

        self.assertEqual(
            retained.durable_state.anchor,
            self.d.ref(second, 2),
        )

        self.assertIsNone(
            retained.durable_state.prepared,
        )

        self.assertEqual(
            self.authority.root_state(),
            retained,
        )

        self.assertEqual(
            peer.root_state(),
            retained,
        )

        # The original policy copy is now stale.

        self.f.blocked(
            request=self.p.next_cas(),
        )

        with self.assertRaises(ValueError):
            self.reopen()

        self.d.assert_floor(2, 1)

    def test_07_rejected_cas_retains_persistent_observation(self):

        old = self.d.snapshot()

        second = self.f.candidate()

        self.d.h.publish_external(second)

        self.f.blocked(
            signed_policy=self.genesis,
        )

        retained = self.stable(second, 2, 2)

        self.d.restore(old)

        with self.assertRaises(ValueError):
            self.reopen()

        self.f.blocked()

        self.assertEqual(
            self.open_root().read(),
            retained,
        )

        self.d.assert_floor(1, 0)

    def test_08_floor_backend_failure_cannot_undo_observation(self):

        second = self.p.next_policy()

        self.d.h.publish_external(second)

        reached = []

        def fail_backend(instance, **arguments):

            state = self.root.read()

            self.assertEqual(state.revision, 2)

            self.assertEqual(
                state.durable_state.anchor,
                self.d.ref(second, 2),
            )

            reached.append(state)

            raise OSError("Injected floor backend failure")

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            fail_backend,
        ):

            with self.assertRaises(ValueError):
                self.f.send(second)

        self.assertEqual(len(reached), 1)

        retained = self.stable(second, 2, 2)

        self.assertEqual(retained, reached[0])

        fresh = self.reopen()

        self.assertEqual(
            fresh.root_state(),
            retained,
        )

        self.d.assert_floor(1, 0)

        self.d.assert_committed(
            self.f.send(
                second,
                gateway=self.f.make_gateway(fresh),
            ),
            2,
        )

        self.assertEqual(
            self.open_root().read(),
            retained,
        )

        self.d.assert_floor(2, 1)

    def assert_missing_root_fails_closed(self, missing):

        self.d.assert_committed(
            self.f.send(),
            2,
        )

        missing.unlink()

        with self.assertRaises(ValueError):
            self.open_root()

        with self.assertRaises(ValueError):
            self.authority.root_state()

        with self.assertRaises(ValueError):
            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):
            self.authority.recover_publication()

        self.f.blocked(
            request=self.p.next_cas(),
        )

        # Public signed recovery remains independent of
        # protected writer authorization availability.

        self.assertEqual(
            self.d.public_read(self.gateway)["epoch"],
            2,
        )

        self.assertEqual(
            self.d.public_lookup(self.gateway)["status"],
            "committed",
        )

        self.assertFalse(missing.exists())

        with self.assertRaises(ValueError):
            self.create_root()

        self.assertFalse(missing.exists())

        self.d.assert_floor(2, 1)

    def test_09_missing_state_blocks_writers_not_public_recovery(self):

        self.assert_missing_root_fails_closed(self.path)

        self.assertTrue(self.fence_path.is_file())

    def test_10_missing_fence_blocks_writers_not_public_recovery(self):

        self.assert_missing_root_fails_closed(self.fence_path)

        self.assertTrue(self.path.is_file())

    def test_11_provisioning_ack_loss_recovers_same_persistent_root(self):

        path = (
            self.s.directory / "sqlite-bootstrap-ack.sqlite3"
        )

        new_root = self.create_root(path)

        original = type(new_root).provision

        reached = []

        def lose_ack(instance, *, state):

            self.assertIs(instance, new_root)

            result = original(
                instance,
                state=state,
            )

            reached.append(result)

            raise OSError(
                "Persistent provisioning acknowledgement lost"
            )

        with patch.object(
            type(new_root),
            "provision",
            lose_ack,
        ):

            with self.assertRaises(ValueError):

                self.f.bootstrap(
                    root_backend=new_root,
                )

        self.assertEqual(len(reached), 1)

        reopened_root = self.open_root(path)

        committed = reopened_root.read()

        self.assertEqual(committed.revision, 1)

        self.assertEqual(
            committed.reference(),
            reached[0],
        )

        fresh = self.f.reopen(
            root_backend=reopened_root,
        )

        self.assertEqual(
            fresh.root_state(),
            committed,
        )

        with self.assertRaises(ValueError):

            self.f.bootstrap(
                root_backend=reopened_root,
            )

        self.assertEqual(
            self.open_root(path).read(),
            committed,
        )

        self.d.assert_floor(1, 0)

    def test_12_finalization_ack_loss_retains_committed_revision(self):

        second = self.f.candidate()

        original = type(self.root).compare_and_set

        reached = []

        def lose_ack(instance, *, expected, replacement):

            result = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            if replacement.revision == 3:

                reached.append(result)

                raise OSError(
                    "Persistent finalization acknowledgement lost"
                )

            return result

        with patch.object(
            type(self.root),
            "compare_and_set",
            lose_ack,
        ):

            with self.assertRaises(ValueError):
                self.f.publish(second)

        self.assertEqual(len(reached), 1)

        retained = self.stable(second, 2, 3)

        self.assertEqual(
            retained.reference(),
            reached[0],
        )

        self.s.assert_history(self.genesis, second)

        fresh = self.reopen()

        self.assertEqual(
            fresh.recover_publication(),
            self.d.pair(second, 2),
        )

        self.assertEqual(
            fresh.root_state(),
            retained,
        )

        self.assertEqual(
            self.open_root().read(),
            retained,
        )

        self.f.blocked(
            signed_policy=second,
            gateway=self.f.make_gateway(fresh),
        )

        self.d.assert_floor(1, 0)


if __name__ == "__main__":
    unittest.main()
