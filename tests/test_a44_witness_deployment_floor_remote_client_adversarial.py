"""A44 / 66.36D: adversarial signed deployment-floor wire-client tests.

Exercises untrusted transport messages, request/reply binding, recovery and
explicit known limits. The test transport is an in-process simulator with NO
authenticated writer authorization or separately protected monotonic root.
"""

import json
import shutil
import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_witness_deployment_floor_remote_client_contract as remote_contract


class A44RemoteDeploymentFloorWireAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.f = remote_contract.A44RemoteDeploymentFloorWireContractTests(
            "test_01_wire_read_and_existing_guard_compatibility"
        )
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def test_01_missing_or_noncallable_transport_rejected(self):
        for invalid in (None, object(), lambda request: b""):
            with self.subTest(transport=repr(invalid)):
                with self.assertRaises(ValueError):
                    self.f.make_client(transport=invalid)
        self.assertEqual(self.f.transport.requests, [])

    def test_02_invalid_read_challenge_never_dispatched(self):
        values = (
            None, "r" * 32, b"r" * 31, b"r" * 33,
            bytearray(b"r" * 32),
        )
        for challenge in values:
            with self.subTest(challenge=repr(challenge)):
                with self.assertRaises(ValueError):
                    with self.f.client.hold(challenge=challenge):
                        pass
        self.assertEqual(self.f.transport.requests, [])

    def test_03_invalid_cas_operation_ids_never_dispatched(self):
        for op in (None, 42, b"a" * 32, "bad", "a" * 31):
            with self.subTest(operation_id=repr(op)):
                with self.assertRaises(ValueError):
                    self.f.client.advance_if_current(
                        operation_id=op,
                        expected_epoch=1,
                        next_epoch=2,
                        expected_minimum_generation=1,
                        next_minimum_generation=2,
                        challenge=b"c" * 32,
                    )
        self.assertEqual(self.f.transport.requests, [])
        self.assertEqual(self.f.fixture.operation_count(), 0)

    def test_04_invalid_cas_counters_never_dispatched(self):
        valid = dict(
            operation_id=remote_contract.floor_contract.OP_A,
            expected_epoch=1,
            next_epoch=2,
            expected_minimum_generation=1,
            next_minimum_generation=2,
            challenge=b"c" * 32,
        )
        changes = (
            {"expected_epoch": True},
            {"next_epoch": 1},
            {"next_epoch": 3},
            {"expected_minimum_generation": -1},
            {"next_minimum_generation": 0},
            {"next_minimum_generation": "2"},
            {"challenge": b"c" * 31},
        )
        for change in changes:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    self.f.client.advance_if_current(**dict(valid, **change))
        self.assertEqual(self.f.transport.requests, [])
        self.assertEqual(self.f.fixture.operation_count(), 0)

    def test_05_invalid_lookup_never_dispatched(self):
        for operation_id in (None, 17, "bad", b"a" * 32):
            with self.subTest(operation_id=repr(operation_id)):
                with self.assertRaises(ValueError):
                    self.f.client.lookup_operation(
                        operation_id=operation_id,
                        challenge=b"l" * 32,
                    )
        for challenge in (None, b"l" * 31, "l" * 32):
            with self.subTest(challenge=repr(challenge)):
                with self.assertRaises(ValueError):
                    self.f.client.lookup_operation(
                        operation_id=remote_contract.floor_contract.OP_A,
                        challenge=challenge,
                    )
        self.assertEqual(self.f.transport.requests, [])

    def test_06_transport_outage_fails_closed(self):
        self.f.transport.outage = True
        with self.assertRaises(ValueError):
            self.f.read()
        with self.assertRaises(ValueError):
            self.f.cas()
        with self.assertRaises(ValueError):
            self.f.lookup()
        self.assertEqual(self.f.transport.requests, [])
        self.assertEqual(self.f.fixture.operation_count(), 0)

    def test_07_malformed_wire_envelopes_rejected(self):
        malformed = (
            b"",
            b"{}",
            b"[]",
            None,
            "not bytes",
            b"\xff",
            b"x" * 16385,
            b'{"message_hex":"00","signature_hex":"00"} ',
            b'{"message_hex":"00","message_hex":"00","signature_hex":"00"}',
            remote_contract.canonical({
                "message_hex": "00",
                "signature_hex": "00",
                "unexpected": 1,
            }),
            remote_contract.canonical({
                "message_hex": "ZZ",
                "signature_hex": "00" * 64,
            }),
        )
        for payload in malformed:
            with self.subTest(payload=repr(payload)[:48]):
                self.f.transport.override = (
                    lambda _valid, _request, p=payload: p
                )
                with self.assertRaises(ValueError):
                    self.f.read()
        self.assertEqual(self.f.fixture.operation_count(), 0)

    def test_08_correctly_signed_noncanonical_payload_rejected(self):
        malformed = (
            b'{} ',
            b'{"x":1,"x":2}',
            b"[]",
            b"\xff",
            b'{"value":NaN}',
        )
        for message in malformed:
            with self.subTest(message=repr(message)):
                signature = self.f.signer.sign(message)
                self.f.transport.override = (
                    lambda _valid, _request, m=message, s=signature:
                    remote_contract.wrap_signed((m, s))
                )
                with self.assertRaises(ValueError):
                    self.f.read()
        self.assertEqual(self.f.fixture.operation_count(), 0)

    def test_09_signed_read_identity_substitution_rejected(self):
        substitutions = (
            ("floor_id", "forged-floor"),
            ("subject_id", "forged-subject"),
            ("authority_id", "forged-authority"),
            ("witness_id", "forged-witness"),
            ("authority_public_key_hex", "0" * 64),
            ("witness_public_key_hex", "f" * 64),
        )
        for field, value in substitutions:
            with self.subTest(field=field):
                self.f.signed_override(
                    lambda doc, name=field, changed=value:
                    {**doc, name: changed}
                )
                with self.assertRaises(ValueError):
                    self.f.read()

    def test_10_signed_read_domain_and_schema_confusion_rejected(self):
        changes = (
            lambda doc: {**doc, "domain": "AdamShell/A44/other/v1"},
            lambda doc: {**doc, "version": True},
            lambda doc: {**doc, "version": 2},
            lambda doc: {**doc, "operation": "lookup"},
            lambda doc: {**doc, "unexpected": "extra"},
            lambda doc: {k: v for k, v in doc.items() if k != "epoch"},
        )
        for index, change in enumerate(changes):
            with self.subTest(case=index):
                self.f.signed_override(change)
                with self.assertRaises(ValueError):
                    self.f.read()

    def test_11_signed_read_counter_tampering_rejected(self):
        changes = (
            {"epoch": 0},
            {"epoch": -1},
            {"epoch": True},
            {"epoch": "1"},
            {"minimum_generation": -1},
            {"minimum_generation": True},
            {"minimum_generation": "1"},
        )
        for change in changes:
            with self.subTest(change=change):
                self.f.signed_override(
                    lambda doc, c=change: {**doc, **c}
                )
                with self.assertRaises(ValueError):
                    self.f.read()

    def test_12_replayed_signed_read_challenge_rejected(self):
        old_request = remote_contract.canonical({
            "domain": remote_contract.WIRE_DOMAIN,
            "version": 1,
            "operation": "read",
            "floor_id": remote_contract.floor_contract.FLOOR_ID,
            "subject_id": remote_contract.floor_contract.SUBJECT_ID,
            "challenge_hex": (b"a" * 32).hex(),
        })
        replay = self.f.transport.exchange(old_request)
        self.f.transport.override = lambda _response, _request: replay
        with self.assertRaises(ValueError):
            self.f.read(challenge=b"b" * 32)
        self.assertEqual(self.f.fixture.operation_count(), 0)

    def test_13_invalid_signature_or_other_signer_rejected(self):
        def corrupt(response, _request):
            envelope = remote_contract.parse_canonical(response)
            envelope["signature_hex"] = "00" * 64
            return remote_contract.canonical(envelope)

        self.f.transport.override = corrupt
        with self.assertRaises(ValueError):
            self.f.read()

        attacker = Ed25519PrivateKey.generate()

        def wrong_signer(response, _request):
            envelope = remote_contract.parse_canonical(response)
            message = bytes.fromhex(envelope["message_hex"])
            return remote_contract.wrap_signed(
                (message, attacker.sign(message))
            )

        self.f.transport.override = wrong_signer
        with self.assertRaises(ValueError):
            self.f.read()

        self.assertEqual(self.f.fixture.operation_count(), 0)

    def test_14_signed_cas_request_binding_rejected_on_substitution(self):
        changes = (
            {"operation_id": remote_contract.floor_contract.OP_B},
            {"expected_epoch": 9},
            {"next_epoch": 9},
            {"expected_minimum_generation": 9},
            {"next_minimum_generation": 9},
            {"status": "unknown"},
            {"version": 2},
        )
        for change in changes:
            with self.subTest(change=change):
                self.f.signed_override(
                    lambda doc, c=change: {**doc, **c}
                )
                with self.assertRaises(ValueError):
                    self.f.cas()

        self.assertEqual(self.f.fixture.operation_count(), 1)
        self.assertEqual(self.f.fixture.read()["epoch"], 2)

    def test_15_signed_committed_cas_cannot_claim_older_state(self):
        for change in (
            {"epoch": 1},
            {"minimum_generation": 1},
        ):
            with self.subTest(change=change):
                self.f.signed_override(
                    lambda doc, c=change: {**doc, **c}
                )
                with self.assertRaises(ValueError):
                    self.f.cas()

        self.f.transport.override = None
        self.assertEqual(self.f.lookup()["status"], "committed")
        self.assertEqual(self.f.fixture.operation_count(), 1)

    def test_16_replayed_cas_acknowledgement_nonce_rejected(self):
        captured = []

        def capture(response, _request):
            captured.append(response)
            return response

        self.f.transport.override = capture
        self.assertEqual(
            self.f.cas(challenge=b"a" * 32)["status"],
            "committed",
        )
        self.assertEqual(len(captured), 1)

        self.f.transport.override = (
            lambda _response, _request: captured[0]
        )
        with self.assertRaises(ValueError):
            self.f.cas(challenge=b"b" * 32)

        self.f.transport.override = None
        self.assertEqual(self.f.lookup()["status"], "committed")
        self.assertEqual(self.f.fixture.operation_count(), 1)

    def test_17_signed_lookup_reply_binding_rejected(self):
        changes = (
            {"operation_id": remote_contract.floor_contract.OP_B},
            {"status": "rejected"},
            {"status": 1},
            {"operation": "read"},
            {"epoch": 0},
            {"challenge_hex": "0" * 64},
        )
        for change in changes:
            with self.subTest(change=change):
                self.f.signed_override(
                    lambda doc, c=change: {**doc, **c}
                )
                with self.assertRaises(ValueError):
                    self.f.lookup()

        self.assertEqual(self.f.fixture.operation_count(), 0)

    def test_18_lost_cas_ack_recovered_only_by_original_lookup(self):
        self.f.transport.lose_cas_reply_once = True

        with self.assertRaises(ValueError):
            self.f.cas()

        self.assertTrue(self.f.transport.lost)
        self.assertEqual(self.f.fixture.operation_count(), 1)
        self.assertEqual(len(self.f.transport.requests), 1)

        self.assertEqual(self.f.lookup()["status"], "committed")
        self.assertEqual(len(self.f.transport.requests), 2)
        self.assertEqual(self.f.fixture.read()["epoch"], 2)

    def test_19_simulated_transport_has_no_writer_authorization(self):
        # KNOWN LIMIT: this in-process test server authenticates no writer.
        # A public-format CAS request can update its SQLite backend.
        challenge = b"z" * 32
        operation_id = remote_contract.floor_contract.OP_A

        request = remote_contract.canonical({
            "domain": remote_contract.WIRE_DOMAIN,
            "version": 1,
            "operation": "cas",
            "floor_id": remote_contract.floor_contract.FLOOR_ID,
            "subject_id": remote_contract.floor_contract.SUBJECT_ID,
            "challenge_hex": challenge.hex(),
            "operation_id": operation_id,
            "expected_epoch": 1,
            "next_epoch": 2,
            "expected_minimum_generation": 1,
            "next_minimum_generation": 2,
        })

        envelope = remote_contract.parse_canonical(
            self.f.transport.exchange(request)
        )

        pair = (
            bytes.fromhex(envelope["message_hex"]),
            bytes.fromhex(envelope["signature_hex"]),
        )

        document = self.f.fixture.signed(
            pair, operation="cas", challenge=challenge,
        )

        self.assertEqual(document["status"], "committed")
        self.assertEqual(self.f.fixture.read()["epoch"], 2)
        self.assertEqual(self.f.fixture.operation_count(), 1)

    def test_20_old_valid_remote_database_rollback_known_limit(self):
        # KNOWN LIMIT: signed transport does not prevent restoring an old
        # valid authority database if the caller's epoch minimum is also old.
        backup = Path(self.f.fixture.temp.name) / "remote-old-floor.sqlite3"
        shutil.copy2(self.f.fixture.path, backup)

        self.assertEqual(self.f.cas()["epoch"], 2)
        self.assertEqual(self.f.read()["epoch"], 2)

        shutil.copy2(backup, self.f.fixture.path)

        self.assertEqual(self.f.read()["epoch"], 1)
        self.assertEqual(self.f.lookup()["status"], "unknown")

        retained = self.f.make_client(minimum_epoch=2)
        with self.assertRaises(ValueError):
            self.f.read(client=retained)

        self.assertEqual(self.f.fixture.operation_count(), 0)


if __name__ == "__main__":
    unittest.main()
