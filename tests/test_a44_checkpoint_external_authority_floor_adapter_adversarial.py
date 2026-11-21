"""A44 adversarial external authority held-floor adapter tests.

Tests distinguish signed transport attacks from deliberate
in-process fault injection at the projection boundary.

A patched canonical source is a TEST INSTRUMENT, not an
assertion that arbitrary Python code can be isolated.

No real external service, independent key enrollment,
persistent monotonic storage or remote lease is established.

All authority, enrollment and backend objects are test doubles.
No checkpoint restoration or republication is authorized.
"""

import json
import sys
import unittest

from contextlib import contextmanager
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_external_authority_floor_adapter as contract

from core.existence.history_receipt_trust_checkpoint_external_authority_floor_adapter import (
    ExternalMonotonicAuthorityFloorAdapter,
)

from core.existence.history_receipt_trust_checkpoint_external_monotonic_authority import (
    SignedCheckpointExternalMonotonicAuthoritySource,
)


ROOT = contract.ROOT
EPOCH = contract.EPOCH
OLD = contract.OLD
NEXT = contract.NEXT
GENERATION = contract.GENERATION
FENCE = contract.FENCE


class TupleSubclass(tuple):
    pass


class IntegerSubclass(int):
    pass


class A44CheckpointExternalAuthorityFloorAdapterAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointExternalAuthorityFloorAdapterContractTests(
                "test_signed_six_field_to_four_field_held_projection"
            )
        )

        self.fixture.setUp()

        self.addCleanup(
            self.fixture.doCleanups
        )

        self.source = self.fixture.source
        self.adapter = self.fixture.adapter
        self.authority = self.fixture.authority

        self.backend = self.fixture.fixture.backend
        self.enrollment = self.fixture.fixture.enrollment

        self.root_key = self.fixture.root_key

    def snapshot(self, **changes):
        values = {
            "root_id": ROOT,
            "root_public_key": self.root_key,
            "epoch": EPOCH,
            "revision": OLD,
            "generation": GENERATION,
            "fence_token": FENCE,
        }

        values.update(changes)

        return (
            values["root_id"],
            values["root_public_key"],
            values["epoch"],
            values["revision"],
            values["generation"],
            values["fence_token"],
        )

    def read(self, source=None):
        selected = (
            self.adapter
            if source is None
            else source
        )

        return self.fixture.read(
            selected
        )

    def gate(self, adapter=None):
        return self.fixture.make_gate(
            adapter
        )

    @contextmanager
    def injected_snapshot(
        self,
        snapshot,
        *,
        suppress=False,
        fail_on_exit=False,
    ):
        """Inject faults after the signed-source boundary.

        This deliberately replaces the canonical class's
        hold method for the duration of a unit test.

        The production adapter must still validate the
        resulting snapshot before exposing any projection.
        """

        events = []

        @contextmanager
        def held(source):
            events.append("enter")

            try:
                try:
                    yield snapshot

                except ValueError:
                    events.append("caller-error")

                    if not suppress:
                        raise

            finally:
                events.append("exit")

                if fail_on_exit:
                    raise OSError(
                        "Injected source release failure."
                    )

        with patch.object(
            SignedCheckpointExternalMonotonicAuthoritySource,
            "hold",
            held,
        ):
            yield events

    def assert_rejected_projection(self, snapshot):
        before = self.backend.read_calls

        with self.injected_snapshot(
            snapshot
        ) as events:

            with self.assertRaises(ValueError):
                with self.gate().hold():
                    self.fail(
                        "Invalid snapshot reached caller."
                    )

            self.assertEqual(
                events,
                ["enter", "caller-error", "exit"],
            )

        self.assertEqual(
            self.backend.read_calls,
            before,
        )

        self.fixture.assert_released()

    def test_malformed_snapshot_container_and_arity(
        self
    ):
        valid = self.snapshot()

        invalid = (
            None,
            object(),
            [],
            {},
            (),
            list(valid),
            valid[:4],
            valid[:5],
            (*valid, "extra"),
            TupleSubclass(valid),
        )

        for candidate in invalid:
            with self.subTest(
                candidate=repr(candidate)[:80],
            ):
                self.assert_rejected_projection(
                    candidate
                )

    def test_root_identity_and_key_projection_binding(
        self
    ):
        invalid = (
            self.snapshot(root_id="foreign_root"),
            self.snapshot(root_id=""),
            self.snapshot(root_id=True),
            self.snapshot(root_id=" leading"),
            self.snapshot(root_public_key=b"short"),
            self.snapshot(root_public_key=b"\x00" * 32),
            self.snapshot(
                root_public_key=bytearray(
                    self.root_key
                ),
            ),
            self.snapshot(
                root_public_key=memoryview(
                    self.root_key
                ),
            ),
        )

        for candidate in invalid:
            with self.subTest(
                candidate=repr(candidate)[:80],
            ):
                self.assert_rejected_projection(
                    candidate
                )

    def test_all_counter_types_validated_before_projection(
        self
    ):
        for field in (
            "epoch",
            "revision",
            "generation",
            "fence_token",
        ):
            for value in (
                True,
                False,
                -1,
                "7",
                7.0,
                None,
                IntegerSubclass(100),
            ):
                with self.subTest(
                    field=field,
                    value=repr(value),
                    type=type(value).__name__,
                ):
                    self.assert_rejected_projection(
                        self.snapshot(
                            **{field: value}
                        )
                    )

    def test_discarded_counters_cannot_bypass_minima(
        self
    ):
        invalid = (
            self.snapshot(epoch=EPOCH + 1),
            self.snapshot(revision=OLD - 1),
            self.snapshot(
                revision=NEXT,
                generation=GENERATION - 1,
            ),
            self.snapshot(
                revision=NEXT,
                fence_token=FENCE - 1,
            ),
        )

        for candidate in invalid:
            with self.subTest(
                candidate=repr(candidate)[:100],
            ):
                self.assert_rejected_projection(
                    candidate
                )

        valid = self.snapshot(
            revision=NEXT,
            generation=GENERATION + 1,
            fence_token=FENCE + 1,
        )

        with self.injected_snapshot(
            valid
        ) as events:

            with self.adapter.hold() as projected:
                self.assertEqual(
                    projected,
                    self.fixture.expected_floor(NEXT),
                )

                self.assertEqual(
                    events,
                    ["enter"],
                )

            self.assertEqual(
                events,
                ["enter", "exit"],
            )

    def test_mutated_canonical_source_pins_rejected(
        self
    ):
        mutations = (
            ("authority", None),
            ("expected_authority_id", ""),
            ("expected_authority_public_key", b"short"),
            ("expected_root_id", True),
            ("expected_root_public_key", b"short"),
            ("expected_enrollment_epoch", True),
            ("minimum_revision", -1),
            ("minimum_generation", True),
            ("minimum_fence_token", -1),
        )

        for field, value in mutations:
            with self.subTest(field=field):
                source = self.fixture.make_source()

                adapter = self.fixture.make_adapter(
                    source
                )

                object.__setattr__(
                    source,
                    field,
                    value,
                )

                with self.assertRaises(ValueError):
                    self.read(adapter)

                with self.assertRaises(ValueError):
                    self.read(
                        self.gate(adapter)
                    )

                self.assertEqual(
                    self.authority.read_calls,
                    0,
                )

                self.assertEqual(
                    self.backend.read_calls,
                    0,
                )

        self.fixture.assert_released()

    def test_suppressed_projection_validation_error(
        self
    ):
        invalid = self.snapshot(
            generation=GENERATION - 1,
        )

        yielded = False

        with self.injected_snapshot(
            invalid,
            suppress=True,
        ) as events:

            with self.assertRaises(ValueError):
                with self.adapter.hold():
                    yielded = True

            self.assertEqual(
                events,
                ["enter", "caller-error", "exit"],
            )

        self.assertFalse(yielded)
        self.assertEqual(self.backend.read_calls, 0)

    def test_suppressed_caller_failure_rejected_at_adapter(
        self
    ):
        with self.injected_snapshot(
            self.snapshot(),
            suppress=True,
        ) as events:

            with self.assertRaises(ValueError):
                with self.adapter.hold() as floor:
                    self.assertEqual(
                        floor,
                        self.fixture.expected_floor(),
                    )

                    self.assertEqual(
                        events,
                        ["enter"],
                    )

                    raise ValueError(
                        "Injected caller verification error."
                    )

            self.assertEqual(
                events,
                ["enter", "caller-error", "exit"],
            )

        self.assertEqual(
            self.read(),
            self.fixture.expected_floor(),
        )

    def test_projection_source_release_failure(
        self
    ):
        with self.injected_snapshot(
            self.snapshot(),
            fail_on_exit=True,
        ) as events:

            with self.assertRaises(ValueError):
                with self.adapter.hold() as floor:
                    self.assertEqual(
                        floor,
                        self.fixture.expected_floor(),
                    )

                    self.assertEqual(
                        events,
                        ["enter"],
                    )

            self.assertEqual(
                events,
                ["enter", "exit"],
            )

        self.assertEqual(
            self.read(),
            self.fixture.expected_floor(),
        )

        self.fixture.assert_released()

    def test_validly_signed_stale_counter_claims_rejected(
        self
    ):
        original = self.authority._signed

        attacks = (
            {"revision": OLD - 1},
            {
                "revision": NEXT,
                "generation": GENERATION - 1,
            },
            {
                "revision": NEXT,
                "fence_token": FENCE - 1,
            },
            {"enrollment_epoch": EPOCH + 1},
        )

        for changes in attacks:
            with self.subTest(changes=changes):

                def altered(
                    _changes=changes,
                    **arguments,
                ):
                    message, _ = original(
                        **arguments
                    )

                    document = json.loads(
                        message
                    )

                    document.update(_changes)

                    encoded = (
                        contract.authority_contract.canonical(
                            document
                        )
                    )

                    return (
                        encoded,
                        self.authority.signer.sign(
                            encoded
                        ),
                    )

                with patch.object(
                    self.authority,
                    "_signed",
                    side_effect=altered,
                ):
                    with self.assertRaises(ValueError):
                        with self.gate().hold():
                            self.fail(
                                "Stale signed counter accepted."
                            )

                self.assertEqual(
                    self.backend.read_calls,
                    0,
                )

                self.assertEqual(
                    self.authority.cas_calls,
                    0,
                )

                self.fixture.assert_released()

        self.assertEqual(
            self.read(self.gate()),
            self.fixture.expected_backend(),
        )

    def test_replay_and_unavailable_authority_no_cached_floor(
        self
    ):
        gate = self.gate()

        self.assertEqual(
            self.read(gate),
            self.fixture.expected_backend(),
        )

        original_challenge = (
            self.authority.read_challenges[0]
        )

        self.authority.read_mode = "replay"

        with self.assertRaises(ValueError):
            self.read(gate)

        self.assertNotEqual(
            original_challenge,
            self.authority.read_challenges[1],
        )

        self.assertEqual(
            self.backend.read_calls,
            1,
        )

        self.authority.read_mode = "valid"
        self.authority.read_failure = True

        with self.assertRaises(ValueError):
            self.read(gate)

        self.assertEqual(
            self.backend.read_calls,
            1,
        )

        self.fixture.assert_released()

        self.authority.read_failure = False

        self.assertEqual(
            self.read(gate),
            self.fixture.expected_backend(),
        )

        self.assertEqual(
            self.authority.read_calls,
            4,
        )

        self.assertEqual(
            self.backend.read_calls,
            2,
        )

        self.assertEqual(
            self.authority.cas_calls,
            0,
        )

    def test_backend_failure_releases_entire_held_chain(
        self
    ):
        self.backend.fail_on_read_number = (
            self.backend.read_calls + 1
        )

        gate = self.gate()

        with self.assertRaises(ValueError):
            with gate.hold():
                self.fail(
                    "Failed backend exposed a checkpoint."
                )

        self.assertEqual(
            self.authority.read_calls,
            1,
        )

        self.assertEqual(
            self.backend.read_calls,
            1,
        )

        self.fixture.assert_released()

        self.backend.fail_on_read_number = None

        with gate.hold() as checkpoint:
            self.assertEqual(
                checkpoint,
                self.fixture.expected_backend(),
            )

            self.assertTrue(self.authority.active)
            self.assertTrue(self.enrollment.active)
            self.assertTrue(self.backend.active)

        self.fixture.assert_released()

        self.assertEqual(
            self.authority.cas_calls,
            0,
        )

        self.assertEqual(
            self.backend.cas_calls,
            0,
        )

    def test_frozen_read_only_adapter_and_rollback_boundary(
        self
    ):
        self.assertIs(
            type(self.adapter),
            ExternalMonotonicAuthorityFloorAdapter,
        )

        self.assertEqual(
            tuple(
                field.name
                for field in fields(self.adapter)
            ),
            ("source",),
        )

        self.assertFalse(
            hasattr(self.adapter, "__dict__")
        )

        with self.assertRaises(FrozenInstanceError):
            self.adapter.source = None

        for name in (
            "advance",
            "advance_if_current",
            "restore",
            "republish",
            "authorize",
            "bootstrap",
            "publish",
        ):
            with self.subTest(operation=name):
                self.assertFalse(
                    hasattr(self.adapter, name)
                )

        self.fixture.advance_authority()

        self.assertEqual(
            self.read(),
            self.fixture.expected_floor(NEXT),
        )

        # Simulate complete rollback of the volatile
        # authority itself, not just the checkpoint backend.
        self.authority.revision = OLD
        self.authority.generation = GENERATION
        self.authority.fence_token = FENCE

        # Old caller-supplied minima remain insufficient.
        self.assertEqual(
            self.read(),
            self.fixture.expected_floor(OLD),
        )

        strict_source = self.fixture.make_source(
            minimum_revision=NEXT,
            minimum_generation=GENERATION + 1,
            minimum_fence_token=FENCE + 1,
        )

        strict_adapter = self.fixture.make_adapter(
            strict_source
        )

        with self.assertRaises(ValueError):
            self.read(strict_adapter)

        before = self.backend.read_calls

        with self.assertRaises(ValueError):
            self.read(
                self.gate(strict_adapter)
            )

        self.assertEqual(
            self.backend.read_calls,
            before,
        )

        self.assertEqual(
            self.authority.cas_calls,
            1,
        )

        self.fixture.assert_released()


if __name__ == "__main__":
    unittest.main()
