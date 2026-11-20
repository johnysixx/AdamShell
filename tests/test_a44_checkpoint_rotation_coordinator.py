"""A44 coordinated signed checkpoint witness rotation contract.

EXPECTED RED: checkpoint_rotation_coordinator module absent.

Proposed public API:

    CheckpointWitnessRotationCoordinator.from_sources(
        root_floor_source=source,
        signed_witness_source=source,
        expected_root_id=str,
        expected_authority_id=str,
        expected_universe_id=str,
        expected_challenge=bytes,
    )

    coordinator.inspect(
        expected_revision=int,
        next_revision=int,
        expected_witness=(message, signature),
        next_witness=(message, signature),
    ) -> CheckpointWitnessRotationObservation

    coordinator.rotate(same arguments) -> observation

The root source supports hold() and advance().
The signed witness store supports hold() and
publish_if_current(expected_witness=..., next_witness=...).

Required publication order:

1. Verify root, old witness and signed successor.
2. Publish successor with compare-and-swap.
3. Re-read both held sources and require successor visible.
4. Advance root revision with CAS.
5. Re-read both sources and require the expected result.

The observations are DATA ONLY. They do not prove
backend identity, durability, independent enrollment,
rollback resistance or cross-backend atomicity.

A failed operation may leave a successor published or
a floor already advanced. No implicit rollback or
blind retry is permitted.

All backends in this test are volatile test doubles.
No restoration or republication authority is granted.
"""

import importlib
import os
import sys
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_checkpoint_root_floor_cas as cas_contract
import test_a44_checkpoint_signed_witness as witness_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_rotation_coordinator"
)

ROOT = cas_contract.ROOT
AUTHORITY = cas_contract.AUTHORITY
WORLD = cas_contract.WORLD

REVISION = cas_contract.REVISION
OLD_FLOOR = REVISION - 1
NEXT_FLOOR = REVISION
NEXT_WITNESS_REVISION = REVISION + 1


class MemoryWitnessStore:
    """Volatile test double; NOT an external security backend."""

    def __init__(
        self,
        snapshot,
        *,
        fail_publish=None,
        fail_exit=None,
        commit_then_fail=False,
        fake_ack=False,
    ):
        self.snapshot = snapshot
        self.fail_publish = fail_publish
        self.fail_exit = fail_exit
        self.commit_then_fail = commit_then_fail
        self.fake_ack = fake_ack

        self.lock = RLock()
        self.active = False
        self.events = []
        self.publish_calls = 0

    @contextmanager
    def hold(self):
        with self.lock:
            self.events.append("enter")
            self.active = True

            try:
                yield self.snapshot
            finally:
                self.active = False
                self.events.append("exit")

                if self.fail_exit is not None:
                    raise self.fail_exit

    def publish_if_current(
        self,
        *,
        expected_witness,
        next_witness,
    ):
        with self.lock:
            self.publish_calls += 1

            if self.fail_publish is not None:
                raise self.fail_publish

            if self.snapshot != expected_witness:
                raise ValueError(
                    "Test witness CAS predecessor mismatch."
                )

            if self.fake_ack:
                return next_witness

            self.snapshot = next_witness
            self.events.append("publish")

            if self.commit_then_fail:
                raise OSError(
                    "Test transport fault after witness publication."
                )

            return self.snapshot


class SuppressingWitnessStore(MemoryWitnessStore):
    """Test double that suppresses ValueError from a held body."""

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


