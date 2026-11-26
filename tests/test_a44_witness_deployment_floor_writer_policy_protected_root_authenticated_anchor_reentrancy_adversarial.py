"""Protected root authenticated transport isolation.

Transport callbacks must not acquire another session or
perform nested client operations.

Legitimate caller nesting remains available.

Transport cleanup must not replace the primary caller
or authentication exception.

Invalid local arguments must not dispatch remote CAS.
"""

import unittest

from contextlib import contextmanager
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_contract as protocol

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_failure_contract as failure


class CallerFailure(Exception):
    pass


class CleanupFailure(Exception):
    pass


class A44AuthenticatedAnchorReentrancyAdversarialTests(
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

    def capture(self, operation):

        try:

            result = operation()

        except Exception as exc:

            return False, None, exc

        return True, result, None

    def assert_clean_and_recoverable(self):

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

        self.assertEqual(
            self.anchor.read(),
            self.initial,
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        self.assertEqual(
            self.f.operations().count("cas"),
            0,
        )

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

        self.assertEqual(
            self.f.operations().count("cas"),
            0,
        )

        self.assertIsNone(
            self.provider.active
        )

    def assert_reentrancy_rejected(
        self,
        method,
    ):

        original = getattr(
            self.provider,
            method,
        )

        callbacks = []
        calls = 0

        if method == "hold":

            @contextmanager
            def reentrant(**kwargs):

                nonlocal calls

                calls += 1

                if calls == 1:

                    callbacks.append(
                        self.capture(
                            self.client.read
                        )
                    )

                with original(**kwargs) as response:

                    yield response

        else:

            def reentrant(**kwargs):

                nonlocal calls

                calls += 1

                if calls == 1:

                    callbacks.append(
                        self.capture(
                            self.client.read
                        )
                    )

                return original(**kwargs)

        with patch.object(
            self.provider,
            method,
            side_effect=reentrant,
        ):

            outer = self.capture(
                self.client.read
            )

        self.assertEqual(
            len(callbacks),
            1,
        )

        operations = list(
            self.f.operations()
        )

        self.assert_clean_and_recoverable()

        returned, result, error = callbacks[0]

        self.assertFalse(
            returned,
            "REENTRANCY_OPEN: transport callback returned",
        )

        self.assertIsNone(result)

        self.assertIsInstance(
            error,
            ValueError,
        )

        self.assertEqual(
            calls,
            1,
            "Unexpected recursive provider dispatch",
        )

        self.assertLessEqual(
            operations.count("hold"),
            1,
        )

        self.assertLessEqual(
            operations.count("read"),
            1,
        )

        self.assertLessEqual(
            operations.count("finish"),
            1,
        )

        # Rejecting a callback may poison the outer
        # session, or a locally rejected attempt may
        # leave it usable. Neither permits nested
        # transport dispatch.

        if outer[0]:

            self.assertEqual(
                outer[1],
                self.initial,
            )

            self.assertEqual(
                operations,
                ["hold", "read", "finish"],
            )

        else:

            self.assertIsInstance(
                outer[2],
                ValueError,
            )

    def assert_primary_failure_preserved(
        self,
        *,
        authentication,
    ):

        original_hold = self.provider.hold
        original_read = self.provider.read

        original_caller = CallerFailure(
            "Synthetic caller exception"
        )

        cleanup_error = CleanupFailure(
            "Synthetic transport cleanup failure"
        )

        observed = []

        @contextmanager
        def replacing_hold(**kwargs):

            try:

                with original_hold(**kwargs) as response:

                    yield response

            except Exception as exc:

                observed.append(exc)

                raise cleanup_error

        def invalid_read(**kwargs):

            return failure.corrupt(
                original_read(**kwargs)
            )

        def caller_operation():

            with self.client.exclusive():

                raise original_caller

        with patch.object(
            self.provider,
            "hold",
            side_effect=replacing_hold,
        ):

            if authentication:

                with patch.object(
                    self.provider,
                    "read",
                    side_effect=invalid_read,
                ):

                    outcome = self.capture(
                        self.client.read
                    )

            else:

                outcome = self.capture(
                    caller_operation
                )

        self.assertEqual(
            len(observed),
            1,
        )

        primary = observed[0]

        if authentication:

            self.assertIsInstance(
                primary,
                ValueError,
            )

        else:

            self.assertIs(
                primary,
                original_caller,
            )

        self.assert_clean_and_recoverable()

        returned, result, error = outcome

        self.assertFalse(returned)
        self.assertIsNone(result)

        self.assertIs(
            error,
            primary,
            "PRIMARY_MASKED: transport replaced primary failure",
        )

    def test_01_read_callback_cannot_reenter(self):

        self.assert_reentrancy_rejected(
            "read"
        )

    def test_02_finish_callback_cannot_reenter(self):

        self.assert_reentrancy_rejected(
            "finish"
        )

    def test_03_hold_callback_cannot_reenter(self):

        self.assert_reentrancy_rejected(
            "hold"
        )

    def test_04_cleanup_cannot_replace_authentication_error(self):

        self.assert_primary_failure_preserved(
            authentication=True,
        )

    def test_05_cleanup_cannot_replace_caller_error(self):

        self.assert_primary_failure_preserved(
            authentication=False,
        )

    def test_06_invalid_local_cas_keeps_valid_session(self):

        with self.client.exclusive():

            with self.assertRaises(ValueError):

                self.client.compare_and_set(
                    expected=None,
                    replacement=self.pending,
                )

            with self.assertRaises(ValueError):

                self.client.compare_and_set(
                    expected=self.initial.reference(),
                    replacement=None,
                )

            self.assertFalse(
                self.client._held.poisoned
            )

            # Legitimate caller nesting must remain
            # available after local input rejection.

            with self.client.exclusive():

                self.assertEqual(
                    self.client.read(),
                    self.initial,
                )

            self.assertEqual(
                self.f.operations().count("cas"),
                0,
            )

        self.assertEqual(
            self.f.operations(),
            ["hold", "read", "finish"],
        )

        self.assert_clean_and_recoverable()


if __name__ == "__main__":
    unittest.main()
