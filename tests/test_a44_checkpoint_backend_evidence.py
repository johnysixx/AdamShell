"""A44 signed external checkpoint backend evidence contract.

EXPECTED RED: checkpoint_backend_evidence module absent.

This contract tests a verifier for signed backend responses,
NOT a real external backend.

Public API:

    CheckpointRootBackendEvidenceVerifier.from_pinned_key(
        expected_backend_id,
        expected_backend_public_key,
        expected_root_id,
        expected_root_public_key,
    )

    verifier.verify_read(
        message,
        signature,
        expected_challenge,
        minimum_revision,
    )

    verifier.verify_cas(
        message,
        signature,
        expected_challenge,
        expected_revision,
        next_revision,
    )

Both verification methods return:
    VerifiedCheckpointRootBackendEvidence

Signed canonical JSON is domain-separated and must contain:

    domain
    version
    operation
    backend_id
    root_id
    root_public_key_hex
    revision
    challenge_hex

CAS evidence additionally contains:
    expected_revision
    next_revision

Read evidence must not contain CAS-specific fields.

All fields are cryptographically bound by Ed25519.
Backend and root public keys are caller-supplied pins.
Neither is independently enrolled by this verifier.

A valid signature does not prove:
- backend independence or genuine execution;
- a durable or rollback-resistant state;
- linearizable CAS publication;
- freshness if the same challenge is reused;
- cross-backend atomicity;
- checkpoint restoration authorization.

No external service or storage is contacted by these tests.
"""

import importlib
import json
import os
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_backend_evidence"
)

DOMAIN = "AdamShell/A44/checkpoint-backend-evidence/v1"

BACKEND = "checkpoint_remote_backend_v1"
ROOT = "checkpoint_trust_root_v1"

REVISION = 13


