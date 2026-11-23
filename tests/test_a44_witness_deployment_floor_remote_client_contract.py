"""A44 / 66.36B RED: pinned wire client for independently hosted floor authority.

Production target:
core.existence.history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_remote_client

PinnedRemoteSignedWitnessDeploymentFloor.from_transport(*, transport,
    expected_floor_id, expected_floor_public_key, expected_subject_id,
    expected_authority_id, expected_authority_public_key, expected_witness_id,
    expected_witness_public_key, minimum_epoch)

The client exposes hold(challenge), advance_if_current(..., challenge), and
lookup_operation(operation_id, challenge). Its transport offers exactly one
exchange(request: bytes) -> bytes boundary. All requests/responses are bounded
canonical ASCII JSON. Wire reply envelope holds message_hex and signature_hex.
All replies are Ed25519-signed by the pinned floor key; verify the semantic
request binding and retained minimum epoch, not only signature correctness.

The in-process transport fixture is NOT a deployed independent service and
provides NO authenticated write authorization or TLS guarantees. A real
service must separately enforce writer authentication, rate limits, protected
key custody, monotonic storage, and authenticated initial pin distribution.
"""

import importlib
import json
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_witness_deployment_floor_sqlite_cas_contract as floor_contract

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_remote_client"
)
CLASS = "PinnedRemoteSignedWitnessDeploymentFloor"
WIRE_DOMAIN = "AdamShell/A44/remote-floor-transport/v1"
BASE = frozenset({
    "domain", "version", "operation", "floor_id", "subject_id", "challenge_hex",
})
CAS = BASE | frozenset({
    "operation_id", "expected_epoch", "next_epoch",
    "expected_minimum_generation", "next_minimum_generation",
})
LOOKUP = BASE | frozenset({"operation_id"})


