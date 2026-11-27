"""Exclusive authenticated provider ownership contracts.

A reentrant SQLite backend fence must not authorize multiple
simultaneous provider sessions over the same storage pair.

Rejected competing sessions must not reach durable reservation,
signing or CAS dispatch.

Independent storage pairs and sequential sessions remain valid.
Foreign-thread providers must serialize through the existing
backend fence.

This contract assumes trusted in-process code and trusted
local storage. It does not establish remote fencing or
hardware-backed rollback resistance.
"""

import hashlib
import sqlite3
import threading
import unittest

from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_contract as base


class SyntheticOwnerAbort(BaseException):
    pass


class A44AuthenticatedAnchorProviderOwnershipContractTests(
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
        self.Provider = type(self.a)

        self.backend = self.f.backend

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.sa = b"a" * 32
        self.sb = b"b" * 32
        self.sc = b"c" * 32

        self.assertEqual(
            self.backend.read(),
            self.initial,
        )

        self.assertEqual(
            self.history(),
            set(),
        )

    def history(self, path=None):

        if path is None:
            path = self.f.path

        path = Path(path).resolve()

        self.assertEqual(
            path.parent,
            self.f.path.resolve().parent,
        )

        with closing(
            sqlite3.connect(
                path.as_uri() + "?mode=ro",
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

        self.assertEqual(
            stored,
            [(expected,)],
        )

        return set(sessions)

    def reopen(self):

        return (
            base.sqlite_root.SQLiteProtectedRootBackend.open(
                path=self.f.path,
                expected_identity=self.initial.identity,
            )
        )

    def new_provider(self, backend=None):

        if backend is None:
            backend = self.backend

        return self.f.make_provider(
            backend=backend,
        )

    def assert_idle(self, provider):

        state = provider._held

        self.assertEqual(state.phase, "idle")
        self.assertIsNone(state.session)
        self.assertIsNone(state.owner)
        self.assertIsNone(state.reference)

        self.assertFalse(state.challenges)
        self.assertFalse(state.poisoned)

    def read(self, provider, session, state=None):

        if state is None:
            state = self.initial

        response = provider.read(
            session=session,
            challenge=b"r" * 32,
        )

        self.f.assert_signed_response(
            response,
            state,
        )

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

            self.read(
                provider,
                session,
                state,
            )

            self.finish(
                provider,
                session,
                state,
            )

        self.assert_idle(provider)

    def assert_nested_rejected(
        self,
        backend,
        label,
    ):

        b = self.new_provider(backend)

        entered = []
        signing = []

        original = self.Provider._signed

        def observe(instance, **kwargs):

            if instance is b:

                signing.append(
                    kwargs["operation"]
                )

            return original(instance, **kwargs)

        with self.a.hold(
            session=self.sa,
        ) as outer:

            self.f.assert_signed_response(
                outer,
                self.initial,
            )

            with patch.object(
                self.Provider,
                "_signed",
                new=observe,
            ):

                try:

                    with b.hold(
                        session=self.sb,
                    ) as response:

                        entered.append(True)

                        self.f.assert_signed_response(
                            response,
                            self.initial,
                        )

                        self.read(b, self.sb)
                        self.finish(b, self.sb)

                except ValueError:

                    self.assertEqual(
                        entered,
                        [],
                        "Competing provider entered before rejection",
                    )

                    self.assertEqual(
                        signing,
                        [],
                        "Competing provider reached signing",
                    )

            self.read(self.a, self.sa)
            self.finish(self.a, self.sa)

        self.assert_idle(self.a)
        self.assert_idle(b)

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

        if entered:

            self.assertEqual(
                signing,
                ["hold", "read", "finish"],
            )

            self.assertEqual(
                self.history(),
                {self.sa, self.sb},
            )

            self.fail(
                "PROVIDER_OWNERSHIP_OPEN:" + label
            )

        self.assertEqual(
            signing,
            [],
        )

        self.assertEqual(
            self.history(),
            {self.sa},
            "Rejected session was durably consumed",
        )

        # Rejection must not burn the competing nonce.
        # It becomes valid after the original owner releases.

        self.complete(
            b,
            self.sb,
        )

        self.assertEqual(
            self.history(),
            {self.sa, self.sb},
        )

    def test_01_same_backend_competing_provider_rejected(self):

        self.assert_nested_rejected(
            self.backend,
            "same_backend",
        )

    def test_02_reopened_backend_competing_provider_rejected(self):

        reopened = self.reopen()

        self.assertIsNot(
            reopened,
            self.backend,
        )

        self.assertEqual(
            reopened._storage,
            self.backend._storage,
        )

        self.assert_nested_rejected(
            reopened,
            "reopened_backend",
        )

    def test_03_competing_provider_cannot_commit_cas(self):

        b = self.new_provider(
            self.reopen()
        )

        entered = []
        committed = []
        signing = []
        dispatched = []

        original_signed = self.Provider._signed

        backend_class = type(self.backend)

        original_cas = (
            backend_class.compare_and_set
        )

        def observe_signing(instance, **kwargs):

            if instance is b:

                signing.append(
                    kwargs["operation"]
                )

            return original_signed(
                instance,
                **kwargs,
            )

        def observe_cas(instance, **kwargs):

            dispatched.append(True)

            return original_cas(
                instance,
                **kwargs,
            )

        outer_rejected = False

        try:

            with self.a.hold(
                session=self.sa,
            ):

                with patch.object(
                    self.Provider,
                    "_signed",
                    new=observe_signing,
                ):

                    with patch.object(
                        backend_class,
                        "compare_and_set",
                        new=observe_cas,
                    ):

                        try:

                            with b.hold(
                                session=self.sb,
                            ):

                                entered.append(True)

                                response = b.compare_and_set(
                                    session=self.sb,
                                    challenge=b"k" * 32,
                                    expected=self.initial.reference(),
                                    replacement=self.pending,
                                )

                                self.f.assert_signed_response(
                                    response,
                                    self.pending,
                                )

                                committed.append(True)

                                self.finish(
                                    b,
                                    self.sb,
                                    self.pending,
                                )

                        except ValueError:

                            self.assertEqual(
                                entered,
                                [],
                                "Competing CAS session entered before rejection",
                            )

                if committed:

                    with self.assertRaises(ValueError):

                        self.read(
                            self.a,
                            self.sa,
                        )

                else:

                    self.read(
                        self.a,
                        self.sa,
                    )

                    self.finish(
                        self.a,
                        self.sa,
                    )

        except ValueError:

            self.assertEqual(
                committed,
                [True],
                "Unexpected owner failure",
            )

            outer_rejected = True

        self.assert_idle(self.a)
        self.assert_idle(b)

        if committed:

            self.assertTrue(
                outer_rejected
            )

            self.assertEqual(
                dispatched,
                [True],
            )

            self.assertEqual(
                signing,
                ["hold", "cas", "finish"],
            )

            self.assertEqual(
                self.reopen().read(),
                self.pending,
            )

            self.assertEqual(
                self.history(),
                {self.sa, self.sb},
            )

            self.fail(
                "PROVIDER_OWNERSHIP_OPEN:nested_cas"
            )

        self.assertEqual(entered, [])
        self.assertEqual(dispatched, [])
        self.assertEqual(signing, [])

        self.assertFalse(
            outer_rejected
        )

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

        self.assertEqual(
            self.history(),
            {self.sa},
        )

        self.complete(
            b,
            self.sb,
        )

    def test_04_distinct_storage_remains_independent(self):

        alternate = (
            self.f.path.resolve().with_name(
                "independent-anchor.sqlite3"
            )
        )

        self.assertEqual(
            alternate.parent,
            self.f.path.resolve().parent,
        )

        other_backend = (
            base.sqlite_root.SQLiteProtectedRootBackend.create(
                path=alternate,
                expected_identity=self.initial.identity,
            )
        )

        other_backend.provision(
            state=self.initial,
        )

        self.assertNotEqual(
            other_backend._storage.storage_id,
            self.backend._storage.storage_id,
        )

        b = self.new_provider(
            other_backend
        )

        with self.a.hold(
            session=self.sa,
        ):

            self.complete(
                b,
                self.sb,
            )

            self.read(
                self.a,
                self.sa,
            )

            self.finish(
                self.a,
                self.sa,
            )

        self.assertEqual(
            self.history(),
            {self.sa},
        )

        self.assertEqual(
            self.history(alternate),
            {self.sb},
        )

        self.assertEqual(
            self.backend.read(),
            self.initial,
        )

        self.assertEqual(
            other_backend.read(),
            self.initial,
        )

        self.assert_idle(self.a)
        self.assert_idle(b)

    def test_05_sequential_ownership_transfer(self):

        b = self.new_provider(
            self.reopen()
        )

        self.complete(
            self.a,
            self.sa,
        )

        self.complete(
            b,
            self.sb,
        )

        self.complete(
            self.a,
            self.sc,
        )

        self.assertEqual(
            self.history(),
            {self.sa, self.sb, self.sc},
        )

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

        self.assert_idle(self.a)
        self.assert_idle(b)

    def test_06_owner_abort_releases_ownership(self):

        b = self.new_provider(
            self.reopen()
        )

        injected = SyntheticOwnerAbort(
            "owner interrupted"
        )

        with self.assertRaises(
            SyntheticOwnerAbort
        ) as caught:

            with self.a.hold(
                session=self.sa,
            ):

                raise injected

        self.assertIs(
            caught.exception,
            injected,
        )

        self.assert_idle(self.a)

        self.assertEqual(
            self.history(),
            {self.sa},
        )

        self.complete(
            b,
            self.sb,
        )

        self.assertEqual(
            self.history(),
            {self.sa, self.sb},
        )

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

        self.assert_idle(b)

    def test_07_foreign_thread_cannot_poison_owner(self):

        results = []

        def worker():

            try:

                self.a.read(
                    session=self.sa,
                    challenge=b"z" * 32,
                )

            except ValueError:

                results.append("REJECTED")

            except BaseException as exc:

                results.append(exc)

            else:

                results.append("ACCEPTED")

        thread = threading.Thread(
            target=worker,
            daemon=True,
        )

        with self.a.hold(
            session=self.sa,
        ):

            thread.start()
            thread.join(10)

            self.assertFalse(
                thread.is_alive(),
                "Foreign-thread operation did not return",
            )

            self.assertEqual(
                results,
                ["REJECTED"],
            )

            self.read(
                self.a,
                self.sa,
            )

            self.finish(
                self.a,
                self.sa,
            )

        self.assert_idle(self.a)

        self.assertEqual(
            self.history(),
            {self.sa},
        )

    def test_08_foreign_thread_provider_serializes(self):

        b = self.new_provider(
            self.reopen()
        )

        entered = threading.Event()
        completed = threading.Event()
        reached_fence = threading.Event()

        results = []

        backend_class = type(self.backend)

        original_exclusive = (
            backend_class.exclusive
        )

        def observe_exclusive(instance):

            if threading.current_thread() is thread:

                reached_fence.set()

            return original_exclusive(instance)

        def worker():

            try:

                with b.hold(
                    session=self.sb,
                ) as response:

                    entered.set()

                    self.f.assert_signed_response(
                        response,
                        self.initial,
                    )

                    self.read(
                        b,
                        self.sb,
                    )

                    self.finish(
                        b,
                        self.sb,
                    )

                results.append("COMPLETED")

            except BaseException as exc:

                results.append(exc)

            finally:

                completed.set()

        thread = threading.Thread(
            target=worker,
            daemon=True,
        )

        with patch.object(
            backend_class,
            "exclusive",
            new=observe_exclusive,
        ):

            try:

                with self.a.hold(
                    session=self.sa,
                ):

                    thread.start()

                    self.assertTrue(
                        reached_fence.wait(5),
                        "Worker did not attempt backend fence",
                    )

                    self.assertFalse(
                        entered.wait(0.5),
                        "Competing thread entered held fence",
                    )

                    self.assertFalse(
                        completed.is_set()
                    )

                    self.assertEqual(
                        self.history(),
                        {self.sa},
                    )

                    self.read(
                        self.a,
                        self.sa,
                    )

                    self.finish(
                        self.a,
                        self.sa,
                    )

                    self.assertFalse(
                        entered.is_set(),
                        "FINISH released ownership prematurely",
                    )

            finally:

                if thread.ident is not None:

                    thread.join(40)

        self.assertFalse(
            thread.is_alive(),
            "Competing provider failed to resume",
        )

        self.assertEqual(
            results,
            ["COMPLETED"],
        )

        self.assertTrue(
            entered.is_set()
        )

        self.assertTrue(
            completed.is_set()
        )

        self.assertEqual(
            self.history(),
            {self.sa, self.sb},
        )

        self.assertEqual(
            self.reopen().read(),
            self.initial,
        )

        self.assert_idle(self.a)
        self.assert_idle(b)


if __name__ == "__main__":
    unittest.main()
