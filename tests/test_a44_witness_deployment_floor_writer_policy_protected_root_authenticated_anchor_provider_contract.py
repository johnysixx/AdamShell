"""Production authenticated protected root provider contract.

The provider authenticates root responses and controls
the lifecycle of an exclusive backend session.

These tests use trusted local SQLite storage and synthetic
signing keys. They do not establish remote caller identity,
hardware key isolation or physical rollback resistance.
"""

import importlib
import tempfile
import unittest

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_contract as protocol


PREFIX = (
    "core.existence.history_receipt_trust_checkpoint_"
    "protected_provisioning_witness_deployment_floor_"
    "writer_policy_protected_root"
)

PROVIDER_MODULE = (
    PREFIX + "_authenticated_anchor_provider"
)

root = importlib.import_module(PREFIX)

sqlite_root = importlib.import_module(
    PREFIX + "_sqlite_reference"
)

client_module = importlib.import_module(
    PREFIX + "_authenticated_anchor_client"
)


class SyntheticCallerFailure(Exception):
    pass


class A44AuthenticatedAnchorProviderContractTests(
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

        self.initial = self.f.initial
        self.pending = self.f.pending
        self.pin = self.f.pin
        self.signer = self.f.signer

        directory = tempfile.TemporaryDirectory(
            prefix="a44-authenticated-provider-"
        )

        self.addCleanup(directory.cleanup)

        self.path = (
            Path(directory.name)
            / "anchor.sqlite3"
        )

        self.backend = (
            sqlite_root.SQLiteProtectedRootBackend.create(
                path=self.path,
                expected_identity=self.initial.identity,
            )
        )

        self.backend.provision(
            state=self.initial
        )

        self.assertEqual(
            self.backend.read(),
            self.initial,
        )

        # Deliberately import inside setUp.
        # The initial RED must be a missing module,
        # not a test collection failure.

        self.m = importlib.import_module(
            PROVIDER_MODULE
        )

        self.provider = self.make_provider()

        self.client = (
            client_module
            .AuthenticatedProtectedRootAnchorClient
            .from_provider(
                provider=self.provider,
                enrollment=self.pin,
            )
        )

    def make_provider(
        self,
        *,
        backend=None,
        enrollment=None,
        signer=None,
    ):

        return (
            self.m
            .AuthenticatedProtectedRootAnchorProvider
            .from_backend(
                backend=(
                    self.backend if backend is None
                    else backend
                ),
                enrollment=(
                    self.pin if enrollment is None
                    else enrollment
                ),
                signer=(
                    self.signer if signer is None
                    else signer
                ),
            )
        )

    def assert_initial(self):

        self.assertEqual(
            self.backend.read(),
            self.initial,
        )

    def assert_pending(self):

        reopened = (
            sqlite_root.SQLiteProtectedRootBackend.open(
                path=self.path,
                expected_identity=self.initial.identity,
            )
        )

        self.assertEqual(
            reopened.read(),
            self.pending,
        )

    def assert_signed_response(self, response, expected):

        self.assertIs(type(response), tuple)
        self.assertEqual(len(response), 2)

        state, signature = response

        self.assertIs(
            type(state),
            root.ProtectedDurableRootState,
        )

        self.assertEqual(
            state,
            expected,
        )

        self.assertIs(
            type(signature),
            bytes,
        )

        self.assertEqual(
            len(signature),
            64,
        )

    def finish(self, *, session, state):

        response = self.provider.finish(
            session=session,
            challenge=b"f" * 32,
            expected=state.reference(),
        )

        self.assert_signed_response(
            response,
            state,
        )

    def test_01_canonical_immutable_provider_configuration(self):

        self.assertIs(
            type(self.provider),
            self.m.AuthenticatedProtectedRootAnchorProvider,
        )

        self.assertFalse(
            hasattr(self.provider, "__dict__")
        )

        self.assertEqual(
            self.provider.enrollment,
            self.pin,
        )

        self.assertEqual(
            self.provider.identity,
            self.initial.identity,
        )

        with self.assertRaises(
            (FrozenInstanceError, AttributeError)
        ):

            self.provider.enrollment = None

        self.assert_initial()

    def test_02_wrong_signing_key_rejected(self):

        wrong_signer = (
            Ed25519PrivateKey.generate()
        )

        with self.assertRaises(ValueError):

            self.make_provider(
                signer=wrong_signer,
            )

        self.assert_initial()

    def test_03_wrong_deployment_identity_rejected(self):

        wrong_identity = replace(
            self.initial.identity,
            provisioning_nonce=(
                bytes(
                    value ^ 1
                    for value in
                    self.initial.identity.provisioning_nonce
                )
            ),
        )

        wrong_pin = replace(
            self.pin,
            identity=wrong_identity,
        )

        with self.assertRaises(ValueError):

            self.make_provider(
                enrollment=wrong_pin,
            )

        self.assert_initial()

    def test_04_nonpersistent_backend_rejected(self):

        memory = root.InMemoryProtectedRootBackend(
            identity=self.initial.identity,
        )

        memory.provision(
            state=self.initial
        )

        with self.assertRaises(ValueError):

            self.make_provider(
                backend=memory,
            )

        self.assertEqual(
            memory.read(),
            self.initial,
        )

        self.assert_initial()

    def test_05_existing_client_authenticates_read(self):

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

        self.assert_initial()

    def test_06_existing_client_authenticates_cas(self):

        result = self.client.compare_and_set(
            expected=self.initial.reference(),
            replacement=self.pending,
        )

        self.assertEqual(
            result,
            self.pending.reference(),
        )

        self.assert_pending()

        self.assertEqual(
            self.client.read(),
            self.pending,
        )

    def test_07_multiple_operations_share_held_session(self):

        with self.client.exclusive():

            self.assertEqual(
                self.client.read(),
                self.initial,
            )

            with self.client.exclusive():

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

        self.assert_pending()

    def test_08_operations_without_hold_rejected(self):

        session = b"s" * 32

        operations = [
            lambda: self.provider.read(
                session=session,
                challenge=b"r" * 32,
            ),
            lambda: self.provider.compare_and_set(
                session=session,
                challenge=b"c" * 32,
                expected=self.initial.reference(),
                replacement=self.pending,
            ),
            lambda: self.provider.finish(
                session=session,
                challenge=b"f" * 32,
                expected=self.initial.reference(),
            ),
        ]

        for operation in operations:

            with self.assertRaises(ValueError):

                operation()

        self.assert_initial()

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

    def test_09_foreign_session_rejected(self):

        session = b"s" * 32
        foreign = b"x" * 32

        # An invalid request may poison the active
        # session. No successful FINISH is expected
        # from this deliberately rejected operation.

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=session,
            ) as response:

                self.assert_signed_response(
                    response,
                    self.initial,
                )

                self.provider.compare_and_set(
                    session=foreign,
                    challenge=b"c" * 32,
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

        self.assert_initial()

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

    def test_10_repeated_challenge_rejected_before_cas(self):

        session = b"s" * 32
        challenge = b"r" * 32

        with self.assertRaises(ValueError):

            with self.provider.hold(
                session=session,
            ) as response:

                self.assert_signed_response(
                    response,
                    self.initial,
                )

                response = self.provider.read(
                    session=session,
                    challenge=challenge,
                )

                self.assert_signed_response(
                    response,
                    self.initial,
                )

                # Reuse a READ challenge for a CAS.
                # The root must remain unchanged.

                self.provider.compare_and_set(
                    session=session,
                    challenge=challenge,
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

        self.assert_initial()

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

    def test_11_operations_after_finish_rejected(self):

        operations = [
            lambda session: self.provider.read(
                session=session,
                challenge=b"r" * 32,
            ),
            lambda session: self.provider.compare_and_set(
                session=session,
                challenge=b"c" * 32,
                expected=self.initial.reference(),
                replacement=self.pending,
            ),
            lambda session: self.provider.finish(
                session=session,
                challenge=b"g" * 32,
                expected=self.initial.reference(),
            ),
        ]

        for index, operation in enumerate(
            operations,
            1,
        ):

            session = bytes([index]) * 32

            with self.assertRaises(ValueError):

                with self.provider.hold(
                    session=session,
                ) as response:

                    self.assert_signed_response(
                        response,
                        self.initial,
                    )

                    self.finish(
                        session=session,
                        state=self.initial,
                    )

                    operation(session)

            self.assert_initial()

        self.assertEqual(
            self.client.read(),
            self.initial,
        )

    def test_12_committed_cas_survives_caller_exception(self):

        original = SyntheticCallerFailure(
            "Synthetic interruption after committed CAS"
        )

        session = b"s" * 32

        with self.assertRaises(
            SyntheticCallerFailure
        ) as captured:

            with self.provider.hold(
                session=session,
            ) as response:

                self.assert_signed_response(
                    response,
                    self.initial,
                )

                response = self.provider.compare_and_set(
                    session=session,
                    challenge=b"c" * 32,
                    expected=self.initial.reference(),
                    replacement=self.pending,
                )

                self.assert_signed_response(
                    response,
                    self.pending,
                )

                raise original

        self.assertIs(
            captured.exception,
            original,
        )

        self.assert_pending()

        self.assertEqual(
            self.client.read(),
            self.pending,
        )


if __name__ == "__main__":
    unittest.main()
