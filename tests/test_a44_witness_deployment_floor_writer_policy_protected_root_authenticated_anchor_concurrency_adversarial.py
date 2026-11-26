"""Authenticated protected root concurrency regressions.

Synthetic transport, temporary root databases and test keys.

These tests establish bounded local client behavior.
They do not establish remote durability, physical fencing
or distributed linearizability.
"""

import threading
import unittest

from contextlib import contextmanager
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_contract as protocol

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_failure_contract as failure


class CleanupFailure(Exception):
    pass


class SyntheticAbort(BaseException):
    pass


def capture(operation):

    try:

        return True, operation(), None

    except BaseException as exc:

        return False, None, exc


class A44AuthenticatedAnchorConcurrencyAdversarialTests(
    unittest.TestCase
):

    def setUp(self):

        self.f = (
            protocol
            .A44AuthenticatedProtectedRootAnchorClientContractTests(
                "test_01_canonical_backend_interface"
            )
        )

        self.addCleanup(self.f.doCleanups)

        self.f.setUp()

        self.client = self.f.client
        self.provider = self.f.provider

        self.anchor = self.f.f.anchor
        self.local = self.f.f.local

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.assertEqual(
            self.anchor.read(),
            self.initial,
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

    def assert_idle(self, client=None):

        client = (
            self.client if client is None
            else client
        )

        self.assertIsNone(
            client._held.session
        )

        self.assertIsNone(
            client._held.reference
        )

        self.assertFalse(
            client._held.poisoned
        )

        self.assertEqual(
            client._held.phase,
            "idle",
        )

    def assert_recovery(self, expected):

        self.assert_idle()

        self.assertIsNone(
            self.provider.active
        )

        self.assertEqual(
            self.anchor.read(),
            expected,
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        before = self.f.operations().count("cas")

        self.assertEqual(
            self.client.read(),
            expected,
        )

        self.assertEqual(
            self.f.operations().count("cas"),
            before,
        )

        self.assert_idle()

        self.assertIsNone(
            self.provider.active
        )

    def cas(self):

        return self.client.compare_and_set(
            expected=self.initial.reference(),
            replacement=self.pending,
        )

    def new_client(self):

        provider = protocol.SignedTestProvider(
            backend=self.anchor,
            signer=self.f.signer,
            enrollment=self.f.pin,
        )

        client = (
            self.f.m
            .AuthenticatedProtectedRootAnchorClient
            .from_provider(
                provider=provider,
                enrollment=self.f.pin,
            )
        )

        return client, provider

    def test_01_cas_callback_isolation(self):

        original = self.provider.compare_and_set

        callbacks = []
        dispatches = []

        def reentrant(**kwargs):

            dispatches.append(True)

            callbacks.append(
                capture(self.client.read)
            )

            return original(**kwargs)

        with patch.object(
            self.provider,
            "compare_and_set",
            side_effect=reentrant,
        ):

            outcome = capture(self.cas)

        self.assertEqual(
            len(callbacks),
            1,
        )

        self.assertFalse(callbacks[0][0])

        self.assertIsInstance(
            callbacks[0][2],
            ValueError,
        )

        self.assertFalse(
            outcome[0],
            "CAS returned success after reentrancy",
        )

        self.assertIsInstance(
            outcome[2],
            ValueError,
        )

        self.assertEqual(
            dispatches,
            [True],
        )

        self.assertEqual(
            self.f.operations(),
            ["hold", "cas"],
        )

        # A committed CAS must not be retried
        # or rolled back after callback rejection.

        self.assert_recovery(
            self.pending
        )

        self.assertEqual(
            self.f.operations().count("cas"),
            1,
        )

    def test_02_cleanup_callback_isolation(self):

        original = self.provider.hold

        callbacks = []

        @contextmanager
        def reentrant_cleanup(**kwargs):

            with original(**kwargs) as response:

                try:

                    yield response

                finally:

                    callbacks.append(
                        capture(self.client.read)
                    )

        with patch.object(
            self.provider,
            "hold",
            side_effect=reentrant_cleanup,
        ):

            outcome = capture(
                self.client.read
            )

        self.assertEqual(
            len(callbacks),
            1,
        )

        self.assertFalse(
            callbacks[0][0]
        )

        self.assertIsInstance(
            callbacks[0][2],
            ValueError,
        )

        self.assertFalse(
            outcome[0],
            "Cleanup reentrancy produced success",
        )

        self.assertIsInstance(
            outcome[2],
            ValueError,
        )

        self.assertEqual(
            self.f.operations(),
            ["hold", "read", "finish"],
        )

        self.assert_recovery(
            self.initial
        )

    def test_03_cleanup_failure_without_primary_error(self):

        original = self.provider.hold

        cleanup_error = CleanupFailure(
            "Synthetic standalone cleanup failure"
        )

        @contextmanager
        def failing_cleanup(**kwargs):

            with original(**kwargs) as response:

                yield response

            raise cleanup_error

        with patch.object(
            self.provider,
            "hold",
            side_effect=failing_cleanup,
        ):

            outcome = capture(
                self.client.read
            )

        self.assertFalse(
            outcome[0]
        )

        self.assertIs(
            outcome[2],
            cleanup_error,
        )

        self.assertEqual(
            self.f.operations(),
            ["hold", "read", "finish"],
        )

        self.assert_recovery(
            self.initial
        )

    def run_parallel(self, operation):

        barrier = threading.Barrier(
            3,
            timeout=10,
        )

        results = {}
        result_lock = threading.Lock()

        def worker(index):

            def invoke():

                barrier.wait()

                return operation()

            outcome = capture(invoke)

            with result_lock:

                results[index] = outcome

        threads = [
            threading.Thread(
                target=worker,
                args=(index,),
                daemon=True,
                name="a44-concurrency-" + str(index),
            )
            for index in range(2)
        ]

        for thread in threads:

            thread.start()

        barrier.wait()

        for thread in threads:

            thread.join(timeout=15)

        self.assertFalse(
            any(
                thread.is_alive()
                for thread in threads
            ),
            "CONCURRENCY_TIMEOUT: worker did not finish",
        )

        self.assertEqual(
            set(results),
            {0, 1},
        )

        return [
            results[index]
            for index in range(2)
        ]

    def test_04_concurrent_reads_are_serialized(self):

        results = self.run_parallel(
            self.client.read
        )

        for returned, result, error in results:

            self.assertTrue(
                returned,
                repr(error),
            )

            self.assertEqual(
                result,
                self.initial,
            )

        self.assertEqual(
            self.f.operations(),
            [
                "hold", "read", "finish",
                "hold", "read", "finish",
            ],
        )

        sessions = [
            session
            for operation, session, challenge
            in self.provider.events
            if operation == "hold"
        ]

        self.assertEqual(
            len(sessions),
            2,
        )

        self.assertNotEqual(
            sessions[0],
            sessions[1],
        )

        self.assert_recovery(
            self.initial
        )

    def test_05_concurrent_cas_has_single_winner(self):

        results = self.run_parallel(
            self.cas
        )

        successes = [
            result
            for returned, result, error in results
            if returned
        ]

        errors = [
            error
            for returned, result, error in results
            if not returned
        ]

        self.assertEqual(
            successes,
            [self.pending.reference()],
        )

        self.assertEqual(
            len(errors),
            1,
        )

        self.assertIsInstance(
            errors[0],
            ValueError,
        )

        self.assertEqual(
            self.f.operations().count("hold"),
            2,
        )

        self.assertEqual(
            self.f.operations().count("cas"),
            1,
        )

        self.assertEqual(
            self.f.operations().count("finish"),
            1,
        )

        self.assert_recovery(
            self.pending
        )

    def test_06_cross_client_replay_rejected(self):

        captured = []

        original = self.provider.read

        def save_response(**kwargs):

            response = original(**kwargs)

            captured.append(
                (
                    kwargs["session"],
                    kwargs["challenge"],
                    response,
                )
            )

            return response

        with patch.object(
            self.provider,
            "read",
            side_effect=save_response,
        ):

            self.assertEqual(
                self.client.read(),
                self.initial,
            )

        self.assertEqual(
            len(captured),
            1,
        )

        client2, provider2 = self.new_client()

        requests = []

        def replay(**kwargs):

            requests.append(
                (
                    kwargs["session"],
                    kwargs["challenge"],
                )
            )

            return captured[0][2]

        with patch.object(
            provider2,
            "read",
            side_effect=replay,
        ):

            with self.assertRaises(ValueError):

                client2.read()

        self.assertEqual(
            len(requests),
            1,
        )

        self.assertNotEqual(
            requests[0][0],
            captured[0][0],
        )

        self.assertNotEqual(
            requests[0][1],
            captured[0][1],
        )

        self.assert_idle(client2)

        self.assertIsNone(
            provider2.active
        )

        self.assertEqual(
            client2.read(),
            self.initial,
        )

        self.assert_recovery(
            self.initial
        )

    def test_07_poison_does_not_leak_between_clients(self):

        client2, provider2 = self.new_client()

        original = self.provider.read

        def invalid_read(**kwargs):

            return failure.corrupt(
                original(**kwargs)
            )

        with self.assertRaises(ValueError):

            with self.client.exclusive():

                with patch.object(
                    self.provider,
                    "read",
                    side_effect=invalid_read,
                ):

                    with self.assertRaises(ValueError):

                        self.client.read()

                self.assertTrue(
                    self.client._held.poisoned
                )

                self.assert_idle(client2)

                self.assertIsNone(
                    provider2.active
                )

                with self.assertRaises(ValueError):

                    self.client.read()

        self.assert_idle()

        self.assert_idle(client2)

        self.assertEqual(
            client2.read(),
            self.initial,
        )

        self.assert_idle(client2)

        self.assert_recovery(
            self.initial
        )

    def test_08_base_exception_restores_idle(self):

        original = SyntheticAbort(
            "Synthetic non-Exception failure"
        )

        def operation():

            with self.client.exclusive():

                raise original

        outcome = capture(operation)

        self.assertFalse(
            outcome[0]
        )

        self.assertIs(
            outcome[2],
            original,
        )

        self.assertEqual(
            self.f.operations(),
            ["hold"],
        )

        self.assert_recovery(
            self.initial
        )


if __name__ == "__main__":
    unittest.main()
