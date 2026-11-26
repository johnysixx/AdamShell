"""Authenticated protected root client contract.

Synthetic provider and keys; no real remote durability claim.
"""

import importlib
import json
import unittest

from contextlib import contextmanager

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat,
)

import test_a44_witness_deployment_floor_writer_policy_protected_root_anchored_backend_contract as previous


PREFIX = (
    "core.existence.history_receipt_trust_checkpoint_"
    "protected_provisioning_witness_deployment_floor_"
    "writer_policy_protected_root_"
)

CLIENT = PREFIX + "authenticated_anchor_client"
ENROLLMENT = PREFIX + "anchor_enrollment"

DOMAIN = "AdamShell/A44/protected-root-anchor-operation/v1"


def reference_fields(reference):

    if reference is None:
        return None

    return [reference.revision, reference.sha256]


class SignedTestProvider:

    def __init__(self, *, backend, signer, enrollment):

        self.backend = backend
        self.signer = signer
        self.enrollment = enrollment
        self.active = None
        self.events = []

    def response(
        self, operation, session, challenge,
        state, expected=None, replacement=None,
    ):

        self.events.append((operation, session, challenge))

        payload = [
            DOMAIN,
            self.enrollment.fingerprint(),
            operation,
            session.hex(),
            challenge.hex(),
            reference_fields(expected),
            reference_fields(replacement),
            reference_fields(state.reference()),
        ]

        message = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")

        return state, self.signer.sign(message)

    def check_session(self, session):

        if self.active is None or session != self.active:
            raise ValueError("No matching held session")

    @contextmanager
    def hold(self, *, session):

        if self.active is not None:
            raise ValueError("Unexpected nested provider hold")

        with self.backend.exclusive():

            self.active = session

            try:

                yield self.response(
                    "hold", session, session,
                    self.backend.read(),
                )

            finally:

                self.active = None

    def read(self, *, session, challenge):

        self.check_session(session)

        return self.response(
            "read", session, challenge,
            self.backend.read(),
        )

    def compare_and_set(
        self, *, session, challenge, expected, replacement,
    ):

        self.check_session(session)

        self.backend.compare_and_set(
            expected=expected,
            replacement=replacement,
        )

        return self.response(
            "cas", session, challenge,
            self.backend.read(),
            expected=expected,
            replacement=replacement.reference(),
        )

    def finish(self, *, session, challenge, expected):

        self.check_session(session)

        state = self.backend.read()

        if state.reference() != expected:
            raise ValueError("Final reference mismatch")

        return self.response(
            "finish", session, challenge,
            state, expected=expected,
        )


class A44AuthenticatedProtectedRootAnchorClientContractTests(
    unittest.TestCase
):

    def setUp(self):

        self.m = importlib.import_module(CLIENT)
        self.e = importlib.import_module(ENROLLMENT)
        self.root = importlib.import_module(
            PREFIX[:-1]
        )

        self.f = previous.A44AnchoredProtectedRootBackendContractTests(
            "test_01_open_equal_canonical_roots"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.initial = self.f.initial
        self.pending = self.f.objects.pending()

        self.signer = Ed25519PrivateKey.from_private_bytes(
            b"k" * 32
        )

        key = self.signer.public_key().public_bytes(
            Encoding.Raw, PublicFormat.Raw
        )

        self.pin = self.e.PinnedProtectedRootAnchorEnrollment(
            identity=self.f.identity,
            anchor_id="authenticated-anchor-alpha",
            anchor_public_key=key,
            enrollment_epoch=1,
        )

        self.provider = SignedTestProvider(
            backend=self.f.anchor,
            signer=self.signer,
            enrollment=self.pin,
        )

        self.client = self.m.AuthenticatedProtectedRootAnchorClient.from_provider(
            provider=self.provider,
            enrollment=self.pin,
        )

    def operations(self):

        return [event[0] for event in self.provider.events]

    def test_01_canonical_backend_interface(self):

        self.assertIsInstance(
            self.client,
            self.root.ProtectedRootBackend,
        )

        self.assertEqual(
            self.client.identity,
            self.f.identity,
        )

        self.assertTrue(
            self.client.__dataclass_params__.frozen
        )

        self.assertFalse(
            hasattr(self.client, "__dict__")
        )

        self.assertEqual(self.provider.events, [])

    def test_02_authenticated_read(self):

        state = self.client.read()

        self.assertIs(
            type(state),
            self.root.ProtectedDurableRootState,
        )

        self.assertEqual(state, self.initial)

        operations = self.operations()

        self.assertEqual(operations[0], "hold")
        self.assertIn("read", operations)
        self.assertEqual(operations[-1], "finish")

        self.assertEqual(operations.count("hold"), 1)
        self.assertEqual(operations.count("finish"), 1)
        self.assertIsNone(self.provider.active)

    def test_03_authenticated_compare_and_set(self):

        result = self.client.compare_and_set(
            expected=self.initial.reference(),
            replacement=self.pending,
        )

        self.assertIs(
            type(result),
            self.root.ProtectedRootReference,
        )

        self.assertEqual(result, self.pending.reference())

        self.assertEqual(
            self.f.anchor.read(),
            self.pending,
        )

        self.assertEqual(
            self.f.local.read(),
            self.initial,
        )

        self.assertEqual(self.operations().count("cas"), 1)

        self.assertEqual(self.client.read(), self.pending)

    def test_04_nested_operations_share_one_held_session(self):

        with self.client.exclusive():

            session = self.provider.active

            self.assertIs(type(session), bytes)
            self.assertEqual(len(session), 32)

            with self.client.exclusive():

                self.assertEqual(self.provider.active, session)
                self.assertEqual(self.client.read(), self.initial)

                self.assertEqual(
                    self.client.compare_and_set(
                        expected=self.initial.reference(),
                        replacement=self.pending,
                    ),
                    self.pending.reference(),
                )

            self.assertEqual(self.provider.active, session)
            self.assertEqual(self.client.read(), self.pending)
            self.assertNotIn("finish", self.operations())

        self.assertIsNone(self.provider.active)

        self.assertEqual(self.operations().count("hold"), 1)
        self.assertEqual(self.operations().count("finish"), 1)

        self.assertTrue(
            all(
                event[1] == session
                for event in self.provider.events
            )
        )

    def test_05_provisioning_is_forbidden(self):

        with self.assertRaises(ValueError):

            self.client.provision(state=self.initial)

        self.assertEqual(self.provider.events, [])

        self.assertEqual(
            self.f.anchor.read(),
            self.initial,
        )

    def test_06_fresh_sessions_and_operation_challenges(self):

        self.assertEqual(self.client.read(), self.initial)
        self.assertEqual(self.client.read(), self.initial)

        events = self.provider.events

        sessions = [
            session
            for operation, session, challenge in events
            if operation == "hold"
        ]

        self.assertEqual(len(sessions), 2)
        self.assertEqual(len(set(sessions)), 2)

        challenges = [
            challenge
            for operation, session, challenge in events
        ]

        self.assertTrue(
            all(
                type(value) is bytes and len(value) == 32
                for value in challenges
            )
        )

        self.assertEqual(
            len(challenges),
            len(set(challenges)),
        )

        self.assertIsNone(self.provider.active)
