"""A44 / 66.41D durable publication adversarial regression.

The subprocess tests terminate real child processes at explicit
transaction boundaries.

Only ephemeral fixture databases and fixture signing keys are used.

No SQLite journal is manually removed. Recovery must use the
normal SQLite transaction mechanisms and the durable authority.

These tests establish process-crash behavior, not hardware
power-loss durability or independent tamper-resistant storage.
"""

import importlib
import os
import sqlite3
import sys
import time
import unittest

from contextlib import closing, contextmanager
from pathlib import Path
from unittest.mock import patch


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_witness_deployment_floor_writer_policy_durable_high_water_contract as contract

import test_a44_witness_deployment_floor_writer_policy_sqlite_adversarial as legacy


MODULE = contract.MODULE

production = importlib.import_module(
    MODULE
)

policy = contract.policy

persistent = production.persistent

ORIGINAL_WORKER = legacy.WORKER_SOURCE


CRASH_WORKER_EXTENSION = r"""
from contextlib import contextmanager

if operation == "crash_publish":

    pair = tuple(
        bytes.fromhex(part)
        for part in config["signed_policy"]
    )

    state_path = authority._configuration.state_path

    original_database = module._database

    original_policy_transaction = (
        module.persistent._transaction
    )

    def stop_at_boundary():

        signal("entered")

        # The parent process terminates this process while
        # it is waiting. Normal Python cleanup must not run.

        wait_for("release")

        raise RuntimeError(
            "Crash worker was unexpectedly released."
        )

    @contextmanager
    def watched_database(path, **arguments):

        state_kind = None

        with original_database(
            path,
            **arguments,
        ) as connection:

            yield connection

            if (
                Path(path).resolve() == state_path
                and arguments.get("write", False)
            ):

                row = connection.execute(
                    "SELECT anchor_epoch, prepared_epoch "
                    "FROM durable_policy_state "
                    "WHERE singleton = 1"
                ).fetchone()

                if row == (1, 2):

                    state_kind = "prepare"

                elif row == (2, None):

                    state_kind = "finalize"

                if (
                    crash_phase == "before_prepare_commit"
                    and state_kind == "prepare"
                ):

                    stop_at_boundary()

                if (
                    crash_phase == "before_finalize_commit"
                    and state_kind == "finalize"
                ):

                    stop_at_boundary()

        if (
            crash_phase == "after_prepare_commit"
            and state_kind == "prepare"
        ):

            stop_at_boundary()

        if (
            crash_phase == "after_finalize_commit"
            and state_kind == "finalize"
        ):

            stop_at_boundary()

    @contextmanager
    def watched_policy_transaction(pins, **arguments):

        candidate_written = False

        with original_policy_transaction(
            pins,
            **arguments,
        ) as connection:

            yield connection

            row = connection.execute(
                "SELECT policy_epoch "
                "FROM writer_policy_head"
            ).fetchone()

            candidate_written = row == (2,)

            if (
                candidate_written
                and crash_phase == "before_policy_commit"
            ):

                stop_at_boundary()

        if (
            candidate_written
            and crash_phase == "after_policy_commit"
        ):

            stop_at_boundary()

    with patch.object(
        module,
        "_database",
        watched_database,
    ), patch.object(
        module.persistent,
        "_transaction",
        watched_policy_transaction,
    ):

        authority.publish_policy(
            signed_policy=pair,
        )

    raise RuntimeError(
        "Requested crash boundary was not reached."
    )

elif operation == "recover":

    try:

        recovered = authority.recover_publication()

        result["status"] = "recovered"

        result["reference"] = list(
            recovered
        )

    except ValueError:

        result["status"] = "rejected"

elif operation == "publish":
"""


