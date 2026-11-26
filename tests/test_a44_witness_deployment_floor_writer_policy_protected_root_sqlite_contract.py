"""SQLite reference protected root backend contract.

The root state and coordination fence use separate databases.

create() explicitly creates an unprovisioned storage pair.
open() only opens an existing, validated storage pair.

Neither operation silently replaces missing or incomplete storage.

provision() initializes canonical stable revision 1 exactly once.
compare_and_set() commits root transitions independently of the
outer authorization fence.

The existing ProtectedRootBackend interface remains unchanged.

This reference models trusted persistent storage. It does not
provide hardware rollback resistance or protection against
replacement of the entire trusted storage pair.
"""

import importlib
import tempfile
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import test_a44_witness_deployment_floor_writer_policy_protected_root_backend_contract as previous


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_sqlite_reference"
)


class A44SQLiteProtectedRootContractTests(unittest.TestCase):

    def setUp(self):

        self.m = importlib.import_module(MODULE)

        self.f = previous.A44ProtectedRootBackendContractTests(
            "test_01_explicit_provisioning"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.r = self.f.m
        self.d = self.f.d

        self.identity = self.f.identity
        self.initial = self.f.initial

        temporary = tempfile.TemporaryDirectory(
            prefix="a44-root-"
        )

        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name).resolve()
        self.path = self.directory / "root.sqlite3"

        self.fence_path = self.path.with_name(
            self.path.name + ".fence.sqlite3"
        )

        self.backend_type = self.m.SQLiteProtectedRootBackend

        self.backend = self.create()

    def create(self, **changes):

        params = {
            "path": self.path,
            "expected_identity": self.identity,
        }

        params.update(changes)

        return self.backend_type.create(**params)

    def reopen(self, **changes):

        params = {
            "path": self.path,
            "expected_identity": self.identity,
        }

        params.update(changes)

        return self.backend_type.open(**params)

    def provision(self):

        self.assertEqual(
            self.backend.provision(state=self.initial),
            self.initial.reference(),
        )

    def advance(self, old, new, backend=None):

        if backend is None:
            backend = self.backend

        return backend.compare_and_set(
            expected=old.reference(),
            replacement=new,
        )

    def assert_state(self, backend, expected):

        actual = backend.read()

        self.assertIs(
            type(actual),
            self.r.ProtectedDurableRootState,
        )

        self.assertEqual(actual, expected)
        self.assertEqual(actual.reference(), expected.reference())

        self.assertIs(
            type(actual.identity),
            self.r.ProtectedDeploymentIdentity,
        )

        self.assertIs(
            type(actual.durable_state),
            self.d.DurablePolicyHighWaterState,
        )

        return actual

    def test_01_explicit_create_and_unprovisioned_open(self):

        self.assertIsInstance(
            self.backend,
            self.r.ProtectedRootBackend,
        )

        self.assertEqual(self.backend.identity, self.identity)

        self.assertTrue(self.path.is_file())
        self.assertTrue(self.fence_path.is_file())

        self.assertGreater(self.path.stat().st_size, 0)
        self.assertGreater(self.fence_path.stat().st_size, 0)

        peer = self.reopen()

        for backend in (self.backend, peer):

            with self.assertRaises(ValueError):
                backend.read()

            with self.assertRaises(ValueError):
                self.advance(
                    self.initial,
                    self.f.pending(),
                    backend=backend,
                )

        self.provision()

        self.assert_state(peer, self.initial)

    def test_02_stable_state_round_trip(self):

        self.provision()

        peer = self.reopen()

        self.assertIsNot(peer, self.backend)

        state = self.assert_state(peer, self.initial)

        with self.assertRaises(AttributeError):
            state.revision = 2

        self.assert_state(self.backend, self.initial)

    def test_03_provisioning_is_one_time_across_instances(self):

        self.provision()

        peer = self.reopen()

        for backend in (self.backend, peer):

            with self.assertRaises(ValueError):
                backend.provision(state=self.initial)

        with self.assertRaises(ValueError):
            self.create()

        self.assert_state(peer, self.initial)

    def test_04_open_missing_storage_does_not_create(self):

        missing = self.directory / "missing.sqlite3"

        before = set(self.directory.iterdir())

        with self.assertRaises(ValueError):
            self.reopen(path=missing)

        self.assertEqual(
            set(self.directory.iterdir()),
            before,
        )

        self.assertFalse(missing.exists())

    def test_05_every_external_identity_component_is_bound(self):

        self.provision()

        for identity in (
            replace(self.identity, deployment_id="other-root"),
            replace(self.identity, configuration_sha256="12" * 32),
            replace(self.identity, provisioning_nonce=b"x" * 32),
        ):

            with self.assertRaises(ValueError):
                self.reopen(expected_identity=identity)

        self.assert_state(self.reopen(), self.initial)

    def test_06_prepared_round_trip_retains_exact_signed_bytes(self):

        self.provision()

        pending = self.f.pending()

        self.assertEqual(
            self.advance(self.initial, pending),
            pending.reference(),
        )

        peer = self.reopen()

        actual = self.assert_state(peer, pending)
        prepared = actual.durable_state.prepared

        self.assertIs(
            type(prepared),
            self.d.PreparedPolicyPublication,
        )

        self.assertEqual(
            prepared.signed_policy,
            pending.durable_state.prepared.signed_policy,
        )

        self.assertIs(type(prepared.signed_policy), tuple)

        self.assertTrue(
            all(type(value) is bytes for value in prepared.signed_policy)
        )

        self.assertEqual(
            actual.durable_state.anchor,
            self.initial.durable_state.anchor,
        )

    def test_07_finalized_round_trip_and_detached_snapshots(self):

        self.provision()

        pending = self.f.pending()
        self.advance(self.initial, pending)

        peer = self.reopen()

        old = self.assert_state(peer, pending)
        final = self.f.finalized(pending)

        self.advance(pending, final, backend=peer)

        self.assert_state(self.backend, final)
        self.assert_state(self.reopen(), final)

        self.assertIsNotNone(old.durable_state.prepared)
        self.assertEqual(old.revision, 2)

    def test_08_stale_reference_and_wrong_digest_rejected(self):

        self.provision()

        pending = self.f.pending()
        self.advance(self.initial, pending)

        peer = self.reopen()

        final = self.f.finalized(pending)

        with self.assertRaises(ValueError):

            self.advance(
                self.initial,
                final,
                backend=peer,
            )

        with self.assertRaises(ValueError):

            peer.compare_and_set(
                expected=self.r.ProtectedRootReference(
                    revision=2,
                    sha256="ef" * 32,
                ),
                replacement=final,
            )

        self.assert_state(peer, pending)

        self.advance(pending, final, backend=peer)

        self.assert_state(self.backend, final)

    def test_09_invalid_transitions_cannot_mutate_storage(self):

        self.provision()

        pending = self.f.pending()

        for invalid in (
            replace(pending, revision=3),
            replace(self.initial, revision=2),
            replace(
                pending,
                identity=replace(
                    self.identity,
                    provisioning_nonce=b"x" * 32,
                ),
            ),
        ):

            with self.assertRaises(ValueError):
                self.advance(self.initial, invalid)

            self.assert_state(self.reopen(), self.initial)

        self.advance(self.initial, pending)

        alternative = self.f.pending(
            self.f.prepared(message=b"alternative")
        )

        for invalid in (
            replace(self.initial, revision=3),
            replace(alternative, revision=3),
        ):

            with self.assertRaises(ValueError):
                self.advance(pending, invalid)

            self.assert_state(self.reopen(), pending)

    def test_10_stable_rollback_and_same_epoch_fork_rejected(self):

        self.provision()

        pending = self.f.pending()
        final = self.f.finalized(pending)

        self.advance(self.initial, pending)
        self.advance(pending, final)

        rollback = replace(self.initial, revision=4)

        fork = replace(
            final,
            revision=4,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=self.d.PolicyReference(
                    epoch=2,
                    sha256="ef" * 32,
                ),
            ),
        )

        for invalid in (rollback, fork):

            with self.assertRaises(ValueError):
                self.advance(final, invalid)

            self.assert_state(self.reopen(), final)

        descendant = replace(
            final,
            revision=4,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=self.d.PolicyReference(
                    epoch=3,
                    sha256="12" * 32,
                ),
            ),
        )

        self.advance(final, descendant)

        self.assert_state(self.reopen(), descendant)

    def test_11_committed_state_survives_outer_fence_exception(self):

        self.provision()

        pending = self.f.pending()

        with self.assertRaises(OSError):

            with self.backend.exclusive():

                with self.backend.exclusive():

                    self.advance(self.initial, pending)

                    self.assert_state(self.backend, pending)

                raise OSError("Interrupted enclosing operation")

        self.assert_state(self.reopen(), pending)

        final = self.f.finalized(pending)

        with self.assertRaises(OSError):

            with self.backend.exclusive():

                self.advance(pending, final)

                raise OSError("Lost finalization acknowledgement")

        self.assert_state(self.reopen(), final)

    def test_12_independent_instances_share_exclusive_fence(self):

        self.provision()

        peer = self.reopen()
        pending = self.f.pending()

        started = threading.Event()
        finished = threading.Event()

        def competitor():

            started.set()

            try:
                return self.advance(
                    self.initial,
                    pending,
                    backend=peer,
                )
            finally:
                finished.set()

        with ThreadPoolExecutor(max_workers=1) as pool:

            with self.backend.exclusive():

                future = pool.submit(competitor)

                self.assertTrue(started.wait(timeout=5))
                self.assertFalse(finished.wait(timeout=0.25))

                self.assert_state(self.backend, self.initial)

            self.assertEqual(
                future.result(timeout=30),
                pending.reference(),
            )

        self.assert_state(self.backend, pending)

    def test_13_missing_state_store_fails_closed(self):

        self.provision()

        self.path.unlink()

        for operation in (
            self.backend.read,
            self.reopen,
            self.create,
        ):

            with self.assertRaises(ValueError):
                operation()

        self.assertFalse(self.path.exists())
        self.assertTrue(self.fence_path.is_file())

    def test_14_missing_fence_store_fails_closed(self):

        self.provision()

        self.fence_path.unlink()

        for operation in (
            self.backend.read,
            self.reopen,
            self.create,
        ):

            with self.assertRaises(ValueError):
                operation()

        self.assertFalse(self.fence_path.exists())
        self.assertTrue(self.path.is_file())


if __name__ == "__main__":
    unittest.main()
