"""A44 experimental trusted root bootstrap contracts.

A trust source must provide an externally authenticated
root identity, raw Ed25519 public key and epoch floor
under one held read operation.

The hold() interface does not prove that a source is
independent, durable, authenticated or rollback-resistant.
A malicious caller-controlled source can still lie.

No production signing keys, real trust enrollment or
persistent authority state are created by these tests.
"""

from contextlib import contextmanager
from unittest.mock import patch

import importlib
import json
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from core.existence.history_receipt_trust_key_provisioning import (
    VerifiedAuthorityKeyCatalog,
)

from test_a44_signed_authority_key_manifest import (
    AUTHORITY,
    ROOT_ID,
    entry,
    manifest_bytes,
    raw_public,
    signed_authority_reply,
)


def api():
    return importlib.import_module(
        "core.existence."
        "history_receipt_trust_root_bootstrap"
    )


class MemoryTrustSource:
    """Untrusted testing substitute, never a security backend."""

    def __init__(self, snapshot, *, failure=None):
        self.snapshot = snapshot
        self.failure = failure
        self.active = False
        self.events = []

    @contextmanager
    def hold(self):
        self.events.append("enter")

        if self.failure is not None:
            raise self.failure

        self.active = True

        try:
            yield self.snapshot
        finally:
            self.active = False
            self.events.append("exit")


def snapshot(root, *, root_id=ROOT_ID, floor=0):
    return (
        root_id,
        raw_public(root),
        floor,
    )


def signed_manifest(root, authority, *, epoch=1):
    message = manifest_bytes(
        [entry(AUTHORITY, raw_public(authority))],
        epoch=epoch,
    )

    return message, root.sign(message)


def bootstrap(source, message, signature):
    return api().bootstrap_signed_authority_key_catalog(
        message,
        signature,
        trusted_source=source,
    )


