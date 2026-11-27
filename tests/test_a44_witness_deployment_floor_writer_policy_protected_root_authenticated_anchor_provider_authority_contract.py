"""End-to-end authority contracts over the production anchor provider.

The provider uses a separately provisioned temporary SQLite
anchor, pinned enrollment and real Ed25519 signatures.

The local replica and anchor are distinct SQLite stores.
No independent hardware or remote trust boundary is claimed.
"""

import hashlib
import importlib
import sqlite3
import tempfile
import unittest

from contextlib import closing
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_authority_contract as previous


PREFIX = (
    "core.existence.history_receipt_trust_checkpoint_"
    "protected_provisioning_witness_deployment_floor_"
    "writer_policy_protected_root"
)

provider_module = importlib.import_module(
    PREFIX + "_authenticated_anchor_provider"
)

sqlite_module = importlib.import_module(
    PREFIX + "_sqlite_reference"
)

client_module = importlib.import_module(
    PREFIX + "_authenticated_anchor_client"
)

authority_module = importlib.import_module(
    PREFIX + "_authority"
)

anchored_module = importlib.import_module(
    PREFIX + "_anchored_backend"
)

root_module = importlib.import_module(PREFIX)

Provider = (
    provider_module.AuthenticatedProtectedRootAnchorProvider
)

Backend = sqlite_module.SQLiteProtectedRootBackend

Client = (
    client_module.AuthenticatedProtectedRootAnchorClient
)

Authority = (
    authority_module.ProtectedDurableWriterPolicyAuthority
)

Anchored = (
    anchored_module.AnchoredProtectedRootBackend
)


class SyntheticSigningFailure(RuntimeError):
    pass


