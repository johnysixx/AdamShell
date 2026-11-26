"""Authentication failure and replay contracts.

Synthetic transport, temporary root databases and test keys.
Signatures authenticate statements, not physical fence durability.
"""

import unittest

from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_contract as previous


def corrupt(response):

    state, signature = response

    return (
        state,
        bytes([signature[0] ^ 1]) + signature[1:],
    )


class A44AuthenticatedProtectedRootAnchorClientFailureTests(
    unittest.TestCase
):

    def setUp(self):

        self.f = (
            previous.A44AuthenticatedProtectedRootAnchorClientContractTests(
                "test_01_canonical_backend_interface"
            )
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.client = self.f.client
        self.provider = self.f.provider

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.anchor = self.f.f.anchor
        self.local = self.f.f.local

        self.other_signer = Ed25519PrivateKey.from_private_bytes(
            b"z" * 32
        )

    def assert_unchanged(self):

        self.assertIsNone(self.provider.active)
        self.assertEqual(self.anchor.read(), self.initial)
        self.assertEqual(self.local.read(), self.initial)

    def test_01_replacement_signer_rejected_before_caller_entry(self):

        entered = []

        with patch.object(
            self.provider, "signer", self.other_signer
        ), patch.object(
            self.provider, "read",
            side_effect=AssertionError("Unauthorized read"),
        ) as forbidden:

            with self.assertRaises(ValueError):

                with self.client.exclusive():
                    entered.append(True)

            forbidden.assert_not_called()

        self.assertEqual(entered, [])
        self.assert_unchanged()

        self.assertEqual(self.client.read(), self.initial)

    def test_02_invalid_read_signature_rejected(self):

        original = self.provider.read

        def invalid_read(**kwargs):
            return corrupt(original(**kwargs))

        with patch.object(
            self.provider, "read", side_effect=invalid_read
        ) as invalid:

            with self.assertRaises(ValueError):
                self.client.read()

            invalid.assert_called_once()

        self.assert_unchanged()

        self.assertEqual(self.client.read(), self.initial)

    def test_03_same_session_read_replay_rejected(self):

        original = self.provider.read
        responses = []
        requests = []

        def replay(**kwargs):

            requests.append(kwargs["challenge"])

            if not responses:
                responses.append(original(**kwargs))

            return responses[0]

        with patch.object(
            self.provider, "read", side_effect=replay
        ):

            with self.assertRaises(ValueError):

                with self.client.exclusive():

                    self.assertEqual(
                        self.client.read(),
                        self.initial,
                    )

                    self.client.read()

        self.assertGreaterEqual(len(requests), 2)
        self.assertNotEqual(requests[0], requests[1])
        self.assert_unchanged()

    def test_04_previous_session_read_replay_rejected(self):

        original = self.provider.read
        captured = []

        def capture(**kwargs):

            response = original(**kwargs)

            captured.append(
                (kwargs["session"], response)
            )

            return response

        with patch.object(
            self.provider, "read", side_effect=capture
        ):

            self.assertEqual(self.client.read(), self.initial)

        self.assertTrue(captured)

        previous_session, response = captured[0]

        sessions = []

        def replay(**kwargs):

            sessions.append(kwargs["session"])

            return response

        with patch.object(
            self.provider, "read", side_effect=replay
        ):

            with self.assertRaises(ValueError):
                self.client.read()

        self.assertTrue(sessions)
        self.assertNotEqual(sessions[0], previous_session)

        self.assert_unchanged()

    def test_05_invalid_cas_ack_does_not_retry_or_rollback(self):

        original = self.provider.compare_and_set

        committed = []

        def invalid_ack(**kwargs):

            response = original(**kwargs)

            committed.append(
                response[0].reference()
            )

            return corrupt(response)

        with patch.object(
            self.provider,
            "compare_and_set",
            side_effect=invalid_ack,
        ) as invalid:

            with self.assertRaises(ValueError):

                self.client.compare_and_set(
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

            invalid.assert_called_once()

        self.assertEqual(
            committed,
            [self.pending.reference()],
        )

        self.assertIsNone(self.provider.active)

        self.assertEqual(self.anchor.read(), self.pending)
        self.assertEqual(self.local.read(), self.initial)

        # A new authenticated session can observe the
        # committed state. It must not invent another CAS.

        self.assertEqual(self.client.read(), self.pending)

        self.assertEqual(
            self.f.operations().count("cas"),
            1,
        )

    def test_06_signed_cas_with_wrong_request_binding_rejected(self):

        original = self.provider.response

        observed = []

        def incorrect_binding(
            operation, session, challenge, state,
            expected=None, replacement=None,
        ):

            if operation == "cas":

                observed.append((expected, replacement))

                # The signature is genuine, but the
                # signed request reference is incorrect.

                expected = self.pending.reference()

            return original(
                operation,
                session,
                challenge,
                state,
                expected=expected,
                replacement=replacement,
            )

        with patch.object(
            self.provider, "response",
            side_effect=incorrect_binding,
        ):

            with self.assertRaises(ValueError):

                self.client.compare_and_set(
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

        self.assertEqual(
            observed,
            [
                (
                    self.initial.reference(),
                    self.pending.reference(),
                )
            ],
        )

        self.assertIsNone(self.provider.active)

        self.assertEqual(self.anchor.read(), self.pending)
        self.assertEqual(self.local.read(), self.initial)

        self.assertEqual(self.client.read(), self.pending)

    def test_07_invalid_finish_signature_rejected(self):

        original = self.provider.finish

        def invalid_finish(**kwargs):

            return corrupt(original(**kwargs))

        with patch.object(
            self.provider, "finish",
            side_effect=invalid_finish,
        ) as invalid:

            with self.assertRaises(ValueError):
                self.client.read()

            invalid.assert_called_once()

        self.assert_unchanged()

        self.assertEqual(self.client.read(), self.initial)

    def test_08_failed_authentication_poisons_held_session(self):

        original = self.provider.read

        def invalid_read(**kwargs):
            return corrupt(original(**kwargs))

        with self.assertRaises(ValueError):

            with self.client.exclusive():

                with patch.object(
                    self.provider, "read",
                    side_effect=invalid_read,
                ):

                    with self.assertRaises(ValueError):
                        self.client.read()

                # Catching the first exception must not
                # restore trust in the compromised session.

                with patch.object(
                    self.provider, "read",
                    side_effect=AssertionError(
                        "Poisoned session attempted read"
                    ),
                ) as forbidden_read, patch.object(
                    self.provider, "compare_and_set",
                    side_effect=AssertionError(
                        "Poisoned session attempted CAS"
                    ),
                ) as forbidden_cas:

                    with self.assertRaises(ValueError):
                        self.client.read()

                    with self.assertRaises(ValueError):

                        self.client.compare_and_set(
                            expected=self.initial.reference(),
                            replacement=self.pending,
                        )

                    forbidden_read.assert_not_called()
                    forbidden_cas.assert_not_called()

        self.assert_unchanged()

        # Only a new independently verified session may
        # restore normal read access.

        self.assertEqual(self.client.read(), self.initial)
