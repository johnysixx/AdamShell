"""A44 signed external monotonic checkpoint authority contract.

EXPECTED RED: production verification source is absent.

Proposed client API:

    SignedCheckpointExternalMonotonicAuthoritySource.from_authority(
        authority=object,
        expected_authority_id=str,
        expected_authority_public_key=bytes,
        expected_root_id=str,
        expected_root_public_key=bytes,
        expected_enrollment_epoch=int,
        minimum_revision=int,
        minimum_generation=int,
        minimum_fence_token=int,
    )

    source.hold() -> held six-field tuple:
        (root_id, root_public_key, enrollment_epoch,
         revision, generation, fence_token)

    source.advance_if_current(
        expected_revision=int,
        next_revision=int,
        expected_generation=int,
        expected_fence_token=int,
    ) -> verified six-field resulting tuple

Injected authority protocol:

    authority.hold(challenge=bytes)
        -> context manager yielding (message, signature)

    authority.advance_if_current(
        expected_revision=int,
        next_revision=int,
        expected_generation=int,
        expected_fence_token=int,
        challenge=bytes,
    ) -> (message, signature)

Messages are strictly canonical ASCII JSON, Ed25519 signed,
domain separated and contain:

    domain, version, operation, authority_id,
    root_id, root_public_key_hex, enrollment_epoch,
    revision, generation, fence_token, challenge_hex

CAS also contains:

    expected_revision, next_revision,
    expected_generation, expected_fence_token

The client's pinned authority key is supplied externally.

SECURITY LIMITATIONS:

- These tests use a volatile authority TEST DOUBLE.
- Client-side pinning is NOT independent key enrollment.
- Signed acknowledgements cannot prove honest execution.
- No real remote service or isolated authority is supplied.
- No independently durable generation/fencing floor exists.
- Caller-provided minimum values can be rolled back.
- No cross-system atomicity or hardware durability.
- No checkpoint restoration or republication authorization.

The final test intentionally demonstrates that a malicious
signing authority may claim a CAS and readback it never
actually persisted. This is a documented trust boundary,
not a cryptographic verification failure.
"""

import importlib
import json
import os
import unittest

from contextlib import contextmanager

from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_external_monotonic_authority"
)

DOMAIN = "AdamShell/A44/checkpoint-monotonic-authority/v1"

AUTHORITY_ID = "checkpoint_external_authority_a44"
ROOT = "checkpoint_root_a44"
ROOT_KEY = bytes(range(32))

EPOCH = 2
OLD = 40
NEXT = 41
GENERATION = 7
FENCE = 11


def public_bytes(private):
    return private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def canonical(document):
    return json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


