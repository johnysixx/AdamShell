"""Authenticated anchor exception suppression regressions.

All providers, signing keys and databases are test fixtures.

Transport cleanup must never hide caller or authentication
failures. An already committed CAS must not be retried or
rolled back merely because acknowledgement failed.
"""

import unittest

from contextlib import contextmanager
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_contract as protocol

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_failure_contract as failure


class CallerFailure(Exception):
    pass


class SuppressingSignedProvider(
    protocol.SignedTestProvider
):
    """Synthetic transport with exception-suppressing cleanup."""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.suppressed = []
        self.hold_count = 0
        self.read_count = 0
        self.cas_count = 0
        self.finish_count = 0

    @contextmanager
    def hold(self, *, session):

        self.hold_count += 1

        if self.active is not None:
            raise ValueError("Unexpected nested hold")

        with self.backend.exclusive():

            self.active = session

            try:

                try:

                    yield self.response(
                        "hold",
                        session,
                        session,
                        self.backend.read(),
                    )

                except Exception as exc:

                    self.suppressed.append(
                        type(exc).__name__
                    )

            finally:

                self.active = None

    def read(self, **kwargs):

        self.read_count += 1

        return super().read(**kwargs)

    def compare_and_set(self, **kwargs):

        self.cas_count += 1

        return super().compare_and_set(**kwargs)

    def finish(self, **kwargs):

        self.finish_count += 1

        return super().finish(**kwargs)


class A44AuthenticatedAnchorSuppressionAdversarialTests(
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

        self.anchor = self.f.f.anchor
        self.local = self.f.f.local

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.provider = SuppressingSignedProvider(
            backend=self.anchor,
            signer=self.f.signer,
            enrollment=self.f.pin,
        )

        self.client = (
            self.f.m
            .AuthenticatedProtectedRootAnchorClient
            .from_provider(
                provider=self.provider,
                enrollment=self.f.pin,
            )
        )

        self.assertEqual(
            self.anchor.read(),
            self.initial,
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

    def invoke(self, operation):

        if operation == "read":
            return self.client.read()

        if operation == "cas":

            return self.client.compare_and_set(
                expected=self.initial.reference(),
                replacement=self.pending,
            )

        raise AssertionError("Unknown test operation")

    def corrupt_method(self, name):

        original = getattr(
            self.provider,
            name,
        )

        def invalid(**kwargs):

            return failure.corrupt(
                original(**kwargs)
            )

        return patch.object(
            self.provider,
            name,
            side_effect=invalid,
        )

    def capture(self, operation):

        try:

            result = operation()

        except Exception as exc:

            return False, None, exc

        return True, result, None

    def assert_cleanup(self):

        self.assertIsNone(
            self.provider.active
        )

        self.assertIsNone(
            self.client._held.session
        )

        self.assertIsNone(
            self.client._held.reference
        )

        self.assertFalse(
            self.client._held.poisoned
        )

    def assert_state_and_recovery(
        self,
        *,
        committed,
        reads,
        finishes,
    ):

        expected = (
            self.pending
            if committed
            else self.initial
        )

        expected_cas_count = (
            1 if committed else 0
        )

        self.assertEqual(
            self.anchor.read(),
            expected,
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        self.assert_cleanup()

        self.assertEqual(
            self.provider.hold_count,
            1,
        )

        self.assertEqual(
            self.provider.read_count,
            reads,
        )

        self.assertEqual(
            self.provider.cas_count,
            expected_cas_count,
        )

        self.assertEqual(
            self.provider.finish_count,
            finishes,
        )

        self.assertEqual(
            self.client.read(),
            expected,
        )

        self.assertEqual(
            self.provider.cas_count,
            expected_cas_count,
        )

        self.assertEqual(
            self.provider.hold_count,
            2,
        )

        self.assert_cleanup()

    def assert_authentication_rejected(
        self,
        outcome,
    ):

        returned, result, error = outcome

        self.assertFalse(
            returned,
            "FAIL_OPEN: authentication failure was suppressed",
        )

        self.assertIsNone(result)

        self.assertIsInstance(
            error,
            ValueError,
        )

    def test_01_caller_exception_cannot_be_suppressed(self):

        original = CallerFailure(
            "Synthetic caller failure"
        )

        def invoke():

            with self.client.exclusive():

                raise original

        returned, result, error = (
            self.capture(invoke)
        )

        self.assert_state_and_recovery(
            committed=False,
            reads=0,
            finishes=0,
        )

        self.assertFalse(
            returned,
            "FAIL_OPEN: caller exception was suppressed",
        )

        self.assertIsNone(result)

        self.assertIs(
            error,
            original,
        )

    def test_02_invalid_read_cannot_be_suppressed(self):

        with self.corrupt_method("read"):

            outcome = self.capture(
                lambda: self.invoke("read")
            )

        self.assert_state_and_recovery(
            committed=False,
            reads=1,
            finishes=0,
        )

        self.assert_authentication_rejected(
            outcome
        )

    def test_03_invalid_finish_after_read_cannot_be_suppressed(self):

        with self.corrupt_method("finish"):

            outcome = self.capture(
                lambda: self.invoke("read")
            )

        self.assert_state_and_recovery(
            committed=False,
            reads=1,
            finishes=1,
        )

        self.assert_authentication_rejected(
            outcome
        )

    def test_04_invalid_cas_ack_cannot_be_suppressed(self):

        with self.corrupt_method(
            "compare_and_set"
        ):

            outcome = self.capture(
                lambda: self.invoke("cas")
            )

        self.assert_state_and_recovery(
            committed=True,
            reads=0,
            finishes=0,
        )

        self.assert_authentication_rejected(
            outcome
        )

    def test_05_invalid_finish_after_cas_cannot_be_suppressed(self):

        with self.corrupt_method("finish"):

            outcome = self.capture(
                lambda: self.invoke("cas")
            )

        self.assert_state_and_recovery(
            committed=True,
            reads=0,
            finishes=1,
        )

        self.assert_authentication_rejected(
            outcome
        )

    def test_06_valid_transport_operations_remain_available(self):

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

        self.assert_cleanup()

        self.assertEqual(
            self.client.compare_and_set(
                expected=self.initial.reference(),
                replacement=self.pending,
            ),
            self.pending.reference(),
        )

        self.assertEqual(
            self.client.read(),
            self.pending,
        )

        self.assertEqual(
            self.anchor.read(),
            self.pending,
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        self.assertEqual(
            self.provider.cas_count,
            1,
        )

        self.assertEqual(
            self.provider.hold_count,
            3,
        )

        self.assertEqual(
            self.provider.read_count,
            2,
        )

        self.assertEqual(
            self.provider.finish_count,
            3,
        )

        self.assertEqual(
            self.provider.suppressed,
            [],
        )

        self.assert_cleanup()


if __name__ == "__main__":
    unittest.main()
