"""A44 / 66.37B RED: pinned Ed25519 writer-authenticated CAS gateway.

Production module:
core.existence.history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_authority

PinnedWriterAuthorizedWitnessDeploymentFloorTransport.from_sources(
    *, backend, writer_public_keys, revoked_writer_ids=()
) -> exchange(request: bytes) -> bytes

Normal remote-floor wire READ and LOOKUP retain canonical signed-response
semantics. Legacy unsigned CAS MUST fail. A writer-authorized CAS uses an
outer canonical envelope with exactly these fields:
 domain, version, writer_id, request_hex, writer_signature_hex.
The signature is Ed25519 over the canonical ASCII JSON of the first four
fields. domain = AdamShell/A44/authorized-writer-floor-cas/v1, version = 1.
request_hex encodes an original canonical remote-floor CAS request including
its operation_id, expected and next epochs/generations, and challenge.

The gateway must pin a snapshot of writer public keys and revoked IDs, reject
unknown/revoked identities and mutated requests before accessing SQLite, and
preserve backend single-transaction receipts/idempotency. This is an in-process
protocol adapter, NOT TLS, independent server deployment, secure signer custody,
a durable revocation register, nor independent rollback protection.
"""

import importlib
import shutil
import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_witness_deployment_floor_remote_client_contract as remote

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_authority"
)
CLASS = "PinnedWriterAuthorizedWitnessDeploymentFloorTransport"
AUTH_DOMAIN = "AdamShell/A44/authorized-writer-floor-cas/v1"
CLAIMS = frozenset({"domain", "version", "writer_id", "request_hex"})
ENVELOPE = CLAIMS | frozenset({"writer_signature_hex"})


