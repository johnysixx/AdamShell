"""A44 / 66.28D protected high-water protocol adversarial tests.

These tests validate signed responses against caller-pinned trust.

The provider is an in-memory mock. Passing these tests does NOT
establish durable publication, remote isolation, trustworthy
provisioning, linearizable external CAS or rollback resistance.

A caller able to substitute the trusted store key can accept
an attacker-signed response. This limitation is tested explicitly.
"""

import json
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

import test_a44_checkpoint_protected_high_water_contract as contract
import test_a44_checkpoint_anchor_cas_backend_contract as backend_contract


class A44ProtectedHighWaterAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44ProtectedHighWaterProtocolContractTests(
                "test_01_pinned_signed_read_accepts_initial_floor"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.provider = self.fixture.provider

    def test_01_attacker_signed_read_is_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        self.provider.response_signer = attacker

        with self.assertRaises(ValueError):
            self.fixture.read()

        self.assertEqual(
            self.provider.floor,
            (10, 20, 30),
        )

    def test_02_signed_identity_and_key_replacements_rejected(self):
        attacks = (
            ("store_id", "attacker-store"),
            ("anchor_id", "attacker-anchor"),
            ("anchor_public_key_hex", "01" * 32),
            ("authority_id", "attacker-authority"),
            ("authority_public_key_hex", "02" * 32),
            ("root_id", "attacker-root"),
            ("root_public_key_hex", "03" * 32),
        )

        for field, bad in attacks:
            with self.subTest(field=field):
                self.provider.rewrite = (
                    lambda operation, document, field=field, bad=bad: {
                        **document,
                        field: bad,
                    }
                )

                with self.assertRaises(ValueError):
                    self.fixture.read()

        self.provider.rewrite = None

        self.assertEqual(
            self.fixture.read(),
            (10, 20, 30),
        )

    def test_03_signing_key_substitution_after_binding_rejected(self):
        client = self.fixture.client()
        attacker = Ed25519PrivateKey.generate()

        self.provider.response_signer = attacker

        with self.assertRaises(ValueError):
            self.fixture.read(client)

        self.provider.response_signer = (
            self.fixture.store_signer
        )

        self.assertEqual(
            self.fixture.read(client),
            (10, 20, 30),
        )

    def test_04_cross_domain_signed_read_rejected(self):
        self.provider.rewrite = (
            lambda operation, document: {
                **document,
                "domain": (
                    "AdamShell/A44/independent-anchor/v1"
                ),
            }
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

    def test_05_wrong_signed_operation_rejected(self):
        self.provider.rewrite = (
            lambda operation, document: {
                **document,
                "operation": "lookup",
            }
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

    def test_06_boolean_protocol_version_rejected(self):
        self.provider.rewrite = (
            lambda operation, document: {
                **document,
                "version": True,
            }
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

    def test_07_signed_enrollment_epoch_replacement_rejected(self):
        epoch = (
            self.fixture.enrollment.expected_enrollment_epoch
        )

        self.provider.rewrite = (
            lambda operation, document: {
                **document,
                "enrollment_epoch": epoch + 1,
            }
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

    def test_08_replayed_challenge_fails_closed_after_cas(self):
        client = self.fixture.client()

        self.provider.rewrite = (
            lambda operation, document: {
                **document,
                "challenge_hex": "00" * 32,
            }
        )

        with self.assertRaises(ValueError):
            self.fixture.read(client)

        # The simulated provider still commits before sending
        # a malformed, freshly signed CAS response.
        with self.assertRaises(ValueError):
            self.fixture.advance(client)

        self.assertEqual(
            self.provider.cas_calls,
            1,
        )

        self.assertIn(
            contract.OP_A,
            self.provider.operations,
        )

        self.provider.rewrite = None

        self.assertEqual(
            client.lookup_operation(
                operation_id=contract.OP_A
            ),
            ("committed", (11, 21, 31)),
        )

    def test_09_signed_duplicate_json_property_rejected(self):
        self.provider.encoder = (
            lambda document: (
                b'{"version":1,'
                + contract.canonical(document)[1:]
            )
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

    def test_10_noncanonical_and_nonfinite_json_rejected(self):
        encoders = (
            lambda document: json.dumps(
                document,
                sort_keys=True,
                indent=2,
            ).encode("ascii"),
            lambda document: contract.canonical(
                document
            ).replace(
                b'"revision":10',
                b'"revision":NaN',
                1,
            ),
        )

        for index, encoder in enumerate(encoders):
            with self.subTest(case=index):
                self.provider.encoder = encoder

                with self.assertRaises(ValueError):
                    self.fixture.read()

        self.provider.encoder = contract.canonical

    def test_11_signed_cas_operation_id_tamper_is_ambiguous(self):
        client = self.fixture.client()

        self.provider.rewrite = (
            lambda operation, document: (
                {
                    **document,
                    "operation_id": contract.OP_B,
                }
                if operation == "cas"
                else document
            )
        )

        with self.assertRaises(ValueError):
            self.fixture.advance(client)

        self.assertEqual(
            self.provider.cas_calls,
            1,
        )

        self.assertIn(
            contract.OP_A,
            self.provider.operations,
        )

        self.provider.rewrite = None

        self.assertEqual(
            client.lookup_operation(
                operation_id=contract.OP_A
            ),
            ("committed", (11, 21, 31)),
        )

        self.assertEqual(
            len(self.provider.operations),
            1,
        )

    def test_12_signed_cas_request_tamper_is_ambiguous(self):
        client = self.fixture.client()

        self.provider.rewrite = (
            lambda operation, document: (
                {
                    **document,
                    "expected_revision": 9,
                }
                if operation == "cas"
                else document
            )
        )

        with self.assertRaises(ValueError):
            self.fixture.advance(client)

        self.assertEqual(
            self.provider.cas_calls,
            1,
        )

        self.provider.rewrite = None

        self.assertEqual(
            client.lookup_operation(
                operation_id=contract.OP_A
            ),
            ("committed", (11, 21, 31)),
        )

    def test_13_signed_cas_status_forgery_rejected(self):
        client = self.fixture.client()

        self.provider.rewrite = (
            lambda operation, document: (
                {
                    **document,
                    "status": "accepted",
                }
                if operation == "cas"
                else document
            )
        )

        with self.assertRaises(ValueError):
            self.fixture.advance(client)

        self.provider.rewrite = None

        self.assertEqual(
            client.lookup_operation(
                operation_id=contract.OP_A
            ),
            ("committed", (11, 21, 31)),
        )

    def test_14_signed_cas_committed_floor_forgery_rejected(self):
        client = self.fixture.client()

        self.provider.rewrite = (
            lambda operation, document: (
                {
                    **document,
                    "revision": 12,
                }
                if operation == "cas"
                else document
            )
        )

        with self.assertRaises(ValueError):
            self.fixture.advance(client)

        self.assertEqual(
            self.provider.floor,
            (11, 21, 31),
        )

        self.provider.rewrite = None

        self.assertEqual(
            client.lookup_operation(
                operation_id=contract.OP_A
            ),
            ("committed", (11, 21, 31)),
        )

    def test_15_signed_lookup_operation_id_forgery_rejected(self):
        client = self.fixture.client()

        self.provider.rewrite = (
            lambda operation, document: (
                {
                    **document,
                    "operation_id": contract.OP_B,
                }
                if operation == "lookup"
                else document
            )
        )

        with self.assertRaises(ValueError):
            client.lookup_operation(
                operation_id=contract.OP_A
            )

        self.assertEqual(
            self.provider.operations,
            {},
        )

    def test_16_signed_lookup_status_and_floor_downgrade_rejected(self):
        client = self.fixture.client()

        self.provider.rewrite = (
            lambda operation, document: (
                {
                    **document,
                    "status": "absent",
                }
                if operation == "lookup"
                else document
            )
        )

        with self.assertRaises(ValueError):
            client.lookup_operation(
                operation_id=contract.OP_A
            )

        self.provider.rewrite = None

        self.assertEqual(
            self.fixture.advance(client),
            (11, 21, 31),
        )

        higher = self.fixture.client(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
        )

        self.provider.rewrite = (
            lambda operation, document: (
                {
                    **document,
                    "revision": 10,
                }
                if operation == "lookup"
                else document
            )
        )

        with self.assertRaises(ValueError):
            higher.lookup_operation(
                operation_id=contract.OP_A
            )

        self.provider.rewrite = None

        self.assertEqual(
            higher.lookup_operation(
                operation_id=contract.OP_A
            ),
            ("committed", (11, 21, 31)),
        )

    def test_17_timeout_before_publication_does_not_auto_retry(self):
        client = self.fixture.client()

        attempts = []

        def fail_before_commit(**arguments):
            attempts.append(
                arguments["operation_id"]
            )

            raise TimeoutError(
                "Injected transport timeout before publication."
            )

        self.provider.advance_if_current = (
            fail_before_commit
        )

        with self.assertRaises(ValueError):
            self.fixture.advance(client)

        self.assertEqual(
            attempts,
            [contract.OP_A],
        )

        self.assertEqual(
            self.provider.operations,
            {},
        )

        self.assertEqual(
            client.lookup_operation(
                operation_id=contract.OP_A
            ),
            ("unknown", (10, 20, 30)),
        )

    def test_18_caller_substituted_trust_key_is_known_limit(self):
        """KNOWN LIMIT: the caller controls the store key pin."""

        attacker = Ed25519PrivateKey.generate()

        attacker_key = backend_contract.public_key(
            attacker
        )

        self.provider.response_signer = attacker

        # Deliberately demonstrate the boundary:
        # a caller who can replace its trusted store key
        # can accept responses from the attacker signer.
        substituted_client = self.fixture.client(
            expected_store_public_key=attacker_key,
        )

        self.assertEqual(
            self.fixture.read(substituted_client),
            (10, 20, 30),
        )

        # The original pinned client still refuses the attack.
        original_client = self.fixture.client()

        self.provider.response_signer = attacker

        with self.assertRaises(ValueError):
            self.fixture.read(original_client)


if __name__ == "__main__":
    unittest.main()
