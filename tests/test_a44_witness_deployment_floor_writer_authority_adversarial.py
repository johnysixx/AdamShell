"""A44 / 66.37D: adversarial tests for pinned Ed25519 writer CAS gate.

The gateway is an in-process reference adapter. These tests cannot prove
isolated key custody, TLS, independently durable revocation, or rollback proof.
"""

import shutil
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_witness_deployment_floor_writer_authority_contract as writer_contract

remote = writer_contract.remote


class A44WriterAuthorizedFloorAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.f = writer_contract.A44PinnedWriterAuthorizedFloorContractTests(
            "test_01_public_read_and_lookup_remain_signed"
        )
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def unchanged(self):
        self.assertEqual(self.f.fixture.fixture.read()["epoch"], 1)
        self.assertEqual(self.f.fixture.fixture.operation_count(), 0)

    def test_01_legacy_unsigned_cas_cannot_bypass_writer_gate(self):
        for request in (
            self.f.request(),
            self.f.request(operation_id=remote.floor_contract.OP_B),
        ):
            with self.subTest(request=request[:90]):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(request)
        self.unchanged()

    def test_02_wrong_wire_input_types_fail_closed(self):
        for value in (
            None, "not bytes", bytearray(self.f.authorized()),
            memoryview(self.f.authorized()), {}, [], 42,
        ):
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(value)
        self.unchanged()

    def test_03_malformed_outer_json_and_duplicate_fields_rejected(self):
        invalid = (
            b"", b"{}", b"[]", b"\xff", b"{" + b"x" * 16384 + b"}",
            self.f.authorized() + b" ",
            b'{"writer_id":"a","writer_id":"b"}',
            remote.canonical({"writer_id": "writer-alpha"}),
            remote.canonical({
                **remote.parse_canonical(self.f.authorized()), "extra": True,
            }),
        )
        for payload in invalid:
            with self.subTest(sample=repr(payload)[:50]):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(payload)
        self.unchanged()

    def test_04_malformed_signatures_rejected_without_db_access(self):
        original = remote.parse_canonical(self.f.authorized())
        for invalid in ("00" * 64, "FF" * 64, "zz" * 64, "a" * 127, "", None):
            with self.subTest(signature=str(invalid)[:12]):
                payload = remote.canonical({
                    **original, "writer_signature_hex": invalid,
                })
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(payload)
        self.unchanged()

    def test_05_wrong_writer_signature_cannot_impersonate_known_identity(self):
        for signer in (self.f.bob, self.f.attacker):
            with self.subTest(signer=type(signer).__name__):
                with self.assertRaises(ValueError):
                    self.f.send(self.f.authorized(
                        writer_id="writer-alpha", signer=signer,
                    ))
        self.unchanged()

    def test_06_signed_cas_payload_mutations_invalidate_signature(self):
        original = remote.parse_canonical(self.f.authorized())
        inner = remote.parse_canonical(bytes.fromhex(original["request_hex"]))
        for change in (
            {"operation_id": remote.floor_contract.OP_B},
            {"expected_epoch": 9},
            {"next_epoch": 9},
            {"expected_minimum_generation": 9},
            {"next_minimum_generation": 9},
            {"challenge_hex": (b"z" * 32).hex()},
            {"floor_id": "wrong-floor"},
        ):
            with self.subTest(change=change):
                damaged = {
                    **original,
                    "request_hex": remote.canonical({**inner, **change}).hex(),
                }
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(remote.canonical(damaged))
        self.unchanged()

    def test_07_identity_change_after_signing_is_rejected(self):
        signed = remote.parse_canonical(self.f.authorized())
        for writer_id in ("writer-beta", "writer-charlie", ""):
            with self.subTest(writer_id=writer_id):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(remote.canonical({
                        **signed, "writer_id": writer_id,
                    }))
        self.unchanged()

    def test_08_wrong_signed_authorization_domain_and_version_rejected(self):
        for changes in (
            {"domain": "AdamShell/A44/other/v1"},
            {"version": 2},
            {"version": True},
        ):
            with self.subTest(change=changes):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(self.f.authorized(**changes))
        self.unchanged()

    def test_09_exact_authorized_cas_replay_is_idempotent(self):
        request = self.f.authorized()
        for _ in range(3):
            result = self.f.send(request)
            self.assertEqual(result["status"], "committed")
            self.assertEqual(result["epoch"], 2)
        self.assertEqual(self.f.fixture.fixture.operation_count(), 1)
        self.assertEqual(self.f.fixture.fixture.read()["epoch"], 2)

    def test_10_same_operation_id_cannot_rebind_signed_cas(self):
        self.assertEqual(self.f.send()["status"], "committed")
        rebound = self.f.authorized(
            request=self.f.request(next_minimum_generation=3)
        )
        with self.assertRaises(ValueError):
            self.f.adapter.exchange(rebound)
        self.assertEqual(self.f.fixture.fixture.operation_count(), 1)
        self.assertEqual(self.f.fixture.fixture.read()["minimum_generation"], 2)

    def test_11_competing_writer_cas_has_one_winner(self):
        requests = tuple(
            self.f.authorized(
                writer_id="writer-alpha" if n % 2 == 0 else "writer-beta",
                signer=self.f.alice if n % 2 == 0 else self.f.bob,
                request=self.f.request(operation_id=op),
            )
            for n, op in enumerate((
                remote.floor_contract.OP_A, remote.floor_contract.OP_B,
                remote.floor_contract.OP_C, remote.floor_contract.OP_D,
            ))
        )
        with ThreadPoolExecutor(max_workers=4) as pool:
            replies = list(pool.map(self.f.adapter.exchange, requests))
        statuses = [
            self.f.response(reply, operation="cas", challenge=b"c" * 32)["status"]
            for reply in replies
        ]
        self.assertEqual(statuses.count("committed"), 1)
        self.assertEqual(statuses.count("rejected"), 3)
        self.assertEqual(self.f.fixture.fixture.operation_count(), 1)
        self.assertEqual(self.f.fixture.fixture.read()["epoch"], 2)

    def test_12_revoked_writer_rejected_even_for_previously_signed_request(self):
        signed = self.f.authorized()
        revoked = self.f.make_adapter(revoked_writer_ids=("writer-alpha",))
        with self.assertRaises(ValueError):
            revoked.exchange(signed)
        self.unchanged()
        authorized_beta = self.f.authorized(
            writer_id="writer-beta", signer=self.f.bob,
        )
        self.assertEqual(self.f.send(authorized_beta, adapter=revoked)["status"],
                         "committed")
        with self.assertRaises(ValueError):
            revoked.exchange(signed)
        self.assertEqual(self.f.fixture.fixture.operation_count(), 1)

    def test_13_roster_mutation_cannot_grant_or_replace_writer(self):
        self.f.writer_keys["writer-alpha"] = remote.floor_contract.public_key(
            self.f.attacker
        )
        self.f.writer_keys["writer-charlie"] = remote.floor_contract.public_key(
            self.f.attacker
        )
        for writer_id in ("writer-alpha", "writer-charlie"):
            with self.subTest(writer_id=writer_id):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(self.f.authorized(
                        writer_id=writer_id, signer=self.f.attacker,
                    ))
        self.unchanged()
        self.assertEqual(self.f.send()["status"], "committed")

    def test_14_revocation_list_mutation_cannot_unrevoke_writer(self):
        original = ["writer-alpha"]
        revoked = self.f.make_adapter(revoked_writer_ids=original)
        original.clear()
        with self.assertRaises(ValueError):
            revoked.exchange(self.f.authorized())
        self.unchanged()
        self.assertEqual(self.f.send(
            self.f.authorized(writer_id="writer-beta", signer=self.f.bob),
            adapter=revoked,
        )["status"], "committed")

    def test_15_invalid_writer_key_catalogs_fail_closed(self):
        floor_key = remote.floor_contract.public_key(self.f.fixture.fixture.signer)
        alice_key = remote.floor_contract.public_key(self.f.alice)
        for catalog in (
            None, {}, {"writer-alpha": b"x" * 31},
            {"writer-alpha": bytearray(alice_key)},
            {"writer-alpha": floor_key},
            {"writer-alpha": alice_key, "writer-beta": alice_key},
            {"writer-alpha": alice_key, "writer-beta": None},
        ):
            with self.subTest(catalog=repr(catalog)[:60]):
                with self.assertRaises(ValueError):
                    self.f.make_adapter(writer_public_keys=catalog)
        self.unchanged()

    def test_16_malformed_inner_signed_cas_requests_fail_closed(self):
        for request in (
            b"", b"{}", b"[]", b"\xff",
            self.f.request() + b" ",
            b'{"operation":"cas","operation":"read"}',
            b"x" * 4097,
        ):
            with self.subTest(request=repr(request)[:45]):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(self.f.authorized(request=request))
        self.unchanged()

    def test_17_signed_inner_identity_schema_and_role_confusion_rejected(self):
        for request in (
            self.f.request(operation="read"),
            self.f.request(operation="lookup"),
            self.f.request(domain="other"),
            self.f.request(version=2),
            self.f.request(floor_id="wrong-floor"),
            self.f.request(subject_id="wrong-subject"),
            self.f.request(challenge_hex="not-hex"),
            self.f.request(extra=True),
        ):
            with self.subTest(request=repr(request)[:65]):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(self.f.authorized(request=request))
        self.unchanged()

    def test_18_invalid_signed_monotonic_cas_parameters_rejected(self):
        for change in (
            {"expected_epoch": 0},
            {"expected_epoch": True},
            {"next_epoch": 1},
            {"next_epoch": 3},
            {"expected_minimum_generation": -1},
            {"next_minimum_generation": 0},
            {"next_minimum_generation": "2"},
            {"next_minimum_generation": 1 << 63},
        ):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    self.f.adapter.exchange(self.f.authorized(
                        request=self.f.request(**change)
                    ))
        self.unchanged()

    def test_19_post_commit_reply_failure_recovered_by_original_lookup(self):
        backend_type = type(self.f.fixture.fixture.backend)
        with patch.object(backend_type, "_signed", side_effect=OSError("lost reply")):
            with self.assertRaises(ValueError):
                self.f.adapter.exchange(self.f.authorized())
        self.assertEqual(self.f.fixture.fixture.read()["epoch"], 2)
        self.assertEqual(self.f.fixture.fixture.operation_count(), 1)
        lookup = self.f.send(
            self.f.request("lookup", challenge=b"l" * 32),
            operation="lookup", challenge=b"l" * 32,
        )
        self.assertEqual(lookup["status"], "committed")
        self.assertEqual(self.f.fixture.fixture.operation_count(), 1)

    def test_20_authorized_gateway_cannot_prevent_valid_old_database_rollback(self):
        backup = Path(self.f.fixture.fixture.temp.name) / "old-writer-floor.sqlite3"
        shutil.copy2(self.f.fixture.fixture.path, backup)
        self.assertEqual(self.f.send()["epoch"], 2)
        shutil.copy2(backup, self.f.fixture.fixture.path)
        read = self.f.send(
            self.f.request("read", challenge=b"r" * 32),
            operation="read", challenge=b"r" * 32,
        )
        self.assertEqual(read["epoch"], 1)
        lookup = self.f.send(
            self.f.request("lookup", challenge=b"l" * 32),
            operation="lookup", challenge=b"l" * 32,
        )
        self.assertEqual(lookup["status"], "unknown")
        self.assertEqual(self.f.fixture.fixture.operation_count(), 0)


if __name__ == "__main__":
    unittest.main()