def public_bytes(private_key):
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def canonical(document):
    return json.dumps(
        document,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


class A44CheckpointBackendEvidenceContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.verifier_type = (
            module.CheckpointRootBackendEvidenceVerifier
        )

        self.evidence_type = (
            module.VerifiedCheckpointRootBackendEvidence
        )

        self.backend_private = Ed25519PrivateKey.generate()
        self.backend_public = public_bytes(
            self.backend_private
        )

        self.root_private = Ed25519PrivateKey.generate()
        self.root_public = public_bytes(
            self.root_private
        )

        self.challenge = os.urandom(32)

        self.verifier = self.make_verifier()

    def make_verifier(self, **changes):
        arguments = {
            "expected_backend_id": BACKEND,
            "expected_backend_public_key":
                self.backend_public,
            "expected_root_id": ROOT,
            "expected_root_public_key":
                self.root_public,
        }

        arguments.update(changes)

        return self.verifier_type.from_pinned_key(
            **arguments
        )

    def document(self, *, operation="read", **changes):
        payload = {
            "domain": DOMAIN,
            "version": 1,
            "operation": operation,
            "backend_id": BACKEND,
            "root_id": ROOT,
            "root_public_key_hex": self.root_public.hex(),
            "revision": REVISION,
            "challenge_hex": self.challenge.hex(),
        }

        if operation == "cas":
            payload["expected_revision"] = REVISION - 1
            payload["next_revision"] = REVISION

        payload.update(changes)
        return payload

    def signed(self, document=None, *, signer=None):
        if document is None:
            document = self.document()

        message = canonical(document)
        private = (
            self.backend_private if signer is None
            else signer
        )

        return message, private.sign(message)

    def read(self, *, document=None, signer=None, **changes):
        message, signature = self.signed(
            document, signer=signer
        )

        arguments = {
            "message": message,
            "signature": signature,
            "expected_challenge": self.challenge,
            "minimum_revision": REVISION - 1,
        }

        arguments.update(changes)

        return self.verifier.verify_read(**arguments)

    def cas(self, *, document=None, signer=None, **changes):
        if document is None:
            document = self.document(operation="cas")

        message, signature = self.signed(
            document, signer=signer
        )

        arguments = {
            "message": message,
            "signature": signature,
            "expected_challenge": self.challenge,
            "expected_revision": REVISION - 1,
            "next_revision": REVISION,
        }

        arguments.update(changes)

        return self.verifier.verify_cas(**arguments)

    def assert_data_only(self, value):
        self.assertIs(type(value), self.evidence_type)
        self.assertIs(value.signature_verified, True)

        for name in (
            "is_independently_trusted",
            "is_authoritative",
            "is_durable",
            "is_restorable",
            "can_republish",
        ):
            self.assertIs(
                getattr(value, name),
                False,
                name,
            )

    def test_valid_signed_backend_read_evidence(self):
        result = self.read()

        self.assert_data_only(result)
        self.assertEqual(result.operation, "read")
        self.assertEqual(result.backend_id, BACKEND)
        self.assertEqual(result.root_id, ROOT)
        self.assertEqual(
            result.root_public_key,
            self.root_public,
        )
        self.assertEqual(result.revision, REVISION)
        self.assertEqual(
            result.challenge,
            self.challenge,
        )

    def test_valid_signed_cas_evidence(self):
        result = self.cas()

        self.assert_data_only(result)
        self.assertEqual(result.operation, "cas")
        self.assertEqual(result.revision, REVISION)
        self.assertEqual(
            result.expected_revision,
            REVISION - 1,
        )
        self.assertEqual(
            result.next_revision,
            REVISION,
        )

    def test_invalid_pinned_backend_and_root_keys_rejected(self):
        invalid = (
            {"expected_backend_id": ""},
            {"expected_backend_id": True},
            {"expected_backend_public_key": b""},
            {"expected_backend_public_key":
                 self.backend_public[:-1]},
            {"expected_backend_public_key":
                 bytearray(self.backend_public)},
            {"expected_root_id": ""},
            {"expected_root_id": True},
            {"expected_root_public_key": b""},
            {"expected_root_public_key":
                 self.root_public[:-1]},
            {"expected_root_public_key":
                 bytearray(self.root_public)},
        )

        for changes in invalid:
            with self.subTest(changes=repr(changes)[:80]):
                with self.assertRaises(ValueError):
                    self.make_verifier(**changes)

    def test_invalid_signature_or_foreign_signer_rejected(self):
        message, signature = self.signed()

        tampered = (
            bytearray(signature),
            b"",
            signature[:-1],
            bytes([signature[0] ^ 1]) + signature[1:],
        )

        for candidate in tampered:
            with self.subTest(
                signature=repr(candidate)[:50]
            ):
                with self.assertRaises(ValueError):
                    self.verifier.verify_read(
                        message=message,
                        signature=candidate,
                        expected_challenge=self.challenge,
                        minimum_revision=REVISION - 1,
                    )

        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.read(signer=attacker)

    def test_noncanonical_and_malformed_messages_rejected(self):
        payload = self.document()
        pretty = json.dumps(
            payload,
            indent=2,
        ).encode("utf-8")

        duplicate = (
            b'{"backend_id":"duplicate",'
            + canonical(payload)[1:]
        )

        malformed = (
            b"",
            b"not-json",
            b"\xff\xfe",
            pretty,
            canonical(payload) + b"\n",
            duplicate,
            bytearray(canonical(payload)),
        )

        for message in malformed:
            with self.subTest(message=repr(message)[:50]):
                if type(message) is bytes:
                    signature = self.backend_private.sign(
                        message
                    )
                else:
                    signature = self.backend_private.sign(
                        bytes(message)
                    )

                with self.assertRaises(ValueError):
                    self.verifier.verify_read(
                        message=message,
                        signature=signature,
                        expected_challenge=self.challenge,
                        minimum_revision=REVISION - 1,
                    )

    def test_signed_domain_version_and_schema_rejected(self):
        invalid_documents = (
            self.document(domain="wrong-domain"),
            self.document(version=2),
            self.document(version=True),
            self.document(operation="other"),
            self.document(extra_field="unexpected"),
            self.document(root_public_key_hex="not-hex"),
            self.document(
                expected_revision=REVISION - 1
            ),
        )

        for document in invalid_documents:
            with self.subTest(
                document=repr(document)[:80]
            ):
                with self.assertRaises(ValueError):
                    self.read(document=document)

    def test_signed_backend_and_root_substitution_rejected(self):
        invalid = (
            self.document(
                backend_id="foreign_backend"
            ),
            self.document(
                root_id="foreign_root"
            ),
            self.document(
                root_public_key_hex=("ab" * 32)
            ),
        )

        for document in invalid:
            with self.subTest(
                document=repr(document)[:80]
            ):
                with self.assertRaises(ValueError):
                    self.read(document=document)

    def test_revision_floor_and_type_rules(self):
        result = self.read(
            minimum_revision=REVISION
        )

        self.assertEqual(
            result.revision,
            REVISION,
        )

        invalid_floors = (
            REVISION + 1,
            -1,
            True,
            "12",
            12.0,
        )

        for floor in invalid_floors:
            with self.subTest(floor=repr(floor)):
                with self.assertRaises(ValueError):
                    self.read(
                        minimum_revision=floor
                    )

        for revision in (True, -1, 13.0, "13"):
            with self.subTest(
                revision=repr(revision)
            ):
                with self.assertRaises(ValueError):
                    self.read(
                        document=self.document(
                            revision=revision
                        )
                    )

    def test_challenge_binding_and_replay_limits(self):
        same = self.read()
        replay = self.read()

        self.assertEqual(
            same.challenge,
            replay.challenge,
        )

        different = os.urandom(32)

        while different == self.challenge:
            different = os.urandom(32)

        with self.assertRaises(ValueError):
            self.read(
                expected_challenge=different
            )

        with self.assertRaises(ValueError):
            self.read(
                expected_challenge=b""
            )

        with self.assertRaises(ValueError):
            self.read(
                document=self.document(
                    challenge_hex=different.hex()
                )
            )

        # Same-challenge replay is not prevented here.
        # This is intentionally a documented limitation.

    def test_cas_predecessor_target_and_reply_consistency(self):
        invalid_calls = (
            {"expected_revision": True},
            {"expected_revision": -1},
            {"expected_revision": REVISION},
            {"next_revision": False},
            {"next_revision": REVISION - 1},
            {"next_revision": REVISION + 1},
            {"next_revision": "13"},
        )

        for changes in invalid_calls:
            with self.subTest(
                changes=repr(changes)
            ):
                with self.assertRaises(ValueError):
                    self.cas(**changes)

        invalid_documents = (
            self.document(
                operation="cas",
                expected_revision=REVISION,
            ),
            self.document(
                operation="cas",
                next_revision=REVISION + 1,
            ),
            self.document(
                operation="cas",
                revision=REVISION - 1,
            ),
            self.document(
                operation="cas",
                extra_field="unexpected",
            ),
        )

        for document in invalid_documents:
            with self.subTest(
                document=repr(document)[:80]
            ):
                with self.assertRaises(ValueError):
                    self.cas(document=document)

    def test_cross_operation_replay_is_rejected(self):
        read_message, read_signature = self.signed()

        with self.assertRaises(ValueError):
            self.verifier.verify_cas(
                message=read_message,
                signature=read_signature,
                expected_challenge=self.challenge,
                expected_revision=REVISION - 1,
                next_revision=REVISION,
            )

        cas_message, cas_signature = self.signed(
            self.document(operation="cas")
        )

        with self.assertRaises(ValueError):
            self.verifier.verify_read(
                message=cas_message,
                signature=cas_signature,
                expected_challenge=self.challenge,
                minimum_revision=REVISION - 1,
            )

    def test_caller_selected_attacker_backend_limit(self):
        attacker = Ed25519PrivateKey.generate()
        attacker_public = public_bytes(attacker)

        forged = self.document()

        message, signature = self.signed(
            forged,
            signer=attacker,
        )

        # The original backend pin rejects an attacker.
        with self.assertRaises(ValueError):
            self.verifier.verify_read(
                message=message,
                signature=signature,
                expected_challenge=self.challenge,
                minimum_revision=REVISION - 1,
            )

        # A caller can supply a different backend pin.
        # Signature verification relative to that pin
        # does NOT independently enroll the new backend.
        selected = self.make_verifier(
            expected_backend_public_key=attacker_public
        )

        result = selected.verify_read(
            message=message,
            signature=signature,
            expected_challenge=self.challenge,
            minimum_revision=REVISION - 1,
        )

        self.assert_data_only(result)
        self.assertEqual(
            result.backend_id,
            BACKEND,
        )
        self.assertEqual(
            result.revision,
            REVISION,
        )


if __name__ == "__main__":
    unittest.main()
