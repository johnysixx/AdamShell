"""A44 / 66.38B: versioned signed writer-policy authority contract.

Production API:

VersionedWriterPolicyAuthority.from_signed_policy(
    *,
    backend,
    expected_policy_id,
    expected_policy_public_key,
    signed_policy,
    minimum_policy_epoch,
    expected_policy_sha256,
)

authority.publish_policy(*, signed_policy)

VersionedWriterPolicyGateway.from_authority(*, authority)
gateway.exchange(request: bytes) -> bytes

The policy signer is separate from floor, provisioning authority, witness,
and writer keys. A policy is a tuple of canonical ASCII JSON bytes and a
64-byte Ed25519 signature. Its SHA-256 is over the exact message bytes.

The trusted bootstrap digest pins the exact initial policy document.
The retained minimum epoch rejects older bootstrap documents.

Subsequent policies must have consecutive epochs and bind the exact
previous policy digest. Publication must be serialized with authorized
CAS execution. Gateway instances must share one live authority and consult
its current policy on every CAS; they cannot retain independent writer
authorization snapshots.

Revoked identities are permanent tombstones within this policy lineage.
Active writer keys may be rotated. Removing revocation tombstones or
reactivating a revoked identity is forbidden in this reference contract.

Public READ and LOOKUP remain compatible with the existing signed floor
wire protocol. Legacy unsigned CAS and v1 writer CAS are rejected.
The v2 writer signature binds the current policy identity, epoch, digest,
writer identity, and complete inner CAS request.

This is an in-process reference authority, not durable policy storage,
independent rollback protection, secure key custody, TLS, or a guarantee
that legacy gateways have been retired from a real deployment.
"""

import hashlib
import importlib
import sys
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_witness_deployment_floor_writer_authority_contract as writer

remote = writer.remote

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy"
)

POLICY_DOMAIN = "AdamShell/A44/writer-floor-policy/v1"
CAS_DOMAIN = "AdamShell/A44/authorized-writer-floor-cas/v2"
POLICY_ID = "deployment-floor-writer-policy"
GENESIS_PREVIOUS = "0" * 64


def public_key(signer):
    return remote.floor_contract.public_key(signer)


def digest(policy):
    return hashlib.sha256(policy[0]).hexdigest()


