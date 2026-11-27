"""Final authenticated provider authority adversarial contracts.

Verify committed finalization, failed FINISH, replica failure,
and stale recovery references through the production composition.
All databases and signing keys belong to temporary test fixtures.
No independent physical rollback resistance is asserted.
"""

import unittest

from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_authority_contract as module


Provider = module.Provider
Backend = module.Backend
Anchored = module.Anchored


class SyntheticFinalizationFailure(RuntimeError):
    pass


class SyntheticFinishFailure(RuntimeError):
    pass


class SyntheticReplicaFailure(RuntimeError):
    pass


class A44AuthenticatedProviderAuthorityAdversarialTests(unittest.TestCase):

    def setUp(self):
        self._observations = {}
        self.f = module.A44RealAuthenticatedProviderAuthorityTests('test_01_canonical_production_composition')
        self.addCleanup(self.f.doCleanups)
        self.f.setUp()
        self.initial = self.f.initial
        self.candidate = self.f.f.f.candidate
        self.genesis = self.f.f.f.genesis
        self.expected_pair = self.f.f.f.d.pair(self.candidate, 2)
        self.assertEqual(self.f.anchor.read(), self.initial)
        self.assertEqual(self.f.local.read(), self.initial)
        self.assertIs(type(self.f.local), Backend)
        self.assertIs(type(self.f.anchor), Backend)
        self.assertNotEqual(self.f.local._storage.path, self.f.anchor._storage.path)
        self.assertNotEqual(self.f.local._storage.storage_id, self.f.anchor._storage.storage_id)
        self.f.assert_clean(self.f.provider)

    def assert_exception_preserved(self, actual, expected):
        pending = [actual]
        visited = set()
        while pending:
            current = pending.pop()
            if id(current) in visited:
                continue
            visited.add(id(current))
            if current is expected:
                return
            for related in (current.__cause__, current.__context__):
                if related is not None:
                    pending.append(related)
        self.fail('Original injected exception lost')

    def assert_pending(self, state):
        self.assertEqual(state.revision, self.initial.revision + 1)
        self.assertEqual(state.durable_state.anchor, self.initial.durable_state.anchor)
        prepared = state.durable_state.prepared
        self.assertIsNotNone(prepared)
        self.assertEqual(prepared.signed_policy, self.candidate)
        self.assertEqual(prepared.candidate.pair(), self.expected_pair)

    def record(self, name, outcome):
        self.assertNotIn(name, self._observations)
        self._observations[name] = outcome
        print('OBSERVATION:', name, outcome, flush=True)

    def reconcile(self, local_state, anchor_state):
        provider, client = self.f.make_client(self.f.open_anchor())
        original = Provider.compare_and_set
        dispatches = []

        def observe(instance, **kwargs):
            if instance is provider:
                dispatches.append(kwargs)
            return original(instance, **kwargs)
        with patch.object(Provider, 'compare_and_set', new=observe):
            receipt = Anchored.recover_local(local_backend=self.f.f.f.f.open_root(), anchor_backend=client, expected_identity=self.f.identity, expected_local=local_state.reference(), expected_anchor=anchor_state.reference())
        self.assertEqual(receipt, anchor_state.reference())
        self.assertEqual(dispatches, [], 'Local reconciliation must not mutate anchor')
        self.f.assert_roots(anchor_state)
        self.f.assert_clean(provider)

    def assert_final_recovery(self, expected):
        provider, client, guard, authority = self.f.reopen()
        self.assertEqual(authority.root_state(), expected)
        self.assertEqual(authority.current_policy_reference(), self.expected_pair)
        self.assertEqual(authority.recover_publication(), self.expected_pair)
        self.f.assert_roots(expected)
        self.f.f.f.s.assert_history(self.genesis, self.candidate)
        self.f.f.assert_revocation_and_authorized_writer(authority)
        self.f.assert_roots(expected)
        self.f.assert_clean(provider)

    def test_01_finalization_signing_failure(self):
        print('\n=== A01 / FINALIZATION SIGNING FAILURE ===', flush=True)
        original = Provider._signed
        injected = SyntheticFinalizationFailure('Finalization signing failed after CAS commit')
        transitions = []
        before_sessions = self.f.history()

        def sign(instance, **kwargs):
            if instance is self.f.provider and kwargs['operation'] == 'cas':
                state = kwargs['state']
                transitions.append(state)
                if state.revision == self.initial.revision + 2:
                    self.assertIsNone(state.durable_state.prepared)
                    self.assertEqual(self.f.anchor.read(), state)
                    raise injected
            return original(instance, **kwargs)
        with patch.object(Provider, '_signed', new=sign):
            with self.assertRaises(Exception) as caught:
                self.f.authority.publish_policy(signed_policy=self.candidate)
        self.assert_exception_preserved(caught.exception, injected)
        self.assertEqual(len(transitions), 2)
        pending, finalized = transitions
        self.assert_pending(pending)
        self.f.assert_finalized(finalized)
        self.assertEqual(self.f.open_anchor().read(), finalized)
        self.assertEqual(self.f.local.read(), pending)
        self.f.f.f.s.assert_history(self.genesis, self.candidate)
        self.assertTrue(before_sessions < self.f.history())
        self.f.assert_clean(self.f.provider)
        print('PASS: Finalized anchor committed.')
        print('PASS: Local replica remains PREPARED.')
        print('PASS: Policy publication committed.')
        print('PASS: No successful publication response.')
        with self.assertRaises(ValueError):
            self.f.authority.current_policy_reference()
        self.reconcile(pending, finalized)
        self.assert_final_recovery(finalized)
        self.record('A01', 'FINALIZED_ANCHOR_RETAINED_LOCAL_RECOVERED')

    def test_02_finish_signing_failure(self):
        print('\n=== A02 / FINISH SIGNING FAILURE ===', flush=True)
        original = Provider._signed
        injected = SyntheticFinishFailure('FINISH signing failed after publication')
        operations = []
        reached = []
        before_sessions = self.f.history()

        def sign(instance, **kwargs):
            if instance is self.f.provider:
                operation = kwargs['operation']
                operations.append(operation)
                if operation == 'finish':
                    state = kwargs['state']
                    self.f.assert_finalized(state)
                    self.assertEqual(self.f.anchor.read(), state)
                    self.assertEqual(self.f.local.read(), state)
                    reached.append(state)
                    raise injected
            return original(instance, **kwargs)
        with patch.object(Provider, '_signed', new=sign):
            with self.assertRaises(Exception) as caught:
                self.f.authority.publish_policy(signed_policy=self.candidate)
        self.assert_exception_preserved(caught.exception, injected)
        self.assertEqual(len(reached), 1)
        self.assertEqual(operations.count('cas'), 2)
        self.assertEqual(operations.count('hold'), 1)
        self.assertEqual(operations.count('finish'), 1)
        finalized = reached[0]
        self.f.assert_roots(finalized)
        self.f.f.f.s.assert_history(self.genesis, self.candidate)
        after_sessions = self.f.history()
        self.assertTrue(before_sessions < after_sessions)
        self.f.assert_clean(self.f.provider)
        print('PASS: Both finalized roots retained.')
        print('PASS: Committed policy retained.')
        print('PASS: FINISH exception preserved.')
        consumed = after_sessions - before_sessions
        provider, client = self.f.make_client(self.f.open_anchor())
        signing = []

        def observe(instance, **kwargs):
            if instance is provider:
                signing.append(kwargs['operation'])
            return original(instance, **kwargs)
        with patch.object(Provider, '_signed', new=observe):
            for session in sorted(consumed):
                with self.assertRaisesRegex(ValueError, 'Protected provider session replay'):
                    with provider.hold(session=session):
                        self.fail('Consumed FINISH session replayed')
        self.assertEqual(signing, [])
        self.assertEqual(self.f.history(), after_sessions)
        self.f.assert_clean(provider)
        self.assert_final_recovery(finalized)
        self.record('A02', 'FINISH_FAILED_COMMITTED_PUBLICATION_RETAINED')

    def test_03_local_replica_write_failure(self):
        print('\n=== A03 / LOCAL REPLICA WRITE FAILURE ===', flush=True)
        original = Backend.compare_and_set
        local_path = self.f.local._storage.path
        anchor_path = self.f.anchor._storage.path
        injected = SyntheticReplicaFailure('Synthetic local replica CAS failure')
        dispatched = []
        before_sessions = self.f.history()

        def compare_and_set(instance, **kwargs):
            path = instance._storage.path
            if path == local_path:
                replacement = kwargs['replacement']
                self.assert_pending(replacement)
                self.assertEqual(self.f.anchor.read(), replacement)
                dispatched.append(('local_failure', replacement))
                raise injected
            if path == anchor_path:
                dispatched.append(('anchor_cas', kwargs['replacement']))
            return original(instance, **kwargs)
        with patch.object(Backend, 'compare_and_set', new=compare_and_set):
            with self.assertRaises(Exception) as caught:
                self.f.authority.publish_policy(signed_policy=self.candidate)
        self.assert_exception_preserved(caught.exception, injected)
        self.assertEqual([item[0] for item in dispatched], ['anchor_cas', 'local_failure'])
        pending = self.f.open_anchor().read()
        self.assert_pending(pending)
        self.assertEqual(dispatched[0][1], pending)
        self.assertEqual(dispatched[1][1], pending)
        self.assertEqual(self.f.local.read(), self.initial)
        self.f.f.f.s.assert_history(self.genesis)
        self.assertTrue(before_sessions < self.f.history())
        self.f.assert_clean(self.f.provider)
        print('PASS: Authoritative preparation retained.')
        print('PASS: Local root unchanged.')
        print('PASS: Policy history unchanged.')
        print('PASS: No automatic anchor rollback.')
        with self.assertRaises(ValueError):
            self.f.authority.current_policy_reference()
        self.reconcile(self.initial, pending)
        provider, client, guard, authority = self.f.reopen()
        self.assertEqual(authority.root_state(), pending)
        with self.assertRaises(ValueError):
            authority.current_policy_reference()
        self.assertEqual(authority.recover_publication(), self.expected_pair)
        finalized = self.f.open_anchor().read()
        self.f.assert_finalized(finalized)
        self.f.assert_roots(finalized)
        self.f.assert_clean(provider)
        self.assert_final_recovery(finalized)
        self.record('A03', 'REPLICA_FAILURE_PREPARATION_RECOVERED')

    def test_04_stale_recovery_reference_rejected(self):
        print('\n=== A04 / STALE RECOVERY REFERENCE ===', flush=True)
        pending = self.f.inject_committed_prepare_failure()
        self.assert_pending(pending)
        self.assertEqual(self.f.local.read(), self.initial)
        provider, client = self.f.make_client(self.f.open_anchor())
        original_provider_cas = Provider.compare_and_set
        original_backend_cas = Backend.compare_and_set
        provider_writes = []
        backend_writes = []

        def observe_provider(instance, **kwargs):
            provider_writes.append(kwargs)
            return original_provider_cas(instance, **kwargs)

        def observe_backend(instance, **kwargs):
            backend_writes.append(kwargs)
            return original_backend_cas(instance, **kwargs)
        before_sessions = self.f.history()
        with patch.object(Provider, 'compare_and_set', new=observe_provider), patch.object(Backend, 'compare_and_set', new=observe_backend):
            with self.assertRaises(ValueError):
                Anchored.recover_local(local_backend=self.f.f.f.f.open_root(), anchor_backend=client, expected_identity=self.f.identity, expected_local=self.initial.reference(), expected_anchor=self.initial.reference())
            with self.assertRaises(ValueError):
                Anchored.recover_local(local_backend=self.f.f.f.f.open_root(), anchor_backend=client, expected_identity=self.f.identity, expected_local=pending.reference(), expected_anchor=pending.reference())
        self.assertEqual(provider_writes, [])
        self.assertEqual(backend_writes, [])
        self.assertEqual(self.f.open_anchor().read(), pending)
        self.assertEqual(self.f.local.read(), self.initial)
        self.f.f.f.s.assert_history(self.genesis)
        self.assertTrue(before_sessions <= self.f.history())
        self.f.assert_clean(provider)
        print('PASS: Stale anchor reference rejected.')
        print('PASS: Incorrect local reference rejected.')
        print('PASS: No provider CAS dispatched.')
        print('PASS: No backend CAS dispatched.')
        print('PASS: Both root states unchanged.')
        self.reconcile(self.initial, pending)
        provider, client, guard, authority = self.f.reopen()
        self.assertEqual(authority.recover_publication(), self.expected_pair)
        finalized = self.f.open_anchor().read()
        self.f.assert_finalized(finalized)
        self.f.assert_roots(finalized)
        self.f.assert_clean(provider)
        self.assert_final_recovery(finalized)
        self.record('A04', 'STALE_RECOVERY_REJECTED_WITHOUT_ROOT_MUTATION')


if __name__ == "__main__":
    unittest.main()
