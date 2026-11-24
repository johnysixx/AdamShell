"""A44 / 66.41B durable writer policy high-water contract.

REQUIRED OBJECTS

PolicyReference(
    *,
    epoch: int,
    sha256: str,
)

PreparedPolicyPublication:
    predecessor: PolicyReference
    candidate: PolicyReference
    signed_policy: tuple[bytes, bytes]

DurablePolicyHighWaterState:
    anchor: PolicyReference
    prepared: PreparedPolicyPublication | None

All state objects are immutable canonical objects.

REQUIRED AUTHORITY API

DurableWriterPolicyAuthority.bootstrap(
    *,
    path,
    high_water_path,
    backend,
    expected_store_id,
    expected_policy_id,
    expected_policy_public_key,
    expected_genesis_sha256,
    initial_policy_reference,
)

DurableWriterPolicyAuthority.open(
    *,
    path,
    high_water_path,
    backend,
    expected_store_id,
    expected_policy_id,
    expected_policy_public_key,
    expected_genesis_sha256,
)

Bootstrap provisions a separate durable store for an existing
authenticated policy database. It requires an explicit exact
current reference from trusted provisioning.

Open never initializes missing storage.

authority.durable_state()
    -> DurablePolicyHighWaterState

authority.current_policy_reference()
    -> tuple[int, str]

authority.retired_writer_keys()
    -> tuple[bytes, ...]

authority.publish_policy(*, signed_policy)
    -> tuple[int, str]

authority.recover_publication()
    -> tuple[int, str]

DurableWriterPolicyGateway.from_authority(*, authority)

gateway.exchange(request: bytes) -> bytes

SECURITY CONTRACT

1. A stable durable anchor authenticates historical lineage.
   Valid descendants are accepted, not just the exact current head.

2. Existing authenticated policy observation is committed to the
   durable store before writer authorization or floor mutation.

3. Invalid or incomplete history never advances the anchor.

4. Before any new policy transaction may commit, an independently
   committed PREPARED record retains the exact signed candidate,
   predecessor and candidate reference.

5. Unresolved PREPARED state blocks writer CAS and ordinary policy
   publication, including publication of another signed candidate.

6. PREPARED must survive exceptions, restart and rollback of the
   policy database alone.

7. Recovery completes exactly the prepared candidate, or verifies
   that the same candidate is already present in authenticated
   history. It must never silently substitute a different candidate.

8. Recovery of an already finalized publication is idempotent.

9. No automatic abort of a durable prepared publication is allowed
   merely because the policy database still contains its predecessor.

10. Cooperating authorities share a durable publication/CAS fence,
    including authorities using distinct policy database copies.

11. A durable observation must survive rejected CAS and backend
    exceptions. A rollback of the policy transaction must not undo it.

12. Policy and floor CAS synchronization must preserve the existing
    SQLite transaction boundary.

13. Durable state inspection is read-only and does not require policy
    database access. Pending state can be inspected without opening
    another policy transaction.

14. Public signed READ and LOOKUP remain available to already opened
    gateways even during pending publication or missing policy storage.

15. Store identity, policy identity, genesis, root and floor identity
    must be bound to the durable store. Storage aliases are forbidden.

16. Stable current-reference and retirement operations reject pending
    publication rather than returning an apparently usable old policy.

17. Open may expose a valid pending state for explicit recovery, but
    does not silently clear or automatically complete that state.

18. A publication candidate is not a finalized anchor before commit
    and successful durable finalization.

TRUST BOUNDARY

The durable reference store is assumed to be independently trusted
against rollback, replacement and unauthorized modification.

A local SQLite reference implementation alone cannot guarantee this
assumption. Simultaneous rollback of all relevant stores remains a
documented limitation.

Legacy gateways and direct backend access are outside this fence.

All tests operate on temporary fixture databases and test keys.
"""


import importlib
import sqlite3
import sys
import threading
import time
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from pathlib import Path
from unittest.mock import patch


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_witness_deployment_floor_writer_policy_high_water_contract as previous


policy = previous.policy

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_durable_high_water"
)

PERSISTENT_MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_sqlite_reference"
)

STORE_ID = "a44-durable-policy-reference"


