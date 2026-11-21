"""A44 / 66.24B pinned signed anchor read contract (EXPECTED RED).

PROPOSED API:
    PinnedSignedCheckpointAnchorSource.from_provider(
        provider=provider,
        expected_anchor_id=str,
        expected_anchor_public_key=bytes,
        expected_authority_id=str,
        expected_authority_public_key=bytes,
        expected_root_id=str,
        expected_root_public_key=bytes,
        expected_enrollment_epoch=int,
        minimum_revision=int,
        minimum_generation=int,
        minimum_fence_token=int,
    )

    source.hold() -> (
        authority_id, authority_public_key,
        root_id, root_public_key, epoch,
        revision, generation, fence_token
    )

Provider protocol:
    provider.hold(challenge=32 immutable random bytes)
    -> context manager yielding:
       (canonical_ASCII_JSON, Ed25519_signature)

Required signed JSON:
    domain="AdamShell/A44/independent-anchor/v1"
    version=1
    operation="read"
    anchor_id
    authority_id
    authority_public_key_hex
    root_id
    root_public_key_hex
    enrollment_epoch
    revision
    generation
    fence_token
    challenge_hex

SECURITY LIMITATIONS:
- Caller pins are NOT independently enrolled.
- Signatures do not prove genuine remote execution.
- No durable monotonic CAS is implemented or established.
- Volatile test provider is NOT rollback resistant.
- Python context managers are not trusted leases.
- No cross-store atomicity, restore or republication.
"""

import importlib
import json
import sys
import unittest

from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_sqlite_signed_authority as sqlite_contract

from core.existence.history_receipt_trust_checkpoint_external_anchor_gate import (
    CheckpointExternalAnchorReadGate,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_pinned_anchor_client"
)

DOMAIN = "AdamShell/A44/independent-anchor/v1"
ANCHOR_ID = "a44-independent-anchor-test"


