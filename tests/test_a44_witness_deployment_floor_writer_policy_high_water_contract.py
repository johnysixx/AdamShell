"""A44 / 66.40B: monotonic observed writer policy contract.

Required production API:

MonotonicObservedWriterPolicyAuthority.create(
    *,
    path,
    backend,
    expected_policy_id,
    expected_policy_public_key,
    signed_genesis_policy,
    expected_genesis_sha256,
)

MonotonicObservedWriterPolicyAuthority.open(
    *,
    path,
    backend,
    expected_policy_id,
    expected_policy_public_key,
    expected_genesis_sha256,
    minimum_policy_epoch=1,
    expected_current_policy_sha256=None,
)

authority.current_policy_reference() -> tuple[int, str]
authority.observed_policy_reference() -> tuple[int, str]
authority.retired_writer_keys() -> tuple[bytes, ...]
authority.publish_policy(*, signed_policy)

MonotonicObservedWriterPolicyGateway.from_authority(
    *,
    authority,
)

gateway.exchange(request: bytes) -> bytes

SECURITY INVARIANTS

1. Opening fully authenticates the retained history and initializes
   the observed high-water reference to its authenticated head.

2. A previously observed reference is a permanent live lineage
   anchor for the lifetime of this authority instance.

3. Every subsequent authenticated history must contain that exact
   epoch and SHA-256 digest.

4. Fully authenticated extensions advance the observed reference.

5. The observed reference must never decrease or switch branches.

6. Current-policy reads and retirement reads advance the reference.

7. Authorized CAS advances the reference before backend mutation.

8. Rejected CAS also retains a fully authenticated current policy.

9. Backend errors and acknowledgement loss cannot undo observation.

10. Successful publication advances the reference only after the
    candidate has committed to the persistent policy store.

11. Failed publication must not retain an uncommitted candidate.
    However, an authenticated existing head observed during the
    attempted publication remains retained.

12. Invalid or incomplete history must never poison the reference.

13. Concurrent operations on the same authority must serialize
    high-water changes with policy-store transaction boundaries.

14. Existing cross-process SQLite policy/CAS fencing is preserved.

15. Public signed READ and LOOKUP remain available independently
    of writer-policy rollback detection.

16. observed_policy_reference() returns the last retained immutable
    reference without requiring access to the policy database.

LIMITS

The observed reference is in-memory and instance-local.
Fresh authorities need externally retained trust pins.
No independent durable monotonic root is implemented here.
Old gateways, independent policy copies and direct backend access
are not automatically fenced.
All database mutations in these tests affect temporary fixtures.
"""


import importlib
import sys
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_witness_deployment_floor_writer_policy_sqlite_contract as persistent


policy = persistent.policy

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_high_water"
)