class SignedMemoryMonotonicAuthority:
    """Volatile signed test double, NOT an external trust anchor."""

    def __init__(self, signer):
        self.signer = signer

        self.revision = OLD
        self.generation = GENERATION
        self.fence_token = FENCE

        self.read_mode = "valid"
        self.read_failure = False
        self.suppress_caller_error = False

        self.fake_ack = False
        self.lie_readback = False
        self.commit_then_fail = False

        self.claimed = None
        self.last_read_pair = None

        self.active = False

        self.read_calls = 0
        self.cas_calls = 0

        self.read_challenges = []
        self.cas_challenges = []

    def _signed(
        self,
        *,
        operation,
        challenge,
        revision,
        generation,
        fence_token,
        mode="valid",
        expected_revision=None,
        next_revision=None,
        expected_generation=None,
        expected_fence_token=None,
    ):
        document = {
            "domain": DOMAIN,
            "version": 1,
            "operation": operation,
            "authority_id": AUTHORITY_ID,
            "root_id": ROOT,
            "root_public_key_hex": ROOT_KEY.hex(),
            "enrollment_epoch": EPOCH,
            "revision": revision,
            "generation": generation,
            "fence_token": fence_token,
            "challenge_hex": challenge.hex(),
        }

        if operation == "cas":
            document.update({
                "expected_revision": expected_revision,
                "next_revision": next_revision,
                "expected_generation": expected_generation,
                "expected_fence_token": expected_fence_token,
            })

        if mode == "malformed_pair":
            return (b"incomplete",)

        if mode == "wrong_authority":
            document["authority_id"] = "rogue_authority"

        if mode == "wrong_root":
            document["root_id"] = "rogue_root"

        if mode == "wrong_root_key":
            document["root_public_key_hex"] = "42" * 32

        if mode == "wrong_epoch":
            document["enrollment_epoch"] = EPOCH + 1

        if mode == "wrong_challenge":
            document["challenge_hex"] = "ff" * 32

        if mode == "wrong_domain":
            document["domain"] = "unrelated_protocol"

        if mode == "extra_field":
            document["unrecognized"] = "unexpected"

        if mode == "bad_revision":
            document["revision"] = True

        if mode == "bad_generation":
            document["generation"] = True

        if mode == "bad_fence":
            document["fence_token"] = True

        message = canonical(document)

        if mode == "noncanonical":
            message += b"\n"

        signature = self.signer.sign(message)

        if mode == "bad_signature":
            signature = (
                bytes([signature[0] ^ 1])
                + signature[1:]
            )

        return message, signature

    @contextmanager
    def hold(self, *, challenge):
        self.read_calls += 1
        self.read_challenges.append(challenge)

        self.active = True

        try:
            if self.read_failure:
                raise OSError(
                    "Injected external read transport failure."
                )

            if (
                self.read_mode == "replay"
                and self.last_read_pair is not None
            ):
                reply = self.last_read_pair

            else:
                if (
                    self.fake_ack
                    and self.lie_readback
                    and self.claimed is not None
                ):
                    revision, generation, fence = self.claimed

                else:
                    revision = self.revision
                    generation = self.generation
                    fence = self.fence_token

                reply = self._signed(
                    operation="read",
                    challenge=challenge,
                    revision=revision,
                    generation=generation,
                    fence_token=fence,
                    mode=self.read_mode,
                )

                self.last_read_pair = reply

            try:
                yield reply

            except ValueError:
                if not self.suppress_caller_error:
                    raise

        finally:
            self.active = False

    def advance_if_current(
        self,
        *,
        expected_revision,
        next_revision,
        expected_generation,
        expected_fence_token,
        challenge,
    ):
        self.cas_calls += 1
        self.cas_challenges.append(challenge)

        if (
            type(expected_revision) is not int
            or type(next_revision) is not int
            or type(expected_generation) is not int
            or type(expected_fence_token) is not int
            or expected_revision != self.revision
            or expected_generation != self.generation
            or expected_fence_token != self.fence_token
            or next_revision <= expected_revision
        ):
            raise ValueError(
                "Test authority stale or invalid CAS."
            )

        claimed = (
            next_revision,
            self.generation + 1,
            self.fence_token + 1,
        )

        if not self.fake_ack:
            (
                self.revision,
                self.generation,
                self.fence_token,
            ) = claimed

        self.claimed = claimed

        if self.commit_then_fail:
            raise OSError(
                "Injected failure after authority CAS."
            )

        return self._signed(
            operation="cas",
            challenge=challenge,
            revision=claimed[0],
            generation=claimed[1],
            fence_token=claimed[2],
            expected_revision=expected_revision,
            next_revision=next_revision,
            expected_generation=expected_generation,
            expected_fence_token=expected_fence_token,
        )