class A44DurableWriterPolicyAdversarialTests(
    unittest.TestCase
):

    def setUp(self):

        self.d = (
            contract.A44DurableWriterPolicyContractTests(
                "test_01_explicit_bootstrap_and_open"
            )
        )

        self.addCleanup(
            self.d.doCleanups
        )

        self.d.setUp()

        self.s = self.d.s
        self.p = self.d.p
        self.h = self.d.h

        self.authority = self.d.authority
        self.gateway = self.d.gateway

        self.genesis = self.d.genesis

        self.store_path = self.d.store_path

        self.fence_path = self.store_path.with_name(
            self.store_path.name + ".fence.sqlite3"
        )

    def candidate(self):

        return self.p.next_policy(
            revoked=("writer-alpha",),
        )

    def helper(self):

        instance = (
            legacy.A44PersistentWriterPolicyAdversarialTests(
                "test_01_stale_gateway_in_separate_process_observes_revocation"
            )
        )

        instance.s = self.s
        instance.p = self.p

        return instance

    def build_worker_source(
        self,
        *,
        policy_path=None,
        crash_phase=None,
    ):

        if policy_path is None:

            policy_path = self.s.path

        replacements = (
            (
                'config["policy_module"]',
                repr(MODULE),
            ),
            (
                "module.SQLitePersistentWriterPolicyAuthority.open(",
                "module.DurableWriterPolicyAuthority.open(",
            ),
            (
                'path=config["policy_path"],',
                "path=" + repr(str(policy_path)) + ",",
            ),
            (
                'expected_policy_id=config["policy_id"],',
                (
                    "high_water_path="
                    + repr(str(self.store_path))
                    + ",\n    expected_store_id="
                    + repr(contract.STORE_ID)
                    + ',\n    expected_policy_id=config["policy_id"],'
                ),
            ),
            (
                "module.PersistentWriterPolicyGateway.from_authority(",
                "module.DurableWriterPolicyGateway.from_authority(",
            ),
            (
                "opening_reference = authority.current_policy_reference()",
                (
                    "opening_reference = "
                    "authority.durable_state().anchor.pair()"
                ),
            ),
            (
                'if operation == "publish":',
                (
                    "crash_phase = "
                    + repr(crash_phase)
                    + "\n"
                    + CRASH_WORKER_EXTENSION
                ),
            ),
        )

        source = ORIGINAL_WORKER

        for old, new in replacements:

            self.assertEqual(
                source.count(old),
                1,
                "Unexpected worker source shape: " + old,
            )

            source = source.replace(
                old,
                new,
                1,
            )

        compile(
            source,
            "<durable-crash-worker>",
            "exec",
        )

        return source

    @contextmanager
    def worker(
        self,
        tag,
        operation,
        *,
        policy_path=None,
        request=None,
        signed_policy=None,
        crash_phase=None,
    ):

        source = self.build_worker_source(
            policy_path=policy_path,
            crash_phase=crash_phase,
        )

        helper = self.helper()

        with patch.object(
            legacy,
            "WORKER_SOURCE",
            source,
        ):

            with helper.worker(
                tag,
                operation,
                request=request,
                signed_policy=signed_policy,
            ) as worker:

                yield worker

    def wait_signal(self, path, process):

        self.helper().wait_signal(
            path,
            process,
            timeout=20,
        )

    def finish_worker(self, process):

        return self.helper().finish_worker(
            process
        )

    def crash_publication(
        self,
        candidate,
        phase,
    ):

        with self.worker(
            "crash-" + phase,
            "crash_publish",
            signed_policy=candidate,
            crash_phase=phase,
        ) as (process, signals):

            self.assertNotEqual(
                process.pid,
                os.getpid(),
            )

            signals["go"].touch()

            self.wait_signal(
                signals["entered"],
                process,
            )

            self.assertIsNone(
                process.poll()
            )

            # Terminate only the child created by this fixture.
            # Do not release its pause or allow normal cleanup.

            process.kill()

            stdout, stderr = process.communicate(
                timeout=15
            )

            self.assertIsNotNone(
                process.returncode
            )

            self.assertNotEqual(
                process.returncode,
                0,
                stdout + "\n" + stderr,
            )

            self.assertFalse(
                signals["release"].exists()
            )

    def assert_policy_history(
        self,
        *signed_policies,
    ):

        # Acquire an ordinary SQLite policy transaction.
        # If SQLite has a hot rollback journal, its normal
        # recovery machinery may resolve it here.
        #
        # No journal removal or manual repair is performed.

        with persistent._transaction(
            self.authority._pins
        ) as connection:

            history = persistent._load_history(
                connection,
                self.authority._pins,
            )

            rows = connection.execute(
                "SELECT policy_epoch, message, signature "
                "FROM writer_policy_history "
                "ORDER BY policy_epoch"
            ).fetchall()

            expected = [
                (
                    epoch,
                    pair[0],
                    pair[1],
                )
                for epoch, pair in enumerate(
                    signed_policies,
                    start=1,
                )
            ]

            self.assertEqual(
                rows,
                expected,
            )

            self.assertEqual(
                history.current.epoch,
                len(signed_policies),
            )

            self.assertEqual(
                history.current.sha256,
                policy.digest(
                    signed_policies[-1]
                ),
            )

    def assert_pending_after_crash(
        self,
        candidate,
    ):

        fresh = self.d.reopen()

        self.d.assert_prepared(
            self.genesis,
            1,
            candidate,
            authority=fresh,
        )

        self.d.assert_pending_blocks_operations()

        self.d.assert_cas_blocked(
            gateway=self.d.make_gateway(fresh),
        )

        self.d.assert_floor(1, 0)

        return fresh

    def assert_recovered(
        self,
        candidate,
        authority=None,
    ):

        self.assertEqual(
            self.d.recover(authority),
            self.d.pair(candidate, 2),
        )

        self.d.assert_stable(
            candidate,
            2,
        )

        self.assert_policy_history(
            self.genesis,
            candidate,
        )

        self.assertEqual(
            self.d.recover(),
            self.d.pair(candidate, 2),
        )

        self.d.assert_cas_blocked(
            signed_policy=candidate,
        )

        self.d.assert_floor(1, 0)

    def execute_sql(
        self,
        path,
        statement,
        parameters=(),
    ):

        with closing(
            sqlite3.connect(
                str(path),
                timeout=5,
            )
        ) as connection:

            with connection:

                connection.execute(
                    statement,
                    parameters,
                )

    def assert_fenced_policy_operations(self):

        with self.assertRaises(ValueError):

            self.d.reopen()

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.authority.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.d.publish(
                self.candidate()
            )

        with self.assertRaises(ValueError):

            self.d.recover()

        self.d.assert_cas_blocked()


    def test_01_process_crash_before_prepare_commit(self):

        second = self.candidate()

        self.crash_publication(
            second,
            "before_prepare_commit",
        )

        fresh = self.d.reopen()

        self.d.assert_stable(
            self.genesis,
            1,
            fresh,
        )

        self.assert_policy_history(
            self.genesis
        )

        self.d.assert_floor(1, 0)

        # No durable preparation completed.
        # Normal publication remains available.

        self.assertEqual(
            self.d.publish(
                second,
                authority=fresh,
            ),
            self.d.pair(second, 2),
        )

        self.d.assert_stable(second, 2)

        self.assert_policy_history(
            self.genesis,
            second,
        )


    def test_02_process_crash_after_prepare_commit(self):

        second = self.candidate()

        self.crash_publication(
            second,
            "after_prepare_commit",
        )

        fresh = self.assert_pending_after_crash(
            second
        )

        self.assert_policy_history(
            self.genesis
        )

        self.assert_recovered(
            second,
            fresh,
        )


    def test_03_process_crash_before_policy_commit(self):

        second = self.candidate()

        self.crash_publication(
            second,
            "before_policy_commit",
        )

        fresh = self.assert_pending_after_crash(
            second
        )

        self.assert_policy_history(
            self.genesis
        )

        self.assert_recovered(
            second,
            fresh,
        )


    def test_04_process_crash_after_policy_commit(self):

        second = self.candidate()

        self.crash_publication(
            second,
            "after_policy_commit",
        )

        fresh = self.assert_pending_after_crash(
            second
        )

        self.assert_policy_history(
            self.genesis,
            second,
        )

        self.assert_recovered(
            second,
            fresh,
        )


    def test_05_process_crash_before_finalize_commit(self):

        second = self.candidate()

        self.crash_publication(
            second,
            "before_finalize_commit",
        )

        fresh = self.assert_pending_after_crash(
            second
        )

        self.assert_policy_history(
            self.genesis,
            second,
        )

        self.assert_recovered(
            second,
            fresh,
        )


    def test_06_process_crash_after_finalize_commit(self):

        second = self.candidate()

        self.crash_publication(
            second,
            "after_finalize_commit",
        )

        fresh = self.d.reopen()

        self.d.assert_stable(
            second,
            2,
            fresh,
        )

        self.assert_recovered(
            second,
            fresh,
        )


    def test_07_separate_process_recovers_prepared_candidate_after_rollback(self):

        old = self.d.snapshot(
            "process-recovery-genesis.sqlite3"
        )

        second = self.candidate()

        self.crash_publication(
            second,
            "after_policy_commit",
        )

        self.assert_policy_history(
            self.genesis,
            second,
        )

        self.d.restore(old)

        self.d.assert_pending_blocks_operations()

        with self.worker(
            "independent-recovery",
            "recover",
        ) as (process, signals):

            signals["go"].touch()

            result = self.finish_worker(
                process
            )

        self.assertEqual(
            result["status"],
            "recovered",
        )

        self.assertEqual(
            result["reference"],
            list(
                self.d.pair(second, 2)
            ),
        )

        self.assertNotEqual(
            result["pid"],
            os.getpid(),
        )

        self.d.assert_stable(
            second,
            2,
        )

        self.assert_policy_history(
            self.genesis,
            second,
        )

        self.d.assert_cas_blocked(
            signed_policy=second,
        )

        self.d.assert_floor(1, 0)


    def test_08_separate_stale_process_on_policy_copy_is_rejected(self):

        copy = self.d.snapshot(
            "stale-process-copy.sqlite3"
        )

        request = self.h.request()

        second = self.candidate()

        with self.worker(
            "stale-copy",
            "cas",
            policy_path=copy,
            request=request,
        ) as (process, signals):

            self.d.publish(second)

            signals["go"].touch()

            result = self.finish_worker(
                process
            )

        self.assertEqual(
            result["status"],
            "rejected",
        )

        self.assertEqual(
            result["opening_reference"],
            list(
                self.d.pair(
                    self.genesis,
                    1,
                )
            ),
        )

        self.d.assert_stable(second, 2)

        self.d.assert_floor(1, 0)

        result = self.d.send(
            second,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.d.assert_committed(
            result,
            2,
        )

        self.d.assert_floor(2, 1)


    def test_09_cross_process_copy_publication_waits_for_floor_cas(self):

        copy = self.d.snapshot(
            "cross-process-publisher-copy.sqlite3"
        )

        second = self.candidate()

        request = self.h.request()

        with self.worker(
            "blocking-cas",
            "blocking_cas",
            request=request,
        ) as (cas, cas_signals):

            with self.worker(
                "copy-publisher",
                "publish",
                policy_path=copy,
                signed_policy=second,
            ) as (publisher, publication_signals):

                cas_signals["go"].touch()

                self.wait_signal(
                    cas_signals["entered"],
                    cas,
                )

                try:

                    # An independent SQLite connection
                    # must observe the shared fence lock.

                    with closing(
                        sqlite3.connect(
                            str(self.fence_path),
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

                    # The policy transaction is held too.

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

                    publication_signals["go"].touch()

                    self.wait_signal(
                        publication_signals["started"],
                        publisher,
                    )

                    time.sleep(0.25)

                    self.assertIsNone(
                        publisher.poll(),
                        "Publication escaped shared fence",
                    )

                    self.d.assert_stable(
                        self.genesis,
                        1,
                    )

                finally:

                    cas_signals["release"].touch()

                cas_result = self.finish_worker(
                    cas
                )

                publication_result = (
                    self.finish_worker(publisher)
                )

        self.assertNotEqual(
            cas_result["pid"],
            publication_result["pid"],
        )

        self.assertEqual(
            cas_result["status"],
            "reply",
        )

        response = self.p.f.response(
            bytes.fromhex(
                cas_result["response"]
            ),
            operation="cas",
            challenge=b"c" * 32,
        )

        self.d.assert_committed(
            response,
            2,
        )

        self.assertEqual(
            publication_result["status"],
            "published",
        )

        self.d.assert_stable(
            second,
            2,
        )

        self.d.assert_cas_blocked(
            request=self.p.next_cas(),
        )

        self.d.assert_floor(2, 1)


    def test_10_conflicting_cross_process_copy_publications_have_one_winner(self):

        copy = self.d.snapshot(
            "competing-publication-copy.sqlite3"
        )

        first = self.candidate()

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.assertNotEqual(
            policy.digest(first),
            policy.digest(alternative),
        )

        with self.worker(
            "publisher-a",
            "publish",
            signed_policy=first,
        ) as (a, a_signals):

            with self.worker(
                "publisher-b",
                "publish",
                policy_path=copy,
                signed_policy=alternative,
            ) as (b, b_signals):

                a_signals["go"].touch()

                b_signals["go"].touch()

                result_a = self.finish_worker(a)

                result_b = self.finish_worker(b)

        self.assertNotEqual(
            result_a["pid"],
            result_b["pid"],
        )

        self.assertCountEqual(
            (
                result_a["status"],
                result_b["status"],
            ),
            (
                "published",
                "rejected",
            ),
        )

        if result_a["status"] == "published":

            winner = first

            winner_path = self.s.path

            loser_path = copy

        else:

            winner = alternative

            winner_path = copy

            loser_path = self.s.path

        self.d.assert_stable(winner, 2)

        winning = self.d.reopen(
            path=winner_path,
        )

        self.assertEqual(
            winning.current_policy_reference(),
            self.d.pair(winner, 2),
        )

        with self.assertRaises(ValueError):

            self.d.reopen(
                path=loser_path,
            )

        self.d.assert_floor(1, 0)


    def test_11_concurrent_recovery_processes_are_idempotent(self):

        second = self.candidate()

        self.crash_publication(
            second,
            "after_prepare_commit",
        )

        with self.worker(
            "recovery-a",
            "recover",
        ) as (a, a_signals):

            with self.worker(
                "recovery-b",
                "recover",
            ) as (b, b_signals):

                a_signals["go"].touch()

                b_signals["go"].touch()

                result_a = self.finish_worker(a)

                result_b = self.finish_worker(b)

        self.assertNotEqual(
            result_a["pid"],
            result_b["pid"],
        )

        expected = list(
            self.d.pair(second, 2)
        )

        for result in (
            result_a,
            result_b,
        ):

            self.assertEqual(
                result["status"],
                "recovered",
            )

            self.assertEqual(
                result["reference"],
                expected,
            )

        self.d.assert_stable(second, 2)

        self.assert_policy_history(
            self.genesis,
            second,
        )

        self.d.assert_floor(1, 0)


    def test_12_missing_coordination_fence_fails_closed(self):

        self.d.assert_committed(
            self.d.send(),
            2,
        )

        second = self.candidate()

        self.d.publish(second)

        self.assertTrue(
            self.fence_path.is_file()
        )

        self.fence_path.unlink()

        # State inspection remains independent of the fence.
        # Policy-sensitive operations must not recreate it.

        self.d.assert_stable(
            second,
            2,
        )

        with self.assertRaises(ValueError):

            self.d.reopen()

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.authority.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.d.publish(
                self.p.next_policy(second)
            )

        with self.assertRaises(ValueError):

            self.d.recover()

        self.d.assert_cas_blocked(
            request=self.p.next_cas(),
        )

        self.assertEqual(
            self.d.public_read()["epoch"],
            2,
        )

        self.assertEqual(
            self.d.public_lookup()["status"],
            "committed",
        )

        self.assertFalse(
            self.fence_path.exists()
        )

        self.d.assert_floor(2, 1)


    def test_13_different_provisioning_nonce_rejects_replaced_fence(self):

        other_path = (
            self.s.directory
            / "different-provisioning.sqlite3"
        )

        other = self.d.bootstrap(
            high_water_path=other_path,
        )

        self.d.assert_stable(
            self.genesis,
            1,
            other,
        )

        other_fence = other_path.with_name(
            other_path.name + ".fence.sqlite3"
        )

        original_nonce = self.authority._nonce

        self.assertNotEqual(
            original_nonce,
            other._nonce,
        )

        self.d.backup_database(
            other_fence,
            self.fence_path,
        )

        self.assert_fenced_policy_operations()

        self.d.assert_stable(
            self.genesis,
            1,
        )

        self.d.assert_floor(1, 0)


    def test_14_missing_policy_database_during_pending_publication(self):

        self.d.assert_committed(
            self.d.send(),
            2,
        )

        second = self.candidate()

        self.d.fail_publication(
            second,
            after_commit=False,
        )

        saved = self.d.snapshot(
            "pending-policy-backup.sqlite3"
        )

        self.s.path.unlink()

        self.d.assert_prepared(
            self.genesis,
            1,
            second,
        )

        with self.assertRaises(ValueError):

            self.d.recover()

        self.d.assert_cas_blocked(
            request=self.p.next_cas(),
        )

        self.assertEqual(
            self.d.public_read()["epoch"],
            2,
        )

        self.assertEqual(
            self.d.public_lookup()["status"],
            "committed",
        )

        self.assertFalse(
            self.s.path.exists()
        )

        self.d.backup_database(
            saved,
            self.s.path,
        )

        self.assertEqual(
            self.d.recover(),
            self.d.pair(second, 2),
        )

        self.d.assert_stable(second, 2)

        self.d.assert_floor(2, 1)


    def test_15_corrupted_prepared_signature_fails_closed(self):

        second = self.candidate()

        self.d.fail_publication(
            second,
            after_commit=False,
        )

        self.execute_sql(
            self.store_path,
            "UPDATE durable_policy_state "
            "SET prepared_signature = zeroblob(64)",
        )

        with self.assertRaises(ValueError):

            self.d.state()

        self.assert_fenced_policy_operations()

        self.assert_policy_history(
            self.genesis
        )

        self.d.assert_floor(1, 0)


    def test_16_corrupted_prepared_digest_fails_closed(self):

        second = self.candidate()

        self.d.fail_publication(
            second,
            after_commit=True,
        )

        self.execute_sql(
            self.store_path,
            "UPDATE durable_policy_state "
            "SET prepared_sha256 = ?",
            ("ab" * 32,),
        )

        with self.assertRaises(ValueError):

            self.d.state()

        self.assert_fenced_policy_operations()

        self.assert_policy_history(
            self.genesis,
            second,
        )

        self.d.assert_floor(1, 0)


    def test_17_hardlinked_durable_store_alias_is_rejected(self):

        alias = (
            self.s.directory
            / "durable-hardlink.sqlite3"
        )

        os.link(
            self.store_path,
            alias,
        )

        try:

            with self.assertRaises(ValueError):

                self.d.reopen(
                    high_water_path=alias,
                )

            with self.assertRaises(ValueError):

                self.d.state()

            self.d.assert_cas_blocked()

        finally:

            alias.unlink()

        self.d.assert_stable(
            self.genesis,
            1,
        )

        self.assertEqual(
            self.authority.current_policy_reference(),
            self.d.pair(self.genesis, 1),
        )

        self.d.assert_floor(1, 0)


    def test_18_corrupted_durable_identity_fails_closed(self):

        self.execute_sql(
            self.store_path,
            "UPDATE durable_policy_metadata "
            "SET identity = ?",
            ("ab" * 32,),
        )

        with self.assertRaises(ValueError):

            self.d.state()

        self.assert_fenced_policy_operations()

        self.assert_policy_history(
            self.genesis
        )

        self.d.assert_floor(1, 0)


    def test_19_pending_recovery_authenticates_exact_candidate_in_descendant_history(self):

        second = self.candidate()

        self.d.fail_publication(
            second,
            after_commit=True,
        )

        third = self.p.next_policy(
            second
        )

        # This legacy publication is explicitly outside
        # the durable fence. Recovery must authenticate
        # the prepared candidate within the newer lineage.

        self.h.publish_external(third)

        self.d.assert_prepared(
            self.genesis,
            1,
            second,
        )

        self.d.assert_pending_blocks_operations()

        self.assertEqual(
            self.d.recover(),
            self.d.pair(third, 3),
        )

        self.d.assert_stable(
            third,
            3,
        )

        self.assert_policy_history(
            self.genesis,
            second,
            third,
        )

        self.d.assert_cas_blocked(
            signed_policy=third,
        )

        self.d.assert_floor(1, 0)


    def test_20_repeated_failed_recovery_preserves_exact_preparation(self):

        second = self.candidate()

        self.d.fail_publication(
            second,
            after_commit=False,
        )

        retained = self.d.state()

        for attempt in range(3):

            with patch.object(
                production,
                "_append_policy",
                side_effect=OSError(
                    "Injected recovery failure "
                    + str(attempt)
                ),
            ):

                with self.assertRaises(ValueError):

                    self.d.recover()

            self.assertEqual(
                self.d.state(),
                retained,
            )

            self.d.assert_pending_blocks_operations()

            self.assert_policy_history(
                self.genesis
            )

            self.d.assert_floor(1, 0)

        fresh = self.d.reopen()

        self.assert_recovered(
            second,
            fresh,
        )


    def test_21_finalization_acknowledgement_loss_retains_committed_anchor(self):

        second = self.candidate()

        original_database = (
            production._database
        )

        reached = []

        @contextmanager
        def lose_finalization_ack(
            path,
            **arguments,
        ):

            finalized = False

            with original_database(
                path,
                **arguments,
            ) as connection:

                yield connection

                if (
                    Path(path).resolve() == self.store_path
                    and arguments.get("write", False)
                ):

                    row = connection.execute(
                        "SELECT anchor_epoch, prepared_epoch "
                        "FROM durable_policy_state"
                    ).fetchone()

                    finalized = row == (2, None)

            if finalized:

                reached.append(True)

                raise OSError(
                    "Injected durable finalization acknowledgement loss"
                )

        with patch.object(
            production,
            "_database",
            lose_finalization_ack,
        ):

            with self.assertRaises(ValueError):

                self.d.publish(second)

        self.assertEqual(
            reached,
            [True],
        )

        self.d.assert_stable(second, 2)

        self.assert_policy_history(
            self.genesis,
            second,
        )

        fresh = self.d.reopen()

        self.assert_recovered(
            second,
            fresh,
        )


    def test_22_observation_acknowledgement_loss_blocks_floor_mutation(self):

        old = self.d.snapshot(
            "observation-ack-genesis.sqlite3"
        )

        second = self.p.next_policy()

        self.h.publish_external(second)

        original_database = (
            production._database
        )

        reached = []

        @contextmanager
        def lose_observation_ack(
            path,
            **arguments,
        ):

            observed = False

            with original_database(
                path,
                **arguments,
            ) as connection:

                yield connection

                if (
                    Path(path).resolve() == self.store_path
                    and arguments.get("write", False)
                ):

                    row = connection.execute(
                        "SELECT anchor_epoch, prepared_epoch "
                        "FROM durable_policy_state"
                    ).fetchone()

                    observed = row == (2, None)

            if observed:

                reached.append(True)

                raise OSError(
                    "Injected durable observation acknowledgement loss"
                )

        with patch.object(
            production,
            "_database",
            lose_observation_ack,
        ):

            self.d.assert_cas_blocked(
                signed_policy=second,
            )

        self.assertEqual(
            reached,
            [True],
        )

        self.d.assert_stable(
            second,
            2,
        )

        self.d.assert_floor(1, 0)

        self.d.restore(old)

        with self.assertRaises(ValueError):

            self.d.reopen()

        self.d.assert_cas_blocked()

        self.d.assert_stable(second, 2)

        self.d.assert_floor(1, 0)


    def test_23_floor_postcommit_reply_loss_preserves_durable_observation(self):

        old = self.d.snapshot(
            "floor-reply-loss-genesis.sqlite3"
        )

        second = self.candidate()

        self.h.publish_external(second)

        backend_type = type(
            self.p.backend
        )

        original = (
            backend_type.advance_if_current
        )

        reached = []

        def lose_floor_reply(instance, **arguments):

            self.d.assert_stable(
                second,
                2,
            )

            original(
                instance,
                **arguments,
            )

            reached.append(True)

            raise OSError(
                "Injected floor postcommit reply loss"
            )

        with patch.object(
            backend_type,
            "advance_if_current",
            lose_floor_reply,
        ):

            with self.assertRaises(ValueError):

                self.d.send(
                    second,
                    writer_id="writer-beta",
                    signer=self.p.f.bob,
                )

        self.assertEqual(
            reached,
            [True],
        )

        self.d.assert_floor(2, 1)

        self.d.assert_stable(second, 2)

        self.d.restore(old)

        self.d.assert_cas_blocked(
            request=self.p.next_cas(),
        )

        self.assertEqual(
            self.d.public_lookup()["status"],
            "committed",
        )

        self.assertEqual(
            self.d.public_read()["epoch"],
            2,
        )

        self.d.assert_floor(2, 1)


    def test_24_public_recovery_does_not_observe_newer_policy(self):

        self.d.assert_committed(
            self.d.send(),
            2,
        )

        second = self.candidate()

        self.h.publish_external(second)

        self.d.assert_stable(
            self.genesis,
            1,
        )

        self.assertEqual(
            self.d.public_read()["epoch"],
            2,
        )

        self.assertEqual(
            self.d.public_lookup()["status"],
            "committed",
        )

        self.d.assert_stable(
            self.genesis,
            1,
        )

        self.assertEqual(
            self.authority.current_policy_reference(),
            self.d.pair(second, 2),
        )

        self.d.assert_stable(second, 2)

        self.d.assert_floor(2, 1)


if __name__ == "__main__":
    unittest.main()