class A44RealAuthenticatedProviderAuthorityTests(
    unittest.TestCase
):

    def setUp(self):

        self.f = (
            previous.A44AuthenticatedProtectedRootAnchorAuthorityTests(
                "test_01_authenticated_publication_and_revocation"
            )
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.base = self.f.base

        self.identity = self.f.identity
        self.initial = self.f.initial
        self.local = self.f.local
        self.pin = self.f.pin
        self.signer = self.f.signer

        directory = tempfile.TemporaryDirectory(
            prefix="a44-real-authority-anchor-"
        )

        self.addCleanup(directory.cleanup)

        self.path = (
            Path(directory.name).resolve()
            / "authority-anchor.sqlite3"
        )

        self.assertTrue(
            self.path.is_relative_to(
                Path(tempfile.gettempdir()).resolve()
            )
        )

        self.anchor = Backend.create(
            path=self.path,
            expected_identity=self.identity,
        )

        self.assertEqual(
            self.anchor.provision(state=self.initial),
            self.initial.reference(),
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        self.assertIsNot(
            self.local,
            self.anchor,
        )

        if isinstance(self.local, Backend):

            self.assertNotEqual(
                self.local._storage.path,
                self.anchor._storage.path,
            )

            self.assertNotEqual(
                self.local._storage.storage_id,
                self.anchor._storage.storage_id,
            )

        self.provider, self.client = self.make_client(
            self.anchor,
        )

        self.guard = self.open_guard(
            self.local,
            self.client,
        )

        self.authority = self.base.reopen(
            root_backend=self.guard,
        )

        self.gateway = self.base.make_gateway(
            self.authority,
        )

        # Rebind the existing fixture's helper methods to the
        # actual production composition.

        self.f.anchor = self.anchor
        self.f.provider = self.provider
        self.f.client = self.client
        self.f.guard = self.guard
        self.f.authority = self.authority
        self.f.gateway = self.gateway

        self.f.f.anchor = self.anchor
        self.f.f.guard = self.guard
        self.f.f.authority = self.authority
        self.f.f.gateway = self.gateway

        self.base.root = self.guard
        self.base.authority = self.authority
        self.base.gateway = self.gateway

        self.assertEqual(
            self.authority.root_state(),
            self.initial,
        )

        self.assert_clean(self.provider)


    def make_client(
        self,
        backend,
        *,
        enrollment=None,
        signer=None,
    ):

        if enrollment is None:
            enrollment = self.pin

        if signer is None:
            signer = self.signer

        provider = Provider.from_backend(
            backend=backend,
            enrollment=enrollment,
            signer=signer,
        )

        client = Client.from_provider(
            provider=provider,
            enrollment=enrollment,
        )

        return provider, client


    def open_anchor(self):

        return Backend.open(
            path=self.path,
            expected_identity=self.identity,
        )


    def open_guard(self, local, client):

        return Anchored.open(
            local_backend=local,
            anchor_backend=client,
            expected_identity=self.identity,
        )


    def reopen(self):

        backend = self.open_anchor()

        provider, client = self.make_client(
            backend,
        )

        guard = self.open_guard(
            self.f.f.f.open_root(),
            client,
        )

        authority = self.base.reopen(
            root_backend=guard,
        )

        self.assert_clean(provider)

        return provider, client, guard, authority


    def history(self):

        with closing(
            sqlite3.connect(
                self.path.as_uri() + "?mode=ro",
                uri=True,
                timeout=5,
                isolation_level=None,
            )
        ) as connection:

            connection.execute("BEGIN")

            sessions = [
                row[0]
                for row in connection.execute(
                    "SELECT session FROM consumed_sessions "
                    "ORDER BY session"
                )
            ]

            metadata = connection.execute(
                "SELECT singleton, enrollment, history_digest "
                "FROM session_metadata"
            ).fetchall()

            version = connection.execute(
                "PRAGMA user_version"
            ).fetchone()

            connection.execute("COMMIT")

        expected = hashlib.sha256(
            b"AdamShell/A44/protected-root-session-history/v2"
            + b"\x00"
            + b"".join(sessions)
            + len(sessions).to_bytes(8, "big")
        ).hexdigest()

        self.assertEqual(version, (2,))
        self.assertEqual(len(metadata), 1)

        singleton, enrollment, actual = metadata[0]

        self.assertEqual(singleton, 1)
        self.assertEqual(actual, expected)

        self.assertTrue(
            all(
                type(value) is bytes
                and len(value) == 32
                for value in sessions
            )
        )

        self.assertEqual(
            len(set(sessions)),
            len(sessions),
        )

        if sessions:

            self.assertIs(
                type(enrollment),
                bytes,
            )

            self.assertTrue(enrollment)

        return set(sessions)


    def assert_clean(self, provider):

        self.assertEqual(
            provider._held.phase,
            "idle",
        )

        self.assertIsNone(provider._held.owner)
        self.assertIsNone(provider._held.session)
        self.assertIsNone(provider._held.reference)

        self.assertFalse(provider._held.poisoned)
        self.assertFalse(provider._held.challenges)

        self.assertEqual(
            provider_module._active_provider_owners(),
            {},
        )

        self.assertEqual(
            sqlite_module._active_leases(),
            {},
        )


    def assert_roots(self, expected):

        self.assertEqual(
            self.open_anchor().read(),
            expected,
        )

        self.assertEqual(
            self.local.read(),
            expected,
        )


    def assert_finalized(self, state):

        self.assertEqual(
            state.revision,
            self.initial.revision + 2,
        )

        self.assertIsNone(
            state.durable_state.prepared
        )

        self.assertEqual(
            state.durable_state.anchor.pair(),
            self.f.f.d.pair(
                self.f.f.candidate,
                2,
            ),
        )


    def publish(self, authority=None):

        if authority is None:
            authority = self.authority

        result = authority.publish_policy(
            signed_policy=self.f.f.candidate,
        )

        self.assertEqual(
            result,
            self.f.f.d.pair(
                self.f.f.candidate,
                2,
            ),
        )

        finalized = self.open_anchor().read()

        self.assert_finalized(finalized)

        self.f.f.s.assert_history(
            self.f.f.genesis,
            self.f.f.candidate,
        )

        return finalized


    def inject_committed_prepare_failure(self):

        original = Provider._signed

        injected = SyntheticSigningFailure(
            "Synthetic authority CAS signing failure"
        )

        reached = []

        def sign(instance, **kwargs):

            if (
                instance is self.provider
                and kwargs["operation"] == "cas"
            ):

                state = kwargs["state"]

                self.assertEqual(
                    state.revision,
                    self.initial.revision + 1,
                )

                self.assertIsNotNone(
                    state.durable_state.prepared
                )

                reached.append(state)

                raise injected

            return original(instance, **kwargs)

        before_local = self.local.read()
        before_sessions = self.history()

        with patch.object(
            Provider,
            "_signed",
            new=sign,
        ):

            with self.assertRaises(Exception) as caught:

                self.authority.publish_policy(
                    signed_policy=self.f.f.candidate,
                )

        self.assertEqual(len(reached), 1)

        # Wrapping at a public authority boundary is allowed,
        # but the exact underlying signing failure must survive.

        pending_error = [caught.exception]
        visited = set()
        found = False

        while pending_error:

            current = pending_error.pop()

            if id(current) in visited:
                continue

            visited.add(id(current))

            if current is injected:

                found = True
                break

            for related in (
                current.__cause__,
                current.__context__,
            ):

                if related is not None:
                    pending_error.append(related)

        self.assertTrue(
            found,
            "Original signing failure lost",
        )

        pending = self.open_anchor().read()

        self.assertEqual(
            pending,
            reached[0],
        )

        self.assertEqual(
            pending.durable_state.prepared.signed_policy,
            self.f.f.candidate,
        )

        self.assertEqual(
            self.local.read(),
            before_local,
        )

        self.assertEqual(
            before_local,
            self.initial,
        )

        self.assertGreater(
            len(self.history()),
            len(before_sessions),
        )

        self.f.f.s.assert_history(
            self.f.f.genesis,
        )

        self.assert_clean(self.provider)

        return pending


    def test_01_canonical_production_composition(self):

        self.assertIs(type(self.provider), Provider)
        self.assertIs(type(self.client), Client)
        self.assertIs(type(self.guard), Anchored)
        self.assertIs(type(self.authority), Authority)

        self.assertIs(
            self.authority._root,
            self.guard,
        )

        self.assertIs(
            self.guard._anchor,
            self.client,
        )

        self.assertIs(
            self.guard._local,
            self.local,
        )

        self.assertIs(
            self.provider._backend,
            self.anchor,
        )

        self.assertIsInstance(
            self.client,
            root_module.ProtectedRootBackend,
        )

        self.assertGreater(
            len(self.history()),
            0,
        )

        self.assert_roots(self.initial)
        self.assert_clean(self.provider)


    def test_02_publication_and_writer_revocation(self):

        operations = []
        original = Provider._signed

        def observe(instance, **kwargs):

            if instance is self.provider:

                operations.append(
                    kwargs["operation"]
                )

            return original(
                instance,
                **kwargs,
            )

        with patch.object(
            Provider,
            "_signed",
            new=observe,
        ):

            finalized = self.publish()

        self.assertEqual(
            operations.count("cas"),
            2,
        )

        self.assertEqual(
            operations.count("hold"),
            1,
        )

        self.assertEqual(
            operations.count("finish"),
            1,
        )

        self.assert_roots(finalized)

        provider, client, guard, fresh = self.reopen()

        self.assertEqual(
            fresh.root_state(),
            finalized,
        )

        self.f.assert_revocation_and_authorized_writer(
            fresh,
        )

        self.assert_roots(finalized)
        self.assert_clean(provider)


    def test_03_direct_authenticated_authority(self):

        direct = self.base.reopen(
            root_backend=self.client,
        )

        self.assertIs(
            direct._root,
            self.client,
        )

        finalized = self.publish(direct)

        self.assertEqual(
            direct.root_state(),
            finalized,
        )

        # Direct mode deliberately has no replica publication.

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        provider, client = self.make_client(
            self.open_anchor()
        )

        fresh = self.base.reopen(
            root_backend=client,
        )

        self.assertEqual(
            fresh.root_state(),
            finalized,
        )

        self.assert_clean(provider)


    def test_04_stale_policy_publication_rejected(self):

        finalized = self.publish()

        operations = []
        original = Provider._signed

        def observe(instance, **kwargs):

            if instance is self.provider:

                operations.append(
                    kwargs["operation"]
                )

            return original(
                instance,
                **kwargs,
            )

        with patch.object(
            Provider,
            "_signed",
            new=observe,
        ):

            with self.assertRaises(ValueError):

                self.authority.publish_policy(
                    signed_policy=self.f.f.genesis,
                )

        self.assertNotIn(
            "cas",
            operations,
        )

        self.assert_roots(finalized)

        self.f.f.s.assert_history(
            self.f.f.genesis,
            self.f.f.candidate,
        )

        self.assert_clean(self.provider)


    def test_05_wrong_signer_rejected_before_session(self):

        before = self.history()

        wrong = Ed25519PrivateKey.from_private_bytes(
            b"w" * 32
        )

        with self.assertRaises(ValueError):

            self.make_client(
                self.open_anchor(),
                signer=wrong,
            )

        self.assertEqual(
            self.history(),
            before,
        )

        self.assert_roots(self.initial)
        self.assert_clean(self.provider)


    def test_06_local_rollback_rejected(self):

        local_path = self.f.f.f.path
        local_fence = self.f.f.f.fence_path

        old_root = local_path.read_bytes()
        old_fence = local_fence.read_bytes()
        old_policy = self.f.f.d.snapshot()

        finalized = self.publish()

        self.f.f.d.restore(old_policy)

        local_path.write_bytes(old_root)
        local_fence.write_bytes(old_fence)

        self.assertEqual(
            self.f.f.f.open_root().read(),
            self.initial,
        )

        self.assertEqual(
            self.open_anchor().read(),
            finalized,
        )

        before_local = local_path.read_bytes()

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.reopen()

        self.base.blocked(
            signed_policy=self.f.f.genesis,
            gateway=self.gateway,
        )

        self.assertEqual(
            local_path.read_bytes(),
            before_local,
        )

        self.assertEqual(
            self.open_anchor().read(),
            finalized,
        )

        self.f.f.d.assert_floor(1, 0)

        self.assert_clean(self.provider)


    def test_07_committed_prepare_signing_failure(self):

        pending = (
            self.inject_committed_prepare_failure()
        )

        self.assertIsNotNone(
            pending.durable_state.prepared
        )

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.reopen()

        self.base.blocked(
            signed_policy=self.f.f.genesis,
            gateway=self.gateway,
        )

        self.assertEqual(
            self.open_anchor().read(),
            pending,
        )

        self.assertEqual(
            self.local.read(),
            self.initial,
        )

        self.f.f.d.assert_floor(1, 0)

        self.assert_clean(self.provider)


    def test_08_explicit_local_and_policy_recovery(self):

        pending = (
            self.inject_committed_prepare_failure()
        )

        provider, client = self.make_client(
            self.open_anchor(),
        )

        original = Provider.compare_and_set
        writes = []

        def observe(instance, **kwargs):

            if instance is provider:
                writes.append(kwargs)

            return original(instance, **kwargs)

        with patch.object(
            Provider,
            "compare_and_set",
            new=observe,
        ):

            recovered = Anchored.recover_local(
                local_backend=self.f.f.f.open_root(),
                anchor_backend=client,
                expected_identity=self.identity,
                expected_local=self.initial.reference(),
                expected_anchor=pending.reference(),
            )

        self.assertEqual(writes, [])

        self.assertEqual(
            recovered,
            pending.reference(),
        )

        self.assert_roots(pending)

        provider, client, guard, fresh = self.reopen()

        self.assertEqual(
            fresh.root_state(),
            pending,
        )

        with self.assertRaises(ValueError):

            fresh.current_policy_reference()

        result = fresh.recover_publication()

        self.assertEqual(
            result,
            self.f.f.d.pair(
                self.f.f.candidate,
                2,
            ),
        )

        finalized = self.open_anchor().read()

        self.assert_finalized(finalized)
        self.assert_roots(finalized)

        self.assertEqual(
            fresh.recover_publication(),
            result,
        )

        self.assert_roots(finalized)

        self.f.f.s.assert_history(
            self.f.f.genesis,
            self.f.f.candidate,
        )

        self.f.assert_revocation_and_authorized_writer(
            fresh,
        )

        self.assert_clean(provider)


    def test_09_persistent_sessions_after_reopen(self):

        before = self.history()

        finalized = self.publish()

        after = self.history()

        self.assertTrue(before < after)

        provider, client, guard, fresh = self.reopen()

        reopened = self.history()

        self.assertTrue(after < reopened)

        signing = []
        original = Provider._signed

        def observe(instance, **kwargs):

            if instance is provider:
                signing.append(
                    kwargs["operation"]
                )

            return original(
                instance,
                **kwargs,
            )

        old_session = sorted(after)[0]

        with patch.object(
            Provider,
            "_signed",
            new=observe,
        ):

            with self.assertRaisesRegex(
                ValueError,
                "Protected provider session replay",
            ):

                with provider.hold(
                    session=old_session,
                ):

                    self.fail(
                        "Consumed session reentered"
                    )

        self.assertEqual(signing, [])

        self.assertEqual(
            self.history(),
            reopened,
        )

        self.assertEqual(
            fresh.root_state(),
            finalized,
        )

        self.assertTrue(
            reopened < self.history()
        )

        self.assert_roots(finalized)
        self.assert_clean(provider)


    def test_10_enrollment_substitution_rejected(self):

        alternate = replace(
            self.pin,
            anchor_id=self.pin.anchor_id + "-alternate",
        )

        self.assertNotEqual(
            alternate.fingerprint(),
            self.pin.fingerprint(),
        )

        provider, client = self.make_client(
            self.open_anchor(),
            enrollment=alternate,
        )

        before = self.history()

        signing = []
        original = Provider._signed

        def observe(instance, **kwargs):

            if instance is provider:
                signing.append(
                    kwargs["operation"]
                )

            return original(
                instance,
                **kwargs,
            )

        with patch.object(
            Provider,
            "_signed",
            new=observe,
        ):

            with self.assertRaises(ValueError):

                self.open_guard(
                    self.local,
                    client,
                )

        self.assertEqual(signing, [])

        self.assertEqual(
            self.history(),
            before,
        )

        self.assert_roots(self.initial)
        self.assert_clean(provider)

        self.assertEqual(
            self.authority.root_state(),
            self.initial,
        )

        self.assert_clean(self.provider)


if __name__ == "__main__":
    unittest.main()