class A44TrustedRootBootstrapTests(unittest.TestCase):

    def test_valid_bootstrap_uses_locked_root_snapshot(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        source = MemoryTrustSource(snapshot(root))

        catalog = bootstrap(
            source,
            message,
            signature,
        )

        self.assertIs(
            type(catalog),
            VerifiedAuthorityKeyCatalog,
        )

        self.assertEqual(catalog.root_id, ROOT_ID)
        self.assertEqual(catalog.epoch, 1)

        self.assertEqual(
            catalog.pinned_keys,
            ((AUTHORITY, raw_public(authority)),),
        )

        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )

        self.assertIs(source.active, False)

        _, reply = signed_authority_reply(authority)

        self.assertIs(
            catalog.make_verifier().verify_attestation(
                reply
            ),
            True,
        )

    def test_missing_or_unusable_trusted_source_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        class MissingHold:
            pass

        class NonCallableHold:
            hold = None

        class InvalidContextManager:
            def hold(self):
                return ("not", "a", "context-manager")

        invalid = (
            None,
            object(),
            {},
            MissingHold(),
            NonCallableHold(),
            InvalidContextManager(),
        )

        for source in invalid:
            with self.subTest(source=repr(source)):
                with self.assertRaises(ValueError):
                    bootstrap(
                        source,
                        message,
                        signature,
                    )

    def test_malformed_trust_snapshot_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        key = raw_public(root)

        invalid = (
            None,
            {},
            [],
            (),
            (ROOT_ID, key),
            (ROOT_ID, key, 0, "extra"),
            [ROOT_ID, key, 0],
            {"root_id": ROOT_ID, "key": key},
            "not-a-snapshot",
        )

        for witness in invalid:
            with self.subTest(witness=repr(witness)):
                source = MemoryTrustSource(witness)

                with self.assertRaises(ValueError):
                    bootstrap(
                        source,
                        message,
                        signature,
                    )

                self.assertIs(source.active, False)

    def test_malformed_root_identity_and_key_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        key = raw_public(root)

        invalid_identities = (
            None,
            "",
            " padded ",
            "bad" + chr(10) + "root",
            "x" * 257,
            123,
        )

        for root_id in invalid_identities:
            with self.subTest(root_id=repr(root_id)):
                source = MemoryTrustSource((
                    root_id,
                    key,
                    0,
                ))

                with self.assertRaises(ValueError):
                    bootstrap(
                        source,
                        message,
                        signature,
                    )

        invalid_keys = (
            None,
            b"",
            bytes(31),
            bytes(33),
            bytearray(key),
            memoryview(key),
            key.hex(),
        )

        for candidate in invalid_keys:
            with self.subTest(key=repr(candidate)):
                source = MemoryTrustSource((
                    ROOT_ID,
                    candidate,
                    0,
                ))

                with self.assertRaises(ValueError):
                    bootstrap(
                        source,
                        message,
                        signature,
                    )

    def test_unapproved_root_and_mismatched_identity_rejected(self):
        root = Ed25519PrivateKey.generate()
        another_root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        invalid_sources = (
            MemoryTrustSource(snapshot(another_root)),
            MemoryTrustSource(snapshot(
                root,
                root_id="different-root",
            )),
        )

        for source in invalid_sources:
            with self.subTest(
                witness=repr(source.snapshot)
            ):
                with self.assertRaises(ValueError):
                    bootstrap(
                        source,
                        message,
                        signature,
                    )

    def test_signed_manifest_tampering_and_wrong_signature_rejected(self):
        root = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        changed = manifest_bytes([
            entry(AUTHORITY, raw_public(attacker))
        ])

        source = MemoryTrustSource(snapshot(root))

        with self.assertRaises(ValueError):
            bootstrap(
                source,
                changed,
                signature,
            )

        with self.assertRaises(ValueError):
            bootstrap(
                source,
                message,
                attacker.sign(message),
            )

        catalog = bootstrap(
            source,
            message,
            signature,
        )

        self.assertEqual(catalog.epoch, 1)

    def test_epoch_floor_is_exclusive_and_strict(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
            epoch=3,
        )

        accepted = bootstrap(
            MemoryTrustSource(snapshot(
                root,
                floor=2,
            )),
            message,
            signature,
        )

        self.assertEqual(accepted.epoch, 3)

        for floor in (
            3, 4, True, -1, 2.5, "2", None,
        ):
            with self.subTest(floor=repr(floor)):
                source = MemoryTrustSource(snapshot(
                    root,
                    floor=floor,
                ))

                with self.assertRaises(ValueError):
                    bootstrap(
                        source,
                        message,
                        signature,
                    )

    def test_trust_lease_spans_cryptographic_validation(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        source = MemoryTrustSource(snapshot(root))

        original = (
            VerifiedAuthorityKeyCatalog
            .from_signed_manifest
        )

        observations = []

        def checked_verification(*args, **kwargs):
            observations.append(source.active)

            self.assertIs(source.active, True)

            return original(*args, **kwargs)

        with patch.object(
            VerifiedAuthorityKeyCatalog,
            "from_signed_manifest",
            side_effect=checked_verification,
        ) as verification:
            catalog = bootstrap(
                source,
                message,
                signature,
            )

        self.assertEqual(catalog.epoch, 1)
        self.assertEqual(verification.call_count, 1)
        self.assertEqual(observations, [True])

        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )

        self.assertIs(source.active, False)

    def test_backend_failures_fail_closed(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        for failure in (
            OSError("trust source unavailable"),
            RuntimeError("trust backend failed"),
        ):
            with self.subTest(failure=repr(failure)):
                source = MemoryTrustSource(
                    snapshot(root),
                    failure=failure,
                )

                with self.assertRaises(ValueError):
                    bootstrap(
                        source,
                        message,
                        signature,
                    )

                self.assertIs(source.active, False)

    def test_lease_released_after_signature_failure(self):
        root = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, _ = signed_manifest(
            root,
            authority,
        )

        source = MemoryTrustSource(snapshot(root))

        with self.assertRaises(ValueError):
            bootstrap(
                source,
                message,
                attacker.sign(message),
            )

        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )

        self.assertIs(source.active, False)

    def test_noncanonical_signed_manifest_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, _ = signed_manifest(
            root,
            authority,
        )

        pretty_message = json.dumps(
            json.loads(message),
            indent=2,
            sort_keys=True,
        ).encode("ascii")

        source = MemoryTrustSource(snapshot(root))

        with self.assertRaises(ValueError):
            bootstrap(
                source,
                pretty_message,
                root.sign(pretty_message),
            )

        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )

    def test_attacker_controlled_source_remains_untrusted(self):
        approved_root = Ed25519PrivateKey.generate()
        attacker_root = Ed25519PrivateKey.generate()
        attacker_authority = Ed25519PrivateKey.generate()

        malicious_message, malicious_signature = (
            signed_manifest(
                attacker_root,
                attacker_authority,
            )
        )

        with self.assertRaises(ValueError):
            bootstrap(
                MemoryTrustSource(
                    snapshot(approved_root)
                ),
                malicious_message,
                malicious_signature,
            )

        # A malicious source can substitute its own
        # root key and epoch. The adapter cannot detect
        # that the source itself is untrusted.
        attacker_source = MemoryTrustSource(
            snapshot(attacker_root)
        )

        attacker_catalog = bootstrap(
            attacker_source,
            malicious_message,
            malicious_signature,
        )

        _, forged_reply = signed_authority_reply(
            attacker_authority
        )

        self.assertIs(
            attacker_catalog.make_verifier().verify_attestation(
                forged_reply
            ),
            True,
        )

        # This is a documented security gap, not a
        # successful production authorization design.


if __name__ == "__main__":
    unittest.main()
