"""A44 adversarial checkpoint backend evidence verification.

These tests exercise cryptographic validation and its trust limits.

A signed backend reply is evidence relative to a caller-supplied
public key. It does NOT prove independent root enrollment, genuine
backend execution, durable CAS, linearizability, rollback resistance
or authorization to restore or republish a checkpoint.

All signatures are created using test-only in-memory Ed25519 keys.
No external backend, network service or persistent store is used.
"""

import json
import os
import sys
import unittest

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_backend_evidence as contract


BACKEND = contract.BACKEND
ROOT = contract.ROOT
DOMAIN = contract.DOMAIN
REVISION = contract.REVISION


_SIGNATURE_UNSET = object()


class A44CheckpointBackendEvidenceAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointBackendEvidenceContractTests(
                "test_valid_signed_backend_read_evidence"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.verifier = self.fixture.verifier

    def verify_read_bytes(self, message, signature=_SIGNATURE_UNSET, **changes):
        if signature is _SIGNATURE_UNSET:
            signature = self.fixture.backend_private.sign(
                bytes(message)
            )

        arguments = dict(
            message=message,
            signature=signature,
            expected_challenge=self.fixture.challenge,
            minimum_revision=REVISION - 1,
        )

        arguments.update(changes)

        return self.verifier.verify_read(**arguments)

    def verify_cas_bytes(self, message, signature=_SIGNATURE_UNSET, **changes):
        if signature is _SIGNATURE_UNSET:
            signature = self.fixture.backend_private.sign(
                bytes(message)
            )

        arguments = dict(
            message=message,
            signature=signature,
            expected_challenge=self.fixture.challenge,
            expected_revision=REVISION - 1,
            next_revision=REVISION,
        )

        arguments.update(changes)

        return self.verifier.verify_cas(**arguments)

    def assert_data_only(self, result):
        self.assertIs(
            type(result),
            self.fixture.evidence_type,
        )

        self.assertIs(result.signature_verified, True)

        for field in (
            "is_independently_trusted",
            "is_authoritative",
            "is_durable",
            "is_restorable",
            "can_republish",
        ):
            self.assertIs(
                getattr(result, field),
                False,
                field,
            )

    def test_direct_constructor_and_mutated_pins_fail_closed(self):
        class BytesChild(bytes):
            pass

        normal = dict(
            expected_backend_id=BACKEND,
            expected_backend_public_key=(
                self.fixture.backend_public
            ),
            expected_root_id=ROOT,
            expected_root_public_key=(
                self.fixture.root_public
            ),
        )

        invalid = (
            {"expected_backend_id": None},
            {"expected_backend_id": True},
            {"expected_backend_id": " backend"},
            {"expected_backend_public_key": None},
            {"expected_backend_public_key": bytearray(
                self.fixture.backend_public
            )},
            {"expected_backend_public_key": BytesChild(
                self.fixture.backend_public
            )},
            {"expected_root_id": ""},
            {"expected_root_id": "wrong\nroot"},
            {"expected_root_public_key": b""},
            {"expected_root_public_key": bytearray(
                self.fixture.root_public
            )},
        )

        for changes in invalid:
            with self.subTest(changes=repr(changes)[:75]):
                arguments = dict(normal)
                arguments.update(changes)

                with self.assertRaises(ValueError):
                    self.fixture.verifier_type(
                        **arguments
                    )

        # A caller can still mutate Python objects using
        # low-level facilities; this module is not an
        # in-process security boundary.
        direct = self.fixture.verifier_type(
            **normal
        )

        object.__setattr__(
            direct,
            "expected_backend_public_key",
            b"invalid",
        )

        message, signature = self.fixture.signed()

        with self.assertRaises(ValueError):
            direct.verify_read(
                message=message,
                signature=signature,
                expected_challenge=self.fixture.challenge,
                minimum_revision=REVISION - 1,
            )

    def test_message_and_signature_exact_types_and_limits(self):
        class BytesChild(bytes):
            pass

        message, signature = self.fixture.signed()

        invalid_messages = (
            None,
            "",
            b"",
            bytearray(message),
            memoryview(message),
            BytesChild(message),
            b"X" * 4097,
        )

        for candidate in invalid_messages:
            with self.subTest(message=repr(candidate)[:50]):
                with self.assertRaises(ValueError):
                    self.verify_read_bytes(
                        candidate,
                        signature,
                    )

        invalid_signatures = (
            None,
            "",
            b"",
            signature[:-1],
            signature + b"\x00",
            bytearray(signature),
            BytesChild(signature),
            b"\x00" * 64,
            bytes([signature[0] ^ 1])
            + signature[1:],
        )

        for candidate in invalid_signatures:
            with self.subTest(
                signature=repr(candidate)[:50]
            ):
                with self.assertRaises(ValueError):
                    self.verify_read_bytes(
                        message,
                        candidate,
                    )

        self.assert_data_only(
            self.verify_read_bytes(
                message,
                signature,
            )
        )

    def test_signed_duplicate_json_properties_rejected(self):
        message, _ = self.fixture.signed()

        duplicate = (
            b'{"backend_id":"foreign",'
            + message[1:],
            b'{"revision":999,'
            + message[1:],
            b'{"challenge_hex":"incorrect",'
            + message[1:],
            b'{"extra":{"value":1,"value":2},'
            + message[1:],
        )

        for candidate in duplicate:
            with self.subTest(
                candidate=candidate[:70]
            ):
                with self.assertRaises(ValueError):
                    self.verify_read_bytes(candidate)

    def test_signed_noncanonical_and_nonfinite_json_rejected(
        self
    ):
        document = self.fixture.document()

        canonical_message = contract.canonical(
            document
        )

        noncanonical = (
            b" " + canonical_message,
            canonical_message + b"\n",
            canonical_message + b" ",
            json.dumps(
                document,
                indent=2,
            ).encode("ascii"),
            json.dumps(
                document,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("ascii"),
        )

        for message in noncanonical:
            with self.subTest(
                message=message[:50]
            ):
                self.assertNotEqual(
                    message,
                    canonical_message,
                )

                with self.assertRaises(ValueError):
                    self.verify_read_bytes(message)

        malformed = (
            b"not-json",
            b"\xff\xfe",
            b"\xef\xbb\xbf" + canonical_message,
            b"null",
            b"[]",
            b"123",
        )

        for message in malformed:
            with self.subTest(
                message=message[:40]
            ):
                with self.assertRaises(ValueError):
                    self.verify_read_bytes(message)

        nan_document = self.fixture.document(
            revision=float("nan")
        )

        nan_message = json.dumps(
            nan_document,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=True,
        ).encode("ascii")

        with self.assertRaises(ValueError):
            self.verify_read_bytes(nan_message)

    def test_wrong_signed_identities_and_schema_fail_closed(
        self
    ):
        invalid = (
            self.fixture.document(
                backend_id="foreign_backend"
            ),
            self.fixture.document(
                backend_id=" backend"
            ),
            self.fixture.document(
                backend_id=True
            ),
            self.fixture.document(
                root_id="foreign_root"
            ),
            self.fixture.document(
                root_id="root\ninvalid"
            ),
            self.fixture.document(
                version=2
            ),
            self.fixture.document(
                version=True
            ),
            self.fixture.document(
                domain="foreign-domain"
            ),
            self.fixture.document(
                operation="other"
            ),
            self.fixture.document(
                unexpected_field="injected"
            ),
            self.fixture.document(
                expected_revision=REVISION - 1
            ),
        )

        for document in invalid:
            with self.subTest(
                document=repr(document)[:80]
            ):
                with self.assertRaises(ValueError):
                    self.fixture.read(
                        document=document
                    )

    def test_signed_root_key_substitution_and_encoding_rejected(
        self
    ):
        other_key = Ed25519PrivateKey.generate()

        foreign_root = contract.public_bytes(
            other_key
        )

        invalid = (
            "not-hex",
            "",
            self.fixture.root_public.hex()[:-2],
            self.fixture.root_public.hex().upper(),
            "00" * 32,
            foreign_root.hex(),
            list(self.fixture.root_public),
            None,
        )

        for candidate in invalid:
            # Uppercase is invalid only when the actual
            # public-key hex contains letters.
            if (
                type(candidate) is str
                and candidate == self.fixture.root_public.hex().upper()
                and candidate == self.fixture.root_public.hex()
            ):
                continue

            with self.subTest(
                root_key=repr(candidate)[:70]
            ):
                with self.assertRaises(ValueError):
                    self.fixture.read(
                        document=self.fixture.document(
                            root_public_key_hex=candidate
                        )
                    )

    def test_challenge_mismatch_and_replay_boundary(self):
        message, signature = self.fixture.signed()

        first = self.verify_read_bytes(
            message,
            signature,
        )

        repeated = self.verify_read_bytes(
            message,
            signature,
        )

        self.assertEqual(
            first.challenge,
            repeated.challenge,
        )

        self.assert_data_only(first)
        self.assert_data_only(repeated)

        other_challenge = os.urandom(32)

        while other_challenge == self.fixture.challenge:
            other_challenge = os.urandom(32)

        with self.assertRaises(ValueError):
            self.verify_read_bytes(
                message,
                signature,
                expected_challenge=other_challenge,
            )

        with self.assertRaises(ValueError):
            self.fixture.read(
                document=self.fixture.document(
                    challenge_hex=other_challenge.hex()
                )
            )

        for invalid in (
            b"",
            bytearray(self.fixture.challenge),
            True,
            None,
        ):
            with self.subTest(
                challenge=repr(invalid)[:50]
            ):
                with self.assertRaises(ValueError):
                    self.verify_read_bytes(
                        message,
                        signature,
                        expected_challenge=invalid,
                    )

    def test_caller_selected_floor_cannot_guarantee_rollback(
        self
    ):
        old_revision = REVISION - 1

        old_document = self.fixture.document(
            revision=old_revision
        )

        # This is accepted because the CALLER selected
        # an older minimum. It is NOT durable anti-rollback.
        old_report = self.fixture.read(
            document=old_document,
            minimum_revision=old_revision,
        )

        self.assertEqual(
            old_report.revision,
            old_revision,
        )

        self.assert_data_only(old_report)

        with self.assertRaises(ValueError):
            self.fixture.read(
                document=old_document,
                minimum_revision=REVISION,
            )

        boundary = self.fixture.read(
            minimum_revision=REVISION
        )

        self.assertEqual(
            boundary.revision,
            REVISION,
        )

        for minimum in (
            -1,
            True,
            "13",
            13.0,
            REVISION + 1,
        ):
            with self.subTest(
                minimum=repr(minimum)
            ):
                with self.assertRaises(ValueError):
                    self.fixture.read(
                        minimum_revision=minimum
                    )

    def test_signed_cas_transition_and_type_confusion_rejected(
        self
    ):
        valid = self.fixture.cas()

        self.assert_data_only(valid)
        self.assertEqual(
            valid.expected_revision,
            REVISION - 1,
        )
        self.assertEqual(
            valid.next_revision,
            REVISION,
        )

        bad_calls = (
            {"expected_revision": True},
            {"expected_revision": -1},
            {"expected_revision": REVISION},
            {"next_revision": False},
            {"next_revision": REVISION - 1},
            {"next_revision": REVISION + 1},
            {"next_revision": "13"},
        )

        for changes in bad_calls:
            with self.subTest(
                changes=repr(changes)
            ):
                with self.assertRaises(ValueError):
                    self.fixture.cas(
                        **changes
                    )

        bad_documents = (
            self.fixture.document(
                operation="cas",
                revision=REVISION - 1,
            ),
            self.fixture.document(
                operation="cas",
                revision=True,
            ),
            self.fixture.document(
                operation="cas",
                expected_revision=True,
            ),
            self.fixture.document(
                operation="cas",
                expected_revision=REVISION,
            ),
            self.fixture.document(
                operation="cas",
                next_revision=REVISION + 1,
            ),
            self.fixture.document(
                operation="cas",
                next_revision=13.0,
            ),
        )

        for document in bad_documents:
            with self.subTest(
                document=repr(document)[:80]
            ):
                with self.assertRaises(ValueError):
                    self.fixture.cas(
                        document=document
                    )

    def test_operation_domain_and_mixed_signature_replay_rejected(
        self
    ):
        read_message, read_signature = (
            self.fixture.signed()
        )

        cas_message, cas_signature = (
            self.fixture.signed(
                self.fixture.document(
                    operation="cas"
                )
            )
        )

        with self.assertRaises(ValueError):
            self.verify_cas_bytes(
                read_message,
                read_signature,
            )

        with self.assertRaises(ValueError):
            self.verify_read_bytes(
                cas_message,
                cas_signature,
            )

        with self.assertRaises(ValueError):
            self.verify_read_bytes(
                read_message,
                cas_signature,
            )

        with self.assertRaises(ValueError):
            self.verify_cas_bytes(
                cas_message,
                read_signature,
            )

        wrong_domain_message, wrong_domain_signature = (
            self.fixture.signed(
                self.fixture.document(
                    domain="another-domain"
                )
            )
        )

        with self.assertRaises(ValueError):
            self.verify_read_bytes(
                wrong_domain_message,
                wrong_domain_signature,
            )

    def test_caller_selected_attacker_backend_pin_is_relative(
        self
    ):
        attacker_private = Ed25519PrivateKey.generate()

        attacker_public = contract.public_bytes(
            attacker_private
        )

        message, signature = self.fixture.signed(
            self.fixture.document(),
            signer=attacker_private,
        )

        with self.assertRaises(ValueError):
            self.verify_read_bytes(
                message,
                signature,
            )

        # A verifier built from an attacker-selected
        # public key verifies the attacker's signature.
        # That does not authenticate the actual backend.
        selected_verifier = self.fixture.make_verifier(
            expected_backend_public_key=attacker_public
        )

        report = selected_verifier.verify_read(
            message=message,
            signature=signature,
            expected_challenge=self.fixture.challenge,
            minimum_revision=REVISION - 1,
        )

        self.assertEqual(
            report.backend_public_key,
            attacker_public,
        )

        self.assert_data_only(report)

    def test_signed_cas_and_forged_python_result_are_data_only(
        self
    ):
        # No CAS backend is instantiated or contacted.
        # A validly signed reply is still accepted by a
        # signature verifier, even without a real commit.
        report = self.fixture.cas()

        self.assert_data_only(report)

        self.assertEqual(
            report.operation,
            "cas",
        )

        self.assertEqual(
            report.revision,
            REVISION,
        )

        # The report class itself can be instantiated by
        # arbitrary Python code without signature checks.
        # It is therefore NOT an authorization token.
        forged = self.fixture.evidence_type(
            operation="cas",
            backend_id=BACKEND,
            backend_public_key=self.fixture.backend_public,
            root_id=ROOT,
            root_public_key=self.fixture.root_public,
            revision=REVISION,
            challenge=self.fixture.challenge,
            expected_revision=REVISION - 1,
            next_revision=REVISION,
        )

        self.assert_data_only(forged)

        # Even frozen Python objects are not a security
        # boundary against malicious in-process code.
        object.__setattr__(
            forged,
            "is_authoritative",
            True,
        )

        self.assertIs(
            forged.is_authoritative,
            True,
        )

        self.assertIs(
            report.is_authoritative,
            False,
        )

        self.assertIs(
            report.is_durable,
            False,
        )

        self.assertIs(
            report.can_republish,
            False,
        )


if __name__ == "__main__":
    unittest.main()