def canonical(document):
    return json.dumps(
        document,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def raw_public_key(signer):
    return signer.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class VolatileSignedAnchorProvider:
    """Throwaway signer: no independent trust or persistence."""

    def __init__(self, signer, snapshot):
        self.signer = signer
        self.snapshot = snapshot
        self.challenges = []
        self.active = False
        self.fields = {}
        self.corrupt_challenge = False
        self.raw_mode = None
        self.response_override = None
        self.enter_error = None
        self.exit_error = None
        self.suppress_errors = False
        self.suppressed = False

    @contextmanager
    def hold(self, *, challenge):
        if self.enter_error is not None:
            raise self.enter_error

        self.active = True
        self.challenges.append(challenge)

        (
            authority_id,
            authority_key,
            root_id,
            root_key,
            epoch,
            revision,
            generation,
            fence,
        ) = self.snapshot

        document = {
            "domain": DOMAIN,
            "version": 1,
            "operation": "read",
            "anchor_id": ANCHOR_ID,
            "authority_id": authority_id,
            "authority_public_key_hex": authority_key.hex(),
            "root_id": root_id,
            "root_public_key_hex": root_key.hex(),
            "enrollment_epoch": epoch,
            "revision": revision,
            "generation": generation,
            "fence_token": fence,
            "challenge_hex": challenge.hex(),
        }

        document.update(self.fields)

        if self.corrupt_challenge:
            altered = bytes(
                (challenge[0] ^ 1,)
            ) + challenge[1:]

            document["challenge_hex"] = altered.hex()

        message = canonical(document)

        if self.raw_mode == "spaced":
            message = json.dumps(
                document,
                sort_keys=True,
            ).encode("ascii")

        elif self.raw_mode == "duplicate":
            message = message.replace(
                b"{",
                b'{"version":1,',
                1,
            )

        signature = self.signer.sign(message)
        response = (message, signature)

        if self.response_override is not None:
            response = self.response_override(
                message,
                signature,
            )

        try:
            try:
                yield response

            except ValueError:
                if not self.suppress_errors:
                    raise

                self.suppressed = True

        finally:
            self.active = False

            if self.exit_error is not None:
                raise self.exit_error


class A44PinnedSignedAnchorClientContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.source_type = (
            module.PinnedSignedCheckpointAnchorSource
        )

        self.fixture = (
            sqlite_contract.A44CheckpointSQLiteSignedAuthorityContractTests(
                "test_canonical_signed_held_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.sqlite_backend = self.fixture.bootstrap()

        self.sqlite_source = self.fixture.client(
            self.sqlite_backend
        )

        self.anchor_signer = Ed25519PrivateKey.generate()
        self.anchor_key = raw_public_key(self.anchor_signer)

        self.baseline = (
            self.sqlite_source.expected_authority_id,
            self.sqlite_source.expected_authority_public_key,
            self.sqlite_source.expected_root_id,
            self.sqlite_source.expected_root_public_key,
            self.sqlite_source.expected_enrollment_epoch,
            sqlite_contract.OLD,
            sqlite_contract.GENERATION,
            sqlite_contract.FENCE,
        )

        self.provider = VolatileSignedAnchorProvider(
            self.anchor_signer,
            self.baseline,
        )

    def source(self, **changes):
        arguments = {
            "provider": self.provider,
            "expected_anchor_id": ANCHOR_ID,
            "expected_anchor_public_key": self.anchor_key,
            "expected_authority_id": self.baseline[0],
            "expected_authority_public_key": self.baseline[1],
            "expected_root_id": self.baseline[2],
            "expected_root_public_key": self.baseline[3],
            "expected_enrollment_epoch": self.baseline[4],
            "minimum_revision": self.baseline[5],
            "minimum_generation": self.baseline[6],
            "minimum_fence_token": self.baseline[7],
        }

        arguments.update(changes)

        return self.source_type.from_provider(
            **arguments
        )

    @staticmethod
    def read(source):
        with source.hold() as snapshot:
            return snapshot

    def test_01_signed_read_matches_anchor_gate_contract(self):
        source = self.source()

        with source.hold() as snapshot:
            self.assertEqual(
                snapshot,
                self.baseline,
            )

            self.assertTrue(self.provider.active)

        self.assertFalse(self.provider.active)

        gate = CheckpointExternalAnchorReadGate.from_sources(
            signed_source=self.sqlite_source,
            anchor_source=source,
        )

        with gate.hold() as observed:
            self.assertEqual(
                observed,
                self.fixture.expected(),
            )

            self.assertTrue(self.provider.active)

        self.assertFalse(self.provider.active)

        self.read(source)

        self.assertEqual(
            len(self.provider.challenges),
            3,
        )

        self.assertEqual(
            len(set(self.provider.challenges)),
            3,
        )

        self.assertTrue(all(
            type(challenge) is bytes
            and len(challenge) == 32
            for challenge in self.provider.challenges
        ))

    def test_02_wrong_signature_and_wrong_pinned_key_rejected(self):
        rogue = Ed25519PrivateKey.generate()

        self.provider.signer = rogue

        with self.assertRaises(ValueError):
            self.read(self.source())

        self.provider.signer = self.anchor_signer

        with self.assertRaises(ValueError):
            self.read(self.source(
                expected_anchor_public_key=raw_public_key(rogue)
            ))

        self.assertFalse(self.provider.active)

    def test_03_challenge_mismatch_rejected(self):
        self.provider.corrupt_challenge = True

        with self.assertRaises(ValueError):
            self.read(self.source())

        self.assertFalse(self.provider.active)

    def test_04_identity_epoch_and_key_binding_rejected(self):
        attacks = (
            ("anchor_id", "wrong-anchor"),
            ("authority_id", "wrong-authority"),
            (
                "authority_public_key_hex",
                (b"x" * 32).hex(),
            ),
            ("root_id", "wrong-root"),
            (
                "root_public_key_hex",
                (b"y" * 32).hex(),
            ),
            ("enrollment_epoch", self.baseline[4] + 1),
            ("domain", "unrelated-domain"),
            ("version", 2),
            ("operation", "cas"),
        )

        for key, value in attacks:
            with self.subTest(field=key):
                self.provider.fields = {key: value}

                with self.assertRaises(ValueError):
                    self.read(self.source())

                self.assertFalse(self.provider.active)

        self.provider.fields = {}

    def test_05_floor_and_counter_types_rejected(self):
        for index in (5, 6, 7):
            attacks = (
                self.baseline[index] - 1,
                True,
                -1,
                1.5,
                1 << 63,
            )

            for value in attacks:
                with self.subTest(
                    index=index,
                    value=repr(value),
                ):
                    altered = list(self.baseline)
                    altered[index] = value

                    self.provider.snapshot = tuple(altered)

                    with self.assertRaises(ValueError):
                        self.read(self.source())

                    self.assertFalse(self.provider.active)

        self.provider.snapshot = self.baseline

    def test_06_noncanonical_or_duplicate_json_rejected(self):
        for mode in ("spaced", "duplicate"):
            with self.subTest(mode=mode):
                self.provider.raw_mode = mode

                with self.assertRaises(ValueError):
                    self.read(self.source())

                self.assertFalse(self.provider.active)

        self.provider.raw_mode = None
        self.provider.fields = {
            "unexpected_field": True
        }

        with self.assertRaises(ValueError):
            self.read(self.source())

        self.provider.fields = {}

    def test_07_malformed_signed_response_rejected(self):
        attacks = (
            lambda m, s: [m, s],
            lambda m, s: (m, s[:63]),
            lambda m, s: (bytearray(m), s),
            lambda m, s: (m, bytearray(s)),
            lambda m, s: (m, s, b"third"),
            lambda m, s: None,
        )

        for transform in attacks:
            with self.subTest(transform=repr(transform)):
                self.provider.response_override = transform

                with self.assertRaises(ValueError):
                    self.read(self.source())

                self.assertFalse(self.provider.active)

        self.provider.response_override = None

    def test_08_provider_enter_and_release_fail_closed(self):
        self.provider.enter_error = RuntimeError(
            "anchor unavailable"
        )

        with self.assertRaises(ValueError):
            self.read(self.source())

        self.provider.enter_error = None

        self.provider.exit_error = RuntimeError(
            "anchor release failed"
        )

        with self.assertRaises(ValueError):
            self.read(self.source())

        self.assertFalse(self.provider.active)

    def test_09_suppressed_caller_error_is_rejected(self):
        self.provider.suppress_errors = True

        with self.assertRaises(ValueError):
            with self.source().hold() as snapshot:
                self.assertEqual(
                    snapshot,
                    self.baseline,
                )

                raise ValueError(
                    "caller verification failed"
                )

        self.assertTrue(self.provider.suppressed)
        self.assertFalse(self.provider.active)

    def test_10_signed_anchor_ahead_or_behind_sqlite_rejected(self):
        updated = self.baseline[:5] + (
            sqlite_contract.NEXT,
            sqlite_contract.GENERATION + 1,
            sqlite_contract.FENCE + 1,
        )

        gate = CheckpointExternalAnchorReadGate.from_sources(
            signed_source=self.sqlite_source,
            anchor_source=self.source(),
        )

        # Anchor ahead of SQLite.
        self.provider.snapshot = updated

        with self.assertRaises(ValueError):
            with gate.hold():
                pass

        # SQLite ahead of anchor.
        self.provider.snapshot = self.baseline
        self.fixture.advance(self.sqlite_source)

        with self.assertRaises(ValueError):
            with gate.hold():
                pass

        self.assertFalse(self.provider.active)

    def test_11_invalid_provider_or_pins_rejected(self):
        attacks = (
            {"provider": None},
            {"provider": object()},
            {"expected_anchor_id": ""},
            {"expected_anchor_public_key": b"short"},
            {"expected_enrollment_epoch": True},
            {"minimum_revision": -1},
            {"minimum_generation": False},
            {"minimum_fence_token": -1},
        )

        for changes in attacks:
            with self.subTest(changes=repr(changes)):
                with self.assertRaises(ValueError):
                    self.source(**changes)

    def test_12_client_exposes_no_publication_capability(self):
        source = self.source()

        forbidden = (
            "advance",
            "advance_if_current",
            "bootstrap",
            "publish",
            "publish_if_current",
            "restore",
            "republish",
        )

        for method in forbidden:
            with self.subTest(method=method):
                self.assertFalse(
                    callable(
                        getattr(source, method, None)
                    )
                )

    def test_13_signed_provider_proves_no_external_independence(self):
        """Known limit: signature does not prove durable CAS."""

        self.assertEqual(
            self.read(self.source()),
            self.baseline,
        )

        self.assertFalse(self.provider.active)


if __name__ == "__main__":
    unittest.main()
