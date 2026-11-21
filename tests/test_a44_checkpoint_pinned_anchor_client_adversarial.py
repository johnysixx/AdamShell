"""A44 / 66.24D adversarial signed anchor client tests.

Tests authenticated-data checks and explicit trust-boundary limits.

KNOWN LIMITATIONS:
- Caller-selected replacement pins can trust a forged signer.
- Joint rollback may remain undetected with stale caller floors.
- A signed read is not proof of a genuine remote held lease.
- No independent enrollment or durable monotonic CAS is proven.

All signing keys are disposable and all SQLite files temporary.
"""

import importlib
import shutil
import sys
import unittest

from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_pinned_anchor_client_contract as contract

from core.existence.history_receipt_trust_checkpoint_external_anchor_gate import (
    CheckpointExternalAnchorReadGate,
)


class BrokenHoldProvider:
    def hold(self, *, challenge):
        return 123


class A44PinnedSignedAnchorClientAdversarialTests(unittest.TestCase):

    def setUp(self):
        self.fixture = (
            contract.A44PinnedSignedAnchorClientContractTests(
                "test_01_signed_read_matches_anchor_gate_contract"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.provider = self.fixture.provider
        self.baseline = self.fixture.baseline

    def source(self, **changes):
        return self.fixture.source(**changes)

    def read(self, source=None):
        if source is None:
            source = self.source()

        return self.fixture.read(source)

    def gate(self, *, sqlite_source=None):
        if sqlite_source is None:
            sqlite_source = self.fixture.sqlite_source

        return CheckpointExternalAnchorReadGate.from_sources(
            signed_source=sqlite_source,
            anchor_source=self.source(),
        )

    def test_01_cached_signed_response_replay_rejected(self):
        cache = []

        def replay(message, signature):
            if not cache:
                cache.append((message, signature))
            return cache[0]

        self.provider.response_override = replay

        self.assertEqual(
            self.read(),
            self.baseline,
        )

        with self.assertRaises(ValueError):
            self.read()

        self.assertEqual(
            len(self.provider.challenges),
            2,
        )

        self.assertNotEqual(
            self.provider.challenges[0],
            self.provider.challenges[1],
        )

        self.assertFalse(self.provider.active)

    def test_02_forged_signer_accepted_after_repin(self):
        """KNOWN LIMIT: caller-controlled trust enrollment."""

        rogue = Ed25519PrivateKey.generate()
        self.provider.signer = rogue

        with self.assertRaises(ValueError):
            self.read()

        rogue_public = contract.raw_public_key(
            rogue
        )

        accepted = self.read(
            self.source(
                expected_anchor_public_key=rogue_public
            )
        )

        self.assertEqual(
            accepted,
            self.baseline,
        )

        self.assertFalse(self.provider.active)

    def test_03_joint_signed_anchor_and_sqlite_rollback(self):
        """KNOWN LIMIT: signed responses do not prove high-water."""

        sqlite_fixture = self.fixture.fixture

        old_copy = (
            Path(sqlite_fixture.folder.name)
            / "old-signed-anchor-db.sqlite3"
        )

        shutil.copyfile(
            sqlite_fixture.path,
            old_copy,
        )

        published = sqlite_fixture.advance(
            self.fixture.sqlite_source
        )

        advanced_anchor = (
            self.baseline[:5] + published[3:]
        )

        self.provider.snapshot = advanced_anchor

        with self.gate().hold() as advanced:
            self.assertEqual(
                advanced[3:],
                published[3:],
            )

        shutil.copyfile(
            old_copy,
            sqlite_fixture.path,
        )

        self.provider.snapshot = self.baseline

        reopened = sqlite_fixture.client(
            sqlite_fixture.reopen()
        )

        with self.gate(
            sqlite_source=reopened
        ).hold() as reverted:
            self.assertEqual(
                reverted,
                sqlite_fixture.expected(),
            )

        self.assertNotEqual(
            reverted[3:],
            published[3:],
        )

        self.assertFalse(self.provider.active)

    def test_04_stale_anchor_rejected_by_gate(self):
        self.fixture.fixture.advance(
            self.fixture.sqlite_source
        )

        with self.assertRaises(ValueError):
            with self.gate().hold():
                pass

        self.assertFalse(self.provider.active)

    def test_05_anchor_ahead_of_sqlite_rejected(self):
        updated = self.baseline[:5] + (
            self.baseline[5] + 1,
            self.baseline[6] + 1,
            self.baseline[7] + 1,
        )

        self.provider.snapshot = updated

        with self.assertRaises(ValueError):
            with self.gate().hold():
                pass

        self.assertFalse(self.provider.active)

    def test_06_higher_caller_floors_reject_stale_state(self):
        attacks = (
            {"minimum_revision": self.baseline[5] + 1},
            {"minimum_generation": self.baseline[6] + 1},
            {"minimum_fence_token": self.baseline[7] + 1},
        )

        for changes in attacks:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.read(
                        self.source(**changes)
                    )

                self.assertFalse(self.provider.active)

    def test_07_modified_signature_rejected(self):
        def corrupt(message, signature):
            changed = (
                signature[:-1]
                + bytes((signature[-1] ^ 1,))
            )

            return message, changed

        self.provider.response_override = corrupt

        with self.assertRaises(ValueError):
            self.read()

        self.assertFalse(self.provider.active)

    def test_08_resigned_trailing_whitespace_rejected(self):
        def corrupt(message, signature):
            changed = message + b" "

            return (
                changed,
                self.fixture.anchor_signer.sign(changed),
            )

        self.provider.response_override = corrupt

        with self.assertRaises(ValueError):
            self.read()

        self.assertFalse(self.provider.active)

    def test_09_resigned_duplicate_json_key_rejected(self):
        def corrupt(message, signature):
            changed = (
                b'{"version":1,'
                + message[1:]
            )

            return (
                changed,
                self.fixture.anchor_signer.sign(changed),
            )

        self.provider.response_override = corrupt

        with self.assertRaises(ValueError):
            self.read()

        self.assertFalse(self.provider.active)

    def test_10_resigned_unicode_escape_rejected(self):
        def corrupt(message, signature):
            original = b'"operation":"read"'
            replacement = b'"operation":"\\u0072ead"'

            if message.count(original) != 1:
                raise AssertionError(
                    "Canonical operation field unavailable."
                )

            changed = message.replace(
                original,
                replacement,
                1,
            )

            return (
                changed,
                self.fixture.anchor_signer.sign(changed),
            )

        self.provider.response_override = corrupt

        with self.assertRaises(ValueError):
            self.read()

        self.assertFalse(self.provider.active)

    def test_11_malformed_signed_hex_fields_rejected(self):
        attacks = (
            ("authority_public_key_hex", "A" * 63),
            ("authority_public_key_hex", "Z" * 64),
            ("root_public_key_hex", "F" * 64),
            ("challenge_hex", "0" * 64),
        )

        for field, value in attacks:
            with self.subTest(field=field):
                self.provider.fields = {
                    field: value
                }

                with self.assertRaises(ValueError):
                    self.read()

                self.assertFalse(self.provider.active)

        self.provider.fields = {}

    def test_12_malformed_signed_pairs_rejected(self):
        attacks = (
            lambda m, s: [m, s],
            lambda m, s: (m, s, b"extra"),
            lambda m, s: (b"x" * 4097, s),
            lambda m, s: (m, s[:63]),
            lambda m, s: None,
        )

        for transform in attacks:
            with self.subTest(transform=repr(transform)):
                self.provider.response_override = transform

                with self.assertRaises(ValueError):
                    self.read()

                self.assertFalse(self.provider.active)

        self.provider.response_override = None

    def test_13_suppressed_verification_error_rejected(self):
        self.provider.suppress_errors = True

        self.provider.fields = {
            "root_id": "forged-root"
        }

        with self.assertRaises(ValueError):
            self.read()

        self.assertTrue(
            self.provider.suppressed
        )

        self.assertFalse(
            self.provider.active
        )

    def test_14_provider_exit_failure_rejected(self):
        self.provider.exit_error = RuntimeError(
            "Simulated anchor lease release failure."
        )

        with self.assertRaises(ValueError):
            with self.source().hold() as snapshot:
                self.assertEqual(
                    snapshot,
                    self.baseline,
                )

        self.assertFalse(
            self.provider.active
        )

    def test_15_invalid_provider_context_rejected(self):
        source = self.source(
            provider=BrokenHoldProvider()
        )

        with self.assertRaises(ValueError):
            self.read(source)

    def test_16_mutated_frozen_pin_revalidated(self):
        source = self.source()

        object.__setattr__(
            source,
            "expected_root_public_key",
            b"short",
        )

        with self.assertRaises(ValueError):
            self.read(source)

        self.assertEqual(
            self.provider.challenges,
            [],
        )

    def test_17_invalid_random_challenge_rejected(self):
        client_module = importlib.import_module(
            contract.MODULE
        )

        with patch.object(
            client_module.os,
            "urandom",
            return_value=b"short",
        ):
            with self.assertRaises(ValueError):
                self.read()

        self.assertEqual(
            self.provider.challenges,
            [],
        )

    def test_18_fake_held_lease_cannot_prove_stability(self):
        """KNOWN LIMIT: Python context alone is not a remote lease."""

        updated = self.baseline[:5] + (
            self.baseline[5] + 1,
            self.baseline[6] + 1,
            self.baseline[7] + 1,
        )

        with self.source().hold() as snapshot:
            self.assertTrue(self.provider.active)

            self.provider.snapshot = updated

            self.assertEqual(
                snapshot,
                self.baseline,
            )

            self.assertNotEqual(
                snapshot,
                self.provider.snapshot,
            )

        self.assertFalse(self.provider.active)


if __name__ == "__main__":
    unittest.main()