class A44PinnedWriterAuthorizedFloorContractTests(unittest.TestCase):
    def setUp(self):
        module = importlib.import_module(MODULE)
        self.adapter_type = getattr(module, CLASS)
        self.fixture = remote.A44RemoteDeploymentFloorWireContractTests(
            "test_01_wire_read_and_existing_guard_compatibility"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.alice = Ed25519PrivateKey.generate()
        self.bob = Ed25519PrivateKey.generate()
        self.attacker = Ed25519PrivateKey.generate()
        self.writer_keys = {
            "writer-alpha": remote.floor_contract.public_key(self.alice),
            "writer-beta": remote.floor_contract.public_key(self.bob),
        }
        self.adapter = self.make_adapter()

    def make_adapter(self, **changes):
        params = dict(
            backend=self.fixture.fixture.backend,
            writer_public_keys=self.writer_keys,
            revoked_writer_ids=(),
        )
        params.update(changes)
        return self.adapter_type.from_sources(**params)

    def request(self, operation="cas", challenge=b"c" * 32, **changes):
        doc = dict(
            domain=remote.WIRE_DOMAIN,
            version=1,
            operation=operation,
            floor_id=remote.floor_contract.FLOOR_ID,
            subject_id=remote.floor_contract.SUBJECT_ID,
            challenge_hex=challenge.hex(),
        )
        if operation == "cas":
            doc.update(
                operation_id=remote.floor_contract.OP_A,
                expected_epoch=1,
                next_epoch=2,
                expected_minimum_generation=1,
                next_minimum_generation=2,
            )
        elif operation == "lookup":
            doc["operation_id"] = remote.floor_contract.OP_A
        doc.update(changes)
        return remote.canonical(doc)

    def authorized(self, *, writer_id="writer-alpha", signer=None,
                   request=None, **claim_changes):
        if signer is None:
            signer = self.alice if writer_id == "writer-alpha" else self.bob
        if request is None:
            request = self.request()
        claims = dict(
            domain=AUTH_DOMAIN,
            version=1,
            writer_id=writer_id,
            request_hex=request.hex(),
        )
        claims.update(claim_changes)
        signature = signer.sign(remote.canonical(claims))
        return remote.canonical({
            **claims, "writer_signature_hex": signature.hex(),
        })

    def response(self, raw, *, operation, challenge):
        envelope = remote.parse_canonical(raw)
        self.assertEqual(set(envelope), {"message_hex", "signature_hex"})
        pair = (
            bytes.fromhex(envelope["message_hex"]),
            bytes.fromhex(envelope["signature_hex"]),
        )
        return self.fixture.fixture.signed(
            pair, operation=operation, challenge=challenge,
        )

    def send(self, request=None, *, adapter=None, operation="cas",
             challenge=b"c" * 32):
        if request is None:
            request = self.authorized()
        if adapter is None:
            adapter = self.adapter
        return self.response(
            adapter.exchange(request), operation=operation, challenge=challenge,
        )

    def test_01_public_read_and_lookup_remain_signed(self):
        read = self.send(self.request("read", challenge=b"r" * 32),
                         operation="read", challenge=b"r" * 32)
        self.assertEqual((read["epoch"], read["minimum_generation"]), (1, 1))
        lookup = self.send(self.request("lookup", challenge=b"l" * 32),
                           operation="lookup", challenge=b"l" * 32)
        self.assertEqual(lookup["status"], "unknown")
        self.assertEqual(self.fixture.fixture.operation_count(), 0)
        client = self.fixture.make_client(transport=self.adapter)
        self.assertEqual(self.fixture.read(client)["epoch"], 1)

    def test_02_authorized_alice_cas_commits_signed_receipt(self):
        result = self.send()
        self.assertEqual((result["status"], result["epoch"]), ("committed", 2))
        self.assertEqual(self.fixture.fixture.operation_count(), 1)
        lookup = self.send(self.request("lookup", challenge=b"l" * 32),
                           operation="lookup", challenge=b"l" * 32)
        self.assertEqual(lookup["status"], "committed")

    def test_03_authorized_bob_cas_commits(self):
        result = self.send(self.authorized(writer_id="writer-beta", signer=self.bob))
        self.assertEqual(result["status"], "committed")
        self.assertEqual(self.fixture.fixture.operation_count(), 1)

    def test_04_legacy_unsigned_cas_is_rejected_without_mutation(self):
        with self.assertRaises(ValueError):
            self.adapter.exchange(self.request())
        self.assertEqual(self.fixture.fixture.operation_count(), 0)
        self.assertEqual(self.fixture.fixture.read()["epoch"], 1)

    def test_05_unknown_writer_rejected_despite_valid_signature(self):
        with self.assertRaises(ValueError):
            self.send(self.authorized(writer_id="writer-charlie",
                                      signer=self.attacker))
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_06_wrong_writer_signing_key_rejected(self):
        with self.assertRaises(ValueError):
            self.send(self.authorized(writer_id="writer-alpha", signer=self.bob))
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_07_writer_signature_covers_entire_cas_payload(self):
        signed = remote.parse_canonical(self.authorized())
        inner = remote.parse_canonical(bytes.fromhex(signed["request_hex"]))
        for change in (
            {"operation_id": remote.floor_contract.OP_B},
            {"expected_epoch": 9},
            {"next_epoch": 9},
            {"expected_minimum_generation": 9},
            {"next_minimum_generation": 9},
            {"challenge_hex": (b"z" * 32).hex()},
        ):
            with self.subTest(change=change):
                damaged = dict(signed)
                damaged["request_hex"] = remote.canonical({**inner, **change}).hex()
                with self.assertRaises(ValueError):
                    self.adapter.exchange(remote.canonical(damaged))
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_08_writer_identity_bound_to_signature(self):
        signed = remote.parse_canonical(self.authorized())
        signed["writer_id"] = "writer-beta"
        with self.assertRaises(ValueError):
            self.adapter.exchange(remote.canonical(signed))
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_09_outer_domain_or_version_confusion_rejected(self):
        for changes in (
            {"domain": "AdamShell/A44/other/v1"},
            {"version": 2},
            {"version": True},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.adapter.exchange(self.authorized(**changes))
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_10_noncanonical_or_malformed_outer_envelope_rejected(self):
        for invalid in (
            None, "not bytes", b"", b"{}", b"[]", b"\xff",
            b"x" * 20000, self.authorized() + b" ",
            b'{"writer_id":"x","writer_id":"y"}',
            remote.canonical({"domain": AUTH_DOMAIN, "version": 1,
                              "writer_id": "writer-alpha", "request_hex": "00",
                              "writer_signature_hex": "00", "extra": 1}),
        ):
            with self.subTest(payload=repr(invalid)[:65]):
                with self.assertRaises(ValueError):
                    self.adapter.exchange(invalid)
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_11_invalid_signature_or_request_hex_rejected(self):
        valid = remote.parse_canonical(self.authorized())
        for changes in (
            {"writer_signature_hex": "00" * 64},
            {"writer_signature_hex": "GG" * 64},
            {"writer_signature_hex": "00"},
            {"writer_signature_hex": None},
            {"request_hex": "0"},
            {"request_hex": "ZZ"},
            {"request_hex": "ff" * 10000},
        ):
            with self.subTest(changes=repr(changes)[:70]):
                with self.assertRaises(ValueError):
                    self.adapter.exchange(remote.canonical({**valid, **changes}))
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_12_invalid_inner_cas_schema_or_identity_rejected(self):
        for request in (
            self.request(operation="read"),
            self.request(operation="lookup"),
            self.request(floor_id="wrong-floor"),
            self.request(subject_id="wrong-subject"),
            self.request(domain="wrong-domain"),
            self.request(version=2),
            self.request(expected_epoch=True),
            self.request(next_epoch=3),
            self.request(unknown_field=1),
            b'{"operation":"cas","operation":"read"}',
        ):
            with self.subTest(request=repr(request)[:80]):
                with self.assertRaises(ValueError):
                    self.adapter.exchange(self.authorized(request=request))
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_13_revoked_writer_rejected_even_with_valid_signature(self):
        revoked = self.make_adapter(revoked_writer_ids=("writer-alpha",))
        with self.assertRaises(ValueError):
            self.send(adapter=revoked)
        allowed = self.send(
            request=self.authorized(writer_id="writer-beta", signer=self.bob),
            adapter=revoked,
        )
        self.assertEqual(allowed["status"], "committed")

    def test_14_external_writer_roster_mutation_cannot_grant_access(self):
        self.writer_keys["writer-alpha"] = remote.floor_contract.public_key(self.attacker)
        self.writer_keys["writer-charlie"] = remote.floor_contract.public_key(self.attacker)
        with self.assertRaises(ValueError):
            self.send(self.authorized(writer_id="writer-alpha", signer=self.attacker))
        with self.assertRaises(ValueError):
            self.send(self.authorized(writer_id="writer-charlie", signer=self.attacker))
        self.assertEqual(self.send()["status"], "committed")
        self.assertEqual(self.fixture.fixture.operation_count(), 1)

    def test_15_invalid_writer_pins_fail_closed_during_construction(self):
        floor_signer_key = remote.floor_contract.public_key(self.fixture.fixture.signer)
        for writers in (
            None, {}, {"writer-alpha": b"x" * 31},
            {123: remote.floor_contract.public_key(self.alice)},
            {"writer-alpha": self.alice},
            {"writer-alpha": floor_signer_key},
            {"writer-alpha": remote.floor_contract.public_key(self.alice),
             "writer-beta": remote.floor_contract.public_key(self.alice)},
        ):
            with self.subTest(writers=repr(writers)[:70]):
                with self.assertRaises(ValueError):
                    self.make_adapter(writer_public_keys=writers)
        self.assertEqual(self.fixture.fixture.operation_count(), 0)

    def test_16_exact_authorized_replay_is_idempotent(self):
        same = self.authorized()
        self.assertEqual(self.send(same)["status"], "committed")
        self.assertEqual(self.send(same)["status"], "committed")
        self.assertEqual(self.fixture.fixture.operation_count(), 1)

    def test_17_conflicting_signed_cas_is_rejected(self):
        self.assertEqual(self.send()["status"], "committed")
        other_request = self.request(operation_id=remote.floor_contract.OP_B)
        rejection = self.send(self.authorized(writer_id="writer-beta",
                                               signer=self.bob,
                                               request=other_request))
        self.assertEqual(rejection["status"], "rejected")
        self.assertEqual(self.fixture.fixture.operation_count(), 1)
        self.assertEqual(self.fixture.fixture.read()["epoch"], 2)

    def test_18_lost_ack_lookup_original_id_without_retry(self):
        signed = self.authorized()
        class LoseAckAfterCommit:
            def __init__(self, adapter):
                self.adapter = adapter

            def exchange(self, request):
                self.adapter.exchange(request)
                raise TimeoutError("Signed response lost after CAS commit")

        with self.assertRaises(TimeoutError):
            LoseAckAfterCommit(self.adapter).exchange(signed)
        self.assertEqual(self.fixture.fixture.operation_count(), 1)
        lookup = self.send(self.request("lookup", challenge=b"l" * 32),
                           operation="lookup", challenge=b"l" * 32)
        self.assertEqual(lookup["status"], "committed")
        self.assertEqual(self.fixture.fixture.operation_count(), 1)

    def test_19_valid_old_database_rollback_remains_possible(self):
        backup = Path(self.fixture.fixture.temp.name) / "pre-auth-cas.sqlite3"
        shutil.copy2(self.fixture.fixture.path, backup)
        self.assertEqual(self.send()["epoch"], 2)
        shutil.copy2(backup, self.fixture.fixture.path)
        read = self.send(self.request("read", challenge=b"r" * 32),
                         operation="read", challenge=b"r" * 32)
        self.assertEqual(read["epoch"], 1)
        lookup = self.send(self.request("lookup", challenge=b"l" * 32),
                           operation="lookup", challenge=b"l" * 32)
        self.assertEqual(lookup["status"], "unknown")
        client = self.fixture.make_client(transport=self.adapter, minimum_epoch=2)
        with self.assertRaises(ValueError):
            self.fixture.read(client)

    def test_20_writer_signed_read_or_lookup_cannot_publish_cas(self):
        for op in ("read", "lookup"):
            with self.subTest(operation=op):
                with self.assertRaises(ValueError):
                    self.adapter.exchange(self.authorized(request=self.request(op)))
        self.assertEqual(self.fixture.fixture.operation_count(), 0)
        self.assertEqual(self.fixture.fixture.read()["epoch"], 1)


if __name__ == "__main__":
    unittest.main()