class A44CheckpointRotationCoordinatorContractTests(
    unittest.TestCase
):

    def setUp(self):
        self.module = importlib.import_module(MODULE)

        self.coordinator_type = (
            self.module.CheckpointWitnessRotationCoordinator
        )

        self.observation_type = (
            self.module.CheckpointWitnessRotationObservation
        )

        self.cas = (
            cas_contract.A44CheckpointRootFloorCASContractTests(
                "test_valid_pinned_root_snapshot"
            )
        )

        self.cas.setUp()
        self.addCleanup(self.cas.doCleanups)

        self.binding = self.cas.fixture

        self.root_source = self.cas.adapter()
        self.old_pair = self.binding.witness_source.snapshot

        self.next_pair = self.binding.witness.signed(
            self.binding.document(
                witness_revision=NEXT_WITNESS_REVISION,
            )
        )

        self.store = MemoryWitnessStore(self.old_pair)

    def make_coordinator(
        self,
        *,
        root_source=None,
        signed_witness_source=None,
    ):
        return self.coordinator_type.from_sources(
            root_floor_source=(
                self.root_source
                if root_source is None
                else root_source
            ),
            signed_witness_source=(
                self.store
                if signed_witness_source is None
                else signed_witness_source
            ),
            expected_root_id=ROOT,
            expected_authority_id=AUTHORITY,
            expected_universe_id=WORLD,
            expected_challenge=self.binding.witness.challenge,
        )

    def arguments(self, **changes):
        values = dict(
            expected_revision=OLD_FLOOR,
            next_revision=NEXT_FLOOR,
            expected_witness=self.old_pair,
            next_witness=self.next_pair,
        )

        values.update(changes)
        return values

    def inspect(self, source=None, **changes):
        source = (
            self.make_coordinator()
            if source is None
            else source
        )

        return source.inspect(**self.arguments(**changes))

    def rotate(self, source=None, **changes):
        source = (
            self.make_coordinator()
            if source is None
            else source
        )

        return source.rotate(**self.arguments(**changes))

    def assert_data_only(self, observation):
        self.assertIs(type(observation), self.observation_type)

        self.assertIs(observation.signature_verified, True)

        for field in (
            "is_independently_trusted",
            "is_authoritative",
            "is_durable",
            "is_restorable",
            "can_republish",
        ):
            self.assertIs(
                getattr(observation, field),
                False,
                field,
            )

    def assert_released(self, store=None, backend=None):
        source = self.store if store is None else store
        backend = (
            self.cas.backend
            if backend is None
            else backend
        )

        self.assertFalse(source.active)
        self.assertFalse(backend.active)

    def test_ready_observation_holds_sources_and_is_data_only(self):
        original = (
            self.module.verify_signed_checkpoint_trust_witness
        )

        observations = []

        def guarded_verify(**kwargs):
            self.assertTrue(self.cas.backend.active)
            self.assertTrue(self.store.active)

            observations.append((
                kwargs["trusted_root_id"],
                kwargs["minimum_witness_revision"],
            ))

            return original(**kwargs)

        with patch.object(
            self.module,
            "verify_signed_checkpoint_trust_witness",
            new=guarded_verify,
        ):
            result = self.inspect()

        self.assertEqual(result.state, "ready")
        self.assertEqual(result.floor_revision, OLD_FLOOR)
        self.assertEqual(result.witness_revision, REVISION)

        self.assertGreaterEqual(len(observations), 2)
        self.assert_data_only(result)

        self.assertEqual(self.store.publish_calls, 0)
        self.assert_released()

    def test_successful_rotation_publishes_witness_before_floor(self):
        trace = []

        class TracedBackend(cas_contract.MemoryCASBackend):
            def advance_if_current(self, **kwargs):
                trace.append("floor")
                return super().advance_if_current(**kwargs)

        class TracedStore(MemoryWitnessStore):
            def publish_if_current(self, **kwargs):
                trace.append("witness")
                return super().publish_if_current(**kwargs)

        backend = TracedBackend((
            ROOT,
            self.cas.public,
            OLD_FLOOR,
        ))

        root = self.cas.adapter(backend=backend)
        store = TracedStore(self.old_pair)

        source = self.make_coordinator(
            root_source=root,
            signed_witness_source=store,
        )

        result = self.rotate(source)

        self.assertEqual(trace, ["witness", "floor"])
        self.assertEqual(result.state, "observed_advanced")
        self.assertEqual(result.floor_revision, NEXT_FLOOR)
        self.assertEqual(
            result.witness_revision,
            NEXT_WITNESS_REVISION,
        )

        self.assert_data_only(result)

        self.assertEqual(store.snapshot, self.next_pair)
        self.assertEqual(backend.snapshot[2], NEXT_FLOOR)

        with self.assertRaises(ValueError):
            self.binding.verify(
                self.binding.make_source(
                    root_source=root,
                    signed_witness_source=(
                        cas_contract.binding_contract
                        .source_contract.HeldSource(self.old_pair)
                    ),
                )
            )

        new_checkpoint = self.binding.verify(
            self.binding.make_source(
                root_source=root,
                signed_witness_source=store,
            )
        )

        self.assertTrue(new_checkpoint.signature_verified)
        self.assertFalse(new_checkpoint.is_authoritative)

        self.assertFalse(store.active)
        self.assertFalse(backend.active)

    def test_invalid_successor_signed_documents_rejected_before_writes(
        self
    ):
        attacker = Ed25519PrivateKey.generate()

        altered_signature = bytearray(self.next_pair[1])
        altered_signature[0] ^= 1

        bad_pairs = (
            (self.next_pair[0], bytes(altered_signature)),
            self.binding.witness.signed(
                self.binding.document(
                    witness_revision=NEXT_WITNESS_REVISION,
                ),
                signer=attacker,
            ),
            self.binding.witness.signed(
                self.binding.document(
                    witness_revision=NEXT_WITNESS_REVISION,
                    authority_id="foreign_authority",
                )
            ),
            self.binding.witness.signed(
                self.binding.document(
                    witness_revision=NEXT_WITNESS_REVISION,
                    universe_id="foreign_universe",
                )
            ),
            self.binding.witness.signed(
                self.binding.document(
                    witness_revision=NEXT_WITNESS_REVISION,
                    challenge_hex=os.urandom(32).hex(),
                )
            ),
            self.binding.witness.signed(
                self.binding.document(
                    witness_revision=REVISION,
                )
            ),
        )

        for candidate in bad_pairs:
            with self.subTest(
                message_prefix=candidate[0][:20],
                signature_prefix=candidate[1][:4].hex(),
            ):
                with self.assertRaises(ValueError):
                    self.rotate(next_witness=candidate)

                self.assertEqual(self.store.publish_calls, 0)
                self.assertEqual(self.store.snapshot, self.old_pair)
                self.assertEqual(
                    self.cas.backend.snapshot[2],
                    OLD_FLOOR,
                )

                self.assert_released()

    def test_malformed_pairs_and_revision_preconditions_rejected(self):
        invalid_changes = (
            {"expected_revision": True},
            {"expected_revision": -1},
            {"next_revision": False},
            {"next_revision": OLD_FLOOR},
            {"next_revision": NEXT_FLOOR + 1},
            {"next_revision": "13"},
            {"expected_witness": None},
            {"expected_witness": [*self.old_pair]},
            {"expected_witness": (bytearray(self.old_pair[0]),
                                  self.old_pair[1])},
            {"next_witness": None},
            {"next_witness": [*self.next_pair]},
            {"next_witness": (self.next_pair[0],
                              bytearray(self.next_pair[1]))},
        )

        for changes in invalid_changes:
            with self.subTest(changes=repr(changes)[:75]):
                with self.assertRaises(ValueError):
                    self.rotate(**changes)

                self.assertEqual(self.store.publish_calls, 0)
                self.assertEqual(self.store.snapshot, self.old_pair)
                self.assertEqual(
                    self.cas.backend.snapshot[2],
                    OLD_FLOOR,
                )

    def test_stale_witness_or_floor_precondition_rejected(self):
        self.store.snapshot = self.next_pair

        observation = self.inspect()

        self.assertEqual(
            observation.state,
            "witness_published",
        )

        with self.assertRaises(ValueError):
            self.rotate()

        self.assertEqual(self.store.publish_calls, 0)

        self.store.snapshot = self.old_pair

        self.root_source.advance(
            expected_revision=OLD_FLOOR,
            next_revision=NEXT_FLOOR,
        )

        with self.assertRaises(ValueError):
            self.rotate()

        self.assertEqual(self.store.publish_calls, 0)
        self.assertEqual(self.store.snapshot, self.old_pair)
        self.assert_released()

    def test_witness_publication_failures_report_uncertain_state(self):
        failing = MemoryWitnessStore(
            self.old_pair,
            fail_publish=OSError(
                "Test failure before witness commit"
            ),
        )

        source = self.make_coordinator(
            signed_witness_source=failing,
        )

        with self.assertRaises(ValueError):
            self.rotate(source)

        self.assertEqual(failing.snapshot, self.old_pair)
        self.assertEqual(self.cas.backend.snapshot[2], OLD_FLOOR)

        self.assertEqual(
            self.inspect(source).state,
            "ready",
        )

        partial = MemoryWitnessStore(
            self.old_pair,
            commit_then_fail=True,
        )

        source = self.make_coordinator(
            signed_witness_source=partial,
        )

        with self.assertRaises(ValueError):
            self.rotate(source)

        self.assertEqual(partial.snapshot, self.next_pair)
        self.assertEqual(self.cas.backend.snapshot[2], OLD_FLOOR)

        self.assertEqual(
            self.inspect(source).state,
            "witness_published",
        )

        self.assert_released(store=partial)

    def test_cas_failure_after_witness_publication_is_observable(self):
        backend = cas_contract.MemoryCASBackend(
            (
                ROOT,
                self.cas.public,
                OLD_FLOOR,
            ),
            fail_advance=OSError(
                "Test CAS failure before commit"
            ),
        )

        root = self.cas.adapter(backend=backend)
        source = self.make_coordinator(root_source=root)

        with self.assertRaises(ValueError):
            self.rotate(source)

        self.assertEqual(self.store.snapshot, self.next_pair)
        self.assertEqual(backend.snapshot[2], OLD_FLOOR)

        observation = self.inspect(source)

        self.assertEqual(
            observation.state,
            "witness_published",
        )

        self.assert_data_only(observation)
        self.assert_released(backend=backend)

    def test_cas_after_commit_error_requires_explicit_inspection(self):
        class CommitThenFail(cas_contract.MemoryCASBackend):
            def advance_if_current(self, **kwargs):
                super().advance_if_current(**kwargs)
                raise OSError(
                    "Test transport failure after CAS commit"
                )

        backend = CommitThenFail((
            ROOT,
            self.cas.public,
            OLD_FLOOR,
        ))

        root = self.cas.adapter(backend=backend)
        source = self.make_coordinator(root_source=root)

        with self.assertRaises(ValueError):
            self.rotate(source)

        self.assertEqual(self.store.snapshot, self.next_pair)
        self.assertEqual(backend.snapshot[2], NEXT_FLOOR)

        observation = self.inspect(source)

        self.assertEqual(
            observation.state,
            "observed_advanced",
        )

        self.assert_data_only(observation)
        self.assert_released(backend=backend)

    def test_false_witness_publish_ack_blocks_floor_advance(self):
        store = MemoryWitnessStore(
            self.old_pair,
            fake_ack=True,
        )

        source = self.make_coordinator(
            signed_witness_source=store,
        )

        with self.assertRaises(ValueError):
            self.rotate(source)

        self.assertEqual(store.publish_calls, 1)
        self.assertEqual(store.snapshot, self.old_pair)
        self.assertEqual(self.cas.backend.snapshot[2], OLD_FLOOR)

        self.assertEqual(
            self.inspect(source).state,
            "ready",
        )

        self.assert_released(store=store)

    def test_false_cas_ack_rejected_by_final_readback(self):
        class FalseCASAck(cas_contract.MemoryCASBackend):
            def advance_if_current(
                self,
                *,
                expected_revision,
                next_revision,
            ):
                return (
                    ROOT,
                    self.snapshot[1],
                    next_revision,
                )

        backend = FalseCASAck((
            ROOT,
            self.cas.public,
            OLD_FLOOR,
        ))

        root = self.cas.adapter(backend=backend)
        source = self.make_coordinator(root_source=root)

        with self.assertRaises(ValueError):
            self.rotate(source)

        self.assertEqual(self.store.snapshot, self.next_pair)
        self.assertEqual(backend.snapshot[2], OLD_FLOOR)

        self.assertEqual(
            self.inspect(source).state,
            "witness_published",
        )

        self.assert_released(backend=backend)

    def test_competing_rotations_have_one_observed_winner(self):
        source = self.make_coordinator()

        def attempt(_):
            try:
                result = self.rotate(source)

                if result.state != "observed_advanced":
                    raise AssertionError(
                        "Unexpected rotation success state."
                    )

                return "advanced"

            except ValueError:
                return "rejected"

        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(pool.map(attempt, range(8)))

        self.assertEqual(outcomes.count("advanced"), 1)
        self.assertEqual(outcomes.count("rejected"), 7)

        self.assertEqual(self.store.snapshot, self.next_pair)
        self.assertEqual(
            self.cas.backend.snapshot[2],
            NEXT_FLOOR,
        )

        self.assertEqual(
            self.inspect(source).state,
            "observed_advanced",
        )

        self.assert_released()

    def test_suppressed_errors_and_volatile_rollback_fail_closed(self):
        malformed = SuppressingWitnessStore(
            (b"", b"invalid")
        )

        source = self.make_coordinator(
            signed_witness_source=malformed,
        )

        with self.assertRaises(ValueError):
            self.inspect(source)

        self.assertFalse(malformed.active)
        self.assertIn("suppressed", malformed.events)

        exit_fault = MemoryWitnessStore(
            self.old_pair,
            fail_exit=ValueError(
                "Test witness lease teardown fault"
            ),
        )

        source = self.make_coordinator(
            signed_witness_source=exit_fault,
        )

        with self.assertRaises(ValueError):
            self.inspect(source)

        self.assertFalse(exit_fault.active)

        result = self.rotate()

        self.assertEqual(result.state, "observed_advanced")

        # Deliberate replacement of both VOLATILE test
        # backends. This demonstrates an absent security
        # property, not a successful durable recovery.
        self.cas.backend.snapshot = (
            ROOT,
            self.cas.public,
            OLD_FLOOR,
        )

        self.store.snapshot = self.old_pair

        observation = self.inspect()

        self.assertEqual(observation.state, "ready")
        self.assert_data_only(observation)

        old_checkpoint = self.binding.verify(
            self.binding.make_source(
                root_source=self.root_source,
                signed_witness_source=self.store,
            )
        )

        self.assertTrue(old_checkpoint.signature_verified)
        self.assertFalse(old_checkpoint.is_authoritative)
        self.assert_released()


if __name__ == "__main__":
    unittest.main()