class A44CheckpointExternalMonotonicAuthorityContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.source_type = (
            module.SignedCheckpointExternalMonotonicAuthoritySource
        )

        self.private = Ed25519PrivateKey.generate()
        self.public = public_bytes(self.private)

        self.authority = SignedMemoryMonotonicAuthority(
            self.private
        )

        self.source = self.make_source()

    def make_source(self, **changes):
        arguments = {
            "authority": self.authority,
            "expected_authority_id": AUTHORITY_ID,
            "expected_authority_public_key": self.public,
            "expected_root_id": ROOT,
            "expected_root_public_key": ROOT_KEY,
            "expected_enrollment_epoch": EPOCH,
            "minimum_revision": OLD,
            "minimum_generation": GENERATION,
            "minimum_fence_token": FENCE,
        }

        arguments.update(changes)

        return self.source_type.from_authority(
            **arguments
        )

    def expected(
        self,
        *,
        revision=OLD,
        generation=GENERATION,
        fence_token=FENCE,
    ):
        return (
            ROOT,
            ROOT_KEY,
            EPOCH,
            revision,
            generation,
            fence_token,
        )

    @staticmethod
    def read(source):
        with source.hold() as snapshot:
            return snapshot

    @staticmethod
    def advance(source, **changes):
        arguments = {
            "expected_revision": OLD,
            "next_revision": NEXT,
            "expected_generation": GENERATION,
            "expected_fence_token": FENCE,
        }

        arguments.update(changes)

        return source.advance_if_current(
            **arguments
        )

    def test_signed_held_read_and_six_field_snapshot(self):
        with self.source.hold() as snapshot:
            self.assertEqual(
                snapshot,
                self.expected(),
            )

            self.assertTrue(
                self.authority.active
            )

            self.assertIs(type(snapshot), tuple)
            self.assertIs(type(snapshot[1]), bytes)

            for index in (2, 3, 4, 5):
                self.assertIs(type(snapshot[index]), int)

        self.assertFalse(self.authority.active)

        self.assertEqual(self.authority.read_calls, 1)
        self.assertEqual(self.authority.cas_calls, 0)

        challenge = self.authority.read_challenges[0]

        self.assertIs(type(challenge), bytes)
        self.assertEqual(len(challenge), 32)

    def test_invalid_pins_and_authority_capabilities_rejected(
        self
    ):
        invalid = (
            {"authority": None},
            {"authority": object()},
            {"expected_authority_id": ""},
            {"expected_authority_id": True},
            {"expected_authority_id": " rogue"},
            {"expected_authority_public_key": b"short"},
            {"expected_authority_public_key": bytearray(self.public)},
            {"expected_root_id": ""},
            {"expected_root_id": True},
            {"expected_root_public_key": b"short"},
            {"expected_root_public_key": bytearray(ROOT_KEY)},
            {"expected_enrollment_epoch": True},
            {"expected_enrollment_epoch": -1},
            {"minimum_revision": True},
            {"minimum_revision": -1},
            {"minimum_generation": True},
            {"minimum_generation": -1},
            {"minimum_fence_token": True},
            {"minimum_fence_token": -1},
        )

        for changes in invalid:
            with self.subTest(changes=repr(changes)[:85]):
                with self.assertRaises(ValueError):
                    self.make_source(**changes)

        self.assertEqual(self.authority.read_calls, 0)
        self.assertEqual(self.authority.cas_calls, 0)

    def test_bad_signed_read_messages_fail_closed(self):
        modes = (
            "malformed_pair",
            "wrong_authority",
            "wrong_root",
            "wrong_root_key",
            "wrong_epoch",
            "wrong_challenge",
            "wrong_domain",
            "extra_field",
            "bad_revision",
            "bad_generation",
            "bad_fence",
            "noncanonical",
            "bad_signature",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                self.authority.read_mode = mode

                with self.assertRaises(ValueError):
                    self.read(self.source)

                self.assertFalse(self.authority.active)

        self.assertEqual(self.authority.cas_calls, 0)

    def test_fresh_challenge_rejects_replayed_response(self):
        self.assertEqual(
            self.read(self.source),
            self.expected(),
        )

        self.authority.read_mode = "replay"

        with self.assertRaises(ValueError):
            self.read(self.source)

        self.assertEqual(self.authority.read_calls, 2)

        self.assertNotEqual(
            self.authority.read_challenges[0],
            self.authority.read_challenges[1],
        )

        self.assertFalse(self.authority.active)

    def test_revision_generation_and_fence_floors(
        self
    ):
        stricter = (
            {"minimum_revision": OLD + 1},
            {"minimum_generation": GENERATION + 1},
            {"minimum_fence_token": FENCE + 1},
        )

        for changes in stricter:
            with self.subTest(changes=changes):
                source = self.make_source(**changes)

                with self.assertRaises(ValueError):
                    self.read(source)

                self.assertFalse(self.authority.active)

        self.assertEqual(
            self.read(self.source),
            self.expected(),
        )

    def test_valid_cas_requires_separate_signed_readback(
        self
    ):
        result = self.advance(self.source)

        self.assertEqual(
            result,
            self.expected(
                revision=NEXT,
                generation=GENERATION + 1,
                fence_token=FENCE + 1,
            ),
        )

        self.assertEqual(self.authority.cas_calls, 1)
        self.assertGreaterEqual(self.authority.read_calls, 1)

        self.assertEqual(self.authority.revision, NEXT)
        self.assertEqual(
            self.authority.generation,
            GENERATION + 1,
        )
        self.assertEqual(
            self.authority.fence_token,
            FENCE + 1,
        )

        self.assertNotEqual(
            self.authority.cas_challenges[0],
            self.authority.read_challenges[0],
        )

        self.assertEqual(
            self.read(self.source),
            result,
        )

    def test_stale_and_invalid_cas_preconditions_rejected(
        self
    ):
        invalid = (
            {"expected_revision": OLD - 1},
            {"expected_revision": True},
            {"expected_generation": GENERATION - 1},
            {"expected_generation": True},
            {"expected_fence_token": FENCE - 1},
            {"expected_fence_token": True},
            {"next_revision": OLD},
            {"next_revision": True},
            {"next_revision": -1},
        )

        for changes in invalid:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.advance(self.source, **changes)

                self.assertEqual(
                    self.authority.revision,
                    OLD,
                )

                self.assertEqual(
                    self.authority.generation,
                    GENERATION,
                )

                self.assertEqual(
                    self.authority.fence_token,
                    FENCE,
                )

        self.assertEqual(
            self.read(self.source),
            self.expected(),
        )

    def test_fake_signed_cas_without_readback_rejected(
        self
    ):
        self.authority.fake_ack = True

        with self.assertRaises(ValueError):
            self.advance(self.source)

        self.assertEqual(self.authority.cas_calls, 1)
        self.assertGreaterEqual(self.authority.read_calls, 1)

        self.assertEqual(
            self.authority.revision,
            OLD,
        )

        self.assertFalse(self.authority.active)

    def test_commit_then_transport_failure_is_uncertain(
        self
    ):
        self.authority.commit_then_fail = True

        with self.assertRaises(ValueError):
            self.advance(self.source)

        self.assertEqual(self.authority.cas_calls, 1)

        # The volatile authority committed before transport
        # failed. The client must NOT auto-retry CAS.
        self.assertEqual(
            self.authority.revision,
            NEXT,
        )

        self.assertEqual(
            self.authority.generation,
            GENERATION + 1,
        )

        self.assertEqual(
            self.authority.fence_token,
            FENCE + 1,
        )

        self.assertEqual(
            self.read(self.source),
            self.expected(
                revision=NEXT,
                generation=GENERATION + 1,
                fence_token=FENCE + 1,
            ),
        )

        self.assertEqual(self.authority.cas_calls, 1)

    def test_provider_failure_and_caller_suppression(
        self
    ):
        self.authority.read_failure = True

        with self.assertRaises(ValueError):
            self.read(self.source)

        self.assertFalse(self.authority.active)

        self.authority.read_failure = False
        self.authority.suppress_caller_error = True

        with self.assertRaises(ValueError):
            with self.source.hold() as snapshot:
                self.assertEqual(
                    snapshot,
                    self.expected(),
                )

                raise ValueError(
                    "Injected caller verification failure."
                )

        self.assertFalse(self.authority.active)

    def test_caller_controlled_signer_repin_limitation(
        self
    ):
        rogue_private = Ed25519PrivateKey.generate()
        rogue = SignedMemoryMonotonicAuthority(
            rogue_private
        )

        with self.assertRaises(ValueError):
            self.read(
                self.make_source(authority=rogue)
            )

        # The caller can instead repin to the rogue key.
        # This demonstrates missing independent enrollment.
        repinned = self.make_source(
            authority=rogue,
            expected_authority_public_key=(
                public_bytes(rogue_private)
            ),
        )

        self.assertEqual(
            self.read(repinned),
            self.expected(),
        )

        for name in (
            "restore",
            "republish",
            "authorize",
            "bootstrap",
        ):
            with self.subTest(name=name):
                self.assertFalse(
                    hasattr(repinned, name)
                )

    def test_fully_signed_false_authority_claim_limitation(
        self
    ):
        self.authority.fake_ack = True
        self.authority.lie_readback = True

        result = self.advance(self.source)

        # Both signed claims agree, but the underlying
        # memory state was never advanced.
        #
        # Expected trust-boundary limitation:
        # a malicious trusted signer can lie.
        self.assertEqual(
            result,
            self.expected(
                revision=NEXT,
                generation=GENERATION + 1,
                fence_token=FENCE + 1,
            ),
        )

        self.assertEqual(
            self.authority.revision,
            OLD,
        )

        self.assertEqual(
            self.authority.generation,
            GENERATION,
        )

        self.assertEqual(
            self.authority.fence_token,
            FENCE,
        )

        self.assertEqual(self.authority.cas_calls, 1)
        self.assertGreaterEqual(self.authority.read_calls, 1)


if __name__ == "__main__":
    unittest.main()
