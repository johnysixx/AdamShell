"""Authenticated provider registry integrity contract.

Session consumption must remain durable without an independently
replaceable session database.

The protected registry must detect isolated deletion or replacement
of consumed session records before generating another signature.

These tests do not claim resistance to coordinated modification
or complete rollback of all trusted persistent commitments.
"""

import sqlite3
import unittest

from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_contract as base


class A44AuthenticatedAnchorProviderRegistryIntegrityContractTests(
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
        self.provider_class = type(self.provider)

        self.backend = self.f.backend
        self.client = self.f.client
        self.initial = self.f.initial

        self.root_path = self.f.path.resolve()

        self.legacy_registry = self.root_path.with_name(
            self.root_path.name + ".sessions.sqlite3"
        )

        self.session = b"s" * 32
        self.other = b"t" * 32
        self.fresh = b"n" * 32

        self.assertEqual(
            self.backend.read(),
            self.initial,
        )

    def fixture_path(self, path):

        path = Path(path).resolve()

        self.assertEqual(
            path.parent,
            self.root_path.parent,
        )

        self.assertNotEqual(
            path.parent,
            Path.cwd().resolve(),
        )

        return path

    def query(self, path, sql, parameters=()):

        path = self.fixture_path(path)

        with closing(
            sqlite3.connect(
                path.as_uri() + "?mode=ro",
                uri=True,
                timeout=5,
            )
        ) as connection:

            return connection.execute(
                sql,
                parameters,
            ).fetchall()

    def mutate(self, path, sql, parameters=()):

        path = self.fixture_path(path)

        with closing(
            sqlite3.connect(
                path.as_uri() + "?mode=rw",
                uri=True,
                timeout=5,
                isolation_level=None,
            )
        ) as connection:

            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("BEGIN IMMEDIATE")

            try:

                connection.execute(sql, parameters)
                connection.execute("COMMIT")

            except BaseException:

                if connection.in_transaction:

                    connection.execute("ROLLBACK")

                raise

    def table_names(self, path):

        return {
            row[0]
            for row in self.query(
                path,
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table'",
            )
        }

    def registry_path(self):

        # Locate the actual session storage during the
        # transition from the legacy sidecar design.

        if "consumed_sessions" in self.table_names(
            self.root_path
        ):

            return self.root_path

        self.assertTrue(
            self.legacy_registry.is_file(),
            "No persistent session storage found",
        )

        return self.legacy_registry

    def sessions(self, path):

        return {
            row[0]
            for row in self.query(
                path,
                "SELECT session FROM consumed_sessions",
            )
        }

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

    def initialize(self):

        self.complete(self.session)

        path = self.registry_path()

        self.assertEqual(
            self.sessions(path),
            {self.session},
        )

        self.assertEqual(
            self.backend.read(),
            self.initial,
        )

        return path

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

        self.assertFalse(
            provider._held.challenges
        )

    def assert_rejected_before_signature(
        self,
        *,
        label,
        reconstruct=False,
    ):

        original = self.provider_class._signed

        signing_calls = []
        entered = []
        rejected = False
        provider = self.provider

        def observe(instance, **kwargs):

            signing_calls.append(
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

            try:

                if reconstruct:

                    reopened = (
                        base.sqlite_root
                        .SQLiteProtectedRootBackend.open(
                            path=self.root_path,
                            expected_identity=self.initial.identity,
                        )
                    )

                    provider = self.f.make_provider(
                        backend=reopened,
                    )

                with provider.hold(
                    session=self.session,
                ) as response:

                    entered.append(True)

                    self.f.assert_signed_response(
                        response,
                        self.initial,
                    )

                    provider.finish(
                        session=self.session,
                        challenge=b"f" * 32,
                        expected=self.initial.reference(),
                    )

            except ValueError:

                rejected = True

        self.assert_idle(provider)

        if entered and not rejected:

            self.fail(
                "REGISTRY_INTEGRITY_OPEN:" + label
            )

        self.assertTrue(
            rejected,
            "Invalid registry was not rejected",
        )

        self.assertEqual(
            entered,
            [],
            "Invalid registry reached HOLD entry",
        )

        self.assertEqual(
            signing_calls,
            [],
            "Invalid registry reached signing",
        )

    def test_01_registry_integrated_into_root_database(self):

        path = self.initialize()

        if path != self.root_path:

            self.fail(
                "REGISTRY_INTEGRITY_OPEN:separate_storage"
            )

        self.assertIn(
            "consumed_sessions",
            self.table_names(self.root_path),
        )

        self.assertFalse(
            self.legacy_registry.exists(),
            "Independent session database remains",
        )

    def test_02_deleted_consumed_session_rejected(self):

        path = self.initialize()

        self.mutate(
            path,
            "DELETE FROM consumed_sessions "
            "WHERE session = ?",
            (self.session,),
        )

        self.assertEqual(
            self.sessions(path),
            set(),
        )

        self.assert_rejected_before_signature(
            label="deleted_session",
        )

    def test_03_same_count_session_substitution_rejected(self):

        path = self.initialize()

        before = self.sessions(path)

        self.mutate(
            path,
            "UPDATE consumed_sessions "
            "SET session = ? WHERE session = ?",
            (self.other, self.session),
        )

        after = self.sessions(path)

        self.assertEqual(
            len(before),
            len(after),
        )

        self.assertEqual(
            after,
            {self.other},
        )

        self.assertNotEqual(
            before,
            after,
        )

        self.assert_rejected_before_signature(
            label="same_count_substitution",
        )

    def test_04_marker_reset_and_history_loss_rejected(self):

        path = self.initialize()

        if path == self.root_path:

            self.mutate(
                path,
                "DROP TABLE consumed_sessions",
            )

            self.assertNotIn(
                "consumed_sessions",
                self.table_names(path),
            )

        else:

            self.fixture_path(path).unlink()

            self.assertFalse(
                path.exists(),
            )

        self.mutate(
            self.root_path,
            "PRAGMA user_version = 0",
        )

        self.assertEqual(
            self.query(
                self.root_path,
                "PRAGMA user_version",
            ),
            [(0,)],
        )

        self.assert_rejected_before_signature(
            label="marker_reset_history_loss",
            reconstruct=True,
        )

    def test_05_reservation_preserves_canonical_root(self):

        before = self.backend.read()
        reference = before.reference()

        self.initialize()

        self.assertEqual(
            self.backend.read(),
            before,
        )

        self.assertEqual(
            self.backend.read().reference(),
            reference,
        )

        self.assertEqual(
            self.client.read(),
            before,
        )

    def test_06_fresh_sessions_remain_available(self):

        path = self.initialize()

        self.complete(self.fresh)

        self.assertEqual(
            self.sessions(path),
            {self.session, self.fresh},
        )

        reopened = (
            base.sqlite_root.SQLiteProtectedRootBackend.open(
                path=self.root_path,
                expected_identity=self.initial.identity,
            )
        )

        second = self.f.make_provider(
            backend=reopened,
        )

        self.complete(
            self.other,
            provider=second,
        )

        self.assertEqual(
            self.sessions(path),
            {
                self.session,
                self.fresh,
                self.other,
            },
        )

        self.assertEqual(
            reopened.read(),
            self.initial,
        )


if __name__ == "__main__":
    unittest.main()