class A44VersionedWriterPolicyContractTests(unittest.TestCase):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.authority_type = module.VersionedWriterPolicyAuthority
        self.gateway_type = module.VersionedWriterPolicyGateway

        self.f = writer.A44PinnedWriterAuthorizedFloorContractTests(
            "test_01_public_read_and_lookup_remain_signed"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.backend = self.f.fixture.fixture.backend
        self.root = Ed25519PrivateKey.generate()
        self.root_key = public_key(self.root)

        self.initial = self.policy()
        self.authority = self.make_authority()
        self.gateway = self.make_gateway()

    def policy(
        self,
        *,
        epoch=1,
        previous=None,
        writers=None,
        revoked=(),
        signer=None,
        **changes,
    ):
        if previous is None:
            previous = GENESIS_PREVIOUS

        if writers is None:
            writers = self.f.writer_keys

        if signer is None:
            signer = self.root

        document = {
            "domain": POLICY_DOMAIN,
            "version": 1,
            "policy_id": POLICY_ID,
            "floor_id": self.backend.floor_id,
            "subject_id": self.backend.subject_id,
            "floor_public_key_hex": public_key(
                self.backend.signer
            ).hex(),
            "policy_epoch": epoch,
            "previous_policy_sha256": previous,
            "writer_public_keys": {
                identity: key.hex()
                for identity, key in writers.items()
            },
            "revoked_writer_ids": sorted(revoked),
        }

        document.update(changes)

        message = remote.canonical(document)

        return message, signer.sign(message)

    def next_policy(self, previous=None, **changes):
        if previous is None:
            previous = self.initial

        document = remote.parse_canonical(previous[0])

        params = {
            "epoch": document["policy_epoch"] + 1,
            "previous": digest(previous),
            "writers": {
                identity: bytes.fromhex(key)
                for identity, key in
                document["writer_public_keys"].items()
            },
            "revoked": tuple(document["revoked_writer_ids"]),
        }

        params.update(changes)

        return self.policy(**params)

    def make_authority(self, policy=None, **changes):
        if policy is None:
            policy = self.initial

        params = {
            "backend": self.backend,
            "expected_policy_id": POLICY_ID,
            "expected_policy_public_key": self.root_key,
            "signed_policy": policy,
            "minimum_policy_epoch": 1,
            "expected_policy_sha256": digest(policy),
        }

        params.update(changes)

        return self.authority_type.from_signed_policy(**params)

    def make_gateway(self, authority=None):
        if authority is None:
            authority = self.authority

        return self.gateway_type.from_authority(
            authority=authority
        )

    def publish(self, policy):
        return self.authority.publish_policy(
            signed_policy=policy
        )

    def authorized(
        self,
        *,
        policy=None,
        writer_id="writer-alpha",
        signer=None,
        request=None,
        **changes,
    ):
        if policy is None:
            policy = self.initial

        if signer is None:
            signer = (
                self.f.alice
                if writer_id == "writer-alpha"
                else self.f.bob
            )

        if request is None:
            request = self.f.request()

        document = remote.parse_canonical(policy[0])

        claims = {
            "domain": CAS_DOMAIN,
            "version": 2,
            "policy_id": document["policy_id"],
            "policy_epoch": document["policy_epoch"],
            "policy_sha256": digest(policy),
            "writer_id": writer_id,
            "request_hex": request.hex(),
        }

        claims.update(changes)

        signature = signer.sign(
            remote.canonical(claims)
        )

        return remote.canonical({
            **claims,
            "writer_signature_hex": signature.hex(),
        })

    def send(self, request=None, gateway=None):
        if request is None:
            request = self.authorized()

        if gateway is None:
            gateway = self.gateway

        return self.f.response(
            gateway.exchange(request),
            operation="cas",
            challenge=b"c" * 32,
        )

    def unchanged(self):
        self.assertEqual(
            self.f.fixture.fixture.read()["epoch"], 1
        )
        self.assertEqual(
            self.f.fixture.fixture.operation_count(), 0
        )

    def next_cas(self):
        return self.f.request(
            operation_id=remote.floor_contract.OP_B,
            expected_epoch=2,
            next_epoch=3,
            expected_minimum_generation=2,
            next_minimum_generation=3,
        )

    def test_01_signed_policy_bootstrap_and_authorized_cas(self):
        result = self.send()

        self.assertEqual(
            (result["status"], result["epoch"]),
            ("committed", 2),
        )

        self.assertEqual(
            self.f.fixture.fixture.operation_count(), 1
        )

    def test_02_public_read_and_lookup_remain_compatible(self):
        client = self.f.fixture.make_client(
            transport=self.gateway
        )

        self.assertEqual(
            self.f.fixture.read(client)["epoch"], 1
        )

        raw = self.gateway.exchange(
            self.f.request(
                "lookup",
                challenge=b"l" * 32,
            )
        )

        result = self.f.response(
            raw,
            operation="lookup",
            challenge=b"l" * 32,
        )

        self.assertEqual(result["status"], "unknown")
        self.unchanged()

    def test_03_wrong_policy_root_key_rejected(self):
        with self.assertRaises(ValueError):
            self.make_authority(
                expected_policy_public_key=public_key(
                    self.f.attacker
                )
            )

        self.unchanged()

    def test_04_tampered_policy_message_or_signature_rejected(self):
        message, signature = self.initial

        document = remote.parse_canonical(message)
        document["revoked_writer_ids"] = ["writer-alpha"]

        cases = (
            (
                remote.canonical(document),
                signature,
            ),
            (
                message,
                bytes([signature[0] ^ 1]) + signature[1:],
            ),
        )

        for policy in cases:
            with self.subTest(policy=policy[0][:40]):
                with self.assertRaises(ValueError):
                    self.make_authority(policy)

        self.unchanged()

    def test_05_policy_identity_and_floor_scope_must_match(self):
        for changes in (
            {"policy_id": "wrong-policy"},
            {"floor_id": "wrong-floor"},
            {"subject_id": "wrong-subject"},
            {"floor_public_key_hex": "ab" * 32},
            {"domain": "wrong-domain"},
            {"version": 2},
            {"version": True},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.make_authority(
                        self.policy(**changes)
                    )

        self.unchanged()

    def test_06_policy_root_must_not_reuse_writer_or_floor_keys(self):
        for signer in (
            self.f.alice,
            self.backend.signer,
        ):
            with self.subTest(signer=public_key(signer).hex()):
                policy = self.policy(signer=signer)

                with self.assertRaises(ValueError):
                    self.make_authority(
                        policy,
                        expected_policy_public_key=public_key(signer),
                    )

        self.unchanged()

    def test_07_bootstrap_requires_exact_retained_policy_digest(self):
        with self.assertRaises(ValueError):
            self.make_authority(
                expected_policy_sha256="ab" * 32
            )

        alternate = self.policy(
            revoked=("writer-alpha",)
        )

        with self.assertRaises(ValueError):
            self.make_authority(
                alternate,
                expected_policy_sha256=digest(self.initial),
            )

        self.unchanged()

    def test_08_retained_policy_epoch_rejects_old_bootstrap(self):
        with self.assertRaises(ValueError):
            self.make_authority(
                minimum_policy_epoch=2
            )

        second = self.next_policy()

        restarted = self.make_authority(
            second,
            minimum_policy_epoch=2,
        )

        gateway = self.make_gateway(restarted)

        with self.assertRaises(ValueError):
            gateway.exchange(self.authorized())

        result = self.send(
            self.authorized(policy=second),
            gateway=gateway,
        )

        self.assertEqual(result["status"], "committed")

    def test_09_policy_publication_requires_trusted_signature(self):
        unauthorized = self.next_policy(
            signer=self.f.attacker,
            revoked=("writer-alpha",),
        )

        with self.assertRaises(ValueError):
            self.publish(unauthorized)

        self.unchanged()

        self.assertEqual(
            self.send()["status"], "committed"
        )

    def test_10_policy_updates_must_be_consecutive_and_chained(self):
        for policy in (
            self.next_policy(epoch=3),
            self.policy(epoch=2, previous="ab" * 32),
            self.next_policy(epoch=True),
            self.next_policy(epoch=0),
            self.next_policy(epoch=1 << 63),
        ):
            with self.subTest(policy=policy[0][:80]):
                with self.assertRaises(ValueError):
                    self.publish(policy)

        self.unchanged()

        self.assertEqual(
            self.send()["status"], "committed"
        )

    def test_11_old_or_equivocating_policy_cannot_replace_current(self):
        second = self.next_policy()
        self.publish(second)

        equivocation = self.next_policy(
            revoked=("writer-alpha",)
        )

        for policy in (
            self.initial,
            equivocation,
        ):
            with self.subTest(policy=policy[0][:50]):
                with self.assertRaises(ValueError):
                    self.publish(policy)

        self.assertEqual(
            self.send(
                self.authorized(policy=second)
            )["status"],
            "committed",
        )

    def test_12_revocation_applies_to_all_shared_gateway_instances(self):
        old_gateway = self.gateway
        another_gateway = self.make_gateway()

        second = self.next_policy(
            revoked=("writer-alpha",)
        )

        self.publish(second)

        for gateway in (
            old_gateway,
            another_gateway,
            self.make_gateway(),
        ):
            for policy in (
                self.initial,
                second,
            ):
                with self.subTest(
                    gateway=id(gateway),
                    policy=digest(policy),
                ):
                    with self.assertRaises(ValueError):
                        gateway.exchange(
                            self.authorized(policy=policy)
                        )

        self.unchanged()

        result = self.send(
            self.authorized(
                policy=second,
                writer_id="writer-beta",
                signer=self.f.bob,
            ),
            gateway=old_gateway,
        )

        self.assertEqual(result["status"], "committed")

    def test_13_rotation_rejects_old_key_on_existing_gateway(self):
        replacement_keys = dict(self.f.writer_keys)

        replacement_keys["writer-alpha"] = public_key(
            self.f.attacker
        )

        second = self.next_policy(
            writers=replacement_keys
        )

        self.publish(second)

        with self.assertRaises(ValueError):
            self.gateway.exchange(
                self.authorized(policy=second)
            )

        with self.assertRaises(ValueError):
            self.gateway.exchange(
                self.authorized()
            )

        self.unchanged()

        result = self.send(
            self.authorized(
                policy=second,
                signer=self.f.attacker,
            )
        )

        self.assertEqual(
            (result["status"], result["epoch"]),
            ("committed", 2),
        )

    def test_14_revocation_tombstones_cannot_be_removed(self):
        second = self.next_policy(
            revoked=("writer-alpha",)
        )

        self.publish(second)

        removed = self.next_policy(
            second,
            revoked=(),
        )

        removed_identity = self.next_policy(
            second,
            writers={
                "writer-beta": public_key(self.f.bob)
            },
            revoked=(),
        )

        for policy in (
            removed,
            removed_identity,
        ):
            with self.subTest(policy=digest(policy)):
                with self.assertRaises(ValueError):
                    self.publish(policy)

        with self.assertRaises(ValueError):
            self.gateway.exchange(
                self.authorized(policy=second)
            )

        self.unchanged()

    def test_15_cas_must_bind_exact_current_policy_identity_epoch_digest(self):
        second = self.next_policy()
        self.publish(second)

        for changes in (
            {"policy_id": "wrong-policy"},
            {"policy_epoch": 1},
            {"policy_epoch": 3},
            {"policy_epoch": True},
            {"policy_sha256": digest(self.initial)},
            {"policy_sha256": "ab" * 32},
            {"domain": writer.AUTH_DOMAIN},
            {"version": 1},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.gateway.exchange(
                        self.authorized(
                            policy=second,
                            **changes,
                        )
                    )

        self.unchanged()

        self.assertEqual(
            self.send(
                self.authorized(policy=second)
            )["status"],
            "committed",
        )

    def test_16_legacy_unsigned_and_v1_writer_cas_are_rejected(self):
        for request in (
            self.f.request(),
            self.f.authorized(),
        ):
            with self.subTest(request=request[:65]):
                with self.assertRaises(ValueError):
                    self.gateway.exchange(request)

        self.unchanged()

    def test_17_current_policy_cas_replay_remains_idempotent(self):
        authorized = self.authorized()

        for _ in range(3):
            self.assertEqual(
                self.send(authorized)["status"],
                "committed",
            )

        self.assertEqual(
            self.f.fixture.fixture.operation_count(), 1
        )

        second = self.next_policy()
        self.publish(second)

        with self.assertRaises(ValueError):
            self.gateway.exchange(authorized)

        result = self.f.response(
            self.gateway.exchange(
                self.f.request(
                    "lookup",
                    challenge=b"l" * 32,
                )
            ),
            operation="lookup",
            challenge=b"l" * 32,
        )

        self.assertEqual(result["status"], "committed")

        self.assertEqual(
            self.f.fixture.fixture.operation_count(), 1
        )

    def test_18_noncanonical_policy_and_invalid_rosters_fail_closed(self):
        message = self.initial[0] + b" "

        noncanonical = (
            message,
            self.root.sign(message),
        )

        invalid_policies = (
            noncanonical,
            self.policy(writer_public_keys={}),
            self.policy(
                writer_public_keys={
                    "writer-alpha": "ff"
                }
            ),
            self.policy(
                writer_public_keys={
                    "writer-alpha": public_key(
                        self.f.alice
                    ).hex(),
                    "writer-beta": public_key(
                        self.f.alice
                    ).hex(),
                }
            ),
            self.policy(
                writer_public_keys={
                    "writer-alpha": self.root_key.hex()
                }
            ),
            self.policy(
                revoked=("writer-unknown",)
            ),
            self.policy(
                revoked_writer_ids=[
                    "writer-alpha",
                    "writer-alpha",
                ]
            ),
            self.policy(unknown_field=1),
        )

        for policy in invalid_policies:
            with self.subTest(policy=digest(policy)):
                with self.assertRaises(ValueError):
                    self.make_authority(policy)

        self.unchanged()

    def test_19_policy_publication_serializes_with_inflight_cas(self):
        entered = threading.Event()
        release = threading.Event()
        publication_started = threading.Event()
        publication_done = threading.Event()

        backend_type = type(self.backend)
        original_cas = backend_type.advance_if_current

        second = self.next_policy(
            revoked=("writer-alpha",)
        )

        request = self.authorized()

        def blocking_cas(backend, **kwargs):
            entered.set()

            if not release.wait(10):
                raise TimeoutError("Test CAS release timed out")

            return original_cas(
                backend,
                **kwargs,
            )

        def publish_second():
            publication_started.set()

            try:
                self.publish(second)
            finally:
                publication_done.set()

        with patch.object(
            backend_type,
            "advance_if_current",
            blocking_cas,
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                cas_future = pool.submit(
                    self.gateway.exchange,
                    request,
                )

                try:
                    self.assertTrue(
                        entered.wait(5)
                    )

                    update_future = pool.submit(
                        publish_second
                    )

                    self.assertTrue(
                        publication_started.wait(5)
                    )

                    self.assertFalse(
                        publication_done.wait(0.2),
                        "Policy changed during authorized CAS",
                    )

                finally:
                    release.set()

                raw = cas_future.result(timeout=10)
                update_future.result(timeout=10)

        result = self.f.response(
            raw,
            operation="cas",
            challenge=b"c" * 32,
        )

        self.assertEqual(
            result["status"], "committed"
        )

        self.assertTrue(publication_done.is_set())

        with self.assertRaises(ValueError):
            self.gateway.exchange(
                self.authorized(
                    policy=second,
                    request=self.next_cas(),
                )
            )

        result = self.send(
            self.authorized(
                policy=second,
                writer_id="writer-beta",
                signer=self.f.bob,
                request=self.next_cas(),
            )
        )

        self.assertEqual(
            (result["status"], result["epoch"]),
            ("committed", 3),
        )

        self.assertEqual(
            self.f.fixture.fixture.operation_count(), 2
        )

    def test_20_old_policy_bootstrap_without_retained_pins_known_limit(self):
        second = self.next_policy(
            revoked=("writer-alpha",)
        )

        self.publish(second)

        with self.assertRaises(ValueError):
            self.gateway.exchange(
                self.authorized(policy=second)
            )

        # Explicit known limit:
        # If the caller loses or rolls back its retained trust pins,
        # an independent in-memory authority can reopen the old policy.
        stale_authority = self.make_authority(
            self.initial,
            minimum_policy_epoch=1,
            expected_policy_sha256=digest(self.initial),
        )

        stale_gateway = self.make_gateway(
            stale_authority
        )

        result = self.send(
            self.authorized(),
            gateway=stale_gateway,
        )

        self.assertEqual(
            (result["status"], result["epoch"]),
            ("committed", 2),
        )

        self.assertEqual(
            self.f.fixture.fixture.operation_count(), 1
        )


if __name__ == "__main__":
    unittest.main()
