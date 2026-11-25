"""A44 protected durable writer policy authority contract.

The protected root is the authoritative security state.

No local durable-state or coordination database is required
by this authority.

REQUIRED API

ProtectedDurableWriterPolicyAuthority.bootstrap(
    *,
    path,
    backend,
    root_backend,
    expected_identity,
    expected_policy_id,
    expected_policy_public_key,
    expected_genesis_sha256,
    initial_policy_reference,
)

ProtectedDurableWriterPolicyAuthority.open(
    *,
    path,
    backend,
    root_backend,
    expected_identity,
    expected_policy_id,
    expected_policy_public_key,
    expected_genesis_sha256,
)

The externally supplied expected_identity must bind:

    deployment_id
    configuration_sha256
    provisioning_nonce

The configuration digest uses the existing durable authority
configuration commitment, with deployment_id as store_id.

The policy database path is not part of that commitment.
Independent policy copies may share one protected root.

Bootstrap requires an exact trusted initial policy reference,
authenticated history and an explicitly unprovisioned root.

Open never provisions or recreates missing root state.

An ambiguous successful bootstrap is resolved by opening the
same provisioned root and validating its externally pinned
identity and authenticated policy lineage.

AUTHORITY METHODS

root_state() -> ProtectedDurableRootState
current_policy_reference() -> tuple[int, str]
retired_writer_keys() -> tuple[bytes, ...]
publish_policy(*, signed_policy) -> tuple[int, str]
recover_publication() -> tuple[int, str]

ProtectedDurableWriterPolicyGateway.from_authority(
    *,
    authority,
)

gateway.exchange(request: bytes) -> bytes

The protected backend exclusive fence must span authenticated
history loading, root transitions, policy publication and floor CAS.

Every protected state transition increments root revision by one.

The exact prepared signed policy must be retained before policy
commit. Unresolved preparation blocks writer authorization.

Recovery finalizes the exact candidate. If authenticated descendants
exist, they may subsequently be observed under the same fence.

The reference backend is an in-memory trust model. It is not
process-durable, hardware-backed, or independently tamper-resistant.
"""

import importlib
import sys
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_witness_deployment_floor_writer_policy_durable_high_water_contract as previous


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_authority"
)

ROOT_MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root"
)

policy = previous.policy