class A44MonotonicObservedWriterPolicyContractTests(
    unittest.TestCase
):

    def setUp(self):

        module = importlib.import_module(
            MODULE
        )

        self.authority_type = (
            module.MonotonicObservedWriterPolicyAuthority
        )

        self.gateway_type = (
            module.MonotonicObservedWriterPolicyGateway
        )

        self.s = (
            persistent.A44PersistentWriterPolicyContractTests(
                "test_01_create_persists_exact_signed_genesis"
            )
        )

        self.addCleanup(
            self.s.doCleanups
        )

        self.s.setUp()

        self.p = self.s.p

        self.genesis = self.s.genesis

        self.genesis_sha = self.s.genesis_sha

        self.authority = self.open()

        self.gateway = self.make_gateway()


    def open(self, **changes):

        params = {
            "path": self.s.path,
            "backend": self.p.backend,
            "expected_policy_id": policy.POLICY_ID,
            "expected_policy_public_key": self.p.root_key,
            "expected_genesis_sha256": self.genesis_sha,
            "minimum_policy_epoch": 1,
            "expected_current_policy_sha256": None,
        }

        params.update(changes)

        return self.authority_type.open(
            **params
        )


    def create(self, **changes):

        params = {
            "path": self.s.path,
            "backend": self.p.backend,
            "expected_policy_id": policy.POLICY_ID,
            "expected_policy_public_key": self.p.root_key,
            "signed_genesis_policy": self.genesis,
            "expected_genesis_sha256": self.genesis_sha,
        }

        params.update(changes)

        return self.authority_type.create(
            **params
        )


    def make_gateway(self, authority=None):

        if authority is None:

            authority = self.authority

        return self.gateway_type.from_authority(
            authority=authority,
        )


    def reference(self, signed_policy, epoch):

        return (
            epoch,
            policy.digest(signed_policy),
        )


    def assert_observed(
        self,
        signed_policy,
        epoch,
        authority=None,
    ):

        if authority is None:

            authority = self.authority

        actual = authority.observed_policy_reference()

        self.assertIs(
            type(actual),
            tuple,
        )

        self.assertEqual(
            actual,
            self.reference(
                signed_policy,
                epoch,
            ),
        )


    def assert_current(
        self,
        signed_policy,
        epoch,
        authority=None,
    ):

        if authority is None:

            authority = self.authority

        self.assertEqual(
            authority.current_policy_reference(),
            self.reference(
                signed_policy,
                epoch,
            ),
        )


    def snapshot(self, name="old-policy.sqlite3"):

        path = self.s.directory / name

        self.s.backup(path)

        self.assertTrue(
            path.is_file()
        )

        return path


    def restore(self, path):

        self.s.restore_backup(path)


    def publish(
        self,
        signed_policy,
        authority=None,
    ):

        if authority is None:

            authority = self.authority

        return authority.publish_policy(
            signed_policy=signed_policy,
        )


    def publish_external(self, signed_policy):

        # Existing 66.39 authority publishes into the
        # same persistent policy database.

        return self.s.publish(
            signed_policy
        )


    def request(
        self,
        signed_policy=None,
        **changes,
    ):

        if signed_policy is None:

            signed_policy = self.genesis

        return self.p.authorized(
            policy=signed_policy,
            **changes,
        )


    def send(
        self,
        signed_policy=None,
        gateway=None,
        **changes,
    ):

        if gateway is None:

            gateway = self.gateway

        raw = self.request(
            signed_policy,
            **changes,
        )

        return self.p.send(
            raw,
            gateway=gateway,
        )


    def assert_floor(self, epoch, operations):

        self.assertEqual(
            self.p.f.fixture.fixture.read()["epoch"],
            epoch,
        )

        self.assertEqual(
            self.s.operation_count(),
            operations,
        )


    def assert_rollback_blocked(
        self,
        retained_policy,
        retained_epoch,
        *,
        request=None,
        floor_epoch=1,
        operations=0,
    ):

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.authority.retired_writer_keys()

        if request is None:

            request = self.request(
                self.genesis
            )

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            side_effect=AssertionError(
                "Rollback must not invoke floor CAS"
            ),
        ) as backend_cas:

            with self.assertRaises(ValueError):

                self.gateway.exchange(
                    request
                )

            backend_cas.assert_not_called()

        self.assert_observed(
            retained_policy,
            retained_epoch,
        )

        self.assert_floor(
            floor_epoch,
            operations,
        )


    def test_01_explicit_create_and_open_initialize_observed_reference(self):

        self.assert_observed(
            self.genesis,
            1,
        )

        self.assert_current(
            self.genesis,
            1,
        )

        new_path = (
            self.s.directory
            / "new-high-water-policy.sqlite3"
        )

        created = self.create(
            path=new_path,
        )

        self.assertTrue(
            new_path.is_file()
        )

        self.assert_observed(
            self.genesis,
            1,
            authority=created,
        )

        reopened = self.open(
            path=new_path,
        )

        self.assert_observed(
            self.genesis,
            1,
            authority=reopened,
        )

        with self.assertRaises(ValueError):

            self.create(
                path=new_path
            )

        missing = (
            self.s.directory
            / "missing-high-water.sqlite3"
        )

        with self.assertRaises(ValueError):

            self.open(
                path=missing
            )

        self.assertFalse(
            missing.exists()
        )

        self.assert_floor(1, 0)


    def test_02_own_successful_publication_retains_new_head(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.assertEqual(
            self.publish(second),
            self.reference(second, 2),
        )

        # No current-policy read is required.

        self.assert_observed(
            second,
            2,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
        )

        with self.assertRaises(ValueError):

            self.publish(second)

        self.s.assert_history(
            self.genesis,
        )

        self.assert_observed(
            second,
            2,
        )


    def test_03_external_head_observation_prevents_rollback(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish_external(
            second
        )

        self.assert_current(
            second,
            2,
        )

        self.assert_observed(
            second,
            2,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
        )


    def test_04_successful_cas_retains_authenticated_policy(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish_external(
            second
        )

        result = self.send(
            second,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            (
                result["status"],
                result["epoch"],
            ),
            ("committed", 2),
        )

        self.assert_observed(
            second,
            2,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
            request=self.request(
                self.genesis,
                request=self.p.next_cas(),
            ),
            floor_epoch=2,
            operations=1,
        )


    def test_05_rejected_stale_cas_retains_newer_authenticated_head(self):

        old = self.snapshot()

        stale_request = self.request()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish_external(
            second
        )

        with self.assertRaises(ValueError):

            self.gateway.exchange(
                stale_request
            )

        self.assert_observed(
            second,
            2,
        )

        self.assert_floor(1, 0)

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
            request=stale_request,
        )


    def test_06_revoked_current_writer_rejection_retains_head(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish_external(
            second
        )

        current_request = self.request(
            second
        )

        with self.assertRaises(ValueError):

            self.gateway.exchange(
                current_request
            )

        self.assert_observed(
            second,
            2,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
        )


    def test_07_retirement_read_advances_observed_lineage(self):

        old = self.snapshot()

        original_key = policy.public_key(
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

        self.publish_external(
            second
        )

        self.assertEqual(
            self.authority.retired_writer_keys(),
            (original_key,),
        )

        self.assert_observed(
            second,
            2,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
        )


    def test_08_observed_same_epoch_fork_is_rejected(self):

        alternative_path = self.snapshot(
            "alternative.sqlite3"
        )

        alternative = self.s.reopen(
            path=alternative_path
        )

        branch_a = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        branch_b = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.assertNotEqual(
            policy.digest(branch_a),
            policy.digest(branch_b),
        )

        self.publish_external(
            branch_a
        )

        self.s.publish(
            branch_b,
            authority=alternative,
        )

        self.assert_current(
            branch_a,
            2,
        )

        self.assert_observed(
            branch_a,
            2,
        )

        self.restore(
            alternative_path
        )

        self.assert_rollback_blocked(
            branch_a,
            2,
            request=self.request(
                branch_b
            ),
        )


    def test_09_higher_epoch_on_conflicting_lineage_is_rejected(self):

        alternative_path = self.snapshot(
            "higher-fork.sqlite3"
        )

        alternative = self.s.reopen(
            path=alternative_path
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

        self.publish_external(
            branch_a
        )

        self.assert_current(
            branch_a,
            2,
        )

        self.s.publish(
            branch_b,
            authority=alternative,
        )

        self.s.publish(
            branch_b_next,
            authority=alternative,
        )

        self.restore(
            alternative_path
        )

        self.assert_rollback_blocked(
            branch_a,
            2,
            request=self.request(
                branch_b_next
            ),
        )

        self.s.assert_history(
            self.genesis,
            branch_b,
            branch_b_next,
        )


    def test_10_valid_history_extension_may_advance_multiple_epochs(self):

        second = self.p.next_policy()

        third = self.p.next_policy(
            second
        )

        fourth = self.p.next_policy(
            third,
            revoked=("writer-alpha",),
        )

        self.publish_external(
            second
        )

        self.assert_current(
            second,
            2,
        )

        self.publish_external(
            third
        )

        self.publish_external(
            fourth
        )

        self.assert_current(
            fourth,
            4,
        )

        self.assert_observed(
            fourth,
            4,
        )

        self.s.assert_history(
            self.genesis,
            second,
            third,
            fourth,
        )

        result = self.send(
            fourth,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.assert_observed(
            fourth,
            4,
        )

        self.assert_floor(2, 1)


    def test_11_corrupted_history_does_not_poison_observed_reference(self):

        old = self.snapshot()

        second = self.p.next_policy()

        self.publish_external(
            second
        )

        self.s.execute_sql(
            "UPDATE writer_policy_history "
            "SET signature = zeroblob(64) "
            "WHERE policy_epoch = 2"
        )

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.authority.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.send(second)

        self.assert_observed(
            self.genesis,
            1,
        )

        self.assert_floor(1, 0)

        self.restore(old)

        # A different valid epoch 2 policy is acceptable
        # because the corrupted history was never authenticated.

        valid = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(valid)

        self.assert_observed(
            valid,
            2,
        )

        self.assert_current(
            valid,
            2,
        )

        self.s.assert_history(
            self.genesis,
            valid,
        )


    def test_12_failed_publication_retains_existing_head_not_candidate(self):

        old = self.snapshot()

        second = self.p.next_policy()

        third = self.p.next_policy(
            second,
            revoked=("writer-alpha",),
        )

        self.publish_external(
            second
        )

        current_snapshot = self.snapshot(
            "committed-second.sqlite3"
        )

        self.s.execute_sql(
            """
            CREATE TRIGGER a44_fail_high_water_publication
            BEFORE UPDATE ON writer_policy_head
            BEGIN
                SELECT RAISE(
                    ABORT,
                    'injected high-water publication failure'
                );
            END
            """
        )

        try:

            with self.assertRaises(ValueError):

                self.publish(third)

            self.assert_observed(
                second,
                2,
            )

            self.s.assert_history(
                self.genesis,
                second,
            )

        finally:

            self.s.execute_sql(
                "DROP TRIGGER a44_fail_high_water_publication"
            )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
        )

        self.restore(
            current_snapshot
        )

        self.assert_current(
            second,
            2,
        )

        self.publish(third)

        self.assert_observed(
            third,
            3,
        )

        self.s.assert_history(
            self.genesis,
            second,
            third,
        )


    def test_13_invalid_candidate_cannot_advance_observed_reference(self):

        invalid = (
            self.p.next_policy(
                signer=self.p.f.attacker,
            ),
            self.p.next_policy(
                epoch=3,
            ),
            self.p.policy(
                epoch=2,
                previous="ab" * 32,
            ),
        )

        for candidate in invalid:

            with self.subTest(
                candidate=policy.digest(candidate),
            ):

                with self.assertRaises(ValueError):

                    self.publish(candidate)

                self.assert_observed(
                    self.genesis,
                    1,
                )

                self.s.assert_history(
                    self.genesis,
                )

                self.assert_floor(1, 0)

        valid = self.p.next_policy()

        self.publish(valid)

        self.assert_observed(
            valid,
            2,
        )


    def test_14_rejected_stale_publication_retains_authenticated_current_head(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        conflicting = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.publish_external(
            second
        )

        # This candidate is validly signed, but it does not
        # extend the already committed current policy.

        with self.assertRaises(ValueError):

            self.publish(
                conflicting
            )

        self.assert_observed(
            second,
            2,
        )

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
        )


    def test_15_precommit_backend_failure_cannot_undo_observation(self):

        old = self.snapshot()

        second = self.p.next_policy()

        self.publish_external(
            second
        )

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            side_effect=OSError(
                "Injected precommit CAS failure"
            ),
        ):

            with self.assertRaises(ValueError):

                self.send(second)

        self.assert_observed(
            second,
            2,
        )

        self.assert_floor(1, 0)

        latest = self.snapshot(
            "latest-after-failure.sqlite3"
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
        )

        self.restore(latest)

        result = self.send(second)

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.assert_observed(
            second,
            2,
        )

        self.assert_floor(2, 1)


    def test_16_postcommit_reply_loss_cannot_undo_observation(self):

        old = self.snapshot()

        second = self.p.next_policy()

        self.publish_external(
            second
        )

        backend_type = type(
            self.p.backend
        )

        original = (
            backend_type.advance_if_current
        )

        def lost_reply(
            instance,
            **arguments,
        ):

            original(
                instance,
                **arguments,
            )

            raise OSError(
                "Injected postcommit reply loss"
            )

        with patch.object(
            backend_type,
            "advance_if_current",
            lost_reply,
        ):

            with self.assertRaises(ValueError):

                self.send(second)

        self.assert_floor(2, 1)

        self.assert_observed(
            second,
            2,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
            request=self.request(
                self.genesis,
                request=self.p.next_cas(),
            ),
            floor_epoch=2,
            operations=1,
        )

        raw = self.gateway.exchange(
            self.p.f.request(
                "lookup",
                challenge=b"l" * 32,
            )
        )

        result = self.p.f.response(
            raw,
            operation="lookup",
            challenge=b"l" * 32,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.assert_observed(
            second,
            2,
        )

        self.assert_floor(2, 1)


    def test_17_concurrent_publications_cannot_regress_observed_head(self):

        old = self.snapshot()

        first = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        second = self.p.next_policy(
            revoked=("writer-beta",),
        )

        barrier = threading.Barrier(2)

        def attempt(candidate):

            barrier.wait(
                timeout=5
            )

            try:

                result = self.publish(
                    candidate
                )

            except ValueError:

                return None

            self.assertEqual(
                result,
                self.reference(
                    candidate,
                    2,
                ),
            )

            return candidate

        with ThreadPoolExecutor(
            max_workers=2
        ) as pool:

            future_a = pool.submit(
                attempt,
                first,
            )

            future_b = pool.submit(
                attempt,
                second,
            )

            results = (
                future_a.result(
                    timeout=40
                ),
                future_b.result(
                    timeout=40
                ),
            )

        winners = [
            item
            for item in results
            if item is not None
        ]

        self.assertEqual(
            len(winners),
            1,
        )

        winner = winners[0]

        self.assert_observed(
            winner,
            2,
        )

        self.assert_current(
            winner,
            2,
        )

        self.s.assert_history(
            self.genesis,
            winner,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            winner,
            2,
        )


    def test_18_public_read_and_lookup_survive_detected_policy_rollback(self):

        old = self.snapshot()

        self.assertEqual(
            self.send()["status"],
            "committed",
        )

        second = self.p.next_policy(
            revoked=(
                "writer-alpha",
                "writer-beta",
            ),
        )

        self.publish(second)

        self.assert_observed(
            second,
            2,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
            request=self.request(
                self.genesis,
                request=self.p.next_cas(),
            ),
            floor_epoch=2,
            operations=1,
        )

        raw = self.gateway.exchange(
            self.p.f.request(
                "lookup",
                challenge=b"l" * 32,
            )
        )

        lookup = self.p.f.response(
            raw,
            operation="lookup",
            challenge=b"l" * 32,
        )

        self.assertEqual(
            lookup["status"],
            "committed",
        )

        client = self.p.f.fixture.make_client(
            transport=self.gateway,
        )

        self.assertEqual(
            self.p.f.fixture.read(client)["epoch"],
            2,
        )

        self.assert_observed(
            second,
            2,
        )

        self.assert_floor(2, 1)


    def test_19_reopen_with_retained_external_reference_rejects_rollback(self):

        old = self.snapshot()

        second = self.p.next_policy()

        self.publish(second)

        retained = (
            self.authority.observed_policy_reference()
        )

        self.assertEqual(
            retained,
            self.reference(second, 2),
        )

        reopened = self.open(
            minimum_policy_epoch=retained[0],
            expected_current_policy_sha256=retained[1],
        )

        self.assert_observed(
            second,
            2,
            authority=reopened,
        )

        self.restore(old)

        with self.assertRaises(ValueError):

            self.open(
                minimum_policy_epoch=retained[0],
            )

        with self.assertRaises(ValueError):

            self.open(
                expected_current_policy_sha256=retained[1],
            )

        with self.assertRaises(ValueError):

            reopened.current_policy_reference()

        self.assert_observed(
            second,
            2,
            authority=reopened,
        )

        self.assert_floor(1, 0)


    def test_20_fresh_unpinned_authority_remains_known_restart_limit(self):

        old = self.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        self.assert_observed(
            second,
            2,
        )

        self.restore(old)

        self.assert_rollback_blocked(
            second,
            2,
        )

        # Known limit:
        # A new authority receives only the genesis trust pin.
        # It does not inherit another instance's live high-water.

        fresh = self.open()

        self.assert_observed(
            self.genesis,
            1,
            authority=fresh,
        )

        self.assert_current(
            self.genesis,
            1,
            authority=fresh,
        )

        self.assert_observed(
            second,
            2,
        )

        self.assert_floor(1, 0)

        # The original authority is protected, while the fresh
        # instance cannot distinguish an older valid database
        # without the retained external reference.


if __name__ == "__main__":
    unittest.main()
