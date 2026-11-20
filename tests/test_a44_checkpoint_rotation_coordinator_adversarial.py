"""A44 adversarial signed checkpoint witness rotation tests.

The coordinator is tested against volatile, untrusted
backend substitutes.

Properties under examination:
- invalid sources and caller-supplied identities;
- direct Python construction bypassing factory validation;
- malformed held snapshots and root substitution;
- altered and mixed signed witness pairs;
- forged verification reports;
- false publication acknowledgements;
- committed publication followed by malformed replies;
- commit followed by failure;
- masked provider errors;
- concurrent competing rotations.

These tests establish adapter behavior only.

They do NOT establish independent root enrollment,
authenticated external backends, durable revision
floors, rollback resistance or distributed atomicity.

No checkpoint restoration or republication is authorized.
"""

import sys
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_rotation_coordinator as contract
import test_a44_checkpoint_root_floor_cas as cas_contract


ROOT = contract.ROOT
AUTHORITY = contract.AUTHORITY
WORLD = contract.WORLD

OLD_FLOOR = contract.OLD_FLOOR
NEXT_FLOOR = contract.NEXT_FLOOR
NEXT_WITNESS_REVISION = contract.NEXT_WITNESS_REVISION


class A44CheckpointRotationCoordinatorAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointRotationCoordinatorContractTests(
                "test_ready_observation_holds_sources_and_is_data_only"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.old_pair = self.fixture.old_pair
        self.next_pair = self.fixture.next_pair

    def assert_unchanged(self):
        self.assertEqual(
            self.fixture.store.snapshot,
            self.old_pair,
        )

        self.assertEqual(
            self.fixture.cas.backend.snapshot[2],
            OLD_FLOOR,
        )

        self.assertEqual(
            self.fixture.store.publish_calls,
            0,
        )

        self.fixture.assert_released()

    def test_invalid_sources_and_configuration_rejected(self):
        normal = dict(
            root_floor_source=self.fixture.root_source,
            signed_witness_source=self.fixture.store,
            expected_root_id=ROOT,
            expected_authority_id=AUTHORITY,
            expected_universe_id=WORLD,
            expected_challenge=(
                self.fixture.binding.witness.challenge
            ),
        )

        invalid = (
            {"root_floor_source": None},
            {"root_floor_source": object()},
            {"signed_witness_source": None},
            {"signed_witness_source": object()},
            {"expected_root_id": ""},
            {"expected_root_id": True},
            {"expected_authority_id": ""},
            {"expected_universe_id": None},
            {"expected_challenge": b""},
            {"expected_challenge": bytearray(
                self.fixture.binding.witness.challenge
            )},
        )

        for change in invalid:
            with self.subTest(change=repr(change)[:80]):
                arguments = dict(normal)
                arguments.update(change)

                with self.assertRaises(ValueError):
                    self.fixture.coordinator_type.from_sources(
                        **arguments
                    )

                self.assert_unchanged()

    def test_direct_construction_revalidates_sources(self):
        base = dict(
            root_floor_source=self.fixture.root_source,
            signed_witness_source=self.fixture.store,
            expected_root_id=ROOT,
            expected_authority_id=AUTHORITY,
            expected_universe_id=WORLD,
            expected_challenge=(
                self.fixture.binding.witness.challenge
            ),
        )

        invalid = (
            {"root_floor_source": object()},
            {"signed_witness_source": object()},
            {"expected_root_id": ""},
            {"expected_authority_id": ""},
            {"expected_universe_id": None},
            {"expected_challenge": b""},
        )

        for change in invalid:
            with self.subTest(change=repr(change)[:70]):
                arguments = dict(base)
                arguments.update(change)

                source = self.fixture.coordinator_type(
                    **arguments
                )

                with self.assertRaises(ValueError):
                    source.inspect(
                        **self.fixture.arguments()
                    )

                with self.assertRaises(ValueError):
                    source.rotate(
                        **self.fixture.arguments()
                    )

                self.assert_unchanged()

    def test_malformed_held_witness_snapshots_rejected(self):
        class TupleChild(tuple):
            pass

        original = self.old_pair

        invalid = (
            None,
            (),
            [],
            [*original],
            TupleChild(original),
            (original[0],),
            (*original, "extra"),
            (bytearray(original[0]), original[1]),
            (original[0], bytearray(original[1])),
            (b"", original[1]),
            (original[0], b""),
            (original[0], original[1][:-1]),
            (b"incorrect signed data", original[1]),
        )

        for candidate in invalid:
            with self.subTest(
                snapshot=repr(candidate)[:75]
            ):
                store = contract.MemoryWitnessStore(
                    candidate
                )

                source = self.fixture.make_coordinator(
                    signed_witness_source=store
                )

                with self.assertRaises(ValueError):
                    self.fixture.inspect(source)

                self.assertFalse(store.active)
                self.assertEqual(store.publish_calls, 0)

                self.assertEqual(
                    self.fixture.cas.backend.snapshot[2],
                    OLD_FLOOR,
                )

        self.assert_unchanged()

    def test_root_identity_and_snapshot_substitution_rejected(self):
        correct = self.fixture.cas.public

        invalid = (
            ("foreign_root", correct, OLD_FLOOR),
            (ROOT, b"X" * 32, OLD_FLOOR),
            (ROOT, correct[:-1], OLD_FLOOR),
            (ROOT, bytearray(correct), OLD_FLOOR),
            (ROOT, correct, True),
            (ROOT, correct, -1),
            (ROOT, correct, "12"),
            (ROOT, correct, OLD_FLOOR, "extra"),
        )

        for snapshot in invalid:
            with self.subTest(
                snapshot=repr(snapshot)[:75]
            ):
                backend = cas_contract.MemoryCASBackend(
                    snapshot
                )

                root = self.fixture.cas.adapter(
                    backend=backend
                )

                source = self.fixture.make_coordinator(
                    root_source=root
                )

                with self.assertRaises(ValueError):
                    self.fixture.inspect(source)

                self.assertFalse(backend.active)
                self.assertEqual(
                    self.fixture.store.publish_calls,
                    0,
                )

        self.assert_unchanged()

    def test_tampered_or_foreign_signed_witnesses_rejected(
        self
    ):
        old_message, old_signature = self.old_pair
        new_message, new_signature = self.next_pair

        broken_old = (
            old_message,
            bytes([old_signature[0] ^ 1])
            + old_signature[1:],
        )

        broken_new = (
            new_message,
            bytes([new_signature[0] ^ 1])
            + new_signature[1:],
        )

        attacker = Ed25519PrivateKey.generate()

        foreign_new = self.fixture.binding.witness.signed(
            self.fixture.binding.document(
                witness_revision=NEXT_WITNESS_REVISION,
            ),
            signer=attacker,
        )

        wrong_universe = self.fixture.binding.witness.signed(
            self.fixture.binding.document(
                witness_revision=NEXT_WITNESS_REVISION,
                universe_id="foreign_universe",
            )
        )

        stale_successor = self.fixture.binding.witness.signed(
            self.fixture.binding.document(
                witness_revision=NEXT_FLOOR,
            )
        )

        alternate_message, alternate_signature = (
            self.fixture.binding.witness.signed(
                self.fixture.binding.document(
                    witness_revision=NEXT_WITNESS_REVISION,
                    minimum_generation=0,
                )
            )
        )

        mixed_pair = (
            new_message,
            alternate_signature,
        )

        self.assertNotEqual(
            new_message,
            alternate_message,
        )

        attacks = (
            {"expected_witness": broken_old},
            {"next_witness": broken_new},
            {"next_witness": foreign_new},
            {"next_witness": wrong_universe},
            {"next_witness": stale_successor},
            {"next_witness": mixed_pair},
        )

        for attack in attacks:
            with self.subTest(
                attack=repr(attack)[:85]
            ):
                with self.assertRaises(ValueError):
                    self.fixture.rotate(**attack)

                self.assert_unchanged()

    def test_forged_signature_verification_report_rejected(self):
        with patch.object(
            self.fixture.module,
            "verify_signed_checkpoint_trust_witness",
            return_value=object(),
        ):
            with self.assertRaises(ValueError):
                self.fixture.rotate()

        self.assert_unchanged()

    def test_false_witness_publication_ack_blocks_floor(self):
        store = contract.MemoryWitnessStore(
            self.old_pair,
            fake_ack=True,
        )

        source = self.fixture.make_coordinator(
            signed_witness_source=store
        )

        with self.assertRaises(ValueError):
            self.fixture.rotate(source)

        self.assertEqual(store.publish_calls, 1)
        self.assertEqual(store.snapshot, self.old_pair)

        self.assertEqual(
            self.fixture.cas.backend.snapshot[2],
            OLD_FLOOR,
        )

        self.assertEqual(
            self.fixture.inspect(source).state,
            "ready",
        )

        self.assertFalse(store.active)
        self.assertFalse(self.fixture.cas.backend.active)

    def test_witness_commit_with_wrong_reply_requires_inspection(
        self
    ):
        class WrongReplyStore(contract.MemoryWitnessStore):
            def publish_if_current(self, **kwargs):
                super().publish_if_current(**kwargs)

                return kwargs["expected_witness"]

        store = WrongReplyStore(self.old_pair)

        source = self.fixture.make_coordinator(
            signed_witness_source=store
        )

        with self.assertRaises(ValueError):
            self.fixture.rotate(source)

        self.assertEqual(store.publish_calls, 1)
        self.assertEqual(store.snapshot, self.next_pair)

        self.assertEqual(
            self.fixture.cas.backend.snapshot[2],
            OLD_FLOOR,
        )

        observation = self.fixture.inspect(source)

        self.assertEqual(
            observation.state,
            "witness_published",
        )

        self.fixture.assert_data_only(observation)
        self.assertFalse(store.active)
        self.assertFalse(self.fixture.cas.backend.active)

    def test_floor_commit_with_corrupt_reply_is_ambiguous(
        self
    ):
        class CorruptReplyBackend(cas_contract.MemoryCASBackend):
            def advance_if_current(self, **kwargs):
                actual = super().advance_if_current(
                    **kwargs
                )

                return (
                    actual[0],
                    actual[1],
                    actual[2] + 1,
                )

        backend = CorruptReplyBackend((
            ROOT,
            self.fixture.cas.public,
            OLD_FLOOR,
        ))

        root = self.fixture.cas.adapter(
            backend=backend
        )

        source = self.fixture.make_coordinator(
            root_source=root
        )

        with self.assertRaises(ValueError):
            self.fixture.rotate(source)

        self.assertEqual(
            backend.snapshot[2],
            NEXT_FLOOR,
        )

        self.assertEqual(
            self.fixture.store.snapshot,
            self.next_pair,
        )

        observation = self.fixture.inspect(source)

        self.assertEqual(
            observation.state,
            "observed_advanced",
        )

        self.fixture.assert_data_only(observation)
        self.assertFalse(backend.active)
        self.assertFalse(self.fixture.store.active)

    def test_false_floor_cas_ack_rejected_by_readback(self):
        class FalseAckBackend(cas_contract.MemoryCASBackend):
            def advance_if_current(
                self,
                *,
                expected_revision,
                next_revision,
            ):
                return (
                    self.snapshot[0],
                    self.snapshot[1],
                    next_revision,
                )

        backend = FalseAckBackend((
            ROOT,
            self.fixture.cas.public,
            OLD_FLOOR,
        ))

        root = self.fixture.cas.adapter(
            backend=backend
        )

        source = self.fixture.make_coordinator(
            root_source=root
        )

        with self.assertRaises(ValueError):
            self.fixture.rotate(source)

        self.assertEqual(
            backend.snapshot[2],
            OLD_FLOOR,
        )

        self.assertEqual(
            self.fixture.store.snapshot,
            self.next_pair,
        )

        observation = self.fixture.inspect(source)

        self.assertEqual(
            observation.state,
            "witness_published",
        )

        self.fixture.assert_data_only(observation)
        self.assertFalse(backend.active)
        self.assertFalse(self.fixture.store.active)

    def test_suppressed_outer_root_error_still_fails_closed(
        self
    ):
        class SuppressingRoot:
            def __init__(self, snapshot):
                self.snapshot = snapshot
                self.active = False
                self.events = []

            @contextmanager
            def hold(self):
                self.active = True
                self.events.append("enter")

                try:
                    try:
                        yield self.snapshot
                    except ValueError:
                        self.events.append("suppressed")
                finally:
                    self.active = False
                    self.events.append("exit")

            def advance(
                self,
                *,
                expected_revision,
                next_revision,
            ):
                raise AssertionError(
                    "Root publication must not execute."
                )

        root = SuppressingRoot(
            self.fixture.cas.backend.snapshot
        )

        malformed_store = contract.MemoryWitnessStore(
            (b"", b"invalid")
        )

        source = self.fixture.make_coordinator(
            root_source=root,
            signed_witness_source=malformed_store,
        )

        with self.assertRaises(ValueError):
            self.fixture.inspect(source)

        self.assertFalse(root.active)
        self.assertFalse(malformed_store.active)

        self.assertIn(
            "suppressed",
            root.events,
        )

        self.assertEqual(
            malformed_store.publish_calls,
            0,
        )

        self.assert_unchanged()

    def test_competing_coordinators_only_one_observed_winner(
        self
    ):
        first = self.fixture.make_coordinator()
        second = self.fixture.make_coordinator()

        coordinators = (first, second)

        def attempt(index):
            source = coordinators[index % 2]

            try:
                observation = source.rotate(
                    **self.fixture.arguments()
                )

                self.fixture.assert_data_only(
                    observation
                )

                return observation.state

            except ValueError:
                return "rejected"

        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(
                pool.map(attempt, range(8))
            )

        self.assertEqual(
            outcomes.count("observed_advanced"),
            1,
        )

        self.assertEqual(
            outcomes.count("rejected"),
            7,
        )

        self.assertEqual(
            self.fixture.store.snapshot,
            self.next_pair,
        )

        self.assertEqual(
            self.fixture.cas.backend.snapshot[2],
            NEXT_FLOOR,
        )

        observation = self.fixture.inspect(first)

        self.assertEqual(
            observation.state,
            "observed_advanced",
        )

        self.fixture.assert_data_only(observation)
        self.fixture.assert_released()


if __name__ == "__main__":
    unittest.main()
