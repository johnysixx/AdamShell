"""A44 / 66.40D monotonic observed policy adversarial regression.

All keys, databases, snapshots and injected failures are temporary
test fixtures.

This suite distinguishes live observation guarantees from independent
durable rollback protection.

Tests documenting a known limitation do not establish protection
against that limitation.
"""

import importlib
import os
import sqlite3
import sys
import threading
import time
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_witness_deployment_floor_writer_policy_high_water_contract as high_contract

import test_a44_witness_deployment_floor_writer_policy_sqlite_adversarial as legacy_adversarial


policy = high_contract.policy

MODULE = high_contract.MODULE

production = importlib.import_module(
    MODULE
)

persistent = production.persistent


class A44MonotonicObservedWriterPolicyAdversarialTests(
    unittest.TestCase
):

    def setUp(self):

        self.h = (
            high_contract.A44MonotonicObservedWriterPolicyContractTests(
                "test_01_explicit_create_and_open_initialize_observed_reference"
            )
        )

        self.addCleanup(
            self.h.doCleanups
        )

        self.h.setUp()

        self.s = self.h.s
        self.p = self.h.p

        self.authority = self.h.authority
        self.gateway = self.h.gateway

        self.genesis = self.h.genesis

    def observed(self):

        return self.authority.observed_policy_reference()

    def assert_observed(self, signed_policy, epoch):

        self.h.assert_observed(
            signed_policy,
            epoch,
        )

    def public_read(self, gateway=None):

        if gateway is None:

            gateway = self.gateway

        client = self.p.f.fixture.make_client(
            transport=gateway,
        )

        return self.p.f.fixture.read(
            client
        )

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

    def worker_helper(self):

        helper = (
            legacy_adversarial.A44PersistentWriterPolicyAdversarialTests(
                "test_01_stale_gateway_in_separate_process_observes_revocation"
            )
        )

        # Reuse the already verified subprocess harness.
        # Do not create an additional fixture or database.

        helper.s = self.s
        helper.p = self.p

        return helper

    def test_01_frozen_authority_gateway_and_reinitialization_guard(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish(
            second
        )

        retained = self.observed()

        self.assertIs(
            type(retained),
            tuple,
        )

        with self.assertRaises(
            FrozenInstanceError
        ):

            self.authority._observed = (
                1,
                self.h.genesis_sha,
            )

        with self.assertRaises(
            FrozenInstanceError
        ):

            self.gateway._authority = (
                self.h.open()
            )

        with self.assertRaises(
            ValueError
        ):

            self.authority.__init__(
                path=self.s.path,
                backend=self.p.backend,
                expected_policy_id=policy.POLICY_ID,
                expected_policy_public_key=self.p.root_key,
                expected_genesis_sha256=self.h.genesis_sha,
            )

        with self.assertRaises(
            ValueError
        ):

            self.authority._initialize_from_opened(
                self.s.authority
            )

        with self.assertRaises(
            ValueError
        ):

            self.h.gateway_type.from_authority(
                authority=self.s.authority,
            )

        self.assertEqual(
            self.observed(),
            retained,
        )

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_floor(1, 0)


    def test_02_observed_reference_remains_available_without_policy_database(self):

        second = self.p.next_policy()

        self.h.publish(second)

        retained = self.observed()

        self.s.path.unlink()

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.authority.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.h.send(second)

        self.assertEqual(
            self.observed(),
            retained,
        )

        self.assertFalse(
            self.s.path.exists()
        )

        self.h.assert_floor(1, 0)


    def test_03_invalid_candidate_signature_retains_authenticated_existing_head(self):

        old = self.h.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish_external(
            second
        )

        invalid = self.p.next_policy(
            second,
            signer=self.p.f.attacker,
        )

        with self.assertRaises(ValueError):

            self.h.publish(
                invalid
            )

        self.assert_observed(
            second,
            2,
        )

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.h.restore(old)

        self.h.assert_rollback_blocked(
            second,
            2,
        )


    def test_04_corrupted_newer_tail_cannot_replace_existing_anchor(self):

        second = self.p.next_policy()

        self.h.publish(second)

        third = self.p.next_policy(
            second
        )

        fourth = self.p.next_policy(
            third
        )

        self.h.publish_external(third)
        self.h.publish_external(fourth)

        valid = self.h.snapshot(
            "valid-fourth.sqlite3"
        )

        self.s.execute_sql(
            "UPDATE writer_policy_history "
            "SET signature = zeroblob(64) "
            "WHERE policy_epoch = 4"
        )

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.authority.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.h.send(fourth)

        # Even the valid intermediate third policy must
        # not be retained from an incomplete verification.

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_floor(1, 0)

        self.h.restore(valid)

        self.h.assert_current(
            fourth,
            4,
        )

        self.assert_observed(
            fourth,
            4,
        )


    def test_05_invalid_persistent_head_cannot_poison_observed_reference(self):

        old = self.h.snapshot()

        second = self.p.next_policy()

        self.h.publish_external(
            second
        )

        self.s.execute_sql(
            "UPDATE writer_policy_head "
            "SET policy_sha256 = ?",
            ("ab" * 32,),
        )

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.h.send(second)

        self.assert_observed(
            self.genesis,
            1,
        )

        self.h.assert_floor(1, 0)

        self.h.restore(old)

        alternative = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish(
            alternative
        )

        self.assert_observed(
            alternative,
            2,
        )


    def test_06_correct_lineage_extension_recovers_after_rollback_detection(self):

        old = self.h.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish(second)

        third = self.p.next_policy(
            second
        )

        self.h.publish_external(third)

        latest = self.h.snapshot(
            "latest-valid.sqlite3"
        )

        self.h.restore(old)

        self.h.assert_rollback_blocked(
            second,
            2,
        )

        self.h.restore(latest)

        self.h.assert_current(
            third,
            3,
        )

        self.assert_observed(
            third,
            3,
        )

        result = self.h.send(
            third,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.h.assert_floor(2, 1)


    def test_07_retirement_observation_rejects_conflicting_valid_lineage(self):

        alternative_path = self.h.snapshot(
            "retirement-alternative.sqlite3"
        )

        alternative = self.s.reopen(
            path=alternative_path,
        )

        writers = dict(
            self.p.f.writer_keys
        )

        original_key = policy.public_key(
            self.p.f.alice
        )

        writers["writer-alpha"] = policy.public_key(
            self.p.f.attacker
        )

        second = self.p.next_policy(
            writers=writers,
        )

        self.h.publish_external(second)

        self.assertEqual(
            self.authority.retired_writer_keys(),
            (original_key,),
        )

        branch_b = self.p.next_policy()

        self.s.publish(
            branch_b,
            authority=alternative,
        )

        branch_b_next = self.p.next_policy(
            branch_b
        )

        self.s.publish(
            branch_b_next,
            authority=alternative,
        )

        valid = self.h.snapshot(
            "retirement-valid.sqlite3"
        )

        self.h.restore(
            alternative_path
        )

        self.h.assert_rollback_blocked(
            second,
            2,
            request=self.h.request(
                branch_b_next
            ),
        )

        self.h.restore(valid)

        self.assertEqual(
            self.authority.retired_writer_keys(),
            (original_key,),
        )

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_floor(1, 0)


    def test_08_high_water_is_advanced_before_floor_backend_invocation(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish_external(
            second
        )

        backend_type = type(
            self.p.backend
        )

        original = (
            backend_type.advance_if_current
        )

        observed_inside_backend = []

        def inspect_cas(
            instance,
            **arguments,
        ):

            observed_inside_backend.append(
                self.observed()
            )

            self.h.assert_floor(1, 0)

            return original(
                instance,
                **arguments,
            )

        with patch.object(
            backend_type,
            "advance_if_current",
            inspect_cas,
        ):

            result = self.h.send(
                second,
                writer_id="writer-beta",
                signer=self.p.f.bob,
            )

        self.assertEqual(
            observed_inside_backend,
            [
                self.h.reference(
                    second,
                    2,
                )
            ],
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.h.assert_floor(2, 1)


    def test_09_invalid_writer_signature_still_retains_authenticated_head(self):

        old = self.h.snapshot()

        second = self.p.next_policy()

        self.h.publish_external(second)

        request = self.h.request(
            second,
            signer=self.p.f.attacker,
        )

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            side_effect=AssertionError(
                "Invalid signer reached floor CAS"
            ),
        ) as backend_cas:

            with self.assertRaises(ValueError):

                self.gateway.exchange(
                    request
                )

            backend_cas.assert_not_called()

        self.assert_observed(
            second,
            2,
        )

        self.h.restore(old)

        self.h.assert_rollback_blocked(
            second,
            2,
        )


    def test_10_malformed_outer_envelope_does_not_claim_observation(self):

        second = self.p.next_policy()

        self.h.publish_external(
            second
        )

        # An invalid outer envelope is rejected before
        # a policy-sensitive transaction is entered.

        with self.assertRaises(ValueError):

            self.gateway.exchange(
                b"{}"
            )

        self.assert_observed(
            self.genesis,
            1,
        )

        self.h.assert_floor(1, 0)

        self.h.assert_current(
            second,
            2,
        )

        self.assert_observed(
            second,
            2,
        )


    def test_11_public_recovery_does_not_advance_policy_observation(self):

        result = self.h.send()

        self.assertEqual(
            result["status"],
            "committed",
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish_external(second)

        self.assertEqual(
            self.public_read()["epoch"],
            2,
        )

        self.assertEqual(
            self.public_lookup()["status"],
            "committed",
        )

        self.assert_observed(
            self.genesis,
            1,
        )

        self.h.assert_floor(2, 1)

        self.h.assert_current(
            second,
            2,
        )

        self.assert_observed(
            second,
            2,
        )


    def test_12_public_recovery_survives_missing_policy_database(self):

        self.assertEqual(
            self.h.send()["status"],
            "committed",
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish(second)

        self.s.path.unlink()

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.h.send(
                second,
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
            self.s.path.exists()
        )

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_floor(2, 1)


    def test_13_failure_after_candidate_verification_before_commit_rolls_back(self):

        second = self.p.next_policy()

        self.h.publish_external(
            second
        )

        third = self.p.next_policy(
            second,
            revoked=("writer-alpha",),
        )

        original_transaction = (
            persistent._transaction
        )

        injection_reached = []

        @contextmanager
        def fail_before_commit(
            pins,
            **arguments,
        ):

            with original_transaction(
                pins,
                **arguments,
            ) as connection:

                yield connection

                row = connection.execute(
                    "SELECT policy_epoch "
                    "FROM writer_policy_head"
                ).fetchone()

                self.assertEqual(
                    row,
                    (3,),
                )

                injection_reached.append(True)

                raise OSError(
                    "Injected failure before policy commit"
                )

        with patch.object(
            persistent,
            "_transaction",
            fail_before_commit,
        ):

            with self.assertRaises(ValueError):

                self.h.publish(third)

        self.assertEqual(
            injection_reached,
            [True],
        )

        self.assert_observed(
            second,
            2,
        )

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.h.publish(third)

        self.assert_observed(
            third,
            3,
        )

        self.s.assert_history(
            self.genesis,
            second,
            third,
        )

        self.h.assert_floor(1, 0)


    def test_14_postcommit_policy_acknowledgement_loss_recovers_by_observation(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        original_transaction = (
            persistent._transaction
        )

        committed = []

        @contextmanager
        def lose_commit_acknowledgement(
            pins,
            **arguments,
        ):

            with original_transaction(
                pins,
                **arguments,
            ) as connection:

                yield connection

            committed.append(True)

            raise OSError(
                "Injected policy commit acknowledgement loss"
            )

        with patch.object(
            persistent,
            "_transaction",
            lose_commit_acknowledgement,
        ):

            with self.assertRaises(ValueError):

                self.h.publish(second)

        self.assertEqual(
            committed,
            [True],
        )

        # The transaction committed, although publication
        # did not return a successful acknowledgement.

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.assert_observed(
            self.genesis,
            1,
        )

        # Explicit recovery authenticates the durable head.

        self.h.assert_current(
            second,
            2,
        )

        self.assert_observed(
            second,
            2,
        )

        with self.assertRaises(ValueError):

            self.h.publish(second)

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_floor(1, 0)


    def test_15_ambiguous_commit_before_reobservation_is_known_limit(self):

        old = self.h.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        original_transaction = (
            persistent._transaction
        )

        @contextmanager
        def lose_acknowledgement(
            pins,
            **arguments,
        ):

            with original_transaction(
                pins,
                **arguments,
            ) as connection:

                yield connection

            raise OSError(
                "Injected postcommit policy acknowledgement loss"
            )

        with patch.object(
            persistent,
            "_transaction",
            lose_acknowledgement,
        ):

            with self.assertRaises(ValueError):

                self.h.publish(second)

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.assert_observed(
            self.genesis,
            1,
        )

        # Known limit: the commit completed but its result
        # was lost before live high-water advancement.
        # Restore the old store before recovery can observe
        # the committed policy.

        self.h.restore(old)

        self.h.assert_current(
            self.genesis,
            1,
        )

        self.assert_observed(
            self.genesis,
            1,
        )

        self.h.assert_floor(1, 0)


    def test_16_instance_lock_covers_commit_to_observed_reference_boundary(self):

        second = self.p.next_policy()

        original_transaction = (
            persistent._transaction
        )

        committed = threading.Event()
        release = threading.Event()
        observer_started = threading.Event()

        @contextmanager
        def pause_after_commit(
            pins,
            **arguments,
        ):

            with original_transaction(
                pins,
                **arguments,
            ) as connection:

                yield connection

            if not committed.is_set():

                committed.set()

                if not release.wait(
                    timeout=15
                ):

                    raise TimeoutError(
                        "Publication boundary release timed out"
                    )

        def observe():

            observer_started.set()

            return self.observed()

        with patch.object(
            persistent,
            "_transaction",
            pause_after_commit,
        ):

            with ThreadPoolExecutor(
                max_workers=2
            ) as pool:

                publication = pool.submit(
                    self.h.publish,
                    second,
                )

                try:

                    self.assertTrue(
                        committed.wait(timeout=10)
                    )

                    self.s.assert_history(
                        self.genesis,
                        second,
                    )

                    observer = pool.submit(
                        observe
                    )

                    self.assertTrue(
                        observer_started.wait(
                            timeout=5
                        )
                    )

                    time.sleep(0.2)

                    self.assertFalse(
                        observer.done(),
                        "Observer escaped instance publication lock",
                    )

                finally:

                    release.set()

                published = publication.result(
                    timeout=20
                )

                observed = observer.result(
                    timeout=20
                )

        expected = self.h.reference(
            second,
            2,
        )

        self.assertEqual(
            published,
            expected,
        )

        self.assertEqual(
            observed,
            expected,
        )

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_floor(1, 0)


    def test_17_all_gateways_of_same_authority_share_live_high_water(self):

        old = self.h.snapshot()

        gateway_a = self.h.make_gateway()
        gateway_b = self.h.make_gateway()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish_external(second)

        with self.assertRaises(ValueError):

            gateway_a.exchange(
                self.h.request(
                    second
                )
            )

        self.assert_observed(
            second,
            2,
        )

        self.h.restore(old)

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            side_effect=AssertionError(
                "Shared gateway rollback reached floor CAS"
            ),
        ) as backend_cas:

            with self.assertRaises(ValueError):

                gateway_b.exchange(
                    self.h.request()
                )

            backend_cas.assert_not_called()

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_floor(1, 0)


    def test_18_independent_live_high_water_is_not_globally_shared_known_limit(self):

        independent = self.h.open()

        old = self.h.snapshot()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.h.publish(second)

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_observed(
            self.genesis,
            1,
            authority=independent,
        )

        self.h.restore(old)

        self.h.assert_rollback_blocked(
            second,
            2,
        )

        # Another already opened authority that never
        # authenticated epoch 2 has no shared high-water.

        self.h.assert_current(
            self.genesis,
            1,
            authority=independent,
        )

        self.h.assert_observed(
            self.genesis,
            1,
            authority=independent,
        )

        self.h.assert_floor(1, 0)


    def test_19_cross_process_publication_waits_for_high_water_cas(self):

        helper = self.worker_helper()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        entered = threading.Event()
        release = threading.Event()

        backend_type = type(
            self.p.backend
        )

        original_cas = (
            backend_type.advance_if_current
        )

        def blocking_cas(
            instance,
            **arguments,
        ):

            entered.set()

            if not release.wait(
                timeout=20
            ):

                raise TimeoutError(
                    "High-water CAS release timed out"
                )

            return original_cas(
                instance,
                **arguments,
            )

        with helper.worker(
            "high-water-publisher",
            "publish",
            signed_policy=second,
        ) as (publisher, signals):

            with patch.object(
                backend_type,
                "advance_if_current",
                blocking_cas,
            ):

                with ThreadPoolExecutor(
                    max_workers=1
                ) as pool:

                    cas_future = pool.submit(
                        self.h.send
                    )

                    try:

                        self.assertTrue(
                            entered.wait(
                                timeout=10
                            )
                        )

                        # Independent connection proves
                        # that the policy SQLite writer
                        # lock remains held during CAS.

                        with closing(
                            sqlite3.connect(
                                str(self.s.path),
                                timeout=0.1,
                                isolation_level=None,
                            )
                        ) as probe:

                            try:

                                with self.assertRaisesRegex(
                                    sqlite3.OperationalError,
                                    "locked|busy",
                                ):

                                    probe.execute(
                                        "BEGIN IMMEDIATE"
                                    )

                            finally:

                                if probe.in_transaction:

                                    probe.rollback()

                        signals["go"].touch()

                        helper.wait_signal(
                            signals["started"],
                            publisher,
                        )

                        time.sleep(0.2)

                        self.assertIsNone(
                            publisher.poll(),
                            "Publication escaped high-water CAS fence",
                        )

                    finally:

                        release.set()

                    result = cas_future.result(
                        timeout=30
                    )

            published = helper.finish_worker(
                publisher
            )

        self.assertNotEqual(
            published["pid"],
            os.getpid(),
        )

        helper.assert_opening_genesis(
            published
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.assertEqual(
            published["status"],
            "published",
        )

        # The local CAS observed genesis. The independent
        # publisher advanced policy only after CAS completed.

        self.assert_observed(
            self.genesis,
            1,
        )

        self.h.assert_current(
            second,
            2,
        )

        with self.assertRaises(ValueError):

            self.h.send(
                second,
                request=self.p.next_cas(),
            )

        self.assert_observed(
            second,
            2,
        )

        self.h.assert_floor(2, 1)


    def test_20_independent_high_water_process_rejects_stale_writer(self):

        helper = self.worker_helper()

        # Adapt the previously verified subprocess program
        # to instantiate the new high-water authority.
        #
        # No committed test source is modified.

        original_source = (
            legacy_adversarial.WORKER_SOURCE
        )

        replacements = (
            (
                'config["policy_module"]',
                repr(MODULE),
            ),
            (
                "module.SQLitePersistentWriterPolicyAuthority.open(",
                "module.MonotonicObservedWriterPolicyAuthority.open(",
            ),
            (
                "module.PersistentWriterPolicyGateway.from_authority(",
                "module.MonotonicObservedWriterPolicyGateway.from_authority(",
            ),
        )

        worker_source = original_source

        for old, new in replacements:

            self.assertEqual(
                worker_source.count(old),
                1,
                "Unexpected subprocess source shape",
            )

            worker_source = worker_source.replace(
                old,
                new,
                1,
            )

        compile(
            worker_source,
            "<high-water-adversarial-worker>",
            "exec",
        )

        request = self.h.request()

        with patch.object(
            legacy_adversarial,
            "WORKER_SOURCE",
            worker_source,
        ):

            with helper.worker(
                "high-water-stale-process",
                "cas",
                request=request,
            ) as (process, signals):

                second = self.p.next_policy(
                    revoked=("writer-alpha",),
                )

                self.h.publish(second)

                signals["go"].touch()

                result = helper.finish_worker(
                    process
                )

        helper.assert_opening_genesis(
            result
        )

        self.assertNotEqual(
            result["pid"],
            os.getpid(),
        )

        self.assertEqual(
            result["status"],
            "rejected",
        )

        self.assert_observed(
            second,
            2,
        )

        self.s.assert_history(
            self.genesis,
            second,
        )

        self.h.assert_floor(1, 0)

        valid = self.h.send(
            second,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            valid["status"],
            "committed",
        )

        self.h.assert_floor(2, 1)


if __name__ == "__main__":
    unittest.main()
