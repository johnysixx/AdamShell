"""Permanent authenticated provider ownership lifecycle contracts.

Provider ownership must cover acquisition, signing, active
operations, FINISH and backend fence cleanup.

Same-thread competing providers must be rejected before
session reservation or signature publication.

Acquisition and cleanup failures must release ownership
without losing the original exception or committed state.

All database operations use temporary test fixtures.
"""

import hashlib
import importlib
import sqlite3
import unittest

from contextlib import closing, contextmanager
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_contract as base


class SyntheticAcquisitionFailure(Exception):
    pass


class SyntheticCleanupFailure(Exception):
    pass


class SyntheticOwnerAbort(BaseException):
    pass


class A44AuthenticatedAnchorProviderOwnershipLifecycleTests(
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

        self.a = self.f.provider
        self.backend = self.f.backend

        self.Provider = type(self.a)
        self.Backend = type(self.backend)

        self.module = importlib.import_module(
            self.Provider.__module__
        )

        self.sqlite = importlib.import_module(
            self.Backend.__module__
        )

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.path = self.f.path.resolve()

        self.reopened = (
            self.Backend.open(
                path=self.path,
                expected_identity=self.initial.identity,
            )
        )

        self.b = self.f.make_provider(
            backend=self.reopened,
        )

        self.sa = b"a" * 32
        self.sb = b"b" * 32

        self.key = self.backend._storage.fence_path

        self.owners = (
            self.module._active_provider_owners()
        )

        self.original_exclusive = (
            self.Backend.exclusive
        )

        self.original_signed = (
            self.Provider._signed
        )

        self.assertEqual(self.owners, {})
        self.assertEqual(self.history(), set())


    def history(self):

        with closing(
            sqlite3.connect(
                self.path.as_uri() + "?mode=ro",
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

            stored = connection.execute(
                "SELECT history_digest FROM session_metadata"
            ).fetchall()

        expected = hashlib.sha256(
            b"AdamShell/A44/protected-root-session-history/v2"
            + b"\x00"
            + b"".join(sessions)
            + len(sessions).to_bytes(8, "big")
        ).hexdigest()

        self.assertEqual(stored, [(expected,)])

        return set(sessions)


    def assert_idle(self, provider):

        held = provider._held

        self.assertEqual(held.phase, "idle")
        self.assertIsNone(held.session)
        self.assertIsNone(held.owner)
        self.assertIsNone(held.reference)

        self.assertFalse(held.poisoned)
        self.assertFalse(held.challenges)


    def assert_claim(self):

        self.assertEqual(
            set(self.owners),
            {self.key},
        )

        return self.owners[self.key]


    def assert_released(self):

        self.assertEqual(self.owners, {})

        self.assertNotIn(
            self.key,
            self.sqlite._active_leases(),
        )

        self.assert_idle(self.a)
        self.assert_idle(self.b)


    def finish(self, provider, session, state=None):

        if state is None:
            state = self.initial

        response = provider.finish(
            session=session,
            challenge=b"f" * 32,
            expected=state.reference(),
        )

        self.f.assert_signed_response(
            response,
            state,
        )


    def complete(self, provider, session, state=None):

        if state is None:
            state = self.initial

        with provider.hold(
            session=session,
        ) as response:

            self.f.assert_signed_response(
                response,
                state,
            )

            response = provider.read(
                session=session,
                challenge=b"r" * 32,
            )

            self.f.assert_signed_response(
                response,
                state,
            )

            self.finish(
                provider,
                session,
                state,
            )

        self.assert_idle(provider)


    def reject_competitor(self):

        token = self.assert_claim()

        before = self.history()

        entered = []
        signing = []

        def observe(instance, **kwargs):

            if instance is self.b:

                signing.append(
                    kwargs["operation"]
                )

            return self.original_signed(
                instance,
                **kwargs,
            )

        with patch.object(
            self.Provider,
            "_signed",
            new=observe,
        ):

            with self.assertRaises(ValueError):

                with self.b.hold(
                    session=self.sb,
                ):

                    entered.append(True)

        self.assertEqual(entered, [])
        self.assertEqual(signing, [])

        self.assertEqual(
            self.history(),
            before,
        )

        self.assertIs(
            self.owners[self.key],
            token,
        )

        self.assert_idle(self.b)


    def recover(self, expected=None):

        if expected is None:
            expected = self.initial

        self.assert_released()

        self.assertEqual(
            self.backend.read(),
            expected,
        )

        self.assertEqual(
            self.reopened.read(),
            expected,
        )

        self.assertNotIn(
            self.sb,
            self.history(),
        )

        self.complete(
            self.b,
            self.sb,
            expected,
        )

        self.assert_released()

        self.assertIn(
            self.sb,
            self.history(),
        )


    def test_01_acquisition_callback_rejected(self):

        calls = []

        @contextmanager
        def exclusive(instance):

            if (
                instance is self.backend
                and self.a._held.phase == "acquiring"
                and not calls
            ):

                calls.append("acquisition")

                self.assertNotIn(
                    self.key,
                    self.sqlite._active_leases(),
                )

                self.assertEqual(
                    self.history(),
                    set(),
                )

                self.reject_competitor()

            with self.original_exclusive(instance):
                yield

        with patch.object(
            self.Backend,
            "exclusive",
            new=exclusive,
        ):

            self.complete(
                self.a,
                self.sa,
            )

        self.assertEqual(
            calls,
            ["acquisition"],
        )

        self.assertEqual(
            self.history(),
            {self.sa},
        )

        self.recover()


    def signing_callback(self, operation):

        calls = []

        def sign(instance, **kwargs):

            if (
                instance is self.a
                and kwargs["operation"] == operation
            ):

                calls.append(operation)

                self.assertIn(
                    self.sa,
                    self.history(),
                )

                self.reject_competitor()

            return self.original_signed(
                instance,
                **kwargs,
            )

        with patch.object(
            self.Provider,
            "_signed",
            new=sign,
        ):

            with self.a.hold(
                session=self.sa,
            ):

                state = self.initial

                if operation == "cas":

                    response = self.a.compare_and_set(
                        session=self.sa,
                        challenge=b"c" * 32,
                        expected=self.initial.reference(),
                        replacement=self.pending,
                    )

                    self.f.assert_signed_response(
                        response,
                        self.pending,
                    )

                    state = self.pending

                self.finish(
                    self.a,
                    self.sa,
                    state,
                )

        self.assertEqual(calls, [operation])

        self.assertEqual(
            self.history(),
            {self.sa},
        )

        self.recover(
            self.pending
            if operation == "cas"
            else self.initial,
        )


    def test_02_hold_signing_callback_rejected(self):

        self.signing_callback("hold")


    def test_03_cas_signing_callback_rejected(self):

        self.signing_callback("cas")


    def test_04_finished_owner_retains_claim(self):

        with self.a.hold(
            session=self.sa,
        ):

            token = self.assert_claim()

            self.finish(
                self.a,
                self.sa,
            )

            self.assertEqual(
                self.a._held.phase,
                "finished",
            )

            self.assertIs(
                self.owners[self.key],
                token,
            )

            self.reject_competitor()

        self.recover()


    def cleanup_callback(self, after_release):

        calls = []

        @contextmanager
        def exclusive(instance):

            outer = (
                instance is self.backend
                and self.a._held.phase == "acquiring"
                and self.key not in
                    self.sqlite._active_leases()
            )

            with self.original_exclusive(instance):

                try:
                    yield

                finally:

                    if outer and not after_release:

                        calls.append("before_release")

                        self.assertIn(
                            self.key,
                            self.sqlite._active_leases(),
                        )

                        self.reject_competitor()

            if outer and after_release:

                calls.append("after_release")

                self.assertNotIn(
                    self.key,
                    self.sqlite._active_leases(),
                )

                self.reject_competitor()

        with patch.object(
            self.Backend,
            "exclusive",
            new=exclusive,
        ):

            self.complete(
                self.a,
                self.sa,
            )

        self.assertEqual(
            calls,
            [
                "after_release"
                if after_release
                else "before_release"
            ],
        )

        self.assertEqual(
            self.history(),
            {self.sa},
        )

        self.recover()


    def test_05_cleanup_callback_rejected(self):

        self.cleanup_callback(False)


    def test_06_post_fence_release_callback_rejected(self):

        self.cleanup_callback(True)


    def test_07_acquisition_failure_releases_claim(self):

        injected = SyntheticAcquisitionFailure(
            "acquisition interrupted"
        )

        calls = []

        @contextmanager
        def exclusive(instance):

            if (
                instance is self.backend
                and not calls
            ):

                calls.append(True)

                self.assert_claim()

                raise injected

            with self.original_exclusive(instance):
                yield

        with patch.object(
            self.Backend,
            "exclusive",
            new=exclusive,
        ):

            with self.assertRaises(
                SyntheticAcquisitionFailure
            ) as caught:

                with self.a.hold(
                    session=self.sa,
                ):

                    self.fail(
                        "Failed acquisition exposed HOLD"
                    )

        self.assertIs(
            caught.exception,
            injected,
        )

        self.assertEqual(calls, [True])
        self.assertEqual(self.history(), set())

        self.assert_released()

        self.complete(
            self.a,
            self.sa,
        )

        self.recover()


    def cleanup_failure(self, owner_abort):

        cleanup = SyntheticCleanupFailure(
            "fence cleanup interrupted"
        )

        primary = SyntheticOwnerAbort(
            "owner interrupted"
        )

        calls = []

        @contextmanager
        def exclusive(instance):

            outer = (
                instance is self.backend
                and self.a._held.phase == "acquiring"
                and self.key not in
                    self.sqlite._active_leases()
            )

            try:

                with self.original_exclusive(instance):
                    yield

            finally:

                if outer:

                    calls.append("cleanup")

                    self.assert_claim()

                    self.assertNotIn(
                        self.key,
                        self.sqlite._active_leases(),
                    )

                    raise cleanup

        with patch.object(
            self.Backend,
            "exclusive",
            new=exclusive,
        ):

            if owner_abort:

                with self.assertRaises(
                    SyntheticOwnerAbort
                ) as caught:

                    with self.a.hold(
                        session=self.sa,
                    ):

                        raise primary

                self.assertIs(
                    caught.exception,
                    primary,
                )

            else:

                with self.assertRaises(
                    SyntheticCleanupFailure
                ) as caught:

                    self.complete(
                        self.a,
                        self.sa,
                    )

                self.assertIs(
                    caught.exception,
                    cleanup,
                )

        self.assertEqual(calls, ["cleanup"])

        self.assertEqual(
            self.history(),
            {self.sa},
        )

        self.recover()


    def test_08_cleanup_failure_releases_claim(self):

        self.cleanup_failure(False)


    def test_09_primary_exception_survives_cleanup(self):

        self.cleanup_failure(True)


    def test_10_repeated_ownership_transfer_no_leak(self):

        expected = set()

        for index in range(1, 9):

            nonce = index.to_bytes(32, "big")

            provider = (
                self.a
                if index % 2
                else self.b
            )

            self.complete(
                provider,
                nonce,
            )

            expected.add(nonce)

            self.assert_released()

            self.assertEqual(
                self.history(),
                expected,
            )

            self.assertEqual(
                self.reopened.read(),
                self.initial,
            )


if __name__ == "__main__":
    unittest.main()
