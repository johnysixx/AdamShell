"""Authenticated protected root authority integration.

All keys, providers and databases are synthetic test fixtures.

The authenticated client is explicitly selected by trusted
deployment configuration. Legacy unpinned entry points are
not implicitly converted into authenticated entry points.

No remote durability or physical fence guarantee is claimed.
"""

import importlib
import unittest

from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat,
)

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_client_contract as protocol

import test_a44_witness_deployment_floor_writer_policy_protected_root_anchored_authority_contract as previous


class A44AuthenticatedProtectedRootAnchorAuthorityTests(
    unittest.TestCase
):

    def setUp(self):

        self.m = importlib.import_module(protocol.CLIENT)
        self.e = importlib.import_module(protocol.ENROLLMENT)

        self.f = previous.A44AnchoredProtectedRootAuthorityContractTests(
            "test_01_publication_and_revocation_use_both_roots"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.base = self.f.base
        self.anchor = self.f.anchor
        self.local = self.f.local
        self.initial = self.f.initial
        self.identity = self.f.identity

        self.signer = Ed25519PrivateKey.from_private_bytes(
            b"v" * 32
        )

        self.other_signer = Ed25519PrivateKey.from_private_bytes(
            b"w" * 32
        )

        self.pin = self.e.PinnedProtectedRootAnchorEnrollment(
            identity=self.identity,
            anchor_id="authority-authenticated-anchor",
            anchor_public_key=self.signer.public_key().public_bytes(
                Encoding.Raw, PublicFormat.Raw
            ),
            enrollment_epoch=1,
        )

        self.provider, self.client = self.make_client(
            self.anchor,
            self.signer,
        )

        self.guard = self.open_guard()

        self.authority = self.base.reopen(
            root_backend=self.guard,
        )

        self.gateway = self.base.make_gateway(
            self.authority,
        )

        self.f.guard = self.guard
        self.f.authority = self.authority
        self.f.gateway = self.gateway

        self.base.root = self.guard
        self.base.authority = self.authority
        self.base.gateway = self.gateway

    def make_client(self, backend, signer):

        provider = protocol.SignedTestProvider(
            backend=backend,
            signer=signer,
            enrollment=self.pin,
        )

        client = self.m.AuthenticatedProtectedRootAnchorClient.from_provider(
            provider=provider,
            enrollment=self.pin,
        )

        return provider, client

    def open_guard(self, local=None, client=None):

        if local is None:
            local = self.local

        if client is None:
            client = self.client

        return self.f.m.AnchoredProtectedRootBackend.open(
            local_backend=local,
            anchor_backend=client,
            expected_identity=self.identity,
        )

    def reopen(self):

        return self.base.reopen(
            root_backend=self.open_guard(
                local=self.f.f.open_root(),
            ),
        )

    def storage_bytes(self):

        return (
            self.f.f.path.read_bytes(),
            self.f.f.fence_path.read_bytes(),
            self.f.s.path.read_bytes(),
        )

    def rollback_local_fixture(self):

        old_root = self.f.f.path.read_bytes()
        old_fence = self.f.f.fence_path.read_bytes()

        old_policy = self.f.d.snapshot()

        finalized = self.f.publish()

        self.f.d.restore(old_policy)

        self.f.f.path.write_bytes(old_root)
        self.f.f.fence_path.write_bytes(old_fence)

        self.assertEqual(
            self.f.f.open_root().read(),
            self.initial,
        )

        self.assertEqual(
            self.anchor.read(),
            finalized,
        )

        self.f.s.assert_history(self.f.genesis)
        self.f.d.assert_floor(1, 0)

        return finalized

    def stale_replacement(self):

        replacement = self.base.new_root()

        replacement.provision(
            state=self.initial,
        )

        self.assertIsNot(replacement, self.anchor)
        self.assertEqual(replacement.identity, self.identity)
        self.assertEqual(replacement.read(), self.initial)

        provider, client = self.make_client(
            replacement,
            self.other_signer,
        )

        return replacement, provider, client

    def assert_revocation_and_authorized_writer(self, fresh):

        gateway = self.base.make_gateway(fresh)

        self.base.blocked(
            signed_policy=self.f.genesis,
            gateway=gateway,
        )

        self.base.blocked(
            signed_policy=self.f.candidate,
            gateway=gateway,
        )

        self.f.d.assert_floor(1, 0)

        response = self.base.send(
            self.f.candidate,
            gateway=gateway,
            writer_id="writer-beta",
            signer=self.f.p.f.bob,
        )

        self.f.d.assert_committed(response, 2)
        self.f.d.assert_floor(2, 1)

    def test_01_authenticated_publication_and_revocation(self):

        self.provider.events.clear()

        finalized = self.f.publish()

        self.assertEqual(finalized.revision, 3)

        operations = [
            event[0]
            for event in self.provider.events
        ]

        self.assertEqual(operations.count("cas"), 2)

        self.assertIsNone(self.provider.active)

        fresh = self.reopen()

        self.assertEqual(fresh.root_state(), finalized)

        self.assert_revocation_and_authorized_writer(fresh)

        self.f.assert_equal_roots(finalized)

    def test_02_same_identity_stale_replacement_rejected(self):

        finalized = self.rollback_local_fixture()

        replacement, provider, client = self.stale_replacement()

        before = self.storage_bytes()

        with patch.object(
            provider, "read",
            side_effect=AssertionError("Untrusted provider read"),
        ) as forbidden_read, patch.object(
            provider, "compare_and_set",
            side_effect=AssertionError("Untrusted provider CAS"),
        ) as forbidden_cas:

            with self.assertRaises(ValueError):

                self.open_guard(
                    local=self.f.f.open_root(),
                    client=client,
                )

            forbidden_read.assert_not_called()
            forbidden_cas.assert_not_called()

        self.assertIsNone(provider.active)
        self.assertEqual(replacement.read(), self.initial)
        self.assertEqual(self.anchor.read(), finalized)

        self.assertEqual(self.storage_bytes(), before)

        self.f.d.assert_floor(1, 0)

    def test_03_original_authenticated_anchor_rejects_rollback(self):

        finalized = self.rollback_local_fixture()

        before = self.storage_bytes()

        with self.assertRaises(ValueError):
            self.reopen()

        with self.assertRaises(ValueError):
            self.authority.current_policy_reference()

        self.base.blocked(
            signed_policy=self.f.genesis,
            gateway=self.gateway,
        )

        self.assertEqual(self.anchor.read(), finalized)
        self.assertEqual(self.storage_bytes(), before)

        self.f.d.assert_floor(1, 0)

    def test_04_existing_authority_rejects_signer_substitution(self):

        finalized = self.f.publish()

        before = self.storage_bytes()

        with patch.object(
            self.provider,
            "signer",
            self.other_signer,
        ):

            with self.assertRaises(ValueError):
                self.authority.current_policy_reference()

            with self.assertRaises(ValueError):
                self.authority.recover_publication()

            self.base.blocked(
                signed_policy=self.f.candidate,
                gateway=self.gateway,
            )

            self.f.d.assert_floor(1, 0)

        self.assertEqual(self.storage_bytes(), before)
        self.assertEqual(self.anchor.read(), finalized)

        self.assertIsNone(self.provider.active)

        self.assert_revocation_and_authorized_writer(
            self.reopen(),
        )

    def test_05_invalid_cas_ack_requires_explicit_recovery(self):

        original = self.provider.compare_and_set

        committed = []

        def corrupt_ack(**kwargs):

            state, signature = original(**kwargs)

            committed.append(state.reference())

            return (
                state,
                bytes([signature[0] ^ 1]) + signature[1:],
            )

        before = self.storage_bytes()

        with patch.object(
            self.provider,
            "compare_and_set",
            side_effect=corrupt_ack,
        ) as failure:

            with self.assertRaises(ValueError):

                self.authority.publish_policy(
                    signed_policy=self.f.candidate,
                )

            failure.assert_called_once()

        pending = self.anchor.read()

        self.assertEqual(pending.revision, 2)

        self.assertEqual(
            pending.durable_state.prepared.signed_policy,
            self.f.candidate,
        )

        self.assertEqual(committed, [pending.reference()])
        self.assertEqual(self.local.read(), self.initial)

        self.assertEqual(self.storage_bytes(), before)

        self.f.s.assert_history(self.f.genesis)

        with self.assertRaises(ValueError):
            self.reopen()

        self.base.blocked(
            signed_policy=self.f.genesis,
            gateway=self.gateway,
        )

        self.f.d.assert_floor(1, 0)

        with patch.object(
            self.provider,
            "compare_and_set",
            side_effect=AssertionError("Recovery wrote anchor"),
        ) as forbidden:

            recovered = (
                self.f.m.AnchoredProtectedRootBackend.recover_local(
                    local_backend=self.f.f.open_root(),
                    anchor_backend=self.client,
                    expected_identity=self.identity,
                    expected_local=self.initial.reference(),
                    expected_anchor=pending.reference(),
                )
            )

            forbidden.assert_not_called()

        self.assertEqual(recovered, pending.reference())
        self.assertEqual(self.local.read(), pending)

        fresh = self.reopen()

        self.assertEqual(
            fresh.recover_publication(),
            self.f.d.pair(self.f.candidate, 2),
        )

        finalized = self.anchor.read()

        self.assertEqual(finalized.revision, 3)
        self.assertIsNone(finalized.durable_state.prepared)

        self.assertEqual(self.local.read(), finalized)
        self.assertEqual(fresh.root_state(), finalized)

        self.f.s.assert_history(
            self.f.genesis,
            self.f.candidate,
        )

        self.assert_revocation_and_authorized_writer(fresh)

    def test_06_unpinned_provider_cannot_authorize_recovery(self):

        finalized = self.rollback_local_fixture()

        replacement, provider, client = self.stale_replacement()

        before = self.storage_bytes()

        with patch.object(
            type(self.local),
            "compare_and_set",
            side_effect=AssertionError("Unauthorized local recovery"),
        ) as forbidden_local, patch.object(
            provider,
            "compare_and_set",
            side_effect=AssertionError("Unauthorized anchor CAS"),
        ) as forbidden_anchor:

            with self.assertRaises(ValueError):

                self.f.m.AnchoredProtectedRootBackend.recover_local(
                    local_backend=self.f.f.open_root(),
                    anchor_backend=client,
                    expected_identity=self.identity,
                    expected_local=self.initial.reference(),
                    expected_anchor=self.initial.reference(),
                )

            forbidden_local.assert_not_called()
            forbidden_anchor.assert_not_called()

        self.assertEqual(self.storage_bytes(), before)
        self.assertEqual(self.anchor.read(), finalized)
        self.assertEqual(replacement.read(), self.initial)

        self.assertIsNone(provider.active)

        self.f.d.assert_floor(1, 0)