class A44ProtectedRootAuthorityContractTests(unittest.TestCase):

    def setUp(self):

        self.m = importlib.import_module(MODULE)
        self.r = importlib.import_module(ROOT_MODULE)

        self.d = previous.A44DurableWriterPolicyContractTests(
            "test_01_explicit_bootstrap_and_open"
        )

        self.addCleanup(self.d.doCleanups)
        self.d.setUp()

        self.s = self.d.s
        self.p = self.d.p
        self.genesis = self.d.genesis

        self.identity = self.r.ProtectedDeploymentIdentity(
            deployment_id=previous.STORE_ID,
            configuration_sha256=(
                self.d.authority._configuration.identity
            ),
            provisioning_nonce=b"p" * 32,
        )

        self.root = self.new_root()

        self.authority_type = (
            self.m.ProtectedDurableWriterPolicyAuthority
        )

        self.gateway_type = (
            self.m.ProtectedDurableWriterPolicyGateway
        )

        self.authority = self.bootstrap()
        self.gateway = self.make_gateway()

    def new_root(self, identity=None):

        return self.r.InMemoryProtectedRootBackend(
            identity=(
                self.identity
                if identity is None
                else identity
            ),
        )

    def parameters(self):

        return {
            "path": self.s.path,
            "backend": self.p.backend,
            "root_backend": self.root,
            "expected_identity": self.identity,
            "expected_policy_id": policy.POLICY_ID,
            "expected_policy_public_key": self.p.root_key,
            "expected_genesis_sha256": self.d.h.genesis_sha,
        }

    def bootstrap(self, **changes):

        params = self.parameters()

        params["initial_policy_reference"] = self.d.ref(
            self.genesis, 1
        )

        params.update(changes)

        return self.authority_type.bootstrap(**params)

    def reopen(self, **changes):

        params = self.parameters()
        params.update(changes)

        return self.authority_type.open(**params)

    def make_gateway(self, authority=None):

        if authority is None:
            authority = self.authority

        return self.gateway_type.from_authority(
            authority=authority,
        )

    def stable(self, signed_policy, epoch, revision):

        state = self.root.read()

        self.assertIs(
            type(state),
            self.r.ProtectedDurableRootState,
        )

        self.assertEqual(state.identity, self.identity)
        self.assertEqual(state.revision, revision)
        self.assertIsNone(state.durable_state.prepared)

        self.assertEqual(
            state.durable_state.anchor,
            self.d.ref(signed_policy, epoch),
        )

        self.assertEqual(
            self.authority.root_state(),
            state,
        )

        return state

    def pending(self, candidate):

        state = self.root.read()

        self.assertEqual(state.revision, 2)

        self.assertEqual(
            state.durable_state.anchor,
            self.d.ref(self.genesis, 1),
        )

        prepared = state.durable_state.prepared

        self.assertIsNotNone(prepared)

        self.assertEqual(
            prepared.predecessor,
            state.durable_state.anchor,
        )

        self.assertEqual(
            prepared.candidate,
            self.d.ref(candidate, 2),
        )

        self.assertEqual(
            prepared.signed_policy,
            candidate,
        )

        return state

    def publish(self, signed_policy, authority=None):

        if authority is None:
            authority = self.authority

        return authority.publish_policy(
            signed_policy=signed_policy,
        )

    def send(self, signed_policy=None, **changes):

        changes.setdefault("gateway", self.gateway)

        return self.d.send(signed_policy, **changes)

    def blocked(self, **changes):

        changes.setdefault("gateway", self.gateway)

        self.d.assert_cas_blocked(**changes)

    def candidate(self):

        return self.p.next_policy(
            revoked=("writer-alpha",),
        )

    def fail_publication(self, candidate, *, after_commit):

        original = self.d.persistent._transaction

        reached = []

        @contextmanager
        def injected(pins, **arguments):

            written = False

            with original(pins, **arguments) as connection:

                yield connection

                row = connection.execute(
                    "SELECT policy_epoch FROM writer_policy_head"
                ).fetchone()

                if row == (2,):

                    self.pending(candidate)
                    written = True
                    reached.append("prepared-before-commit")

                    if not after_commit:
                        raise OSError("Policy precommit failure")

            if written and after_commit:

                reached.append("committed")

                raise OSError(
                    "Policy commit acknowledgement lost"
                )

        with patch.object(
            self.d.persistent,
            "_transaction",
            injected,
        ):

            with self.assertRaises(ValueError):
                self.publish(candidate)

        expected = ["prepared-before-commit"]

        if after_commit:
            expected.append("committed")

        self.assertEqual(reached, expected)

        return self.pending(candidate)

    def test_01_explicit_bootstrap_and_open(self):

        original = self.stable(self.genesis, 1, 1)

        fresh = self.reopen()

        self.assertEqual(fresh.root_state(), original)

        self.assertEqual(
            fresh.current_policy_reference(),
            self.d.pair(self.genesis, 1),
        )

        missing = self.new_root()

        with self.assertRaises(ValueError):
            self.reopen(root_backend=missing)

        with self.assertRaises(ValueError):
            missing.read()

        with self.assertRaises(ValueError):
            self.bootstrap()

        self.assertEqual(self.root.read(), original)

        self.d.assert_floor(1, 0)

    def test_02_external_identity_and_configuration_binding(self):

        wrong_identities = (
            replace(
                self.identity,
                deployment_id="different-deployment",
            ),
            replace(
                self.identity,
                configuration_sha256="ab" * 32,
            ),
            replace(
                self.identity,
                provisioning_nonce=b"x" * 32,
            ),
        )

        for identity in wrong_identities:

            with self.assertRaises(ValueError):
                self.reopen(expected_identity=identity)

        wrong_config = wrong_identities[1]

        unprovisioned = self.new_root(wrong_config)

        with self.assertRaises(ValueError):

            self.bootstrap(
                root_backend=unprovisioned,
                expected_identity=wrong_config,
            )

        with self.assertRaises(ValueError):
            unprovisioned.read()

        with self.assertRaises(ValueError):

            self.reopen(
                expected_policy_id="wrong-policy",
            )

        self.stable(self.genesis, 1, 1)
        self.d.assert_floor(1, 0)

    def test_03_policy_and_legacy_durable_rollback_rejected(self):

        old_policy = self.d.snapshot("protected-old-policy.sqlite3")

        old_durable = (
            self.s.directory / "protected-old-durable.sqlite3"
        )

        self.d.backup_database(
            self.d.store_path,
            old_durable,
        )

        second = self.candidate()

        self.assertEqual(
            self.publish(second),
            self.d.pair(second, 2),
        )

        retained = self.stable(second, 2, 3)

        self.d.restore(old_policy)

        self.d.backup_database(
            old_durable,
            self.d.store_path,
        )

        with self.assertRaises(ValueError):
            self.reopen()

        with self.assertRaises(ValueError):
            self.authority.current_policy_reference()

        self.blocked()

        self.assertEqual(self.root.read(), retained)

        self.d.assert_floor(1, 0)

    def test_04_replacement_root_cannot_substitute_nonce(self):

        old_policy = self.d.snapshot()

        second = self.candidate()
        self.publish(second)

        retained = self.stable(second, 2, 3)

        self.d.restore(old_policy)

        alternative_identity = replace(
            self.identity,
            provisioning_nonce=b"x" * 32,
        )

        alternative = self.new_root(alternative_identity)

        self.bootstrap(
            root_backend=alternative,
            expected_identity=alternative_identity,
        )

        with self.assertRaises(ValueError):

            self.reopen(
                root_backend=alternative,
                expected_identity=self.identity,
            )

        self.blocked()

        self.assertEqual(self.root.read(), retained)

        self.d.assert_floor(1, 0)

    def test_05_independent_policy_copies_share_protected_root(self):

        copy = self.d.snapshot("protected-copy.sqlite3")

        peer = self.reopen(path=copy)

        second = self.candidate()

        self.publish(second)

        self.assertEqual(
            peer.root_state(),
            self.stable(second, 2, 3),
        )

        self.blocked(
            gateway=self.make_gateway(peer),
        )

        with self.assertRaises(ValueError):
            self.reopen(path=copy)

        self.d.assert_committed(
            self.send(
                second,
                writer_id="writer-beta",
                signer=self.p.f.bob,
            ),
            2,
        )

        self.d.assert_floor(2, 1)

    def test_06_pending_survives_policy_and_legacy_store_rollback(self):

        old_policy = self.d.snapshot()

        old_state = (
            self.s.directory / "legacy-state-backup.sqlite3"
        )

        self.d.backup_database(
            self.d.store_path,
            old_state,
        )

        second = self.candidate()

        retained = self.fail_publication(
            second,
            after_commit=True,
        )

        self.s.assert_history(self.genesis, second)

        self.d.restore(old_policy)

        self.d.backup_database(
            old_state,
            self.d.store_path,
        )

        fresh = self.reopen()

        self.assertEqual(fresh.root_state(), retained)

        self.blocked(
            gateway=self.make_gateway(fresh),
        )

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        with self.assertRaises(ValueError):
            self.publish(alternative, authority=fresh)

        self.assertEqual(
            fresh.recover_publication(),
            self.d.pair(second, 2),
        )

        self.stable(second, 2, 3)
        self.s.assert_history(self.genesis, second)
        self.blocked(signed_policy=second)

        self.d.assert_floor(1, 0)

    def test_07_precommit_failure_recovers_exact_prepared_candidate(self):

        second = self.candidate()

        self.fail_publication(
            second,
            after_commit=False,
        )

        self.s.assert_history(self.genesis)

        with self.assertRaises(ValueError):
            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):
            self.authority.retired_writer_keys()

        self.blocked()

        self.assertEqual(
            self.authority.recover_publication(),
            self.d.pair(second, 2),
        )

        state = self.stable(second, 2, 3)

        self.assertEqual(
            self.authority.recover_publication(),
            self.d.pair(second, 2),
        )

        self.assertEqual(self.root.read(), state)

        self.s.assert_history(self.genesis, second)
        self.d.assert_floor(1, 0)

    def test_08_conflicting_signed_history_cannot_replace_prepared(self):

        old = self.d.snapshot()

        second = self.candidate()

        retained = self.fail_publication(
            second,
            after_commit=False,
        )

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.d.h.publish_external(alternative)

        with self.assertRaises(ValueError):
            self.authority.recover_publication()

        self.assertEqual(self.root.read(), retained)

        self.blocked(signed_policy=alternative)

        self.d.restore(old)

        self.assertEqual(
            self.authority.recover_publication(),
            self.d.pair(second, 2),
        )

        self.stable(second, 2, 3)
        self.d.assert_floor(1, 0)

    def test_09_rejected_cas_retains_authenticated_observation(self):

        old = self.d.snapshot()

        second = self.candidate()

        self.d.h.publish_external(second)

        self.blocked(signed_policy=self.genesis)

        retained = self.stable(second, 2, 2)

        self.d.restore(old)

        self.blocked()

        with self.assertRaises(ValueError):
            self.reopen()

        self.assertEqual(self.root.read(), retained)

        self.d.assert_floor(1, 0)

    def test_10_backend_failure_cannot_undo_root_observation(self):

        second = self.p.next_policy()

        self.d.h.publish_external(second)

        reached = []

        def fail_backend(instance, **arguments):

            state = self.root.read()

            self.assertEqual(
                state.durable_state.anchor,
                self.d.ref(second, 2),
            )

            self.assertEqual(state.revision, 2)

            reached.append(state)

            raise OSError("Floor backend failure")

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            fail_backend,
        ):

            with self.assertRaises(ValueError):
                self.send(second)

        self.assertEqual(len(reached), 1)

        self.assertEqual(
            self.stable(second, 2, 2),
            reached[0],
        )

        self.d.assert_floor(1, 0)

    def test_11_local_legacy_state_not_required_and_public_recovery_available(self):

        self.d.store_path.unlink()

        fence = self.d.store_path.with_name(
            self.d.store_path.name + ".fence.sqlite3"
        )

        fence.unlink()

        fresh = self.reopen()

        self.assertEqual(
            fresh.current_policy_reference(),
            self.d.pair(self.genesis, 1),
        )

        self.d.assert_committed(
            self.send(),
            2,
        )

        self.s.path.unlink()

        with self.assertRaises(ValueError):
            self.authority.current_policy_reference()

        self.blocked(
            request=self.p.next_cas(),
        )

        self.assertEqual(
            self.d.public_read(self.gateway)["epoch"],
            2,
        )

        self.assertEqual(
            self.d.public_lookup(self.gateway)["status"],
            "committed",
        )

        self.assertFalse(self.s.path.exists())
        self.assertFalse(self.d.store_path.exists())
        self.assertFalse(fence.exists())

        self.stable(self.genesis, 1, 1)
        self.d.assert_floor(2, 1)

    def test_12_bootstrap_ack_loss_requires_same_root_recovery(self):

        new = self.new_root()

        original = type(new).provision

        reached = []

        def lose_ack(instance, *, state):

            self.assertIs(instance, new)

            result = original(instance, state=state)

            reached.append(result)

            raise OSError("Root provisioning acknowledgement lost")

        with patch.object(
            type(new),
            "provision",
            lose_ack,
        ):

            with self.assertRaises(ValueError):
                self.bootstrap(root_backend=new)

        self.assertEqual(len(reached), 1)

        committed = new.read()

        self.assertEqual(committed.revision, 1)
        self.assertEqual(committed.identity, self.identity)

        fresh = self.reopen(root_backend=new)

        self.assertEqual(fresh.root_state(), committed)

        with self.assertRaises(ValueError):
            self.bootstrap(root_backend=new)

        self.assertEqual(new.read(), committed)

        self.d.assert_floor(1, 0)

    def test_13_shared_root_fence_spans_floor_cas(self):

        copy = self.d.snapshot("shared-root-copy.sqlite3")

        peer = self.reopen(path=copy)

        second = self.candidate()

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

            return self.publish(second, authority=peer)

        with patch.object(
            backend_type,
            "advance_if_current",
            blocking_backend,
        ):

            with ThreadPoolExecutor(max_workers=2) as pool:

                cas = pool.submit(self.send)

                try:

                    self.assertTrue(entered.wait(timeout=10))

                    publication = pool.submit(
                        competing_publication
                    )

                    self.assertTrue(started.wait(timeout=5))

                    with self.assertRaises(TimeoutError):
                        publication.result(timeout=0.25)

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

        self.stable(second, 2, 3)

        self.blocked(request=self.p.next_cas())

        self.d.assert_floor(2, 1)

    def test_14_finalization_ack_loss_preserves_root_revision(self):

        second = self.candidate()

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
                    "Protected finalization acknowledgement lost"
                )

            return result

        with patch.object(
            type(self.root),
            "compare_and_set",
            lose_ack,
        ):

            with self.assertRaises(ValueError):
                self.publish(second)

        self.assertEqual(len(reached), 1)

        retained = self.stable(second, 2, 3)

        self.s.assert_history(self.genesis, second)

        fresh = self.reopen()

        self.assertEqual(
            fresh.recover_publication(),
            self.d.pair(second, 2),
        )

        self.assertEqual(self.root.read(), retained)

        self.blocked(signed_policy=second)
        self.d.assert_floor(1, 0)


if __name__ == "__main__":
    unittest.main()