class A44DurableWriterPolicyContractTests(unittest.TestCase):

    def setUp(self):

        module = importlib.import_module(MODULE)

        self.reference_type = module.PolicyReference

        self.prepared_type = (
            module.PreparedPolicyPublication
        )

        self.state_type = (
            module.DurablePolicyHighWaterState
        )

        self.authority_type = (
            module.DurableWriterPolicyAuthority
        )

        self.gateway_type = (
            module.DurableWriterPolicyGateway
        )

        self.persistent = importlib.import_module(
            PERSISTENT_MODULE
        )

        self.h = (
            previous.A44MonotonicObservedWriterPolicyContractTests(
                "test_01_explicit_create_and_open_initialize_observed_reference"
            )
        )

        self.addCleanup(self.h.doCleanups)

        self.h.setUp()

        self.s = self.h.s
        self.p = self.h.p

        self.genesis = self.h.genesis

        self.store_path = (
            self.s.directory / "durable-policy-anchor.sqlite3"
        )

        self.authority = self.bootstrap()

        self.gateway = self.make_gateway()


    def ref(self, signed_policy, epoch):

        return self.reference_type(
            epoch=epoch,
            sha256=policy.digest(signed_policy),
        )


    def pair(self, signed_policy, epoch):

        return (
            epoch,
            policy.digest(signed_policy),
        )


    def parameters(self):

        return {
            "path": self.s.path,
            "high_water_path": self.store_path,
            "backend": self.p.backend,
            "expected_store_id": STORE_ID,
            "expected_policy_id": policy.POLICY_ID,
            "expected_policy_public_key": self.p.root_key,
            "expected_genesis_sha256": self.h.genesis_sha,
        }


    def bootstrap(self, **changes):

        params = self.parameters()

        params["initial_policy_reference"] = self.ref(
            self.genesis,
            1,
        )

        params.update(changes)

        return self.authority_type.bootstrap(
            **params
        )


    def reopen(self, **changes):

        params = self.parameters()

        params.update(changes)

        return self.authority_type.open(
            **params
        )


    def make_gateway(self, authority=None):

        if authority is None:
            authority = self.authority

        return self.gateway_type.from_authority(
            authority=authority,
        )


    def state(self, authority=None):

        if authority is None:
            authority = self.authority

        state = authority.durable_state()

        self.assertIs(type(state), self.state_type)

        self.assertIs(
            type(state.anchor),
            self.reference_type,
        )

        return state


    def assert_stable(
        self,
        signed_policy,
        epoch,
        authority=None,
    ):

        state = self.state(authority)

        self.assertEqual(
            state.anchor,
            self.ref(signed_policy, epoch),
        )

        self.assertIsNone(state.prepared)

        return state


    def assert_prepared(
        self,
        predecessor,
        predecessor_epoch,
        candidate,
        authority=None,
    ):

        state = self.state(authority)

        self.assertEqual(
            state.anchor,
            self.ref(
                predecessor,
                predecessor_epoch,
            ),
        )

        pending = state.prepared

        self.assertIs(
            type(pending),
            self.prepared_type,
        )

        self.assertEqual(
            pending.predecessor,
            state.anchor,
        )

        self.assertEqual(
            pending.candidate,
            self.ref(
                candidate,
                predecessor_epoch + 1,
            ),
        )

        self.assertIs(
            type(pending.signed_policy),
            tuple,
        )

        self.assertEqual(
            pending.signed_policy,
            candidate,
        )

        self.assertTrue(
            all(
                type(item) is bytes
                for item in pending.signed_policy
            )
        )

        return state


    def publish(self, signed_policy, authority=None):

        if authority is None:
            authority = self.authority

        return authority.publish_policy(
            signed_policy=signed_policy,
        )


    def recover(self, authority=None):

        if authority is None:
            authority = self.authority

        return authority.recover_publication()


    def send(
        self,
        signed_policy=None,
        gateway=None,
        **changes,
    ):

        if gateway is None:
            gateway = self.gateway

        return self.h.send(
            signed_policy,
            gateway=gateway,
            **changes,
        )


    def snapshot(self, name="old-policy.sqlite3"):

        return self.h.snapshot(name)


    def restore(self, path):

        self.h.restore(path)


    def assert_floor(self, epoch, operations):

        self.h.assert_floor(
            epoch,
            operations,
        )


    def assert_committed(self, result, epoch):

        self.assertEqual(
            (
                result["status"],
                result["epoch"],
            ),
            ("committed", epoch),
        )


    def assert_cas_blocked(
        self,
        *,
        gateway=None,
        signed_policy=None,
        **changes,
    ):

        if gateway is None:
            gateway = self.gateway

        request = self.h.request(
            signed_policy,
            **changes,
        )

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            side_effect=AssertionError(
                "Blocked writer request reached floor CAS"
            ),
        ) as backend_cas:

            with self.assertRaises(ValueError):

                gateway.exchange(request)

            backend_cas.assert_not_called()


    def assert_pending_blocks_operations(self):

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.authority.retired_writer_keys()

        self.assert_cas_blocked()


    def backup_database(self, source, destination):

        source = Path(source).resolve()

        destination = Path(destination).resolve()

        with closing(
            sqlite3.connect(
                source.as_uri() + "?mode=ro",
                uri=True,
            )
        ) as original:

            with closing(
                sqlite3.connect(str(destination))
            ) as copy:

                original.backup(copy)


    def public_read(self, gateway=None):

        if gateway is None:
            gateway = self.gateway

        client = self.p.f.fixture.make_client(
            transport=gateway,
        )

        return self.p.f.fixture.read(client)


    def public_lookup(self, gateway=None):

        if gateway is None:
            gateway = self.gateway

        raw = gateway.exchange(
            self.p.f.request(
                "lookup",
                challenge=b"l" * 32,
            )
        )

        return self.p.f.response(
            raw,
            operation="lookup",
            challenge=b"l" * 32,
        )


    def fail_publication(self, candidate, *, after_commit):

        """Inject failure at the existing policy transaction boundary.

        The PREPARED record must already be durably observable from
        an independently opened authority before policy commit.
        """

        peer = self.reopen()

        predecessor = self.state().anchor

        self.assertEqual(
            predecessor,
            self.ref(self.genesis, 1),
        )

        original_transaction = (
            self.persistent._transaction
        )

        reached = []

        @contextmanager
        def injected_transaction(pins, **arguments):

            candidate_written = False

            with original_transaction(
                pins,
                **arguments,
            ) as connection:

                yield connection

                row = connection.execute(
                    "SELECT policy_epoch "
                    "FROM writer_policy_head"
                ).fetchone()

                if row == (2,):

                    self.assert_prepared(
                        self.genesis,
                        1,
                        candidate,
                        authority=peer,
                    )

                    candidate_written = True

                    reached.append(
                        "prepared-before-policy-commit"
                    )

                    if not after_commit:

                        raise OSError(
                            "Injected policy precommit failure"
                        )

            if candidate_written and after_commit:

                reached.append(
                    "policy-commit-completed"
                )

                raise OSError(
                    "Injected policy commit acknowledgement loss"
                )

        with patch.object(
            self.persistent,
            "_transaction",
            injected_transaction,
        ):

            with self.assertRaises(ValueError):

                self.publish(candidate)

        expected = [
            "prepared-before-policy-commit"
        ]

        if after_commit:

            expected.append(
                "policy-commit-completed"
            )

        self.assertEqual(reached, expected)

        self.assert_prepared(
            self.genesis,
            1,
            candidate,
        )

        self.assert_prepared(
            self.genesis,
            1,
            candidate,
            authority=peer,
        )


    def test_01_explicit_bootstrap_and_open(self):

        self.assertTrue(
            self.store_path.is_file()
        )

        self.assert_stable(
            self.genesis,
            1,
        )

        fresh = self.reopen()

        self.assert_stable(
            self.genesis,
            1,
            fresh,
        )

        self.assertEqual(
            fresh.current_policy_reference(),
            self.pair(self.genesis, 1),
        )

        missing = (
            self.s.directory / "missing-anchor.sqlite3"
        )

        with self.assertRaises(ValueError):

            self.reopen(
                high_water_path=missing,
            )

        self.assertFalse(missing.exists())

        self.assert_floor(1, 0)


    def test_02_bootstrap_requires_trusted_exact_reference_and_no_overwrite(self):

        original = self.state()

        with self.assertRaises(ValueError):

            self.bootstrap()

        self.assertEqual(
            self.state(),
            original,
        )

        second = self.p.next_policy()

        self.h.publish_external(second)

        new_path = (
            self.s.directory / "other-anchor.sqlite3"
        )

        with self.assertRaises(ValueError):

            self.bootstrap(
                high_water_path=new_path,
            )

        self.assertFalse(new_path.exists())

        fresh = self.bootstrap(
            high_water_path=new_path,
            expected_store_id="a44-explicit-provisioning",
            initial_policy_reference=self.ref(
                second,
                2,
            ),
        )

        self.assert_stable(
            second,
            2,
            fresh,
        )

        self.assert_floor(1, 0)


    def test_03_successful_publication_persists_anchor_across_reopen(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.assertEqual(
            self.publish(second),
            self.pair(second, 2),
        )

        self.assert_stable(second, 2)

        fresh = self.reopen()

        self.assert_stable(
            second,
            2,
            fresh,
        )

        self.restore(old)

        with self.assertRaises(ValueError):

            self.reopen()

        self.assert_cas_blocked(
            gateway=self.make_gateway(fresh),
        )

        self.assert_stable(
            second,
            2,
            fresh,
        )

        self.assert_floor(1, 0)


    def test_04_independent_live_authority_shares_durable_anchor(self):

        peer = self.reopen()

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        # Peer has not performed a policy-sensitive read.

        self.assert_stable(
            second,
            2,
            peer,
        )

        self.restore(old)

        self.assert_cas_blocked(
            gateway=self.make_gateway(peer),
        )

        with self.assertRaises(ValueError):

            peer.current_policy_reference()

        self.assert_floor(1, 0)


    def test_05_historical_anchor_accepts_authenticated_descendants(self):

        second = self.p.next_policy()

        self.publish(second)

        third = self.p.next_policy(
            second
        )

        fourth = self.p.next_policy(
            third,
            revoked=("writer-alpha",),
        )

        self.h.publish_external(third)
        self.h.publish_external(fourth)

        self.assert_stable(second, 2)

        fresh = self.reopen()

        self.assert_stable(
            fourth,
            4,
            fresh,
        )

        self.assert_stable(fourth, 4)

        self.assertEqual(
            fresh.current_policy_reference(),
            self.pair(fourth, 4),
        )

        self.assert_committed(
            self.send(
                fourth,
                gateway=self.make_gateway(fresh),
                writer_id="writer-beta",
            ),
            2,
        )

        self.assert_floor(2, 1)


    def test_06_higher_conflicting_lineage_is_rejected(self):

        alternative_path = self.snapshot(
            "alternative.sqlite3"
        )

        alternate = self.s.reopen(
            path=alternative_path,
        )

        branch_a = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        branch_b = self.p.next_policy(
            revoked=("writer-beta",),
        )

        branch_b_next = self.p.next_policy(
            branch_b
        )

        self.publish(branch_a)

        self.s.publish(
            branch_b,
            authority=alternate,
        )

        with self.assertRaises(ValueError):

            self.reopen(
                path=alternative_path,
            )

        self.s.publish(
            branch_b_next,
            authority=alternate,
        )

        with self.assertRaises(ValueError):

            self.reopen(
                path=alternative_path,
            )

        self.restore(alternative_path)

        self.assert_cas_blocked(
            signed_policy=branch_b_next,
        )

        self.assert_stable(branch_a, 2)

        self.assert_floor(1, 0)


    def test_07_rejected_cas_commits_authenticated_observation(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish_external(second)

        self.assert_cas_blocked(
            signed_policy=self.genesis,
        )

        self.assert_stable(second, 2)

        self.restore(old)

        with self.assertRaises(ValueError):

            self.reopen()

        self.assert_cas_blocked()

        self.assert_stable(second, 2)

        self.assert_floor(1, 0)


    def test_08_retirement_read_persists_observed_anchor(self):

        old = self.snapshot()

        original = policy.public_key(
            self.p.f.alice,
        )

        writers = dict(
            self.p.f.writer_keys,
        )

        writers["writer-alpha"] = policy.public_key(
            self.p.f.attacker,
        )

        second = self.p.next_policy(
            writers=writers,
        )

        self.h.publish_external(second)

        self.assertEqual(
            self.authority.retired_writer_keys(),
            (original,),
        )

        self.assert_stable(second, 2)

        self.restore(old)

        with self.assertRaises(ValueError):

            self.reopen()

        self.assert_cas_blocked()

        self.assert_floor(1, 0)


    def test_09_backend_failure_cannot_undo_durable_observation(self):

        second = self.p.next_policy()

        self.h.publish_external(second)

        peer = self.reopen()

        # Reset the fixture to a separate fresh durable store
        # so the CAS itself performs the observation.

        old_store = (
            self.s.directory / "cas-observation.sqlite3"
        )

        old_policy = self.snapshot(
            "cas-observation-second.sqlite3"
        )

        # The original store is already at epoch 2.
        # Use a separate explicitly provisioned genesis fixture
        # by restoring a new policy copy at genesis is unnecessary:
        # the next extension is not yet observed.

        third = self.p.next_policy(second)

        self.h.publish_external(third)

        self.assert_stable(second, 2)

        observed_inside_backend = []

        def fail_backend(instance, **arguments):

            observed_inside_backend.append(
                self.state(peer)
            )

            raise OSError(
                "Injected floor backend failure"
            )

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            fail_backend,
        ):

            with self.assertRaises(ValueError):

                self.send(third)

        self.assertEqual(
            len(observed_inside_backend),
            1,
        )

        self.assertEqual(
            observed_inside_backend[0].anchor,
            self.ref(third, 3),
        )

        self.assertIsNone(
            observed_inside_backend[0].prepared,
        )

        self.assert_stable(third, 3)

        self.restore(old_policy)

        with self.assertRaises(ValueError):

            self.reopen()

        self.assert_floor(1, 0)


    def test_10_invalid_candidate_does_not_create_pending_state(self):

        second = self.p.next_policy()

        self.h.publish_external(second)

        invalid = self.p.next_policy(
            second,
            signer=self.p.f.attacker,
        )

        with self.assertRaises(ValueError):

            self.publish(invalid)

        self.assert_stable(second, 2)

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.assert_floor(1, 0)


    def test_11_precommit_failure_retains_prepared_candidate(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.fail_publication(
            second,
            after_commit=False,
        )

        self.s.assert_history(
            self.genesis
        )

        self.assert_pending_blocks_operations()

        self.assertEqual(
            self.recover(),
            self.pair(second, 2),
        )

        self.assert_stable(second, 2)

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.assert_cas_blocked(
            signed_policy=second,
        )

        self.assert_floor(1, 0)


    def test_12_postcommit_acknowledgement_loss_recovers_existing_candidate(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.fail_publication(
            second,
            after_commit=True,
        )

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.assert_pending_blocks_operations()

        self.assertEqual(
            self.recover(),
            self.pair(second, 2),
        )

        self.assertEqual(
            self.recover(),
            self.pair(second, 2),
        )

        self.assert_stable(second, 2)

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.assert_floor(1, 0)


    def test_13_postcommit_rollback_recovers_exact_prepared_candidate(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.fail_publication(
            second,
            after_commit=True,
        )

        self.restore(old)

        self.assert_pending_blocks_operations()

        self.assert_prepared(
            self.genesis,
            1,
            second,
        )

        self.assertEqual(
            self.recover(),
            self.pair(second, 2),
        )

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.assert_stable(second, 2)

        self.assert_cas_blocked(
            signed_policy=second,
        )

        self.assert_committed(
            self.send(
                second,
                writer_id="writer-beta",
            ),
            2,
        )

        self.assert_floor(2, 1)


    def test_14_pending_publication_cannot_be_replaced(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.assertNotEqual(
            policy.digest(second),
            policy.digest(alternative),
        )

        self.fail_publication(
            second,
            after_commit=False,
        )

        peer = self.reopen()

        with self.assertRaises(ValueError):

            self.publish(
                alternative,
                authority=peer,
            )

        with self.assertRaises(ValueError):

            self.publish(
                second,
                authority=peer,
            )

        self.assert_prepared(
            self.genesis,
            1,
            second,
            authority=peer,
        )

        self.assert_cas_blocked(
            gateway=self.make_gateway(peer),
        )

        self.assertEqual(
            self.recover(peer),
            self.pair(second, 2),
        )

        self.assert_stable(second, 2)

        self.assert_floor(1, 0)


    def test_15_fresh_authority_exposes_pending_state_without_clearing_it(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.fail_publication(
            second,
            after_commit=True,
        )

        self.restore(old)

        fresh = self.reopen()

        self.assert_prepared(
            self.genesis,
            1,
            second,
            authority=fresh,
        )

        self.assert_cas_blocked(
            gateway=self.make_gateway(fresh),
        )

        self.assertEqual(
            self.recover(fresh),
            self.pair(second, 2),
        )

        again = self.reopen()

        self.assert_stable(
            second,
            2,
            again,
        )

        self.assert_floor(1, 0)


    def test_16_public_signed_recovery_remains_available_while_pending(self):

        self.assert_committed(
            self.send(),
            2,
        )

        second = self.p.next_policy(
            revoked=(
                "writer-alpha",
                "writer-beta",
            ),
        )

        self.fail_publication(
            second,
            after_commit=False,
        )

        self.assertEqual(
            self.public_read()["epoch"],
            2,
        )

        self.assertEqual(
            self.public_lookup()["status"],
            "committed",
        )

        self.assert_cas_blocked(
            request=self.p.next_cas(),
        )

        self.assert_prepared(
            self.genesis,
            1,
            second,
        )

        self.assert_floor(2, 1)


    def test_17_missing_durable_store_fails_closed_without_recreation(self):

        self.assert_committed(
            self.send(),
            2,
        )

        self.store_path.unlink()

        with self.assertRaises(ValueError):

            self.reopen()

        with self.assertRaises(ValueError):

            self.authority.durable_state()

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.recover()

        self.assert_cas_blocked(
            request=self.p.next_cas(),
        )

        self.assertEqual(
            self.public_read()["epoch"],
            2,
        )

        self.assertEqual(
            self.public_lookup()["status"],
            "committed",
        )

        self.assertFalse(
            self.store_path.exists()
        )

        self.assert_floor(2, 1)


    def test_18_store_identity_and_database_aliases_are_rejected(self):

        with self.assertRaises(ValueError):

            self.reopen(
                expected_store_id="a44-wrong-store",
            )

        with self.assertRaises(ValueError):

            self.reopen(
                expected_policy_id="a44-wrong-policy",
            )

        with self.assertRaises(ValueError):

            self.reopen(
                expected_policy_public_key=policy.public_key(
                    self.p.f.attacker
                ),
            )

        with self.assertRaises(ValueError):

            self.reopen(
                expected_genesis_sha256="ab" * 32,
            )

        with self.assertRaises(ValueError):

            self.reopen(
                high_water_path=self.s.path,
            )

        with self.assertRaises(ValueError):

            self.reopen(
                high_water_path=self.p.backend._path,
            )

        with self.assertRaises(ValueError):

            self.reopen(
                path=self.store_path,
            )

        self.assert_stable(
            self.genesis,
            1,
        )

        self.assert_floor(1, 0)


    def test_19_corrupted_history_cannot_poison_durable_anchor(self):

        old = self.snapshot()

        second = self.p.next_policy()

        self.h.publish_external(second)

        self.s.execute_sql(
            "UPDATE writer_policy_history "
            "SET signature = zeroblob(64) "
            "WHERE policy_epoch = 2"
        )

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.reopen()

        self.assert_cas_blocked(
            signed_policy=second,
        )

        self.assert_stable(
            self.genesis,
            1,
        )

        self.restore(old)

        valid = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(valid)

        self.assert_stable(valid, 2)

        self.assert_floor(1, 0)


    def test_20_detached_immutable_state_and_prepared_objects(self):

        original = self.state()

        with self.assertRaises(AttributeError):

            original.anchor.epoch = 9

        with self.assertRaises(AttributeError):

            original.prepared = None

        second = self.p.next_policy()

        self.fail_publication(
            second,
            after_commit=False,
        )

        pending = self.assert_prepared(
            self.genesis,
            1,
            second,
        )

        with self.assertRaises(AttributeError):

            pending.prepared.signed_policy = self.genesis

        with self.assertRaises(AttributeError):

            pending.prepared.candidate.sha256 = "ab" * 32

        self.recover()

        self.assertIsNone(original.prepared)

        self.assertEqual(
            original.anchor,
            self.ref(self.genesis, 1),
        )

        self.assertEqual(
            pending.prepared.signed_policy,
            second,
        )

        self.assert_stable(second, 2)


    def test_21_shared_durable_fence_serializes_cas_and_copy_publication(self):

        alternative_path = self.snapshot(
            "concurrent-policy-copy.sqlite3"
        )

        publisher = self.reopen(
            path=alternative_path,
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        entered = threading.Event()
        release = threading.Event()
        publishing = threading.Event()

        backend_type = type(
            self.p.backend
        )

        original_cas = (
            backend_type.advance_if_current
        )

        def blocking_cas(instance, **arguments):

            entered.set()

            if not release.wait(timeout=20):

                raise TimeoutError(
                    "CAS release timed out"
                )

            return original_cas(
                instance,
                **arguments,
            )

        def publish_from_copy():

            publishing.set()

            return self.publish(
                second,
                authority=publisher,
            )

        with patch.object(
            backend_type,
            "advance_if_current",
            blocking_cas,
        ):

            with ThreadPoolExecutor(
                max_workers=2
            ) as pool:

                cas_future = pool.submit(
                    self.send
                )

                try:

                    self.assertTrue(
                        entered.wait(timeout=10)
                    )

                    publication = pool.submit(
                        publish_from_copy
                    )

                    self.assertTrue(
                        publishing.wait(timeout=5)
                    )

                    time.sleep(0.25)

                    self.assertFalse(
                        publication.done(),
                        "Publication escaped shared durable CAS fence",
                    )

                    self.assert_stable(
                        self.genesis,
                        1,
                    )

                finally:

                    release.set()

                self.assert_committed(
                    cas_future.result(timeout=40),
                    2,
                )

                self.assertEqual(
                    publication.result(timeout=40),
                    self.pair(second, 2),
                )

        self.assert_stable(second, 2)

        self.assert_cas_blocked(
            request=self.p.next_cas(),
        )

        self.assert_floor(2, 1)


    def test_22_distinct_policy_copies_share_one_durable_anchor(self):

        alternative_path = self.snapshot(
            "independent-policy-copy.sqlite3"
        )

        independent = self.reopen(
            path=alternative_path,
        )

        independent_gateway = self.make_gateway(
            independent
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        self.assert_stable(
            second,
            2,
            independent,
        )

        self.assert_cas_blocked(
            gateway=independent_gateway,
        )

        with self.assertRaises(ValueError):

            independent.current_policy_reference()

        with self.assertRaises(ValueError):

            self.reopen(
                path=alternative_path,
            )

        self.assert_committed(
            self.send(
                second,
                writer_id="writer-beta",
            ),
            2,
        )

        self.assert_floor(2, 1)


    def test_23_pending_recovery_rejects_conflicting_persisted_history(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        conflicting = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.fail_publication(
            second,
            after_commit=False,
        )

        # Legacy authority is deliberately outside the new fence.
        # Its publication simulates conflicting persistent history.

        self.h.publish_external(conflicting)

        with self.assertRaises(ValueError):

            self.recover()

        self.assert_prepared(
            self.genesis,
            1,
            second,
        )

        self.s.assert_history(
            self.genesis,
            conflicting,
        )

        self.assert_cas_blocked(
            signed_policy=conflicting,
        )

        self.restore(old)

        self.assertEqual(
            self.recover(),
            self.pair(second, 2),
        )

        self.assert_stable(second, 2)

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.assert_floor(1, 0)


    def test_24_simultaneous_store_rollback_is_explicit_trust_boundary(self):

        old_policy = self.snapshot()

        old_anchor = (
            self.s.directory / "old-anchor.sqlite3"
        )

        self.backup_database(
            self.store_path,
            old_anchor,
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        self.assert_stable(second, 2)

        # Deliberately violate the independent durable-store
        # trust assumption. This is not a protection test.

        self.restore(old_policy)

        self.backup_database(
            old_anchor,
            self.store_path,
        )

        fresh = self.reopen()

        self.assert_stable(
            self.genesis,
            1,
            fresh,
        )

        self.assertEqual(
            fresh.current_policy_reference(),
            self.pair(self.genesis, 1),
        )

        self.assert_floor(1, 0)


if __name__ == "__main__":
    unittest.main()
