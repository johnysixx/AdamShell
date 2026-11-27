"""Protected root storage compatibility contracts.

New storage uses explicit schema v2.

Legacy root-only storage remains readable and writable through
the original backend interface, but authenticated session
reservation requires v2.

Opening or using storage never performs an implicit migration
or reconstructs a missing session history.

Database modifications in these tests are confined to temporary
fixtures. Coordinated replacement of trusted persistent storage
remains outside the rollback-resistance guarantee.
"""

import hashlib
import sqlite3
import unittest

from contextlib import closing
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_contract as base


class A44AuthenticatedAnchorProviderStorageCompatibilityContractTests(
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

        self.backend = self.f.backend
        self.provider = self.f.provider
        self.provider_class = type(self.provider)

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.path = self.f.path.resolve()

        self.fence = self.path.with_name(
            self.path.name + ".fence.sqlite3"
        )

        self.sidecar = self.path.with_name(
            self.path.name + ".sessions.sqlite3"
        )

        self.session = b"s" * 32
        self.fresh = b"n" * 32

        self.assertEqual(
            self.backend.read(),
            self.initial,
        )

        self.assertFalse(
            self.sidecar.exists()
        )

    def fixture_path(self, path):

        path = Path(path).resolve()

        self.assertEqual(
            path.parent,
            self.path.parent,
        )

        self.assertNotEqual(
            path.parent,
            Path.cwd().resolve(),
        )

        return path

    def connect(self, path, mode):

        path = self.fixture_path(path)

        return sqlite3.connect(
            path.as_uri() + "?mode=" + mode,
            uri=True,
            timeout=5,
            isolation_level=None,
        )

    def query(self, sql, params=(), path=None):

        if path is None:
            path = self.path

        with closing(
            self.connect(path, "ro")
        ) as connection:

            return connection.execute(
                sql,
                params,
            ).fetchall()

    def mutate(self, statements):

        with closing(
            self.connect(self.path, "rw")
        ) as connection:

            connection.execute(
                "PRAGMA synchronous=FULL"
            )

            connection.execute(
                "BEGIN IMMEDIATE"
            )

            try:

                for sql, params in statements:

                    connection.execute(
                        sql,
                        params,
                    )

                connection.execute("COMMIT")

            except BaseException:

                if connection.in_transaction:

                    connection.execute("ROLLBACK")

                raise

    def version(self):

        return self.query(
            "PRAGMA user_version"
        )[0][0]

    def tables(self, path=None):

        return {
            row[0]
            for row in self.query(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table'",
                path=path,
            )
        }

    def sessions(self):

        return {
            row[0]
            for row in self.query(
                "SELECT session FROM consumed_sessions"
            )
        }

    def snapshot(self):

        result = [
            self.path.read_bytes(),
            self.fence.read_bytes(),
        ]

        if self.sidecar.exists():

            result.append(
                self.sidecar.read_bytes()
            )

        else:

            result.append(None)

        return tuple(result)

    def reopen(self):

        return (
            base.sqlite_root.SQLiteProtectedRootBackend.open(
                path=self.path,
                expected_identity=self.initial.identity,
            )
        )

    def make_legacy(self):

        # Reconstruct the original root-only schema.
        # This is a synthetic compatibility fixture,
        # not a production migration procedure.

        self.mutate([
            (
                "DROP TABLE consumed_sessions",
                (),
            ),
            (
                "DROP TABLE session_metadata",
                (),
            ),
            (
                "PRAGMA user_version = 0",
                (),
            ),
        ])

        self.assertEqual(
            self.version(),
            0,
        )

        self.assertEqual(
            self.tables(),
            {
                "root_metadata",
                "root_state",
            },
        )

    def complete(self, session, provider=None):

        if provider is None:
            provider = self.provider

        with provider.hold(
            session=session,
        ) as response:

            self.f.assert_signed_response(
                response,
                self.initial,
            )

            response = provider.read(
                session=session,
                challenge=b"r" * 32,
            )

            self.f.assert_signed_response(
                response,
                self.initial,
            )

            response = provider.finish(
                session=session,
                challenge=b"f" * 32,
                expected=self.initial.reference(),
            )

            self.f.assert_signed_response(
                response,
                self.initial,
            )

        self.assertEqual(
            provider._held.phase,
            "idle",
        )

    def assert_rejected(
        self,
        *,
        reconstruct=False,
        provider=None,
        session=None,
    ):

        if provider is None:
            provider = self.provider

        if session is None:
            session = self.fresh

        before = self.snapshot()

        signing = []
        entered = []

        original = self.provider_class._signed

        def observe(instance, **kwargs):

            signing.append(
                kwargs["operation"]
            )

            return original(
                instance,
                **kwargs,
            )

        with patch.object(
            self.provider_class,
            "_signed",
            new=observe,
        ):

            with self.assertRaises(ValueError):

                if reconstruct:

                    provider = self.f.make_provider(
                        backend=self.reopen(),
                    )

                with provider.hold(
                    session=session,
                ):

                    entered.append(True)

        self.assertEqual(
            entered,
            [],
            "Rejected storage reached HOLD entry",
        )

        self.assertEqual(
            signing,
            [],
            "Rejected storage reached signing boundary",
        )

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
            provider._held.challenges
        )

        self.assertFalse(
            provider._held.poisoned
        )

        self.assertEqual(
            self.snapshot(),
            before,
            "Rejected operation modified persistent storage",
        )

    def test_01_new_storage_v2_canonical(self):

        self.assertEqual(
            self.version(),
            2,
        )

        self.assertEqual(
            self.tables(),
            {
                "root_metadata",
                "root_state",
                "session_metadata",
                "consumed_sessions",
            },
        )

        self.assertEqual(
            self.tables(self.fence),
            {"root_metadata"},
        )

        empty_digest = hashlib.sha256(
            b"AdamShell/A44/protected-root-session-history/v2"
            + b"\x00"
            + (0).to_bytes(8, "big")
        ).hexdigest()

        self.assertEqual(
            self.query(
                "SELECT singleton,enrollment,history_digest "
                "FROM session_metadata"
            ),
            [
                (1, None, empty_digest),
            ],
        )

        self.assertEqual(
            self.sessions(),
            set(),
        )

        self.complete(
            self.session
        )

        self.assertEqual(
            self.sessions(),
            {self.session},
        )

        self.assertFalse(
            self.sidecar.exists()
        )

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

    def test_02_legacy_v1_read_compatibility(self):

        self.make_legacy()

        before = self.snapshot()

        reopened = self.reopen()

        self.assertEqual(
            reopened.read(),
            self.initial,
        )

        self.assertEqual(
            self.snapshot(),
            before,
        )

        self.assertEqual(
            self.version(),
            0,
        )

    def test_03_legacy_v1_backend_cas_compatibility(self):

        self.make_legacy()

        reopened = self.reopen()

        result = reopened.compare_and_set(
            expected=self.initial.reference(),
            replacement=self.pending,
        )

        self.assertEqual(
            result,
            self.pending.reference(),
        )

        self.assertEqual(
            self.reopen().read(),
            self.pending,
        )

        self.assertEqual(
            self.version(),
            0,
        )

        self.assertEqual(
            self.tables(),
            {
                "root_metadata",
                "root_state",
            },
        )

        self.assertFalse(
            self.sidecar.exists()
        )

    def test_04_legacy_v1_authenticated_hold_rejected(self):

        self.make_legacy()

        self.assert_rejected()

        self.assert_rejected(
            reconstruct=True,
        )

        self.assertEqual(
            self.version(),
            0,
        )

        self.assertFalse(
            self.sidecar.exists()
        )

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

    def test_05_legacy_marker_rejected(self):

        self.make_legacy()

        self.mutate([
            (
                "PRAGMA user_version = 1093940225",
                (),
            ),
        ])

        self.assertEqual(
            self.version(),
            1093940225,
        )

        self.assert_rejected()

        self.assert_rejected(
            reconstruct=True,
        )

    def test_06_unknown_storage_version_rejected(self):

        self.mutate([
            (
                "PRAGMA user_version = 999",
                (),
            ),
        ])

        self.assert_rejected()

        self.assert_rejected(
            reconstruct=True,
        )

        self.assertEqual(
            self.version(),
            999,
        )

    def test_07_missing_session_table_rejected(self):

        self.complete(
            self.session
        )

        self.mutate([
            (
                "DROP TABLE consumed_sessions",
                (),
            ),
        ])

        self.assertNotIn(
            "consumed_sessions",
            self.tables(),
        )

        self.assert_rejected()

        self.assert_rejected(
            reconstruct=True,
        )

        self.assertNotIn(
            "consumed_sessions",
            self.tables(),
        )

    def test_08_version_reset_with_v2_tables_rejected(self):

        self.complete(
            self.session
        )

        self.mutate([
            (
                "PRAGMA user_version = 0",
                (),
            ),
        ])

        self.assertEqual(
            self.version(),
            0,
        )

        self.assertIn(
            "consumed_sessions",
            self.tables(),
        )

        self.assert_rejected()

        self.assert_rejected(
            reconstruct=True,
        )

        self.assertEqual(
            self.sessions(),
            {self.session},
        )

    def test_09_legacy_sidecar_never_imported_or_deleted(self):

        # Synthetic sidecar sentinel. No legacy data
        # is imported or modified by the provider.

        payload = (
            b"legacy-session-registry-sentinel"
        )

        with self.fixture_path(
            self.sidecar
        ).open("xb") as handle:

            handle.write(payload)

        self.assert_rejected()

        self.assert_rejected(
            reconstruct=True,
        )

        self.assertEqual(
            self.sidecar.read_bytes(),
            payload,
        )

        self.assertEqual(
            self.sessions(),
            set(),
        )

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

        self.sidecar.unlink()

        self.complete(
            self.session
        )

    def test_10_changed_enrollment_rejected(self):

        self.complete(
            self.session
        )

        changed = replace(
            self.f.pin,
            anchor_id=(
                self.f.pin.anchor_id
                + "-different"
            ),
        )

        self.assertNotEqual(
            changed.fingerprint(),
            self.f.pin.fingerprint(),
        )

        other = self.f.make_provider(
            enrollment=changed,
        )

        self.assert_rejected(
            provider=other,
        )

        self.assertEqual(
            self.sessions(),
            {self.session},
        )

        self.complete(
            self.fresh
        )

        self.assertEqual(
            self.sessions(),
            {
                self.session,
                self.fresh,
            },
        )

    def test_11_corrupted_history_digest_rejected(self):

        self.complete(
            self.session
        )

        original = self.query(
            "SELECT history_digest "
            "FROM session_metadata"
        )[0][0]

        corrupted = "0" * 64

        self.assertNotEqual(
            original,
            corrupted,
        )

        self.mutate([
            (
                "UPDATE session_metadata "
                "SET history_digest = ?",
                (corrupted,),
            ),
        ])

        self.assert_rejected()

        self.assert_rejected(
            reconstruct=True,
        )

        self.assertEqual(
            self.sessions(),
            {self.session},
        )

        self.mutate([
            (
                "UPDATE session_metadata "
                "SET history_digest = ?",
                (original,),
            ),
        ])

        self.assert_rejected(
            session=self.session,
        )

        self.complete(
            self.fresh
        )

    def test_12_complete_downgrade_cannot_enable_replay(self):

        self.complete(
            self.session
        )

        self.make_legacy()

        # A root-only backend remains compatible, but
        # a provider cannot silently recreate history.

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

        self.assert_rejected(
            session=self.session,
        )

        self.assert_rejected(
            reconstruct=True,
            session=self.session,
        )

        self.assert_rejected(
            reconstruct=True,
            session=self.fresh,
        )

        self.assertEqual(
            self.version(),
            0,
        )

        self.assertEqual(
            self.tables(),
            {
                "root_metadata",
                "root_state",
            },
        )

        self.assertFalse(
            self.sidecar.exists()
        )


if __name__ == "__main__":
    unittest.main()
