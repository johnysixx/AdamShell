"""A44 external checkpoint root-floor CAS adapter contract.

EXPECTED RED: checkpoint_root_floor_cas module absent.

The external backend must expose:

    hold() -> context manager yielding:
        (root_id, raw_root_public_key, minimum_witness_revision)

    advance_if_current(
        expected_revision=int,
        next_revision=int,
    ) -> same three-element tuple after successful publication

The backend is responsible for:
- authenticating its identity independently of this adapter;
- protecting the enrolled root key;
- executing linearizable compare-and-swap;
- persisting the revision floor across actual restarts;
- resisting rollback or replacement of persistent state;
- preserving consistency during failures.

A Python adapter CANNOT establish those properties.

The memory backend below is a TEST DOUBLE. It exercises
API-level invariants, not actual storage security.

No checkpoint restoration or republication is authorized.
"""

import importlib
import sys
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import Event, RLock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_checkpoint_signed_binding as binding_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_root_floor_cas"
)

ROOT = binding_contract.ROOT
AUTHORITY = binding_contract.AUTHORITY
WORLD = binding_contract.WORLD
REVISION = binding_contract.REVISION


class MemoryCASBackend:
    """Volatile test double; NOT a protected external backend."""

    def __init__(
        self,
        snapshot,
        *,
        fail_enter=None,
        fail_exit=None,
        fail_advance=None,
    ):
        self.snapshot = snapshot
        self.fail_enter = fail_enter
        self.fail_exit = fail_exit
        self.fail_advance = fail_advance
        self.lock = RLock()
        self.active = False
        self.events = []

    @contextmanager
    def hold(self):
        with self.lock:
            self.events.append("enter")

            if self.fail_enter is not None:
                raise self.fail_enter

            self.active = True

            try:
                yield self.snapshot
            finally:
                self.active = False
                self.events.append("exit")

                if self.fail_exit is not None:
                    raise self.fail_exit

    def advance_if_current(
        self,
        *,
        expected_revision,
        next_revision,
    ):
        with self.lock:
            if self.fail_advance is not None:
                raise self.fail_advance

            root_id, public_key, current = self.snapshot

            if (
                type(expected_revision) is not int
                or type(next_revision) is not int
                or current != expected_revision
                or next_revision <= current
            ):
                raise ValueError("Test-double CAS conflict.")

            self.snapshot = (
                root_id,
                public_key,
                next_revision,
            )

            self.events.append("advance")
            return self.snapshot


class SuppressingCASBackend(MemoryCASBackend):
    """Test double that masks ValueError thrown into hold()."""

    @contextmanager
    def hold(self):
        with self.lock:
            self.events.append("enter")
            self.active = True

            try:
                yield self.snapshot
            except ValueError:
                self.events.append("suppressed")
            finally:
                self.active = False
                self.events.append("exit")


