"""A44 adversarial split checkpoint source binding tests.

Ten control tests verify existing behavior.

Two intentionally failing tests detect a nested context-manager
failure: generation provider __exit__ raises ValueError after
a successful verification and the outer key provider suppresses
that error.

A completion flag set BEFORE both providers exit can incorrectly
represent the combined lease as successful.

No independent trust, monotonic persistence, historical
publication, or restore authorization is claimed.
"""

import sys
import unittest

from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_checkpoint_source_binding as contract


AUTHORITY = contract.AUTHORITY
GENERATION = contract.GENERATION


class MaskingKeyProvider:
    """Key source suppressing a nested ValueError on exit."""

    def __init__(self, public_key):
        self.snapshot = (AUTHORITY, public_key)
        self.active = False
        self.events = []

    @contextmanager
    def hold(self):
        self.events.append("enter")
        self.active = True

        try:
            yield self.snapshot
        except ValueError:
            self.events.append("suppressed")
        finally:
            self.active = False
            self.events.append("exit")


class FailingGenerationExit:
    """Generation lease fails during release."""

    def __init__(self):
        self.snapshot = (AUTHORITY, GENERATION - 1)
        self.active = False
        self.events = []

    @contextmanager
    def hold(self):
        self.events.append("enter")
        self.active = True

        try:
            yield self.snapshot
        finally:
            self.active = False
            self.events.append("exit-error")
            raise ValueError(
                "Injected generation lease release failure."
            )


class A44CheckpointSourceBindingAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.harness = (
            contract.A44CheckpointSourceBindingContractTests(
                "test_matching_dual_lease_snapshot"
            )
        )

        self.harness.setUp()
        self.addCleanup(self.harness.doCleanups)

    def assert_released(self, key_source, generation_source):
        self.assertFalse(key_source.active)
        self.assertFalse(generation_source.active)

    def test_normal_dual_source_verification_data_only(self):
        result = self.harness.verify()

        self.assertTrue(result.signature_verified)
        self.assertEqual(result.generation, GENERATION)

        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assert_released(
            self.harness.key_source,
            self.harness.generation_source,
        )

    def test_key_provider_enter_failure_rejected(self):
        key = contract.HeldSource(
            (AUTHORITY, self.harness.fixture.public),
            fail_enter=OSError("Injected key source failure"),
        )

        source = self.harness.make_source(
            key_source=key
        )

        with self.assertRaises(ValueError):
            self.harness.verify(source)

        self.assert_released(
            key,
            self.harness.generation_source,
        )

    def test_generation_provider_enter_failure_releases_key(self):
        generation = contract.HeldSource(
            (AUTHORITY, GENERATION - 1),
            fail_enter=OSError(
                "Injected generation source enter failure"
            ),
        )

        source = self.harness.make_source(
            generation_source=generation
        )

        with self.assertRaises(ValueError):
            self.harness.verify(source)

        self.assert_released(
            self.harness.key_source,
            generation,
        )

        self.assertEqual(
            self.harness.key_source.events,
            ["enter", "exit"],
        )

    def test_key_provider_exit_failure_rejected(self):
        key = contract.HeldSource(
            (AUTHORITY, self.harness.fixture.public),
            fail_exit=OSError(
                "Injected key source exit failure"
            ),
        )

        source = self.harness.make_source(
            key_source=key
        )

        with self.assertRaises(ValueError):
            self.harness.verify(source)

        self.assert_released(
            key,
            self.harness.generation_source,
        )

    def test_unmasked_generation_exit_failure_rejected(self):
        generation = FailingGenerationExit()

        source = self.harness.make_source(
            generation_source=generation
        )

        with self.assertRaises(ValueError):
            self.harness.verify(source)

        self.assert_released(
            self.harness.key_source,
            generation,
        )

    def test_key_tuple_subclass_rejected(self):
        class TupleSubclass(tuple):
            pass

        key = contract.HeldSource(
            TupleSubclass(
                (AUTHORITY, self.harness.fixture.public)
            )
        )

        with self.assertRaises(ValueError):
            self.harness.verify(
                self.harness.make_source(key_source=key)
            )

        self.assert_released(
            key,
            self.harness.generation_source,
        )

    def test_generation_tuple_subclass_rejected(self):
        class TupleSubclass(tuple):
            pass

        generation = contract.HeldSource(
            TupleSubclass(
                (AUTHORITY, GENERATION - 1)
            )
        )

        with self.assertRaises(ValueError):
            self.harness.verify(
                self.harness.make_source(
                    generation_source=generation
                )
            )

        self.assert_released(
            self.harness.key_source,
            generation,
        )

    def test_foreign_authority_in_either_source_rejected(self):
        key = contract.HeldSource(
            ("foreign_authority", self.harness.fixture.public)
        )

        with self.assertRaises(ValueError):
            self.harness.verify(
                self.harness.make_source(key_source=key)
            )

        generation = contract.HeldSource(
            ("foreign_authority", GENERATION - 1)
        )

        with self.assertRaises(ValueError):
            self.harness.verify(
                self.harness.make_source(
                    generation_source=generation
                )
            )

        self.assert_released(key, generation)

    def test_attacker_selected_key_is_not_independent_trust(self):
        attacker = Ed25519PrivateKey.generate()

        message, _ = self.harness.fixture.signed()
        attacker_signature = attacker.sign(message)

        with self.assertRaises(ValueError):
            self.harness.verify(
                message=message,
                signature=attacker_signature,
            )

        attacker_key_source = contract.HeldSource(
            (AUTHORITY, contract.public_key(attacker))
        )

        source = self.harness.make_source(
            key_source=attacker_key_source
        )

        result = self.harness.verify(
            source,
            message=message,
            signature=attacker_signature,
        )

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assert_released(
            attacker_key_source,
            self.harness.generation_source,
        )

    def test_untrusted_generation_rollback_remains_possible(self):
        source = self.harness.make_source()

        self.harness.generation_source.replace(
            (AUTHORITY, GENERATION)
        )

        with self.assertRaises(ValueError):
            self.harness.verify(source)

        self.harness.generation_source.replace(
            (AUTHORITY, 0)
        )

        result = self.harness.verify(source)

        self.assertTrue(result.signature_verified)
        self.assertEqual(result.generation, GENERATION)
        self.assertFalse(result.is_authoritative)

    def test_masked_generation_exit_must_fail_direct_lease(self):
        key = MaskingKeyProvider(
            self.harness.fixture.public
        )
        generation = FailingGenerationExit()

        source = self.harness.make_source(
            key_source=key,
            generation_source=generation,
        )

        # EXPECTED RED:
        # The generation lease fails to close.
        # The outer key provider suppresses that failure.
        # A completed=True flag set before both releases
        # cannot prove that teardown succeeded.
        with self.assertRaises(ValueError):
            with source.hold() as witness:
                self.assertEqual(
                    witness,
                    (
                        AUTHORITY,
                        self.harness.fixture.public,
                        GENERATION - 1,
                    ),
                )
                self.assertTrue(key.active)
                self.assertTrue(generation.active)

    def test_masked_generation_exit_must_fail_verification(self):
        key = MaskingKeyProvider(
            self.harness.fixture.public
        )
        generation = FailingGenerationExit()

        source = self.harness.make_source(
            key_source=key,
            generation_source=generation,
        )

        # EXPECTED RED:
        # A cryptographically valid result cannot be
        # returned if a required held provider failed
        # during nested lease teardown.
        with self.assertRaises(ValueError):
            self.harness.verify(source)


if __name__ == "__main__":
    unittest.main()
