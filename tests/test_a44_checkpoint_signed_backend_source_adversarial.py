"""A44 adversarial signed checkpoint backend-source tests.

The tests exercise fail-closed signature enforcement,
lease handling, CAS acknowledgement verification,
fresh challenges and post-CAS signed readback.

All storage backends are volatile test doubles.

Passing tests do NOT prove independent key enrollment,
actual external backend execution, durable persistence,
rollback resistance or cross-backend atomicity.

No restore or republication authority is granted.
"""

import sys
import unittest

from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_signed_backend_source as contract
import test_a44_checkpoint_rotation_coordinator as rotation_contract

import core.existence.history_receipt_trust_checkpoint_signed_backend_source as source_module

from core.existence.history_receipt_trust_checkpoint_backend_evidence import (
    CheckpointRootBackendEvidenceVerifier,
)


OLD = contract.OLD
NEXT = contract.NEXT


class A44CheckpointSignedBackendSourceAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointSignedBackendSourceContractTests(
                "test_signed_held_read_keeps_lease"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.backend = self.fixture.backend
        self.source = self.fixture.source

    def make_backend(self, **changes):
        return self.fixture.make_backend(**changes)

    def make_source(self, backend=None, **changes):
        if backend is None:
            backend = self.backend

        return self.fixture.make_source(
            backend=backend,
            **changes,
        )

    def assert_released(self, backend):
        self.assertFalse(backend.active)

    def assert_rejects(self, action):
        with self.assertRaises(ValueError):
            action()

    def test_direct_constructor_rejects_invalid_dependencies(self):
        verifier = self.source.verifier

        invalid = (
            (None, verifier, OLD),
            (object(), verifier, OLD),
            (self.backend, None, OLD),
            (self.backend, object(), OLD),
            (self.backend, verifier, -1),
            (self.backend, verifier, True),
            (self.backend, verifier, "12"),
        )

        for backend, candidate_verifier, floor in invalid:
            with self.subTest(
                backend=type(backend).__name__,
                verifier=type(candidate_verifier).__name__,
                floor=repr(floor),
            ):
                with self.assertRaises(ValueError):
                    self.fixture.source_type(
                        backend=backend,
                        verifier=candidate_verifier,
                        minimum_revision=floor,
                    )

        self.assertEqual(self.backend.read_calls, 0)
        self.assertEqual(self.backend.cas_calls, 0)

    def test_low_level_mutated_source_fields_fail_closed(self):
        source = self.make_source()

        object.__setattr__(
            source,
            "minimum_revision",
            True,
        )

        with self.assertRaises(ValueError):
            with source.hold():
                pass

        self.assertEqual(self.backend.read_calls, 0)

        another = self.make_source()

        object.__setattr__(
            another.verifier,
            "expected_backend_public_key",
            b"invalid",
        )

        with self.assertRaises(ValueError):
            with another.hold():
                pass

        self.assertEqual(self.backend.read_calls, 0)
        self.assert_released(self.backend)

    def test_unsigned_and_tampered_read_responses_rejected(self):
        modes = (
            "legacy",
            "malformed_pair",
            "bad_signature",
            "noncanonical",
            "wrong_operation",
            "wrong_backend",
            "wrong_root",
            "wrong_root_key",
            "wrong_challenge",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                backend = self.make_backend()
                backend.read_mode = mode

                source = self.make_source(backend=backend)

                with self.assertRaises(ValueError):
                    with source.hold():
                        pass

                self.assertEqual(backend.read_calls, 1)
                self.assertEqual(backend.cas_calls, 0)
                self.assert_released(backend)

    def test_signature_verification_occurs_inside_read_lease(self):
        original = (
            CheckpointRootBackendEvidenceVerifier.verify_read
        )

        observations = []

        def guarded_verify(verifier, **kwargs):
            self.assertTrue(self.backend.active)
            observations.append(kwargs["expected_challenge"])

            return original(verifier, **kwargs)

        with patch.object(
            CheckpointRootBackendEvidenceVerifier,
            "verify_read",
            new=guarded_verify,
        ):
            with self.source.hold() as snapshot:
                self.assertEqual(snapshot[2], OLD)
                self.assertTrue(self.backend.active)

        self.assertEqual(len(observations), 1)
        self.assert_released(self.backend)

        with patch.object(
            CheckpointRootBackendEvidenceVerifier,
            "verify_read",
            side_effect=ValueError(
                "Injected cryptographic verification failure"
            ),
        ):
            with self.assertRaises(ValueError):
                with self.source.hold():
                    pass

        self.assertEqual(self.backend.read_calls, 2)
        self.assertEqual(self.backend.cas_calls, 0)
        self.assert_released(self.backend)

    def test_caller_selected_floor_is_not_durable_rollback(self):
        backend = self.make_backend(
            revision=OLD - 1
        )

        weak_source = self.make_source(
            backend=backend,
            minimum_revision=OLD - 1,
        )

        with weak_source.hold() as snapshot:
            self.assertEqual(
                snapshot[2],
                OLD - 1,
            )

        strict_source = self.make_source(
            backend=backend,
            minimum_revision=OLD,
        )

        with self.assertRaises(ValueError):
            with strict_source.hold():
                pass

        self.assertEqual(backend.cas_calls, 0)
        self.assert_released(backend)

        # Both minimum floors are caller-selected.
        # Neither is independently trusted persistent state.

    def test_invalid_cas_arguments_never_contact_backend(self):
        invalid = (
            (True, NEXT),
            (-1, NEXT),
            (OLD - 1, NEXT),
            (OLD, False),
            (OLD, OLD),
            (OLD, OLD - 1),
            ("12", NEXT),
            (OLD, "13"),
            (OLD, 13.0),
            (None, NEXT),
        )

        for previous, target in invalid:
            with self.subTest(
                previous=repr(previous),
                target=repr(target),
            ):
                self.assert_rejects(
                    lambda: self.source.advance(
                        expected_revision=previous,
                        next_revision=target,
                    )
                )

        self.assertEqual(self.backend.read_calls, 0)
        self.assertEqual(self.backend.cas_calls, 0)
        self.assertEqual(self.backend.revision, OLD)
        self.assert_released(self.backend)

    def test_invalid_signed_cas_acknowledgements_fail_closed(
        self
    ):
        modes = (
            "legacy",
            "malformed_pair",
            "bad_signature",
            "noncanonical",
            "wrong_challenge",
            "wrong_predecessor",
            "wrong_operation",
            "wrong_backend",
            "wrong_root",
            "wrong_root_key",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                backend = self.make_backend()
                backend.cas_mode = mode

                source = self.make_source(backend=backend)

                self.assert_rejects(
                    lambda: source.advance(
                        expected_revision=OLD,
                        next_revision=NEXT,
                    )
                )

                self.assertEqual(backend.cas_calls, 1)
                self.assertEqual(backend.read_calls, 0)

                # In the test double, publication happened
                # before the invalid reply was returned.
                self.assertEqual(
                    backend.revision,
                    NEXT,
                )

                self.assert_released(backend)

    def test_validly_signed_false_cas_ack_is_caught_by_readback(
        self
    ):
        backend = self.make_backend()
        backend.fake_ack = True

        source = self.make_source(backend=backend)

        self.assert_rejects(
            lambda: source.advance(
                expected_revision=OLD,
                next_revision=NEXT,
            )
        )

        self.assertEqual(backend.cas_calls, 1)
        self.assertEqual(backend.read_calls, 1)
        self.assertEqual(backend.revision, OLD)

        self.assertNotEqual(
            backend.cas_challenges[0],
            backend.read_challenges[0],
        )

        with source.hold() as snapshot:
            self.assertEqual(snapshot[2], OLD)

        self.assert_released(backend)

    def test_commit_then_transport_failure_is_not_rolled_back(
        self
    ):
        backend = self.make_backend()
        backend.commit_then_fail = True

        source = self.make_source(backend=backend)

        self.assert_rejects(
            lambda: source.advance(
                expected_revision=OLD,
                next_revision=NEXT,
            )
        )

        self.assertEqual(backend.cas_calls, 1)
        self.assertEqual(backend.read_calls, 0)
        self.assertEqual(backend.revision, NEXT)

        # Explicit reinspection is required.
        with source.hold() as snapshot:
            self.assertEqual(snapshot[2], NEXT)

        self.assertEqual(backend.cas_calls, 1)
        self.assert_released(backend)

    def test_corrupted_or_stale_signed_readback_is_rejected(
        self
    ):
        modes = (
            "stale",
            "bad_signature",
            "wrong_challenge",
            "wrong_root",
            "legacy",
            "malformed_pair",
            "noncanonical",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                backend = self.make_backend()
                backend.read_mode_after_cas = mode

                source = self.make_source(backend=backend)

                self.assert_rejects(
                    lambda: source.advance(
                        expected_revision=OLD,
                        next_revision=NEXT,
                    )
                )

                self.assertEqual(backend.cas_calls, 1)
                self.assertEqual(backend.read_calls, 1)
                self.assertEqual(backend.revision, NEXT)
                self.assert_released(backend)

    def test_replayed_or_repeated_challenge_fails_closed(self):
        backend = self.make_backend()
        source = self.make_source(backend=backend)

        with source.hold() as snapshot:
            self.assertEqual(snapshot[2], OLD)

        backend.read_mode_after_cas = "replay"

        self.assert_rejects(
            lambda: source.advance(
                expected_revision=OLD,
                next_revision=NEXT,
            )
        )

        self.assertEqual(backend.cas_calls, 1)
        self.assertEqual(backend.read_calls, 2)
        self.assertEqual(backend.revision, NEXT)

        self.assertNotEqual(
            backend.read_challenges[0],
            backend.read_challenges[1],
        )

        self.assert_released(backend)

        repeated_backend = self.make_backend()
        repeated_source = self.make_source(
            backend=repeated_backend
        )

        # The CAS can commit while the source rejects
        # inability to obtain a distinct readback nonce.
        with patch.object(
            source_module.os,
            "urandom",
            return_value=b"\x07" * 32,
        ):
            self.assert_rejects(
                lambda: repeated_source.advance(
                    expected_revision=OLD,
                    next_revision=NEXT,
                )
            )

        self.assertEqual(repeated_backend.cas_calls, 1)
        self.assertEqual(repeated_backend.read_calls, 0)
        self.assertEqual(repeated_backend.revision, NEXT)
        self.assert_released(repeated_backend)

    def test_rotation_rejects_false_witness_publication(
        self
    ):
        fixture = (
            rotation_contract.A44CheckpointRotationCoordinatorContractTests(
                "test_ready_observation_holds_sources_and_is_data_only"
            )
        )

        fixture.setUp()
        self.addCleanup(fixture.doCleanups)

        backend = self.make_backend(
            root_public=fixture.cas.public,
            revision=rotation_contract.OLD_FLOOR,
        )

        signed_root = self.make_source(
            backend=backend,
            expected_root_public_key=fixture.cas.public,
            minimum_revision=rotation_contract.OLD_FLOOR,
        )

        fixture.store.fake_ack = True

        coordinator = fixture.make_coordinator(
            root_source=signed_root
        )

        before = fixture.inspect(coordinator)

        self.assertEqual(before.state, "ready")
        fixture.assert_data_only(before)

        self.assert_rejects(
            lambda: fixture.rotate(coordinator)
        )

        self.assertEqual(fixture.store.publish_calls, 1)
        self.assertEqual(backend.cas_calls, 0)

        after = fixture.inspect(coordinator)

        self.assertEqual(after.state, "ready")
        fixture.assert_data_only(after)

        self.assertEqual(
            backend.revision,
            rotation_contract.OLD_FLOOR,
        )

        self.assertFalse(fixture.store.active)
        self.assert_released(backend)


if __name__ == "__main__":
    unittest.main()
