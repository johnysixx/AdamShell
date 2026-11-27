"""Permanent authenticated provider signing adversarial contracts.

The signature boundary must reject malformed responses,
reentrant operations and poisoned sessions.

A durably committed session cannot be reused after signing
failure. A committed CAS must not be rolled back or retried
merely because its signature could not be returned.

Direct trusted backend mutation remains a separate boundary:
the provider must detect divergence without pretending that
it prevented an already committed out-of-band transition.
"""

import hashlib
import importlib
import sqlite3
import unittest

from contextlib import closing
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_contract as base


class SyntheticSigningFailure(Exception):
    pass


class A44AuthenticatedAnchorProviderSigningAdversarialTests(
    unittest.TestCase
):

    def setUp(self):

        self.f = (
            base.A44AuthenticatedAnchorProviderContractTests(
                "test_01_canonical_immutable_provider_configuration"
            )
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.provider = self.f.provider
        self.client = self.f.client
        self.backend = self.f.backend

        self.Provider = type(self.provider)

        self.module = importlib.import_module(
            self.Provider.__module__
        )

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.session = b"s" * 32

    def assert_idle(self):

        held = self.provider._held

        self.assertEqual(held.phase, "idle")
        self.assertIsNone(held.session)
        self.assertIsNone(held.owner)
        self.assertIsNone(held.reference)

        self.assertFalse(held.poisoned)
        self.assertFalse(held.challenges)

    def history(self):

        with closing(
            sqlite3.connect(
                self.f.path.resolve().as_uri() + "?mode=ro",
                uri=True,
                timeout=5,
            )
        ) as connection:

            sessions = [
                row[0]
                for row in connection.execute(
                    "SELECT session FROM consumed_sessions "
                    "ORDER BY session"
                )
            ]

            commitment = connection.execute(
                "SELECT history_digest FROM session_metadata"
            ).fetchall()

        expected = hashlib.sha256(
            b"AdamShell/A44/protected-root-session-history/v2"
            + b"\x00"
            + b"".join(sessions)
            + len(sessions).to_bytes(8, "big")
        ).hexdigest()

        self.assertEqual(
            commitment,
            [(expected,)],
        )

        return set(sessions)

    def assert_recovery(self, expected):

        self.assert_idle()

        self.assertEqual(
            self.backend.read(),
            expected,
        )

        reopened = (
            base.sqlite_root.SQLiteProtectedRootBackend.open(
                path=self.f.path,
                expected_identity=self.initial.identity,
            )
        )

        self.assertEqual(
            reopened.read(),
            expected,
        )

        self.assertEqual(
            self.client.read(),
            expected,
        )

        self.history()
        self.assert_idle()

    def finish(self, state=None):

        if state is None:
            state = self.initial

        return self.provider.finish(
            session=self.session,
            challenge=b"f" * 32,
            expected=state.reference(),
        )

    def read(self, challenge=b"r" * 32):

        return self.provider.read(
            session=self.session,
            challenge=challenge,
        )

    def cas(self):

        return self.provider.compare_and_set(
            session=self.session,
            challenge=b"c" * 32,
            expected=self.initial.reference(),
            replacement=self.pending,
        )

    def assert_poisoned_operations_rejected(self):

        for operation in (
            self.read,
            self.cas,
            self.finish,
        ):

            with self.assertRaises(ValueError):
                operation()

    def assert_replay_rejected(self, session=None):

        if session is None:
            session = self.session

        before = self.history()
        signing_calls = []
        entered = []

        original = self.Provider._signed

        def observe(instance, **kwargs):

            signing_calls.append(
                kwargs["operation"]
            )

            return original(instance, **kwargs)

        with patch.object(
            self.Provider,
            "_signed",
            new=observe,
        ):

            with self.assertRaises(ValueError):

                with self.provider.hold(
                    session=session,
                ):

                    entered.append(True)

        self.assertEqual(entered, [])
        self.assertEqual(signing_calls, [])
        self.assertEqual(self.history(), before)

        self.assert_idle()

    def fail_signing(self, operation):

        injected = SyntheticSigningFailure(operation)

        original = self.Provider._signed
        calls = []
        sessions = []

        def fail(instance, **kwargs):

            name = kwargs["operation"]
            calls.append(name)

            if name == operation:

                sessions.append(
                    kwargs["session"]
                )

                raise injected

            return original(instance, **kwargs)

        return injected, calls, sessions, fail

    def test_01_hold_signing_failure_consumes_session(self):

        injected, calls, sessions, fail = (
            self.fail_signing("hold")
        )

        entered = []

        with patch.object(
            self.Provider,
            "_signed",
            new=fail,
        ):

            with self.assertRaises(
                SyntheticSigningFailure
            ) as caught:

                with self.provider.hold(
                    session=self.session,
                ):

                    entered.append(True)

        self.assertIs(caught.exception, injected)
        self.assertEqual(calls, ["hold"])
        self.assertEqual(entered, [])
        self.assertEqual(sessions, [self.session])

        self.assertIn(
            self.session,
            self.history(),
        )

        self.assert_replay_rejected()
        self.assert_recovery(self.initial)

    def test_02_read_signing_failure_poisons_session(self):

        injected, calls, sessions, fail = (
            self.fail_signing("read")
        )

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=self.session,
            ):

                with patch.object(
                    self.Provider,
                    "_signed",
                    new=fail,
                ):

                    with self.assertRaises(
                        SyntheticSigningFailure
                    ) as caught:

                        self.read()

                self.assertIs(
                    caught.exception,
                    injected,
                )

                self.assert_poisoned_operations_rejected()

        self.assertEqual(calls, ["read"])
        self.assertEqual(sessions, [self.session])

        self.assert_replay_rejected()
        self.assert_recovery(self.initial)

    def test_03_cas_signing_failure_preserves_commit(self):

        injected, calls, sessions, fail = (
            self.fail_signing("cas")
        )

        with patch.object(
            self.Provider,
            "_signed",
            new=fail,
        ):

            with self.assertRaises(
                SyntheticSigningFailure
            ) as caught:

                self.client.compare_and_set(
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

        self.assertIs(caught.exception, injected)
        self.assertEqual(calls, ["hold", "cas"])
        self.assertEqual(len(sessions), 1)

        self.assertEqual(
            self.backend.read(),
            self.pending,
        )

        self.assertEqual(
            self.pending.revision,
            self.initial.revision + 1,
        )

        self.assertIn(
            sessions[0],
            self.history(),
        )

        self.assert_replay_rejected(
            sessions[0]
        )

        self.assert_recovery(self.pending)

    def test_04_finish_signing_failure_preserves_exception(self):

        injected, calls, sessions, fail = (
            self.fail_signing("finish")
        )

        with patch.object(
            self.Provider,
            "_signed",
            new=fail,
        ):

            with self.assertRaises(
                SyntheticSigningFailure
            ) as caught:

                self.client.read()

        self.assertIs(caught.exception, injected)

        self.assertEqual(
            calls,
            ["hold", "read", "finish"],
        )

        self.assertEqual(len(sessions), 1)

        self.assert_replay_rejected(
            sessions[0]
        )

        self.assert_recovery(self.initial)

    def test_05_invalid_signature_rejected(self):

        signer_type = type(self.f.signer)
        original = signer_type.sign

        calls = []

        def corrupt(instance, message):

            signature = original(
                instance,
                message,
            )

            calls.append(message)

            return (
                bytes([signature[0] ^ 1])
                + signature[1:]
            )

        entered = []

        with patch.object(
            signer_type,
            "sign",
            new=corrupt,
        ):

            with self.assertRaises(ValueError):

                with self.provider.hold(
                    session=self.session,
                ):

                    entered.append(True)

        self.assertEqual(len(calls), 1)
        self.assertEqual(entered, [])

        self.assert_replay_rejected()
        self.assert_recovery(self.initial)

    def assert_signing_reentrancy(
        self,
        operation,
        expected,
    ):

        original = self.Provider._signed

        calls = []
        nested_rejected = []

        def reenter(instance, **kwargs):

            name = kwargs["operation"]

            calls.append(name)

            if name == operation:

                try:

                    instance.read(
                        session=kwargs["session"],
                        challenge=b"z" * 32,
                    )

                except ValueError:

                    nested_rejected.append(name)

                else:

                    self.fail(
                        "Reentrant signing operation accepted"
                    )

            return original(instance, **kwargs)

        with patch.object(
            self.Provider,
            "_signed",
            new=reenter,
        ):

            with self.assertRaises(ValueError):

                with self.provider.hold(
                    session=self.session,
                ):

                    if operation == "read":

                        self.read()

                    elif operation == "cas":

                        self.cas()

                    elif operation == "finish":

                        self.finish()

                    else:

                        self.fail(
                            "Reentrant HOLD was exposed"
                        )

        expected_calls = (
            ["hold"]
            if operation == "hold"
            else ["hold", operation]
        )

        self.assertEqual(
            calls,
            expected_calls,
        )

        self.assertEqual(
            nested_rejected,
            [operation],
        )

        self.assert_replay_rejected()
        self.assert_recovery(expected)

    def test_06_hold_signing_reentrancy_rejected(self):

        self.assert_signing_reentrancy(
            "hold",
            self.initial,
        )

    def test_07_read_signing_reentrancy_rejected(self):

        self.assert_signing_reentrancy(
            "read",
            self.initial,
        )

    def test_08_cas_signing_reentrancy_preserves_commit(self):

        self.assert_signing_reentrancy(
            "cas",
            self.pending,
        )

    def test_09_finish_signing_reentrancy_rejected(self):

        self.assert_signing_reentrancy(
            "finish",
            self.initial,
        )

    def test_10_challenge_capacity_exhaustion_fails_closed(self):

        with patch.object(
            self.module,
            "_MAX_SESSION_CHALLENGES",
            3,
        ):

            with self.assertRaises(ValueError):

                with self.provider.hold(
                    session=self.session,
                ):

                    self.read(b"a" * 32)
                    self.read(b"b" * 32)

                    with self.assertRaises(ValueError):
                        self.cas()

                    with self.assertRaises(ValueError):
                        self.finish()

        self.assert_replay_rejected()
        self.assert_recovery(self.initial)

    def test_11_completed_session_replay_never_signs(self):

        with self.provider.hold(
            session=self.session,
        ):

            self.read()
            self.finish()

        self.assert_replay_rejected()
        self.assert_recovery(self.initial)

    def test_12_out_of_band_root_transition_detected(self):

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=self.session,
            ):

                result = self.backend.compare_and_set(
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

                self.assertEqual(
                    result,
                    self.pending.reference(),
                )

                with self.assertRaises(ValueError):
                    self.read()

                with self.assertRaises(ValueError):
                    self.finish(self.pending)

        self.assert_replay_rejected()
        self.assert_recovery(self.pending)


if __name__ == "__main__":
    unittest.main()
