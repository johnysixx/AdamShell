"""A44 / 66.31D: adversarial tests of signed provisioning generation.

Protocol tests use a simulated in-memory authority; they do NOT
prove independent durability, honest CAS, hardware trust or
authenticated deployment. The authority public key is caller-pinned.
"""

import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_checkpoint_protected_provisioning_floor_contract as floor_contract


class A44ProtectedProvisioningFloorAdversarialTests(unittest.TestCase):

    def setUp(self):
        self.fixture = floor_contract.A44ProtectedProvisioningFloorContractTests(
            "test_01_signed_initial_generation"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.authority = self.fixture.authority

    def client(self, **changes):
        return self.fixture.client(**changes)

    def rejected_read(self):
        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_01_attacker_signed_read_rejected(self):
        self.authority.response_signer = Ed25519PrivateKey.generate()
        self.rejected_read()

    def test_02_wrong_pinned_verifier_key_rejected(self):
        attacker = Ed25519PrivateKey.generate()
        client = self.client(
            expected_authority_public_key=floor_contract.public_key(attacker)
        )
        with self.assertRaises(ValueError):
            client.read_generation()

    def test_03_signed_authority_identity_substitution_rejected(self):
        self.authority.rewrite = lambda op, doc: {
            **doc, "authority_id": "attacker-generation-authority"
        }
        self.rejected_read()

    def test_04_signed_subject_identity_substitution_rejected(self):
        self.authority.rewrite = lambda op, doc: {
            **doc, "subject_id": "unrelated-project"
        }
        self.rejected_read()

    def test_05_signed_domain_and_version_substitution_rejected(self):
        for field, value in (
            ("domain", "AdamShell/A44/other-protocol/v1"),
            ("version", 2),
            ("version", True),
            ("version", "1"),
        ):
            with self.subTest(field=field, value=value):
                self.authority.rewrite = (
                    lambda op, doc, key=field, v=value: {**doc, key: v}
                )
                self.rejected_read()

    def test_06_signed_operation_and_challenge_substitution_rejected(self):
        for field, value in (
            ("operation", "cas"),
            ("challenge_hex", "00" * 32),
        ):
            with self.subTest(field=field):
                self.authority.rewrite = (
                    lambda op, doc, key=field, v=value: {**doc, key: v}
                )
                self.rejected_read()

    def test_07_signed_extra_or_missing_property_rejected(self):
        self.authority.rewrite = lambda op, doc: {
            **doc, "injected_property": "attacker"
        }
        self.rejected_read()
        self.authority.rewrite = lambda op, doc: {
            key: value for key, value in doc.items() if key != "generation"
        }
        self.rejected_read()

    def test_08_duplicate_signed_json_property_rejected(self):
        self.authority.encoder = lambda doc: floor_contract.canonical(doc).replace(
            b'"version":1', b'"version":1,"version":1'
        )
        self.rejected_read()

    def test_09_noncanonical_or_nonascii_signed_json_rejected(self):
        for suffix in (b" ", b"\n", b"\xff"):
            with self.subTest(suffix=repr(suffix)):
                self.authority.encoder = (
                    lambda doc, end=suffix: floor_contract.canonical(doc) + end
                )
                self.rejected_read()

    def test_10_malformed_signed_response_pair_rejected(self):
        for response in (
            (b"{}",),
            ("{}", b"0" * 64),
            (b"{}", b"short"),
            (b"{}", b"0" * 64),
        ):
            with self.subTest(response_type=repr(response)[:45]):
                self.authority.replay_read = response
                self.rejected_read()

    def test_11_signed_invalid_generation_rejected(self):
        for value in (True, -1, 1 << 100, "1", None):
            with self.subTest(value=repr(value)):
                self.authority.rewrite = (
                    lambda op, doc, v=value: {**doc, "generation": v}
                )
                self.rejected_read()

    def test_12_replayed_signed_read_rejected(self):
        client = self.client()
        self.assertEqual(client.read_generation(), 1)
        self.authority.replay_read = self.authority._signed(
            "read", b"R" * 32
        )
        with self.assertRaises(ValueError):
            client.read_generation()
        self.assertEqual(self.authority.generation, 1)

    def test_13_invalid_cas_and_lookup_operation_ids_rejected(self):
        client = self.client()
        for operation_id in (
            "", "a" * 31, "A" * 32, "g" * 32, None, True, 123
        ):
            with self.subTest(operation_id=repr(operation_id)):
                with self.assertRaises(ValueError):
                    self.fixture.advance(
                        client, operation_id=operation_id
                    )
                with self.assertRaises(ValueError):
                    client.lookup_operation(operation_id=operation_id)
        self.assertEqual(self.authority.generation, 1)

    def test_14_stale_or_nonmonotonic_cas_rejected(self):
        for before, after in ((0, 1), (1, 1), (1, 3), (1, -1)):
            with self.subTest(before=before, after=after):
                with self.assertRaises(ValueError):
                    self.fixture.advance(
                        expected_generation=before,
                        next_generation=after,
                    )
                self.assertEqual(self.authority.generation, 1)
                self.assertEqual(self.authority.operations, {})

    def test_15_signed_cas_status_forgery_rejected_without_retry(self):
        client = self.client()
        self.authority.rewrite = lambda op, doc: (
            {**doc, "status": "unknown"} if op == "cas" else doc
        )
        with self.assertRaises(ValueError):
            self.fixture.advance(client)
        self.assertEqual(self.authority.cas_calls, 1)
        self.authority.rewrite = None
        self.assertEqual(
            client.lookup_operation(operation_id=floor_contract.OP_A),
            ("committed", 2),
        )

    def test_16_signed_cas_request_echo_forgery_rejected(self):
        client = self.client()
        self.authority.rewrite = lambda op, doc: (
            {**doc, "expected_generation": 0} if op == "cas" else doc
        )
        with self.assertRaises(ValueError):
            self.fixture.advance(client)
        self.assertEqual(self.authority.cas_calls, 1)
        self.authority.rewrite = None
        self.assertEqual(
            client.lookup_operation(operation_id=floor_contract.OP_A),
            ("committed", 2),
        )

    def test_17_signed_cas_challenge_forgery_rejected(self):
        client = self.client()
        self.authority.rewrite = lambda op, doc: (
            {**doc, "challenge_hex": "00" * 32}
            if op == "cas" else doc
        )
        with self.assertRaises(ValueError):
            self.fixture.advance(client)
        self.assertEqual(self.authority.cas_calls, 1)
        self.authority.rewrite = None
        self.assertEqual(
            client.lookup_operation(operation_id=floor_contract.OP_A),
            ("committed", 2),
        )

    def test_18_signed_lookup_status_and_echo_forgery_rejected(self):
        client = self.client()
        for field, value in (
            ("status", "rejected"),
            ("operation_id", floor_contract.OP_A),
        ):
            with self.subTest(field=field):
                self.authority.rewrite = lambda op, doc, key=field, v=value: (
                    {**doc, key: v} if op == "lookup" else doc
                )
                with self.assertRaises(ValueError):
                    client.lookup_operation(operation_id=floor_contract.OP_B)
        self.assertEqual(self.authority.generation, 1)
        self.assertEqual(self.authority.operations, {})

    def test_19_signed_floor_rollback_rejected_by_pinned_client(self):
        old = self.client()
        self.assertEqual(self.fixture.advance(old), 2)
        raised = self.client(minimum_generation=2)
        self.assertEqual(raised.read_generation(), 2)
        self.authority.generation = 1
        with self.assertRaises(ValueError):
            raised.read_generation()
        with self.assertRaises(ValueError):
            raised.lookup_operation(operation_id=floor_contract.OP_A)
        with self.assertRaises(ValueError):
            self.fixture.bind(raised)

    def test_20_lost_cas_ack_is_not_automatically_retried(self):
        client = self.client()
        self.authority.fail_after_commit = True
        with self.assertRaises(ValueError):
            self.fixture.advance(client)
        self.assertEqual(self.authority.cas_calls, 1)
        self.assertEqual(
            client.lookup_operation(operation_id=floor_contract.OP_A),
            ("committed", 2),
        )
        self.assertEqual(self.authority.cas_calls, 1)

    def test_21_new_client_rejects_old_bootstrap_after_advance(self):
        original_client = self.client()
        self.assertEqual(self.fixture.advance(original_client), 2)
        restarted_client = self.client()
        self.assertEqual(restarted_client.read_generation(), 2)
        with self.assertRaises(ValueError):
            self.fixture.bind(restarted_client)

    def test_22_caller_repinning_attacker_authority_known_limit(self):
        attacker = Ed25519PrivateKey.generate()
        replacement = floor_contract.SimulatedSignedProvisioningFloorAuthority(
            attacker
        )
        client = self.client(
            authority=replacement,
            expected_authority_public_key=floor_contract.public_key(attacker),
        )
        self.assertEqual(client.read_generation(), 1)
        # Externally supplied pins cannot authenticate themselves.


if __name__ == "__main__":
    unittest.main()