def canonical(doc):
    return json.dumps(
        doc, sort_keys=True, ensure_ascii=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("ascii")


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate transport property")
        result[key] = value
    return result


def invalid_constant(_value):
    raise ValueError("Nonfinite transport number")


def parse_canonical(payload):
    if type(payload) is not bytes or len(payload) > 16384 or not payload:
        raise ValueError("Invalid transport bytes")
    doc = json.loads(
        payload.decode("ascii"),
        object_pairs_hook=unique,
        parse_constant=invalid_constant,
    )
    if type(doc) is not dict or canonical(doc) != payload:
        raise ValueError("Noncanonical transport document")
    return doc


def wrap_signed(pair):
    message, signature = pair
    return canonical({"message_hex": message.hex(), "signature_hex": signature.hex()})


class SimulatedWireFloorServer:
    """One-process loopback only; neither TLS nor an authorization service."""

    def __init__(self, backend):
        self.backend = backend
        self.requests = []
        self.override = None
        self.outage = False
        self.lose_cas_reply_once = False
        self.lost = False

    def exchange(self, request):
        if self.outage:
            raise TimeoutError("Simulated transport outage")
        doc = parse_canonical(request)
        operation = doc.get("operation")
        expected_fields = {"read": BASE, "cas": CAS, "lookup": LOOKUP}.get(operation)
        if expected_fields is None or set(doc) != expected_fields:
            raise ValueError("Invalid wire request fields")
        if (
            doc["domain"] != WIRE_DOMAIN
            or type(doc["version"]) is not int or doc["version"] != 1
            or doc["floor_id"] != floor_contract.FLOOR_ID
            or doc["subject_id"] != floor_contract.SUBJECT_ID
            or type(doc["challenge_hex"]) is not str
            or len(doc["challenge_hex"]) != 64
        ):
            raise ValueError("Invalid wire request identity/version/challenge")
        challenge = bytes.fromhex(doc["challenge_hex"])
        self.requests.append(doc)
        if operation == "read":
            with self.backend.hold(challenge=challenge) as pair:
                response = wrap_signed(pair)
        elif operation == "cas":
            pair = self.backend.advance_if_current(
                operation_id=doc["operation_id"],
                expected_epoch=doc["expected_epoch"],
                next_epoch=doc["next_epoch"],
                expected_minimum_generation=doc["expected_minimum_generation"],
                next_minimum_generation=doc["next_minimum_generation"],
                challenge=challenge,
            )
            if self.lose_cas_reply_once and not self.lost:
                self.lost = True
                raise TimeoutError("Commit completed but CAS acknowledgement lost")
            response = wrap_signed(pair)
        else:
            pair = self.backend.lookup_operation(
                operation_id=doc["operation_id"], challenge=challenge,
            )
            response = wrap_signed(pair)
        if self.override is not None:
            return self.override(response, doc)
        return response


class A44RemoteDeploymentFloorWireContractTests(unittest.TestCase):
    def setUp(self):
        module = importlib.import_module(MODULE)
        self.client_type = getattr(module, CLASS)
        self.fixture = floor_contract.A44WitnessDeploymentFloorSQLiteCASContractTests(
            "test_01_bootstrap_signed_initial_read"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.transport = SimulatedWireFloorServer(self.fixture.backend)
        self.signer = self.fixture.signer
        self.client = self.make_client()

    def make_client(self, **changes):
        kwargs = dict(
            transport=self.transport,
            expected_floor_id=floor_contract.FLOOR_ID,
            expected_floor_public_key=floor_contract.public_key(self.signer),
            expected_subject_id=floor_contract.SUBJECT_ID,
            expected_authority_id=self.fixture.authority_id,
            expected_authority_public_key=self.fixture.authority_key,
            expected_witness_id=self.fixture.witness_id,
            expected_witness_public_key=self.fixture.witness_key,
            minimum_epoch=1,
        )
        kwargs.update(changes)
        return self.client_type.from_transport(**kwargs)

    def read(self, client=None, challenge=b"r" * 32):
        if client is None:
            client = self.client
        with client.hold(challenge=challenge) as pair:
            return self.fixture.signed(pair, operation="read", challenge=challenge)

    def cas(self, client=None, operation_id=floor_contract.OP_A,
            expected_epoch=1, next_epoch=2,
            expected_minimum_generation=1, next_minimum_generation=2,
            challenge=b"c" * 32):
        if client is None:
            client = self.client
        pair = client.advance_if_current(
            operation_id=operation_id, expected_epoch=expected_epoch,
            next_epoch=next_epoch,
            expected_minimum_generation=expected_minimum_generation,
            next_minimum_generation=next_minimum_generation,
            challenge=challenge,
        )
        return self.fixture.signed(pair, operation="cas", challenge=challenge)

    def lookup(self, client=None, operation_id=floor_contract.OP_A, challenge=b"l" * 32):
        if client is None:
            client = self.client
        pair = client.lookup_operation(operation_id=operation_id, challenge=challenge)
        return self.fixture.signed(pair, operation="lookup", challenge=challenge)

    def signed_override(self, change):
        def override(response, _request):
            pair = parse_canonical(response)
            doc = json.loads(bytes.fromhex(pair["message_hex"]).decode("ascii"))
            changed = change(doc)
            message = canonical(changed)
            return wrap_signed((message, self.signer.sign(message)))
        self.transport.override = override

    def test_01_wire_read_and_existing_guard_compatibility(self):
        self.assertEqual(self.read()["minimum_generation"], 1)
        gate = self.fixture.gate(backend=self.client)
        self.assertEqual(gate.read_generation(), 1)
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_02_canonical_wire_request_has_no_private_signer(self):
        self.read()
        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(set(request), BASE)
        self.assertEqual(request["challenge_hex"], (b"r" * 32).hex())
        self.assertEqual(request["domain"], WIRE_DOMAIN)
        self.assertFalse(hasattr(self.client, "signer"))
        self.assertFalse(hasattr(self.client, "private_key"))
        self.assertFalse(hasattr(self.client, "backend"))
        self.assertFalse(hasattr(self.client, "_path"))

    def test_03_signed_cas_and_lookup_survive_server_reopen(self):
        self.assertEqual(self.cas()["status"], "committed")
        self.transport.backend = self.fixture.reopened()
        self.assertEqual(self.read()["epoch"], 2)
        self.assertEqual(self.lookup()["status"], "committed")
        self.assertEqual(self.fixture.operation_count(), 1)

    def test_04_stale_cas_is_signed_rejection_not_publication(self):
        self.cas()
        reply = self.cas(operation_id=floor_contract.OP_B)
        self.assertEqual(reply["status"], "rejected")
        self.assertEqual(reply["epoch"], 2)
        self.assertEqual(self.fixture.operation_count(), 1)
        self.assertEqual(self.lookup(operation_id=floor_contract.OP_B)["status"], "unknown")

    def test_05_same_operation_is_idempotent_over_wire(self):
        self.assertEqual(self.cas()["status"], "committed")
        self.assertEqual(self.cas()["status"], "committed")
        self.assertEqual(self.fixture.operation_count(), 1)
        self.assertEqual(self.lookup()["status"], "committed")

    def test_06_lost_cas_ack_requires_lookup_not_blind_retry(self):
        self.transport.lose_cas_reply_once = True
        with self.assertRaises(ValueError):
            self.cas()
        self.assertTrue(self.transport.lost)
        self.assertEqual(self.fixture.operation_count(), 1)
        self.assertEqual(len(self.transport.requests), 1)
        self.assertEqual(self.lookup()["status"], "committed")
        self.assertEqual(len(self.transport.requests), 2)

    def test_07_wrong_signing_public_key_pin_fails_closed(self):
        attacker = Ed25519PrivateKey.generate()
        client = self.make_client(
            expected_floor_public_key=floor_contract.public_key(attacker)
        )
        with self.assertRaises(ValueError):
            self.read(client)
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_08_signature_corruption_rejected(self):
        def corrupt(response, _request):
            doc = parse_canonical(response)
            doc["signature_hex"] = "00" * 64
            return canonical(doc)
        self.transport.override = corrupt
        with self.assertRaises(ValueError):
            self.read()

    def test_09_authenticated_but_wrong_identity_and_keys_rejected(self):
        for field, wrong in (
            ("floor_id", "forged-floor"),
            ("subject_id", "forged-subject"),
            ("authority_id", "forged-authority"),
            ("witness_id", "forged-witness"),
            ("authority_public_key_hex", "0" * 64),
            ("witness_public_key_hex", "f" * 64),
        ):
            with self.subTest(field=field):
                self.signed_override(lambda doc, f=field, w=wrong: {**doc, f: w})
                with self.assertRaises(ValueError):
                    self.read()
        self.transport.override = None

    def test_10_replayed_signed_read_with_old_challenge_rejected(self):
        replay = self.transport.exchange(canonical({
            "domain": WIRE_DOMAIN, "version": 1, "operation": "read",
            "floor_id": floor_contract.FLOOR_ID,
            "subject_id": floor_contract.SUBJECT_ID,
            "challenge_hex": (b"a" * 32).hex(),
        }))
        self.transport.override = lambda _response, _request: replay
        with self.assertRaises(ValueError):
            self.read(challenge=b"b" * 32)

    def test_11_retained_epoch_rejects_old_signed_service_floor(self):
        client = self.make_client(minimum_epoch=2)
        with self.assertRaises(ValueError):
            self.read(client)
        self.assertEqual(self.cas()["epoch"], 2)
        self.assertEqual(self.read(client)["epoch"], 2)

    def test_12_signed_domain_version_and_operation_confusion_rejected(self):
        for change in (
            {"domain": "AdamShell/A44/other/v1"},
            {"version": 2},
            {"operation": "lookup"},
            {"minimum_generation": True},
            {"epoch": "1"},
            {"challenge_hex": "0" * 64},
        ):
            with self.subTest(change=change):
                self.signed_override(lambda doc, c=change: {**doc, **c})
                with self.assertRaises(ValueError):
                    self.read()
        self.transport.override = None

    def test_13_cas_reply_must_bind_original_operation_and_parameters(self):
        for change in (
            {"operation_id": floor_contract.OP_B},
            {"expected_epoch": 9},
            {"next_epoch": 9},
            {"expected_minimum_generation": 9},
            {"next_minimum_generation": 9},
            {"status": "unknown"},
        ):
            with self.subTest(change=change):
                self.signed_override(lambda doc, c=change: {**doc, **c})
                with self.assertRaises(ValueError):
                    self.cas(operation_id=floor_contract.OP_A)
        # A prior committed CAS is permissible on subsequent same-ID attempts.
        self.assertEqual(self.fixture.operation_count(), 1)
        self.transport.override = None

    def test_14_lookup_reply_must_bind_original_operation_id(self):
        self.signed_override(lambda doc: {**doc, "operation_id": floor_contract.OP_B})
        with self.assertRaises(ValueError):
            self.lookup(operation_id=floor_contract.OP_A)
        self.transport.override = None
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_15_noncanonical_or_malformed_reply_envelope_rejected(self):
        for response in (
            b"{}", b"", None, "not bytes", b"[]",
            b'{"message_hex":"00","signature_hex":"00","extra":1}',
            b'{"message_hex":"00","message_hex":"00","signature_hex":"00"}',
            b'{"message_hex":"00","signature_hex":"00"} ',
            b"a" * 20000,
        ):
            with self.subTest(response=repr(response)[:30]):
                self.transport.override = lambda _original, _request, r=response: r
                with self.assertRaises(ValueError):
                    self.read()
        self.transport.override = None

    def test_16_transport_outage_fails_closed_no_cas(self):
        self.transport.outage = True
        with self.assertRaises(ValueError):
            self.read()
        with self.assertRaises(ValueError):
            self.cas()
        with self.assertRaises(ValueError):
            self.lookup()
        self.assertEqual(self.transport.requests, [])
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_17_invalid_cas_inputs_do_not_cross_transport_boundary(self):
        valid = dict(
            operation_id=floor_contract.OP_A,
            expected_epoch=1, next_epoch=2,
            expected_minimum_generation=1, next_minimum_generation=2,
            challenge=b"c" * 32,
        )
        for change in (
            {"operation_id": "bad"},
            {"expected_epoch": True},
            {"next_epoch": 1},
            {"next_minimum_generation": 0},
            {"challenge": b"x" * 31},
        ):
            with self.subTest(change=change):
                request = dict(valid, **change)
                with self.assertRaises(ValueError):
                    self.client.advance_if_current(**request)
        self.assertEqual(self.transport.requests, [])
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_18_wrong_initial_trust_pins_fail_closed(self):
        for change in (
            {"expected_floor_id": ""},
            {"expected_floor_public_key": b"x" * 31},
            {"expected_subject_id": "forged-subject"},
            {"expected_authority_public_key": b"x" * 31},
            {"expected_witness_public_key": b"x" * 31},
            {"minimum_epoch": 0},
        ):
            with self.subTest(change=change):
                try:
                    client = self.make_client(**change)
                except ValueError:
                    pass
                else:
                    with self.assertRaises(ValueError):
                        self.read(client)
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_19_wire_read_hold_is_not_server_side_transaction(self):
        with self.client.hold(challenge=b"r" * 32) as pair:
            before = self.fixture.signed(pair, operation="read", challenge=b"r" * 32)
            self.assertEqual(before["epoch"], 1)
            self.assertEqual(self.fixture.cas()["epoch"], 2)
        self.assertEqual(self.read()["epoch"], 2)
        # A bounded signed RPC snapshot does not lock the remote authority.

    def test_20_client_contains_no_private_signer_or_sqlite_path(self):
        self.assertNotIn("signer", dir(self.client))
        self.assertNotIn("_path", dir(self.client))
        self.assertNotIn("backend", dir(self.client))
        self.assertEqual(self.read()["epoch"], 1)


if __name__ == "__main__":
    unittest.main()
