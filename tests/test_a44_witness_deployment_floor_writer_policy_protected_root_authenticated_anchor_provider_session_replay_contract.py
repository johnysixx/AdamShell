"""Durable authenticated provider session replay contract.

A session that reached the HOLD signing boundary must
remain consumed after completion, signing failure,
caller interruption or committed root mutation.

Replay rejection must occur before another HOLD response
is exposed and before another signature is generated.

These contracts assume trusted local SQLite persistence.
They do not establish physical rollback resistance or
remote caller authentication.
"""

import importlib
import unittest

from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_contract as base


PREFIX = (
    "core.existence.history_receipt_trust_checkpoint_"
    "protected_provisioning_witness_deployment_floor_"
    "writer_policy_protected_root"
)

provider_module = importlib.import_module(
    PREFIX + "_authenticated_anchor_provider"
)

Provider = (
    provider_module.AuthenticatedProtectedRootAnchorProvider
)


class SyntheticSigningFailure(Exception):
    pass


class SyntheticAbort(BaseException):
    pass


class A44AuthenticatedAnchorProviderSessionReplayContractTests(
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

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.session = b"s" * 32

    def reopen_backend(self):

        return (
            base.sqlite_root.SQLiteProtectedRootBackend.open(
                path=self.f.path,
                expected_identity=self.initial.identity,
            )
        )

    def new_provider(self, backend=None):

        if backend is None:

            backend = self.backend

        return Provider.from_backend(
            backend=backend,
            enrollment=self.f.pin,
            signer=self.f.signer,
        )

    def assert_idle(self, provider):

        self.assertEqual(
            provider._held.phase,
            "idle",
        )

        self.assertIsNone(
            provider._held.session
        )

        self.assertIsNone(
            provider._held.owner
        )

        self.assertIsNone(
            provider._held.reference
        )

        self.assertFalse(
            provider._held.poisoned
        )

        self.assertFalse(
            provider._held.challenges
        )

    def assert_persisted(self, expected):

        self.assertEqual(
            self.backend.read(),
            expected,
        )

        self.assertEqual(
            self.reopen_backend().read(),
            expected,
        )

    def complete(
        self,
        provider,
        *,
        session,
        expected,
    ):

        with provider.hold(
            session=session,
        ) as hold_response:

            self.f.assert_signed_response(
                hold_response,
                expected,
            )

            read_response = provider.read(
                session=session,
                challenge=b"r" * 32,
            )

            self.f.assert_signed_response(
                read_response,
                expected,
            )

            finish_response = provider.finish(
                session=session,
                challenge=b"f" * 32,
                expected=expected.reference(),
            )

            self.f.assert_signed_response(
                finish_response,
                expected,
            )

        self.assert_idle(provider)

        return (
            hold_response,
            read_response,
            finish_response,
        )

    def assert_replay_rejected(
        self,
        provider,
        *,
        expected,
        label,
    ):

        original = Provider._signed

        signing_calls = []
        entered = False
        rejected = False

        def observe_signature(instance, **kwargs):

            signing_calls.append(
                kwargs["operation"]
            )

            return original(
                instance,
                **kwargs,
            )

        with patch.object(
            Provider,
            "_signed",
            new=observe_signature,
        ):

            try:

                with provider.hold(
                    session=self.session,
                ) as response:

                    entered = True

                    self.f.assert_signed_response(
                        response,
                        expected,
                    )

                    provider.finish(
                        session=self.session,
                        challenge=b"f" * 32,
                        expected=expected.reference(),
                    )

            except ValueError:

                rejected = True

        # Verify persistence and cleanup even when
        # the current implementation accepts replay.

        self.assert_idle(provider)

        self.assert_persisted(expected)

        # A replay rejection must not disable fresh
        # sessions or leave the durable fence held.

        self.complete(
            provider,
            session=b"n" * 32,
            expected=expected,
        )

        self.assert_persisted(expected)

        if entered and not rejected:

            self.fail(
                "SESSION_REPLAY_ACCEPTED:" + label
            )

        self.assertTrue(
            rejected,
            "Replay was not explicitly rejected",
        )

        self.assertFalse(
            entered,
            "Replay reached caller entry",
        )

        self.assertEqual(
            signing_calls,
            [],
            "Replay reached the signing boundary",
        )

    def test_01_same_provider_replay_rejected(self):

        self.complete(
            self.provider,
            session=self.session,
            expected=self.initial,
        )

        self.assert_replay_rejected(
            self.provider,
            expected=self.initial,
            label="same_provider",
        )

    def test_02_new_provider_replay_rejected(self):

        self.complete(
            self.provider,
            session=self.session,
            expected=self.initial,
        )

        second = self.new_provider()

        self.assertIsNot(
            second,
            self.provider,
        )

        self.assert_replay_rejected(
            second,
            expected=self.initial,
            label="new_provider",
        )

    def test_03_reopened_backend_replay_rejected(self):

        self.complete(
            self.provider,
            session=self.session,
            expected=self.initial,
        )

        reopened = self.reopen_backend()

        self.assertIsNot(
            reopened,
            self.backend,
        )

        second = self.new_provider(
            backend=reopened,
        )

        self.assert_replay_rejected(
            second,
            expected=self.initial,
            label="reopened_backend",
        )

    def test_04_failed_hold_signing_consumes_session(self):

        original = Provider._signed

        injected = SyntheticSigningFailure(
            "Synthetic HOLD signing failure"
        )

        entered = False
        signing_calls = []

        def fail_hold(instance, **kwargs):

            signing_calls.append(
                kwargs["operation"]
            )

            if kwargs["operation"] == "hold":

                raise injected

            return original(
                instance,
                **kwargs,
            )

        with patch.object(
            Provider,
            "_signed",
            new=fail_hold,
        ):

            with self.assertRaises(
                SyntheticSigningFailure
            ) as caught:

                with self.provider.hold(
                    session=self.session,
                ):

                    entered = True

        self.assertIs(
            caught.exception,
            injected,
        )

        self.assertFalse(entered)

        self.assertEqual(
            signing_calls,
            ["hold"],
        )

        self.assert_idle(
            self.provider
        )

        self.assert_persisted(
            self.initial
        )

        self.assert_replay_rejected(
            self.new_provider(
                backend=self.reopen_backend(),
            ),
            expected=self.initial,
            label="failed_hold_signing",
        )

    def test_05_exposed_hold_abort_consumes_session(self):

        injected = SyntheticAbort(
            "Abort after exposed signed HOLD"
        )

        exposed = []

        with self.assertRaises(
            SyntheticAbort
        ) as caught:

            with self.provider.hold(
                session=self.session,
            ) as response:

                self.f.assert_signed_response(
                    response,
                    self.initial,
                )

                exposed.append(response)

                raise injected

        self.assertIs(
            caught.exception,
            injected,
        )

        self.assertEqual(
            len(exposed),
            1,
        )

        self.assert_idle(
            self.provider
        )

        self.assert_replay_rejected(
            self.new_provider(
                backend=self.reopen_backend(),
            ),
            expected=self.initial,
            label="exposed_hold_abort",
        )

    def test_06_committed_cas_consumes_session(self):

        with self.provider.hold(
            session=self.session,
        ) as response:

            self.f.assert_signed_response(
                response,
                self.initial,
            )

            response = self.provider.compare_and_set(
                session=self.session,
                challenge=b"c" * 32,
                expected=self.initial.reference(),
                replacement=self.pending,
            )

            self.f.assert_signed_response(
                response,
                self.pending,
            )

            response = self.provider.finish(
                session=self.session,
                challenge=b"f" * 32,
                expected=self.pending.reference(),
            )

            self.f.assert_signed_response(
                response,
                self.pending,
            )

        self.assert_idle(
            self.provider
        )

        self.assert_persisted(
            self.pending
        )

        self.assertEqual(
            self.backend.read().revision,
            self.initial.revision + 1,
        )

        self.assert_replay_rejected(
            self.new_provider(
                backend=self.reopen_backend(),
            ),
            expected=self.pending,
            label="committed_cas",
        )

    def test_07_fresh_sessions_remain_available(self):

        first = self.complete(
            self.provider,
            session=self.session,
            expected=self.initial,
        )

        second = self.complete(
            self.new_provider(
                backend=self.reopen_backend(),
            ),
            session=b"n" * 32,
            expected=self.initial,
        )

        self.assertNotEqual(
            first[0][1],
            second[0][1],
        )

        self.assertNotEqual(
            first[1][1],
            second[1][1],
        )

        self.assertNotEqual(
            first[2][1],
            second[2][1],
        )

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

        self.assert_persisted(
            self.initial
        )

    def test_08_stale_cas_remains_rejected(self):

        self.assertEqual(
            self.client.compare_and_set(
                expected=self.initial.reference(),
                replacement=self.pending,
            ),
            self.pending.reference(),
        )

        provider = self.new_provider(
            backend=self.reopen_backend(),
        )

        entered = False

        with self.assertRaises(ValueError):

            with provider.hold(
                session=self.session,
            ) as response:

                entered = True

                self.f.assert_signed_response(
                    response,
                    self.pending,
                )

                provider.compare_and_set(
                    session=self.session,
                    challenge=b"c" * 32,
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

        self.assertTrue(
            entered,
            "Fresh session itself was rejected",
        )

        self.assert_idle(provider)

        self.assert_persisted(
            self.pending
        )

        self.assertEqual(
            self.client.read(),
            self.pending,
        )

        self.assertEqual(
            self.backend.read().revision,
            self.initial.revision + 1,
        )


if __name__ == "__main__":
    unittest.main()