class A44CheckpointRootFloorCASContractTests(unittest.TestCase):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.adapter_type = (
            module.ExternalCheckpointRootFloorAdapter
        )

        self.fixture = (
            binding_contract.A44CheckpointSignedBindingContractTests(
                "test_valid_single_signed_witness_checkpoint_verification"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.public = self.fixture.witness.root_public

        self.backend = MemoryCASBackend((
            ROOT,
            self.public,
            REVISION - 1,
        ))

    def adapter(self, backend=None, **changes):
        arguments = {
            "backend": (
                self.backend if backend is None else backend
            ),
            "expected_root_id": ROOT,
            "expected_root_public_key": self.public,
        }

        arguments.update(changes)

        return self.adapter_type.from_backend(**arguments)

    def test_valid_pinned_root_snapshot(self):
        adapter = self.adapter()

        with adapter.hold() as snapshot:
            self.assertIs(type(snapshot), tuple)
            self.assertEqual(
                snapshot,
                (ROOT, self.public, REVISION - 1),
            )
            self.assertTrue(self.backend.active)

        self.assertFalse(self.backend.active)
        self.assertEqual(
            self.backend.events,
            ["enter", "exit"],
        )

    def test_existing_signed_binding_accepts_adapter(self):
        adapter = self.adapter()

        source = self.fixture.make_source(
            root_source=adapter
        )

        result = self.fixture.verify(source)

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assertFalse(self.backend.active)
        self.assertFalse(self.fixture.witness_source.active)

    def test_missing_backend_operations_rejected(self):
        class ReadOnly:
            def hold(self):
                raise AssertionError("Should not enter hold.")

        class WriteOnly:
            def advance_if_current(self, **kwargs):
                raise AssertionError("Should not write.")

        for candidate in (
            None,
            object(),
            ReadOnly(),
            WriteOnly(),
        ):
            with self.subTest(candidate=type(candidate).__name__):
                with self.assertRaises(ValueError):
                    self.adapter_type.from_backend(
                        backend=candidate,
                        expected_root_id=ROOT,
                        expected_root_public_key=self.public,
                    )

    def test_malformed_pinned_identity_or_key_rejected(self):
        for changes in (
            {"expected_root_id": ""},
            {"expected_root_id": " foreign_root"},
            {"expected_root_id": None},
            {"expected_root_public_key": b""},
            {"expected_root_public_key": self.public[:-1]},
            {"expected_root_public_key": bytearray(self.public)},
            {"expected_root_public_key": None},
        ):
            with self.subTest(changes=repr(changes)[:65]):
                with self.assertRaises(ValueError):
                    self.adapter(**changes)

    def test_malformed_snapshot_rejected(self):
        valid = self.backend.snapshot

        malformed = (
            None,
            (),
            [],
            [*valid],
            (ROOT,),
            (*valid, "extra"),
            (ROOT, bytearray(self.public), REVISION - 1),
            (ROOT, self.public[:-1], REVISION - 1),
            (ROOT, self.public, True),
            (ROOT, self.public, -1),
        )

        adapter = self.adapter()

        for snapshot in malformed:
            with self.subTest(snapshot=repr(snapshot)[:60]):
                self.backend.snapshot = snapshot

                with self.assertRaises(ValueError):
                    with adapter.hold():
                        pass

                self.assertFalse(self.backend.active)

        self.backend.snapshot = valid

    def test_root_substitution_rejected(self):
        import os

        adapter = self.adapter()

        self.backend.snapshot = (
            ROOT,
            os.urandom(32),
            REVISION - 1,
        )

        if self.backend.snapshot[1] == self.public:
            raise AssertionError("Unexpected random key collision.")

        with self.assertRaises(ValueError):
            with adapter.hold():
                pass

        self.assertFalse(self.backend.active)

        self.backend.snapshot = (
            "foreign_root",
            self.public,
            REVISION - 1,
        )

        with self.assertRaises(ValueError):
            with adapter.hold():
                pass

        self.assertFalse(self.backend.active)

    def test_cas_advances_revision_and_blocks_old_witness(self):
        adapter = self.adapter()

        result = adapter.advance(
            expected_revision=REVISION - 1,
            next_revision=REVISION,
        )

        self.assertEqual(
            result,
            (ROOT, self.public, REVISION),
        )

        self.assertEqual(
            self.backend.snapshot,
            (ROOT, self.public, REVISION),
        )

        with self.assertRaises(ValueError):
            self.fixture.verify(
                self.fixture.make_source(
                    root_source=adapter
                )
            )

        self.assertFalse(self.backend.active)

    def test_stale_cas_rejected_without_state_change(self):
        adapter = self.adapter()

        adapter.advance(
            expected_revision=REVISION - 1,
            next_revision=REVISION,
        )

        before = self.backend.snapshot

        with self.assertRaises(ValueError):
            adapter.advance(
                expected_revision=REVISION - 1,
                next_revision=REVISION + 1,
            )

        self.assertEqual(self.backend.snapshot, before)

    def test_invalid_cas_parameters_rejected(self):
        adapter = self.adapter()

        invalid = (
            (-1, REVISION),
            (True, REVISION),
            (REVISION - 1, False),
            (REVISION - 1, REVISION - 1),
            (REVISION - 1, REVISION - 2),
            (REVISION - 1, "13"),
            ("12", REVISION),
            (REVISION - 1, 13.0),
        )

        for previous, target in invalid:
            with self.subTest(
                previous=repr(previous),
                target=repr(target),
            ):
                with self.assertRaises(ValueError):
                    adapter.advance(
                        expected_revision=previous,
                        next_revision=target,
                    )

        self.assertEqual(
            self.backend.snapshot,
            (ROOT, self.public, REVISION - 1),
        )

    def test_concurrent_cas_only_one_succeeds(self):
        adapter = self.adapter()

        def attempt(_):
            try:
                adapter.advance(
                    expected_revision=REVISION - 1,
                    next_revision=REVISION,
                )
                return "committed"
            except ValueError:
                return "rejected"

        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(pool.map(attempt, range(8)))

        self.assertEqual(outcomes.count("committed"), 1)
        self.assertEqual(outcomes.count("rejected"), 7)

        self.assertEqual(
            self.backend.snapshot,
            (ROOT, self.public, REVISION),
        )

    def test_held_lease_blocks_test_backend_cas(self):
        adapter = self.adapter()
        started = Event()

        def advance():
            started.set()
            return adapter.advance(
                expected_revision=REVISION - 1,
                next_revision=REVISION,
            )

        with ThreadPoolExecutor(max_workers=1) as pool:
            with adapter.hold() as snapshot:
                self.assertEqual(
                    snapshot[2],
                    REVISION - 1,
                )

                future = pool.submit(advance)

                self.assertTrue(started.wait(timeout=10))
                self.assertFalse(future.done())

                self.assertTrue(self.backend.active)

            result = future.result(timeout=10)

        self.assertEqual(
            result,
            (ROOT, self.public, REVISION),
        )

        self.assertFalse(self.backend.active)

    def test_backend_failures_and_masked_errors_fail_closed(self):
        backend = MemoryCASBackend(
            (ROOT, self.public, REVISION - 1),
            fail_advance=OSError("Test CAS failure"),
        )

        adapter = self.adapter(backend=backend)

        with self.assertRaises(ValueError):
            adapter.advance(
                expected_revision=REVISION - 1,
                next_revision=REVISION,
            )

        self.assertEqual(
            backend.snapshot[2],
            REVISION - 1,
        )

        exit_fault = MemoryCASBackend(
            (ROOT, self.public, REVISION - 1),
            fail_exit=ValueError("Test lease exit failure"),
        )

        with self.assertRaises(ValueError):
            with self.adapter(backend=exit_fault).hold():
                pass

        self.assertFalse(exit_fault.active)

        suppressing = SuppressingCASBackend(
            (ROOT, self.public, REVISION - 1)
        )

        with self.assertRaises(ValueError):
            with self.adapter(backend=suppressing).hold():
                raise ValueError("Injected verification failure")

        self.assertFalse(suppressing.active)
        self.assertIn("suppressed", suppressing.events)


if __name__ == "__main__":
    unittest.main()
