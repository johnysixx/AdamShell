"""Authenticated protected root provider validation contract.

The provider rejects malformed requests and enforces
fail-closed lifecycle rules for a held local SQLite fence.

This contract does not establish remote caller identity,
durable replay tracking across process restarts, hardware
rollback resistance or signing-key isolation.
"""

import unittest

from dataclasses import replace

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_contract as base


class SyntheticAbort(BaseException):
    pass


class BytesSubclass(bytes):
    pass


class A44AuthenticatedAnchorProviderValidationContractTests(
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

    def assert_initial_and_recoverable(self):

        self.f.assert_initial()

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

        self.f.assert_initial()

    def reject_held(self, operation):

        # Invalid requests deliberately escape the session.
        # Any already committed root transition must survive
        # cleanup, but these requests must never dispatch CAS.

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=self.session,
            ) as response:

                self.f.assert_signed_response(
                    response,
                    self.initial,
                )

                operation()

        self.assert_initial_and_recoverable()

    def read_request(
        self,
        *,
        session=None,
        challenge=b"r" * 32,
    ):

        return self.provider.read(
            session=(
                self.session if session is None
                else session
            ),
            challenge=challenge,
        )

    def cas_request(
        self,
        *,
        expected,
        replacement,
        challenge=b"c" * 32,
    ):

        return self.provider.compare_and_set(
            session=self.session,
            challenge=challenge,
            expected=expected,
            replacement=replacement,
        )

    def finish_request(
        self,
        *,
        expected,
        challenge=b"f" * 32,
    ):

        return self.provider.finish(
            session=self.session,
            challenge=challenge,
            expected=expected,
        )

    def test_01_noncanonical_enrollment_rejected(self):

        for enrollment in (
            object(),
            {},
            self.f.pin.fingerprint(),
        ):

            with self.subTest(
                kind=type(enrollment).__name__
            ):

                with self.assertRaises(ValueError):

                    self.f.make_provider(
                        enrollment=enrollment,
                    )

        self.assert_initial_and_recoverable()

    def test_02_invalid_signer_rejected(self):

        for signer in (
            object(),
            {},
            b"k" * 32,
            self.f.signer.public_key(),
        ):

            with self.subTest(
                kind=type(signer).__name__
            ):

                with self.assertRaises(ValueError):

                    self.f.make_provider(
                        signer=signer,
                    )

        self.assert_initial_and_recoverable()

    def test_03_unprovisioned_backend_cannot_hold(self):

        unprovisioned = (
            base.sqlite_root.SQLiteProtectedRootBackend.create(
                path=self.f.path.with_name(
                    "unprovisioned.sqlite3"
                ),
                expected_identity=self.initial.identity,
            )
        )

        provider = self.f.make_provider(
            backend=unprovisioned,
        )

        entered = False

        with self.assertRaises(ValueError):

            with provider.hold(
                session=self.session,
            ):

                entered = True

        self.assertFalse(
            entered,
            "Unprovisioned root entered HOLD",
        )

        # Failed HOLD must not retain the backend fence.

        unprovisioned.provision(
            state=self.initial
        )

        client = (
            base.client_module
            .AuthenticatedProtectedRootAnchorClient
            .from_provider(
                provider=provider,
                enrollment=self.f.pin,
            )
        )

        self.assertEqual(
            client.read(),
            self.initial,
        )

        self.assert_initial_and_recoverable()

    def test_04_strict_session_validation(self):

        malformed = (
            None,
            True,
            32,
            "s" * 32,
            b"",
            b"s" * 31,
            b"s" * 33,
            bytearray(b"s" * 32),
            memoryview(b"s" * 32),
            BytesSubclass(b"s" * 32),
        )

        for session in malformed:

            with self.subTest(
                kind=type(session).__name__,
                value=repr(session),
            ):

                entered = False

                with self.assertRaises(ValueError):

                    with self.provider.hold(
                        session=session,
                    ):

                        entered = True

                self.assertFalse(
                    entered,
                    "Invalid session entered HOLD",
                )

        self.assert_initial_and_recoverable()

    def test_05_strict_challenge_validation(self):

        malformed = (
            None,
            True,
            32,
            "r" * 32,
            b"",
            b"r" * 31,
            b"r" * 33,
            bytearray(b"r" * 32),
            memoryview(b"r" * 32),
            BytesSubclass(b"r" * 32),
        )

        # Every malformed challenge must be rejected
        # for all three authenticated operations.

        for index, challenge in enumerate(
            malformed,
            1,
        ):

            for operation in ("read", "cas", "finish"):

                with self.subTest(
                    operation=operation,
                    kind=type(challenge).__name__,
                ):

                    self.session = (
                        index.to_bytes(31, "big")
                        + bytes([
                            {
                                "read": 1,
                                "cas": 2,
                                "finish": 3,
                            }[operation]
                        ])
                    )

                    if operation == "read":

                        self.reject_held(
                            lambda: self.read_request(
                                challenge=challenge,
                            )
                        )

                    elif operation == "cas":

                        self.reject_held(
                            lambda: self.cas_request(
                                expected=self.initial.reference(),
                                replacement=self.pending,
                                challenge=challenge,
                            )
                        )

                    else:

                        self.reject_held(
                            lambda: self.finish_request(
                                expected=self.initial.reference(),
                                challenge=challenge,
                            )
                        )

    def test_06_hold_challenge_cannot_be_reused(self):

        self.reject_held(
            lambda: self.cas_request(
                expected=self.initial.reference(),
                replacement=self.pending,
                challenge=self.session,
            )
        )

    def test_07_noncanonical_expected_reference_rejected(self):

        malformed = (
            None,
            True,
            self.initial.revision,
            self.initial.reference().sha256,
            {
                "revision": self.initial.revision,
                "sha256": self.initial.reference().sha256,
            },
        )

        for index, expected in enumerate(
            malformed,
            1,
        ):

            with self.subTest(
                kind=type(expected).__name__
            ):

                self.session = bytes([index]) * 32

                self.reject_held(
                    lambda: self.cas_request(
                        expected=expected,
                        replacement=self.pending,
                    )
                )

    def test_08_noncanonical_replacement_rejected(self):

        malformed = (
            None,
            True,
            self.pending.reference(),
            self.pending.durable_state,
            {},
        )

        for index, replacement in enumerate(
            malformed,
            1,
        ):

            with self.subTest(
                kind=type(replacement).__name__
            ):

                self.session = bytes([index]) * 32

                self.reject_held(
                    lambda: self.cas_request(
                        expected=self.initial.reference(),
                        replacement=replacement,
                    )
                )

    def test_09_stale_cas_reference_rejected(self):

        self.assertEqual(
            self.client.compare_and_set(
                expected=self.initial.reference(),
                replacement=self.pending,
            ),
            self.pending.reference(),
        )

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=self.session,
            ) as response:

                self.f.assert_signed_response(
                    response,
                    self.pending,
                )

                self.cas_request(
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

        self.f.assert_pending()

        self.assertEqual(
            self.client.read(),
            self.pending,
        )

    def test_10_replacement_identity_cannot_change(self):

        nonce = bytes(
            value ^ 1
            for value in
            self.pending.identity.provisioning_nonce
        )

        identity = replace(
            self.pending.identity,
            provisioning_nonce=nonce,
        )

        replacement = replace(
            self.pending,
            identity=identity,
        )

        self.reject_held(
            lambda: self.cas_request(
                expected=self.initial.reference(),
                replacement=replacement,
            )
        )

    def test_11_revision_jump_rejected(self):

        replacement = replace(
            self.pending,
            revision=self.pending.revision + 1,
        )

        self.reject_held(
            lambda: self.cas_request(
                expected=self.initial.reference(),
                replacement=replacement,
            )
        )

    def test_12_wrong_finish_reference_rejected(self):

        self.reject_held(
            lambda: self.finish_request(
                expected=self.pending.reference(),
            )
        )

    def test_13_caught_error_cannot_restore_session(self):

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=self.session,
            ):

                self.f.assert_signed_response(
                    self.read_request(),
                    self.initial,
                )

                # The repeated challenge must poison
                # the active provider session.

                with self.assertRaises(ValueError):

                    self.cas_request(
                        expected=self.initial.reference(),
                        replacement=self.pending,
                        challenge=b"r" * 32,
                    )

                # All following requests are otherwise
                # valid and have fresh challenges.

                with self.assertRaises(ValueError):

                    self.read_request(
                        challenge=b"x" * 32,
                    )

                with self.assertRaises(ValueError):

                    self.cas_request(
                        expected=self.initial.reference(),
                        replacement=self.pending,
                    )

                with self.assertRaises(ValueError):

                    self.finish_request(
                        expected=self.initial.reference(),
                    )

                self.f.assert_initial()

        self.assert_initial_and_recoverable()

    def test_14_nested_hold_rejected(self):

        entered = False

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=self.session,
            ):

                with self.provider.hold(
                    session=b"n" * 32,
                ):

                    entered = True

        self.assertFalse(
            entered,
            "Nested provider HOLD entered",
        )

        self.assert_initial_and_recoverable()

    def test_15_normal_exit_requires_finish(self):

        entered = False

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=self.session,
            ):

                entered = True

                self.f.assert_signed_response(
                    self.read_request(),
                    self.initial,
                )

                # Normal context exit without FINISH
                # must not imply protocol success.

        self.assertTrue(
            entered,
            "The valid HOLD itself was rejected",
        )

        self.assert_initial_and_recoverable()

    def test_16_base_exception_preserved_and_session_reset(self):

        original = SyntheticAbort(
            "Synthetic abort inside provider HOLD"
        )

        with self.assertRaises(
            SyntheticAbort
        ) as caught:

            with self.provider.hold(
                session=self.session,
            ):

                self.f.assert_signed_response(
                    self.cas_request(
                        expected=self.initial.reference(),
                        replacement=self.pending,
                    ),
                    self.pending,
                )

                raise original

        self.assertIs(
            caught.exception,
            original,
        )

        # The committed root is not reverted just
        # because the surrounding session failed.

        self.f.assert_pending()

        self.assertEqual(
            self.client.read(),
            self.pending,
        )

        self.f.assert_pending()


if __name__ == "__main__":
    unittest.main()
