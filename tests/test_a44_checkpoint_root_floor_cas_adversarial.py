"""A44 adversarial external checkpoint root-floor CAS tests.

These tests validate the Python adapter against simulated
backend behavior and failures.

Important security distinctions:

1. A returned CAS tuple does NOT prove backend publication.
2. A failed CAS call does NOT prove backend rollback.
3. A Python RLock does NOT establish cross-process durability.
4. Caller-selected root pins do NOT prove independent enrollment.
5. A resettable memory backend does NOT resist state replacement.

All test backends here are untrusted test doubles.

No checkpoint restoration or republication is authorized.
"""

import sys
import unittest

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_root_floor_cas as contract
import test_a44_checkpoint_signed_witness as witness_contract


ROOT = contract.ROOT
REVISION = contract.REVISION


class A44CheckpointRootFloorCASAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointRootFloorCASContractTests(
                "test_valid_pinned_root_snapshot"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.public = self.fixture.public

    def adapter(self, backend=None):
        if backend is None:
            return self.fixture.adapter()

        return self.fixture.adapter(backend=backend)

    def test_factory_rejects_missing_interfaces_and_invalid_pins(self):
        class ReadOnly:
            def hold(self):
                raise AssertionError("Unexpected hold.")

        class WriteOnly:
            def advance_if_current(self, **kwargs):
                raise AssertionError("Unexpected CAS.")

        for backend in (
            None,
            object(),
            ReadOnly(),
            WriteOnly(),
        ):
            with self.subTest(
                backend=type(backend).__name__
            ):
                with self.assertRaises(ValueError):
                    self.fixture.adapter_type.from_backend(
                        backend=backend,
                        expected_root_id=ROOT,
                        expected_root_public_key=self.public,
                    )

        for changes in (
            {"expected_root_id": ""},
            {"expected_root_id": " foreign_root"},
            {"expected_root_id": True},
            {"expected_root_public_key": b""},
            {"expected_root_public_key": self.public[:-1]},
            {"expected_root_public_key": bytearray(self.public)},
            {"expected_root_public_key": True},
        ):
            with self.subTest(changes=repr(changes)[:65]):
                with self.assertRaises(ValueError):
                    self.fixture.adapter(**changes)

    def test_direct_construction_revalidates_fields(self):
        invalid = (
            ("", self.public, self.fixture.backend),
            (True, self.public, self.fixture.backend),
            (ROOT, b"invalid", self.fixture.backend),
            (
                ROOT,
                bytearray(self.public),
                self.fixture.backend,
            ),
            (ROOT, self.public, object()),
        )

        for root_id, key, backend in invalid:
            with self.subTest(
                root_id=repr(root_id),
                backend=type(backend).__name__,
            ):
                # Dataclass construction bypasses from_backend().
                adapter = self.fixture.adapter_type(
                    backend=backend,
                    expected_root_id=root_id,
                    expected_root_public_key=key,
                )

                with self.assertRaises(ValueError):
                    with adapter.hold():
                        pass

                with self.assertRaises(ValueError):
                    adapter.advance(
                        expected_revision=REVISION - 1,
                        next_revision=REVISION,
                    )

    def test_strict_held_snapshot_rejection(self):
        original = self.fixture.backend.snapshot
        adapter = self.adapter()

        class TupleChild(tuple):
            pass

        class BytesChild(bytes):
            pass

        invalid = (
            None,
            (),
            [],
            TupleChild(original),
            (ROOT,),
            (*original, "extra"),
            ("foreign_root", self.public, REVISION - 1),
            (ROOT, b"invalid", REVISION - 1),
            (ROOT, bytearray(self.public), REVISION - 1),
            (ROOT, BytesChild(self.public), REVISION - 1),
            (ROOT, self.public, True),
            (ROOT, self.public, -1),
            (ROOT, self.public, 12.0),
            (ROOT, self.public, "12"),
        )

        try:
            for snapshot in invalid:
                with self.subTest(
                    snapshot=repr(snapshot)[:70]
                ):
                    self.fixture.backend.snapshot = snapshot

                    with self.assertRaises(ValueError):
                        with adapter.hold():
                            pass

                    self.assertFalse(
                        self.fixture.backend.active
                    )

        finally:
            self.fixture.backend.snapshot = original

    def test_backend_entry_exit_and_suppression_fail_closed(self):
        valid = self.fixture.backend.snapshot

        failures = (
            contract.MemoryCASBackend(
                valid,
                fail_enter=ValueError("entry fault"),
            ),
            contract.MemoryCASBackend(
                valid,
                fail_exit=ValueError("exit fault"),
            ),
            contract.MemoryCASBackend(
                valid,
                fail_exit=OSError("backend teardown fault"),
            ),
        )

        for backend in failures:
            with self.subTest(
                enter=repr(backend.fail_enter),
                exit=repr(backend.fail_exit),
            ):
                with self.assertRaises(ValueError):
                    with self.adapter(backend).hold():
                        pass

                self.assertFalse(backend.active)

        suppressing = contract.SuppressingCASBackend(valid)

        with self.assertRaises(ValueError):
            with self.adapter(suppressing).hold():
                raise ValueError(
                    "Injected caller verification failure"
                )

        self.assertFalse(suppressing.active)
        self.assertIn(
            "suppressed",
            suppressing.events,
        )

        malformed = contract.SuppressingCASBackend(
            (ROOT, b"invalid", REVISION - 1)
        )

        with self.assertRaises(ValueError):
            with self.adapter(malformed).hold():
                pass

        self.assertFalse(malformed.active)
        self.assertIn(
            "suppressed",
            malformed.events,
        )

    def test_invalid_cas_parameters_never_reach_backend(self):
        class SpyBackend(contract.MemoryCASBackend):
            def __init__(self, snapshot):
                super().__init__(snapshot)
                self.calls = 0

            def advance_if_current(self, **kwargs):
                self.calls += 1
                return super().advance_if_current(**kwargs)

        valid = self.fixture.backend.snapshot

        backend = SpyBackend(valid)
        adapter = self.adapter(backend)

        invalid = (
            (-1, REVISION),
            (True, REVISION),
            (REVISION - 1, False),
            (REVISION - 1, REVISION - 1),
            (REVISION - 1, REVISION - 2),
            (REVISION - 1, "13"),
            ("12", REVISION),
            (REVISION - 1, 13.0),
            (None, REVISION),
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

        self.assertEqual(backend.calls, 0)
        self.assertEqual(backend.snapshot, valid)

    def test_malformed_cas_backend_replies_rejected(self):
        original = self.fixture.backend.snapshot

        class ReplyBackend(contract.MemoryCASBackend):
            def __init__(self, snapshot, reply):
                super().__init__(snapshot)
                self.reply = reply
                self.calls = 0

            def advance_if_current(self, **kwargs):
                self.calls += 1
                return self.reply

        malformed = (
            None,
            (),
            [],
            (ROOT, self.public),
            (ROOT, self.public, REVISION, "extra"),
            ("foreign_root", self.public, REVISION),
            (ROOT, b"invalid", REVISION),
            (ROOT, bytearray(self.public), REVISION),
            (ROOT, self.public, True),
            (ROOT, self.public, REVISION - 1),
            (ROOT, self.public, REVISION + 1),
        )

        for reply in malformed:
            with self.subTest(reply=repr(reply)[:70]):
                backend = ReplyBackend(original, reply)
                adapter = self.adapter(backend)

                with self.assertRaises(ValueError):
                    adapter.advance(
                        expected_revision=REVISION - 1,
                        next_revision=REVISION,
                    )

                self.assertEqual(backend.calls, 1)
                self.assertEqual(
                    backend.snapshot,
                    original,
                )

    def test_backend_can_lie_about_committed_publication(self):
        class LyingBackend(contract.MemoryCASBackend):
            def advance_if_current(
                self,
                *,
                expected_revision,
                next_revision,
            ):
                # Return the expected tuple without changing
                # any backend state. The adapter cannot detect
                # a malicious backend from this response alone.
                return (
                    self.snapshot[0],
                    self.snapshot[1],
                    next_revision,
                )

        original = self.fixture.backend.snapshot
        backend = LyingBackend(original)
        adapter = self.adapter(backend)

        reply = adapter.advance(
            expected_revision=REVISION - 1,
            next_revision=REVISION,
        )

        self.assertEqual(
            reply,
            (ROOT, self.public, REVISION),
        )

        self.assertEqual(
            backend.snapshot,
            original,
        )

        with adapter.hold() as actual:
            self.assertEqual(
                actual[2],
                REVISION - 1,
            )

        self.assertFalse(backend.active)

        # This is a demonstrated security limitation.
        # No independent durability is established.

    def test_backend_commits_then_returns_corrupt_reply(self):
        class CorruptReplyBackend(contract.MemoryCASBackend):
            def advance_if_current(self, **kwargs):
                committed = super().advance_if_current(
                    **kwargs
                )

                # Backend already committed. Its reply
                # is now inconsistent with the requested CAS.
                return (
                    committed[0],
                    committed[1],
                    committed[2] + 1,
                )

        original = self.fixture.backend.snapshot
        backend = CorruptReplyBackend(original)
        adapter = self.adapter(backend)

        with self.assertRaises(ValueError):
            adapter.advance(
                expected_revision=REVISION - 1,
                next_revision=REVISION,
            )

        # Rejection of the response does NOT roll back
        # an already completed backend operation.
        self.assertEqual(
            backend.snapshot,
            (ROOT, self.public, REVISION),
        )

        with adapter.hold() as snapshot:
            self.assertEqual(snapshot[2], REVISION)

        with self.assertRaises(ValueError):
            adapter.advance(
                expected_revision=REVISION - 1,
                next_revision=REVISION,
            )

    def test_backend_commits_then_raises_uncertain_outcome(self):
        class AfterCommitFailure(contract.MemoryCASBackend):
            def advance_if_current(self, **kwargs):
                super().advance_if_current(**kwargs)

                raise OSError(
                    "Injected transport failure after commit"
                )

        original = self.fixture.backend.snapshot

        backend = AfterCommitFailure(original)
        adapter = self.adapter(backend)

        with self.assertRaises(ValueError):
            adapter.advance(
                expected_revision=REVISION - 1,
                next_revision=REVISION,
            )

        self.assertEqual(
            backend.snapshot,
            (ROOT, self.public, REVISION),
        )

        with adapter.hold() as observed:
            self.assertEqual(observed[2], REVISION)

        # Do not infer rollback from a failed response.
        # Backend state must be reconciled before retry.

    def test_competing_cas_publications_have_one_winner(self):
        backend = contract.MemoryCASBackend(
            self.fixture.backend.snapshot
        )

        adapter = self.adapter(backend)

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
            outcomes = list(
                pool.map(attempt, range(8))
            )

        self.assertEqual(
            outcomes.count("committed"),
            1,
        )

        self.assertEqual(
            outcomes.count("rejected"),
            7,
        )

        self.assertEqual(
            backend.snapshot,
            (ROOT, self.public, REVISION),
        )

        # One-winner behavior is provided by this test
        # backend's RLock, not by the Python adapter.

    def test_held_read_serializes_test_backend_publication(self):
        backend = contract.MemoryCASBackend(
            self.fixture.backend.snapshot
        )

        adapter = self.adapter(backend)
        started = Event()

        def publish():
            started.set()

            return adapter.advance(
                expected_revision=REVISION - 1,
                next_revision=REVISION,
            )

        with ThreadPoolExecutor(max_workers=1) as pool:
            with adapter.hold() as held:
                self.assertEqual(
                    held[2],
                    REVISION - 1,
                )

                future = pool.submit(publish)

                self.assertTrue(
                    started.wait(timeout=10)
                )

                self.assertFalse(future.done())
                self.assertTrue(backend.active)

            published = future.result(timeout=10)

        self.assertEqual(
            published,
            (ROOT, self.public, REVISION),
        )

        self.assertFalse(backend.active)

    def test_rollback_and_caller_selected_root_limitations(self):
        adapter = self.adapter()

        adapter.advance(
            expected_revision=REVISION - 1,
            next_revision=REVISION,
        )

        binding = self.fixture.fixture

        with self.assertRaises(ValueError):
            binding.verify(
                binding.make_source(
                    root_source=adapter,
                )
            )

        # Simulate an attacker replacing the state
        # of the VOLATILE TEST BACKEND.
        self.fixture.backend.snapshot = (
            ROOT,
            self.public,
            0,
        )

        replay = binding.verify(
            binding.make_source(
                root_source=adapter,
            )
        )

        self.assertTrue(replay.signature_verified)
        self.assertFalse(replay.is_authoritative)

        attacker = Ed25519PrivateKey.generate()

        attacker_public = witness_contract.public_bytes(
            attacker
        )

        attacker_backend = contract.MemoryCASBackend((
            ROOT,
            attacker_public,
            REVISION - 1,
        ))

        # The original pinned key correctly rejects
        # an unexpected backend root.
        with self.assertRaises(ValueError):
            with self.adapter(attacker_backend).hold():
                pass

        # But a CALLER can select both a different pin
        # and a witness signed by that different root.
        caller_selected_adapter = (
            self.fixture.adapter_type.from_backend(
                backend=attacker_backend,
                expected_root_id=ROOT,
                expected_root_public_key=attacker_public,
            )
        )

        attacker_witness = binding.signed_source(
            signer=attacker
        )

        result = binding.verify(
            binding.make_source(
                root_source=caller_selected_adapter,
                signed_witness_source=attacker_witness,
            )
        )

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assertFalse(attacker_backend.active)
        self.assertFalse(attacker_witness.active)


if __name__ == "__main__":
    unittest.main()
